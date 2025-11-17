"""
LLM-PKG: Full-Featured Document Processing & QA Platform
=========================================================
This FastAPI application provides document upload, scanning (Docling-like),
and configurable LangChain/LangGraph pipelines for Q&A and analysis.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from rich.logging import RichHandler

from llm_pkg.auth.router import router as auth_router
from llm_pkg.chat_router import router as chat_router
from llm_pkg.config import graph_manager, llm_loader
from llm_pkg.database.models import create_tables
from llm_pkg.document_processor import DocumentProcessor
from llm_pkg.qa_engine import QAEngine
from llm_pkg.storage import STORAGE_DIR

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router)
app.include_router(chat_router)

# Initialize components
doc_processor = DocumentProcessor()
qa_engine = QAEngine(
    llm_loader, graph_manager
)  # Global instance for non-auth endpoints


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
    DEPRECATED: Upload a document for processing.
    
    This endpoint is deprecated and should not be used.
    Use POST /chat/upload-document instead for proper conversation isolation.
    
    This endpoint does not enforce conversation-specific isolation and may cause
    documents to bleed across conversations.
    """
    raise HTTPException(
        status_code=410,  # Gone
        detail="This endpoint is deprecated. Please use POST /chat/upload-document with conversation_id instead."
    )


@app.get("/documents")
async def list_documents() -> JSONResponse:
    """
    DEPRECATED: List all uploaded documents with metadata.
    
    This endpoint is deprecated and should not be used.
    Use GET /chat/documents?conversation_id={id} instead for proper conversation isolation.
    """
    raise HTTPException(
        status_code=410,  # Gone
        detail="This endpoint is deprecated. Please use GET /chat/documents with conversation_id instead."
    )


@app.post("/query")
async def query_documents(
    question: str = Form(...),
    provider: str | None = Form(None),
    document_name: str | None = Form(None),
) -> JSONResponse:
    """
    DEPRECATED: Query documents using LangChain/LangGraph.
    
    This endpoint is deprecated and should not be used.
    Use POST /chat/send instead for proper conversation isolation and tracking.
    """
    raise HTTPException(
        status_code=410,  # Gone
        detail="This endpoint is deprecated. Please use POST /chat/send with conversation_id instead."
    )


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
                "default": (
                    {
                        "provider": (
                            llm_loader.default.provider if llm_loader.default else None
                        ),
                        "model": (
                            llm_loader.default.model if llm_loader.default else None
                        ),
                    }
                    if llm_loader.default
                    else None
                ),
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

    # Probe database connection without crashing the app if unavailable
    from sqlalchemy import text
    from llm_pkg.database.models import engine

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("📊 Database connection OK")
    except Exception as e:
        logger.warning(
            "⚠️  Database is not reachable right now. The API will start, "
            "but endpoints that require the database will fail until it is available. "
            "Start Postgres (e.g., docker-compose up -d postgres) and run migrations (alembic upgrade head)."
        )
        logger.warning(f"DB connection error: {e}")

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
