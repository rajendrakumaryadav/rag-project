"""
Document storage and vector database operations.
Uses PostgreSQL with pgvector for vector storage.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from llm_pkg.database.models import Document as DBDocument
from llm_pkg.database.models import get_db

# Determine storage directory with safe fallbacks. Priority:
# 1) STORAGE_DIR env var
# 2) project-local ./data/uploads
# 3) docker default /app/data/uploads
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_STORAGE = os.getenv("STORAGE_DIR")
LOCAL_STORAGE = PROJECT_ROOT / "data" / "uploads"
DOCKER_STORAGE = Path("/app/data/uploads")

if ENV_STORAGE:
    STORAGE_DIR = Path(ENV_STORAGE)
elif LOCAL_STORAGE.exists():
    STORAGE_DIR = LOCAL_STORAGE
else:
    # Use docker path as last-resort default but do NOT create it at import time.
    STORAGE_DIR = DOCKER_STORAGE


def _ensure_storage_dir() -> None:
    """Create the storage directory if it doesn't exist.

    This is called lazily by functions that write to disk to avoid permission
    issues during import in development environments.
    """
    try:
        STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise RuntimeError(
            f"Unable to create storage directory at {STORAGE_DIR}: {e}"
        ) from e


class DocumentMetadata:
    """Document metadata for file storage."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.uploaded_at = datetime.fromtimestamp(path.stat().st_mtime)
        self.name = path.name
        self.size_bytes = path.stat().st_size

    def to_dict(self) -> dict[str, str | int]:
        return {
            "path": str(self.path),
            "uploaded_at": self.uploaded_at.isoformat(),
            "name": self.name,
            "size_bytes": self.size_bytes,
        }


def save_document(
    file_bytes: bytes, filename: str, user_id: Optional[int] = None
) -> Path:
    """Save document to file system and database."""
    _ensure_storage_dir()

    target_path = STORAGE_DIR / filename
    with target_path.open("wb") as out_file:
        out_file.write(file_bytes)

    # Save to database (best-effort) - tests may not have a DB available, so do not raise on DB errors
    import logging
    logger = logging.getLogger(__name__)

    db = None
    try:
        db = next(get_db())
        try:
            content = file_bytes.decode("utf-8", errors="ignore")
            db_doc = DBDocument(
                filename=filename,
                content=content,
                file_path=str(target_path),
                user_id=user_id,
            )
            db.add(db_doc)
            db.commit()
            db.refresh(db_doc)
        except Exception as e:
            # Log and continue without failing - some environments (tests) won't have DB configured
            logger.warning(f"Failed to save document metadata to DB: {e}")
    finally:
        if db is not None:
            db.close()

    return target_path


def list_documents() -> Iterable[Path]:
    """List all document files. If storage dir doesn't exist, return empty iterator."""
    if not STORAGE_DIR.exists():
        return []
    return sorted(STORAGE_DIR.glob("*"))


def list_document_metadata() -> list[DocumentMetadata]:
    """List metadata for all document files."""
    return [DocumentMetadata(path) for path in list_documents()]


def read_document(path: Path) -> Document:
    """Read document from file system."""
    with path.open("rb") as doc_file:
        content = doc_file.read()
    return Document(
        page_content=content.decode("utf-8", errors="ignore"),
        metadata={"source": str(path), "filename": path.name},
    )


class PostgreSQLVectorStore(VectorStore):
    """PostgreSQL-based vector store using pgvector."""

    def __init__(
        self,
        embedding_function: Embeddings,
        user_id: Optional[int] = None,
        conversation_id: Optional[int] = None
    ):
        self.embedding_function = embedding_function
        self.user_id = user_id
        self.conversation_id = conversation_id

    def add_texts(
        self, texts: List[str], metadatas: Optional[List[dict]] = None, **kwargs
    ) -> List[str]:
        """Add texts to the vector store."""
        embeddings = self.embedding_function.embed_documents(texts)

        db = next(get_db())
        try:
            ids = []
            for i, (text, embedding) in enumerate(zip(texts, embeddings)):
                metadata = metadatas[i] if metadatas else {}

                # Create document record
                db_doc = DBDocument(
                    filename=metadata.get("source", f"chunk_{i}"),
                    content=text,
                    embedding=embedding,
                    user_id=self.user_id,
                    conversation_id=self.conversation_id,
                )
                db.add(db_doc)
                db.commit()
                db.refresh(db_doc)
                ids.append(str(db_doc.id))

            return ids
        finally:
            db.close()

    def similarity_search(self, query: str, k: int = 10, **kwargs) -> List[Document]:
        """Search for similar documents.
        
        Args:
            query: Search query
            k: Number of results to return (default 10 to get chunks from multiple docs)
        """
        query_embedding = self.embedding_function.embed_query(query)

        db = next(get_db())
        try:
            # Use pgvector's cosine similarity
            from sqlalchemy import text

            # Build query to find similar documents
            # Only search within conversation-specific documents for strict isolation
            if self.conversation_id:
                sql = text("""
                    SELECT id, filename, content,
                           1 - (embedding <=> :query_embedding) as similarity
                    FROM documents
                    WHERE embedding IS NOT NULL
                    AND user_id = :user_id
                    AND conversation_id = :conversation_id
                    ORDER BY embedding <=> :query_embedding
                    LIMIT :k
                """)
                result = db.execute(
                    sql,
                    {
                        "query_embedding": query_embedding,
                        "user_id": self.user_id,
                        "conversation_id": self.conversation_id,
                        "k": k,
                    },
                )
            else:
                # If no conversation_id, only search documents without conversation
                sql = text("""
                    SELECT id, filename, content,
                           1 - (embedding <=> :query_embedding) as similarity
                    FROM documents
                    WHERE embedding IS NOT NULL
                    AND user_id = :user_id
                    AND conversation_id IS NULL
                    ORDER BY embedding <=> :query_embedding
                    LIMIT :k
                """)
                result = db.execute(
                    sql,
                    {"query_embedding": query_embedding, "user_id": self.user_id, "k": k},
                )

            documents = []
            for row in result:
                doc = Document(
                    page_content=row.content,
                    metadata={
                        "source": row.filename,
                        "id": row.id,
                        "similarity": float(row.similarity),
                    },
                )
                documents.append(doc)

            return documents
        finally:
            db.close()

    def delete(self, ids: Optional[List[str]] = None, **kwargs) -> None:
        """Delete documents by IDs."""
        if not ids:
            return

        db = next(get_db())
        try:
            doc_ids = [int(id) for id in ids]
            db.query(DBDocument).filter(DBDocument.id.in_(doc_ids)).delete()
            db.commit()
        finally:
            db.close()

    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        **kwargs,
    ) -> PostgreSQLVectorStore:
        """Create vector store from texts."""
        instance = cls(embedding, **kwargs)
        instance.add_texts(texts, metadatas)
        return instance
