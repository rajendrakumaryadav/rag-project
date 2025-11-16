from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from langchain_core.documents import Document

STORAGE_DIR = Path(__file__).resolve().parents[1] / "data" / "uploads"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


class DocumentMetadata:
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


def save_document(file_bytes: bytes, filename: str) -> Path:
    target_path = STORAGE_DIR / filename
    with target_path.open("wb") as out_file:
        out_file.write(file_bytes)
    return target_path


def list_documents() -> Iterable[Path]:
    return sorted(STORAGE_DIR.glob("*"))


def list_document_metadata() -> list[DocumentMetadata]:
    return [DocumentMetadata(path) for path in list_documents()]


def read_document(path: Path) -> Document:
    with path.open("rb") as doc_file:
        content = doc_file.read()
    return Document(page_content=content.decode("utf-8", errors="ignore"))
