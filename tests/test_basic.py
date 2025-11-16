"""
Tests for LLM-PKG
=================
"""

import pytest

from llm_pkg.document_processor import DocumentProcessor
from llm_pkg.storage import DocumentMetadata, list_documents, save_document


class TestStorage:
    """Test storage module."""

    def test_save_document(self, tmp_path):
        """Test saving a document."""
        content = b"Test content"
        filename = "test.txt"

        # Mock STORAGE_DIR
        import llm_pkg.storage as storage

        storage.STORAGE_DIR = tmp_path

        path = save_document(content, filename)

        assert path.exists()
        assert path.name == filename
        assert path.read_bytes() == content

    def test_list_documents(self, tmp_path):
        """Test listing documents."""
        import llm_pkg.storage as storage

        storage.STORAGE_DIR = tmp_path

        # Create test files
        (tmp_path / "file1.txt").write_text("Content 1")
        (tmp_path / "file2.txt").write_text("Content 2")

        docs = list(list_documents())

        assert len(docs) == 2
        assert all(d.exists() for d in docs)

    def test_document_metadata(self, tmp_path):
        """Test document metadata."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")

        metadata = DocumentMetadata(test_file)

        assert metadata.name == "test.txt"
        assert metadata.size_bytes > 0
        assert metadata.uploaded_at is not None


class TestDocumentProcessor:
    """Test document processor."""

    @pytest.mark.asyncio
    async def test_process_text_file(self, tmp_path):
        """Test processing a text file."""
        processor = DocumentProcessor()

        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("This is a test document.\nWith multiple lines.")

        result = await processor.process_document(test_file)

        assert result["filename"] == "test.txt"
        assert result["format"] == "txt"
        assert "full_text" in result
        assert result["summary"]["total_lines"] == 2

    @pytest.mark.asyncio
    async def test_unsupported_format(self, tmp_path):
        """Test processing unsupported format."""
        processor = DocumentProcessor()

        # Create unsupported file
        test_file = tmp_path / "test.xyz"
        test_file.write_text("Content")

        with pytest.raises(ValueError):
            await processor.process_document(test_file)

    def test_create_langchain_documents(self):
        """Test creating LangChain documents."""
        processor = DocumentProcessor()

        processed_data = {
            "filename": "test.txt",
            "format": "txt",
            "full_text": "Test content",
            "summary": {},
        }

        docs = processor.create_langchain_documents(processed_data)

        assert len(docs) == 1
        assert docs[0].page_content == "Test content"
        assert docs[0].metadata["source"] == "test.txt"


class TestConfig:
    """Test configuration loading."""

    def test_llm_loader(self):
        """Test LLM loader."""
        from llm_pkg.config import llm_loader

        # Should have loaded config
        assert len(llm_loader.providers) > 0
        assert llm_loader.default is not None


@pytest.mark.asyncio
async def test_fastapi_health():
    """Test FastAPI health endpoint."""
    from httpx import ASGITransport, AsyncClient

    from llm_pkg.app import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")

        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_fastapi_root():
    """Test FastAPI root endpoint."""
    from httpx import ASGITransport, AsyncClient

    from llm_pkg.app import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/")

        assert response.status_code == 200
        assert "message" in response.json()


@pytest.mark.asyncio
async def test_fastapi_config():
    """Test FastAPI config endpoint."""
    from httpx import ASGITransport, AsyncClient

    from llm_pkg.app import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/config")

        assert response.status_code == 200
        assert "providers" in response.json()
