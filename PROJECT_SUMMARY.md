# Project Summary: LLM-PKG

## Overview

**LLM-PKG** is a practical document processing and question-answering platform built with:
- **uv**: Fast Python package manager (used in setup scripts)
- **LangChain**: LLM application framework
- **LangGraph**: Workflow orchestration
- **FastAPI**: Modern web framework
- **Docling-like processing**: Document scanning and structure analysis
- **PostgreSQL + pgvector**: Vector storage and retrieval (primary storage)

## What Has Been Created

### Core Application Files

1. **`llm_pkg/app.py`** - FastAPI server with REST API endpoints
   - Document upload and management
   - Q&A endpoints
   - Configuration management
   - Health checks

2. **`llm_pkg/document_processor.py`** - Docling-like document processing
   - PDF, TXT, MD format support
   - Text extraction with pdfplumber and pypdf
   - Structure analysis (headings, tables, lists)
   - Metadata extraction
   - LangChain document creation

3. **`llm_pkg/qa_engine.py`** - Q&A engine with RAG
   - LangChain / LangGraph integration
   - Vector store using PostgreSQL + pgvector for retrieval
   - Multi-provider support
   - Document chunking and embedding

4. **`llm_pkg/config.py`** - Configuration management
   - TOML-based configuration with environment variable interpolation
   - Multi-provider support (OpenAI, Azure, Ollama, OpenRouter)
   - Hot-reload capability

5. **`llm_pkg/storage.py`** - Document storage and metadata management

6. **`llm_pkg/cli.py`** - Command-line interface
   - Interactive mode and direct commands

### Configuration Files

7. **`config/llm_config.toml`** - LLM provider configuration
   - OpenAI, Azure, Ollama, OpenRouter sections
   - Examples of creative vs precise parameter groups

8. **`pyproject.toml`** - Project configuration (dependencies, entry points)

### Documentation & Helpers

9. **`README.md`** - Main documentation and quickstart
10. **`QUICKSTART.md`** - 5-minute guide (updated for Docker-first usage)
11. **`CONFIGURATION.md`** - Provider setup and troubleshooting
12. **`setup.sh`, `Makefile`** - Developer helper scripts

## Key Features Implemented

- Document upload & processing (PDF/TXT/MD)
- Docling-like scanning and structure extraction
- RAG-based Q&A with LangChain and LangGraph
- PostgreSQL + pgvector vector storage (preferred)
- Configurable multi-provider LLM setup
- REST API and interactive CLI
- Docker Compose for multi-service deployment

## How to Use (summary)

### Docker (recommended)

```bash
cd /home/rajendrayadav/Documents/projects/llm-pkg
cp .env.example .env
# update .env with API keys
docker-compose up --build
```

Access API at http://localhost/api and frontend at http://localhost.

### Local development

Follow the README development section to create a virtualenv, install dependencies, start Postgres (docker recommended), run migrations (alembic), and start the backend with `uvicorn llm_pkg.app:app --reload`.

## Next Steps / Customization

- Configure provider API keys in `config/llm_config.toml` or `.env`
- Extend `llm_pkg/qa_engine.py` for custom workflows
- Add new document formats in `llm_pkg/document_processor.py`
- Add endpoints in `llm_pkg/app.py` for integrations

## Testing & Maintenance

Run unit tests with the provided Makefile:

```bash
make test
```

Format and lint using:

```bash
make format
make lint
```

## Status

The project is functional and set up for Docker-based deployment and local development. The primary vector store is PostgreSQL with pgvector; legacy FAISS references were removed in favor of the database-backed approach.

## Runtime (Docker Compose)

When using the provided Docker Compose setup the services and ports are mapped as follows (see `docker-compose.yml` and `nginx.conf`):

- `postgres` (PostgreSQL + pgvector): container listens on 5432 (host mapped to 5432).
- `backend` (FastAPI): runs inside Docker on port 8000. The container command runs migrations then starts Uvicorn on `--port 8000`.
- `nginx` (reverse proxy + static frontend): exposes container port 80 to host port 8080 and proxies `/api/` requests to the backend at `backend:8000`.

Therefore, when running with Docker Compose:
- Frontend (served by nginx): http://localhost:8080
- Backend API (proxied): http://localhost:8080/api
- API docs (proxied): http://localhost:8080/api/docs
- Health (proxied): http://localhost:8080/health

If you access the backend directly (not via nginx), use http://localhost:8000 for API calls.
