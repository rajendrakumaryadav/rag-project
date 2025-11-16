"""
LLM-PKG: Full-Featured Document Processing & QA Platform
=========================================================
This FastAPI application provides document upload, scanning (Docling-like),
and configurable LangChain/LangGraph pipelines for Q&A and analysis.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from rich.logging import RichHandler

from llm_pkg.config import graph_manager, llm_loader
from llm_pkg.document_processor import DocumentProcessor
from llm_pkg.qa_engine import QAEngine
from llm_pkg.storage import STORAGE_DIR, list_document_metadata, save_document

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger("llm_pkg")

# Initialize FastAPI
app = FastAPI(
    title="LLM-PKG: Document Processing & QA Platform",
    description="Upload documents, process them with Docling-like scanning, and query using LangChain/LangGraph",
    version="0.1.0",
)

# Initialize components
doc_processor = DocumentProcessor()
qa_engine = QAEngine(llm_loader, graph_manager)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with API information."""
    return {
        "message": "LLM-PKG Document Processing & QA Platform",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "llm-pkg"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> JSONResponse:
    """
    Upload a document for processing.

    Supports: PDF, TXT, DOCX, and other text-based formats.
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")

        # Read file content
        content = await file.read()

        # Save document
        file_path = save_document(content, file.filename)
        logger.info(f"Document uploaded: {file.filename}")

        # Process document (Docling-like scanning)
        processed_data = await doc_processor.process_document(file_path)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Document uploaded and processed successfully",
                "filename": file.filename,
                "path": str(file_path),
                "processed_data": processed_data,
            },
        )
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_documents() -> JSONResponse:
    """List all uploaded documents with metadata."""
    try:
        docs = list_document_metadata()
        return JSONResponse(
            status_code=200,
            content={
                "count": len(docs),
                "documents": [doc.to_dict() for doc in docs],
            },
        )
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query")
async def query_documents(
    question: str = Form(...),
    provider: str | None = Form(None),
    document_name: str | None = Form(None),
) -> JSONResponse:
    """
    Query documents using LangChain/LangGraph.

    Args:
        question: The question to ask
        provider: Optional provider name (openai, azure, ollama)
        document_name: Optional specific document to query
    """
    try:
        if not question:
            raise HTTPException(status_code=400, detail="Question is required")

        logger.info(f"Processing query: {question[:50]}...")

        # Execute query using QA engine
        result = await qa_engine.query(
            question=question,
            provider=provider,
            document_name=document_name,
        )

        return JSONResponse(
            status_code=200,
            content={
                "question": question,
                "answer": result["answer"],
                "sources": result.get("sources", []),
                "provider": result.get("provider"),
                "metadata": result.get("metadata", {}),
            },
        )
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_config() -> JSONResponse:
    """Get current LLM configuration."""
    try:
        return JSONResponse(
            status_code=200,
            content={
                "providers": {
                    name: {
                        "provider": cfg.provider,
                        "model": cfg.model,
                    }
                    for name, cfg in llm_loader.providers.items()
                },
                "default": {
                    "provider": llm_loader.default.provider
                    if llm_loader.default
                    else None,
                    "model": llm_loader.default.model if llm_loader.default else None,
                }
                if llm_loader.default
                else None,
            },
        )
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/config/reload")
async def reload_config() -> JSONResponse:
    """Reload LLM configuration from TOML file."""
    try:
        llm_loader.reload()
        logger.info("Configuration reloaded successfully")
        return JSONResponse(
            status_code=200,
            content={"message": "Configuration reloaded successfully"},
        )
    except Exception as e:
        logger.error(f"Error reloading config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{filename}")
async def delete_document(filename: str) -> JSONResponse:
    """Delete a specific document."""
    try:
        file_path = STORAGE_DIR / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")

        file_path.unlink()
        logger.info(f"Document deleted: {filename}")

        return JSONResponse(
            status_code=200,
            content={"message": f"Document '{filename}' deleted successfully"},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    logger.info("🚀 LLM-PKG starting up...")
    logger.info(f"📁 Storage directory: {STORAGE_DIR}")
    logger.info(f"⚙️  Loaded {len(llm_loader.providers)} provider(s)")
    logger.info("✅ Application ready!")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("👋 LLM-PKG shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "llm_pkg.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


def main() -> None:
    """Entry point for the console script `llm-pkg-server`.

    Runs a uvicorn server pointing at this FastAPI app. Mirrors the behavior of
    `python -m llm_pkg.app` but without requiring -m execution.
    """
    import uvicorn

    uvicorn.run(
        "llm_pkg.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
