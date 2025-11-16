"""
LLM-PKG: Document Processing & QA Platform
===========================================

A full-featured document processing and question-answering platform
combining document scanning, LangChain, and LangGraph.

Main Components:
- DocumentProcessor: Process and extract information from documents
- QAEngine: Question-answering with RAG
- LLMLoader: Multi-provider LLM configuration
- Storage: Document storage management

Example Usage:
    >>> from llm_pkg import DocumentProcessor, QAEngine, llm_loader, graph_manager
    >>> processor = DocumentProcessor()
    >>> qa = QAEngine(llm_loader, graph_manager)
    >>> result = await qa.query("What is this document about?")
"""

__version__ = "0.1.0"
__author__ = "Rajendra Yadav"
__email__ = "rajendra@example.com"

from llm_pkg.config import llm_loader, graph_manager, LLMLoader, LangGraphManager
from llm_pkg.document_processor import DocumentProcessor
from llm_pkg.qa_engine import QAEngine
from llm_pkg.storage import (
    save_document,
    list_documents,
    list_document_metadata,
    DocumentMetadata,
    STORAGE_DIR,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    # Main classes
    "DocumentProcessor",
    "QAEngine",
    "LLMLoader",
    "LangGraphManager",
    # Instances
    "llm_loader",
    "graph_manager",
    # Storage functions
    "save_document",
    "list_documents",
    "list_document_metadata",
    "DocumentMetadata",
    "STORAGE_DIR",
]
