# LLM-PKG: Document Processing & QA Platform - Generated using GitHub Copilot + Visual Studio Code


![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103+-green.svg)
![React](https://img.shields.io/badge/React-18+-blue.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector%20%28pg16%29-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-1.0+-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A full-featured document processing and question-answering platform that combines document scanning (Docling-like), LangChain, and LangGraph to create an intelligent document analysis system.

<img width="1920" height="1008" alt="image" src="https://github.com/user-attachments/assets/c44e488e-1dd3-4fdb-aa81-07417ab39078" />

## Quick highlights

- Upload and process PDFs, TXT and Markdown
- Docling-like document scanning (structure, metadata, tables)
- RAG-powered Q&A using configurable LLM providers (OpenAI, Azure, Ollama, OpenRouter)
- PostgreSQL with pgvector for embeddings and retrieval (recommended over legacy FAISS)
- FastAPI backend + React frontend (Dockerized)
- CLI for quick interactions and batch processing

## Table of Contents

- Features
- Architecture
- Prerequisites
- Quick Start (Docker recommended)
- Development setup
- Usage examples (API / Python / CLI)
- Configuration
- Project structure
- Troubleshooting & tests

## Features

- Document upload & processing: PDF, TXT, MD
- Docling-like scanning: headings, lists, tables, layout and metadata
- Retrieval-Augmented Generation (RAG) with LangChain and LangGraph
- Multi-provider LLM support (OpenAI, Azure OpenAI, Ollama, OpenRouter)
- JWT authentication and user management
- Vector storage using PostgreSQL + pgvector
- Docker Compose for easy deployment (backend, frontend, nginx, postgres)

## Architecture (high level)

```
Frontend (React)  <->  Nginx  <->  FastAPI backend  <->  PostgreSQL (pgvector)
                                          ^
                                          |-- LangChain / LangGraph / LLM providers
```

## Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend development)
- Docker & Docker Compose (recommended)
- uv (optional; used by the project's setup scripts)
- Optional: Ollama for local LLM inference

## Quick Start (Docker - recommended)

1. Clone and prepare the project root:

```bash
cd /home/rajendrayadav/Documents/projects/llm-pkg
cp .env.example .env
# Edit .env to add API keys and secrets
```

2. Start services with Docker Compose (build on first run):

```bash
# from project root
docker-compose up --build
# or in background
docker-compose up -d --build
```

3. Access the services:

- Frontend: http://localhost:8080
- API: http://localhost:8080/api
- API docs (Swagger/OpenAPI): http://localhost:8080/api/docs
- Health: http://localhost:8080/health

Notes:
- If you change configuration files, restart the backend container or call the config reload endpoint: POST /api/config/reload
- The `.env` file is the primary place to provide provider API keys. Do not commit it to git.

## Development setup (local)

1. Create a Python virtualenv and install the package:

```bash
# Using uv (project uses uv in scripts) or standard venv
uv venv
source .venv/bin/activate
uv pip install -e .
```

2. Install DB dependencies (if needed):

```bash
pip install pgvector alembic sqlalchemy psycopg2-binary
```

3. Start a local Postgres with pgvector support (docker recommended):

The project uses the official pgvector Postgres image in `docker-compose.yml` (image: `pgvector/pgvector:pg16`). If you prefer to run Postgres locally for development, use the pgvector image which includes the pgvector extension preinstalled.

```bash
# Run pgvector-enabled Postgres (pg16)
docker run -d --name pgvector-dev \
  -e POSTGRES_DB=llm_pkg \
  -e POSTGRES_USER=llm_user \
  -e POSTGRES_PASSWORD=llm_password \
  -p 5432:5432 pgvector/pgvector:pg16
alembic upgrade head
```

4. Frontend development (optional):

```bash
cd frontend
npm install
npm start
```

5. Run backend locally:

```bash
uvicorn llm_pkg.app:app --reload
```

Visit frontend at http://localhost:3000 and API at http://localhost:8000 when running locally.

## Usage examples

API examples (replace host/port depending on your setup):

Upload a document:

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"
```

List documents:

```bash
curl -X GET "http://localhost:8000/documents"
```

Query documents (RAG):

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "question=What are the main topics in this document?" \
  -d "provider=openai"
```

Python usage (example):

```python
from llm_pkg.config import llm_loader, graph_manager
from llm_pkg.document_processor import DocumentProcessor
from llm_pkg.qa_engine import QAEngine
from pathlib import Path

# Initialize components
doc_processor = DocumentProcessor()
qa_engine = QAEngine(llm_loader, graph_manager)

async def process_doc():
    file_path = Path("document.pdf")
    processed = await doc_processor.process_document(file_path)
    print(processed.get("summary"))
```

CLI examples:

```bash
# Interactive mode
llm-pkg

# Direct commands
llm-pkg upload report.pdf
llm-pkg query "Summarize the executive summary"
```

## Configuration

Primary configuration for providers lives in `config/llm_config.toml`. You can also use environment variables (see `.env.example`).

Key configuration tips:
- Use environment variables for API keys to avoid committing secrets
- For local development, Ollama provides a convenient local model server
- In production, prefer robust providers (Azure/OpenAI) and configure rate limits and retries

See `CONFIGURATION.md` and `OPENROUTER_GUIDE.md` for provider-specific instructions.

## Project structure

A high-level view of important files and directories:

```
src/llm_pkg/          # Python package (FastAPI app, processors, QA engine, CLI)
frontend/             # React frontend
config/               # llm_config.toml and related config
data/uploads/         # Uploaded files
alembic/              # DB migrations
Dockerfile & docker-compose.yml
```

## CLI (Command-line interface)

This project includes a small CLI tool that lets you interact with the app from the command line. The console script is installed as `llm-pkg` when you install the package in editable mode or as a packaged install.

Installation (local development):

```bash
# Create and activate virtualenv
python -m venv .venv
source .venv/bin/activate

# Install the package in editable mode (creates the `llm-pkg` console script)
pip install -e .
```

Run the CLI (interactive mode):

```bash
# Start interactive mode
llm-pkg
# Or, without installing the console script
python -m llm_pkg.cli
```

Direct (non-interactive) commands:

```bash
# Upload a file (local path)
llm-pkg upload path/to/document.pdf

# List uploaded documents
llm-pkg list

# Query (RAG)
llm-pkg query "Summarize the executive summary"

# Show configured LLM providers
llm-pkg config
```

Running the CLI inside the backend container (Docker Compose):

```bash
# List documents inside the running backend container
docker-compose exec backend llm-pkg list

# Upload a file that is mounted into the container at /app/data/uploads
# (copy the file into ./data/uploads on the host so it's available inside the container)
docker-compose exec backend llm-pkg upload /app/data/uploads/report.pdf

# Run a query inside the container
docker-compose exec backend llm-pkg query "What are the key points?"
```

Notes & tips:
- The `llm-pkg` console script is defined in `pyproject.toml` under `[project.scripts]` and points to `llm_pkg.cli:main`.
- When running commands that access the database or storage, ensure the backend or Postgres containers are running (if using Docker Compose) or that your local DB is reachable and migrations have been applied (`alembic upgrade head`).
- Uploads are persisted to `./data/uploads` on the host (mounted into the backend at `/app/data/uploads` by `docker-compose.yml`).

## Tests & development commands

Run unit tests:

```bash
make test
```

Development helpers are available in the `Makefile` (format, lint, test, run).

## Troubleshooting

- API Key errors: re-check `.env` / `config/llm_config.toml` values
- Ollama connection refused: run `ollama serve` and verify host/port
- Database errors: ensure Postgres is reachable and migrations have run

## Contribution & License

- License: MIT (see `LICENSE`)
- Contributions welcome: open issues or PRs

I made the following precise edits to match the runtime defined in `docker-compose.yml` and `nginx.conf`:

- Replaced references to `http://localhost` (frontend) with `http://localhost:8080` to match nginx host port mapping.
- Clarified API endpoints when using Docker Compose: `http://localhost:8080/api` (via nginx proxy) and direct backend URL `http://localhost:8000` for when you access the backend container or run locally.
- Mentioned service names (`postgres`, `backend`, `nginx`) and that `backend` is reachable inside Docker at `backend:8000` and that nginx proxies `/api/` to `backend:8000`.
- Noted health check path: `http://localhost:8080/health` (proxied to backend `/health`).
