"""
Document Processor - Docling-like Document Scanning
====================================================
Processes various document formats, extracts text, metadata, and structure.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import pdfplumber
import pypdf
from langchain_core.documents import Document

logger = logging.getLogger("llm_pkg.document_processor")


class DocumentProcessor:
    """
    Docling-like document processor.
    Extracts text, metadata, structure, and semantic information from documents.
    """

    def __init__(self):
        self.supported_formats = {".pdf", ".txt", ".md"}

    async def process_document(self, file_path: Path) -> dict[str, Any]:
        """
        Process a document and extract all relevant information.

        Args:
            file_path: Path to the document

        Returns:
            Dictionary containing processed document data
        """
        suffix = file_path.suffix.lower()

        if suffix not in self.supported_formats:
            raise ValueError(f"Unsupported format: {suffix}")

        logger.info(f"Processing document: {file_path.name}")

        if suffix == ".pdf":
            return await self._process_pdf(file_path)
        elif suffix in {".txt", ".md"}:
            return await self._process_text(file_path)
        else:
            raise ValueError(f"Unsupported format: {suffix}")

    async def _process_pdf(self, file_path: Path) -> dict[str, Any]:
        """Process PDF documents with advanced extraction."""
        metadata = {}
        pages = []
        full_text = ""

        # Extract basic metadata using pypdf
        try:
            with open(file_path, "rb") as f:
                pdf_reader = pypdf.PdfReader(f)
                metadata = {
                    "num_pages": len(pdf_reader.pages),
                    "metadata": pdf_reader.metadata or {},
                }
        except Exception as e:
            logger.warning(f"Error extracting PDF metadata: {e}")

        # Extract text and structure using pdfplumber
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    text = page.extract_text() or ""

                    # Extract tables
                    tables = page.extract_tables()

                    # Extract words with positions (for layout analysis)
                    words = page.extract_words()

                    page_data = {
                        "page_number": page_num,
                        "text": text,
                        "num_tables": len(tables) if tables else 0,
                        "num_words": len(words) if words else 0,
                        "width": page.width,
                        "height": page.height,
                    }

                    # Add table data if present
                    if tables:
                        page_data["tables"] = [
                            {"rows": len(table), "cols": len(table[0]) if table else 0}
                            for table in tables
                        ]

                    pages.append(page_data)
                    full_text += f"\n--- Page {page_num} ---\n{text}\n"

        except Exception as e:
            logger.error(f"Error processing PDF with pdfplumber: {e}")
            raise

        # Analyze document structure
        structure = self._analyze_structure(full_text, pages)

        return {
            "filename": file_path.name,
            "format": "pdf",
            "metadata": metadata,
            "pages": pages,
            "structure": structure,
            "full_text": full_text,
            "summary": {
                "total_pages": len(pages),
                "total_words": sum(p.get("num_words", 0) for p in pages),
                "has_tables": any(p.get("num_tables", 0) > 0 for p in pages),
            },
        }

    async def _process_text(self, file_path: Path) -> dict[str, Any]:
        """Process plain text and markdown documents."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            # Basic text analysis
            lines = text.split("\n")
            words = text.split()

            structure = self._analyze_structure(text, [])

            return {
                "filename": file_path.name,
                "format": file_path.suffix[1:],
                "metadata": {
                    "size_bytes": file_path.stat().st_size,
                },
                "full_text": text,
                "structure": structure,
                "summary": {
                    "total_lines": len(lines),
                    "total_words": len(words),
                    "total_characters": len(text),
                },
            }
        except Exception as e:
            logger.error(f"Error processing text file: {e}")
            raise

    def _analyze_structure(self, text: str, pages: list[dict]) -> dict[str, Any]:
        """
        Analyze document structure (Docling-like).
        Identifies sections, headings, lists, etc.
        """
        lines = text.split("\n")

        # Detect potential headings (simple heuristic)
        headings = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and len(stripped) < 100:
                # Check if line is all caps or starts with number/marker
                if (
                    stripped.isupper()
                    or stripped[0].isdigit()
                    or stripped.startswith("#")
                    or stripped.startswith("*")
                ):
                    headings.append(
                        {
                            "line_number": i + 1,
                            "text": stripped[:50],
                        }
                    )

        # Detect lists
        list_items = sum(
            1 for line in lines if line.strip().startswith(("•", "-", "*", "1.", "2."))
        )

        return {
            "num_headings": len(headings[:10]),  # Limit to first 10
            "headings": headings[:10],
            "num_list_items": list_items,
            "has_structure": len(headings) > 0,
        }

    def create_langchain_documents(
        self, processed_data: dict[str, Any]
    ) -> list[Document]:
        """
        Convert processed data to LangChain Document objects.

        Args:
            processed_data: Output from process_document

        Returns:
            List of LangChain Document objects
        """
        documents = []

        if processed_data["format"] == "pdf":
            # Create one document per page
            for page in processed_data["pages"]:
                doc = Document(
                    page_content=page["text"],
                    metadata={
                        "source": processed_data["filename"],
                        "page": page["page_number"],
                        "format": "pdf",
                    },
                )
                documents.append(doc)
        else:
            # Single document for text files
            doc = Document(
                page_content=processed_data["full_text"],
                metadata={
                    "source": processed_data["filename"],
                    "format": processed_data["format"],
                },
            )
            documents.append(doc)

        return documents
