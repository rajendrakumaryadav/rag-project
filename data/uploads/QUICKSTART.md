# Quick Start Guide

Get up and running with LLM-PKG in 5 minutes (Docker recommended).

## What changed / why
This guide has been updated to exactly reflect the runtime defined in the project's Docker files and nginx config. Specifically:
- The backend service listens on port 8000 inside the container and is published to the host at 8000 by docker-compose.
- Nginx listens on port 80 inside its container and is published to the host at 8080 by docker-compose; nginx proxies API requests from `/api/` to the backend upstream `backend:8000`.
- The frontend build sets `REACT_APP_API_URL=/api` so the production build expects the proxied path.
- Docker build args forwarded from `docker-compose.yml`: `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `AZURE_OPENAI_API_KEY`.

## Prerequisites

- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- Docker & Docker Compose (recommended)
- API key for at least one LLM provider (OpenAI, Azure, or Ollama)

## Installation

### Option 1: Docker (Recommended)

```bash
cd /home/rajendrayadav/Documents/projects/llm-pkg
cp .env.example .env
# Edit .env and add your API keys and SECRET_KEY
# docker-compose uses environment variables and build args (OPENAI_API_KEY, AZURE_OPENAI_API_KEY, GOOGLE_API_KEY).
docker-compose up --build
# Or run in background:
# docker-compose up -d --build
```

Important runtime notes (from `docker-compose.yml`, `Dockerfile.nginx`, and `nginx.conf`):
- Services in docker-compose:
  - `postgres` (image: `pgvector/pgvector:pg16`), host port 5432 -> container 5432.
  - `backend` (built from project Dockerfile), host port 8000 -> container 8000.
  - `nginx` (built from `Dockerfile.nginx`), host port 8080 -> container 80.
- Nginx upstream name for the backend is `backend:8000` (see `nginx.conf`).
- Nginx proxies requests from the host path `/api/` to the backend (so production frontend uses `/api` as API base).
- The frontend build sets `REACT_APP_API_URL=/api` in the nginx Dockerfile, so the production frontend expects the proxied path by default.
- Data upload directory on the host is mounted into the backend at `./data/uploads:/app/data/uploads`.

After containers are up:
- Frontend (served by nginx): http://localhost:8080
- API via nginx proxy (proxied path): http://localhost:8080/api
- Swagger / OpenAPI docs via nginx: http://localhost:8080/api/docs
- Health (proxied): http://localhost:8080/health

If you run the backend directly (not via nginx), the backend listens on port 8000 inside the container and is published to the host at 8000 by the compose file:
- Backend API direct: http://localhost:8000
- Docs direct: http://localhost:8000/docs
- Health direct: http://localhost:8000/health

### Option 2: Local development (manual)

```bash
# Create virtual environment and install
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Install DB-related packages (if needed)
pip install pgvector alembic sqlalchemy psycopg2-binary
```

Start a local Postgres (docker recommended):

```bash
docker run -d --name postgres-dev \
  -e POSTGRES_DB=llm_pkg \
  -e POSTGRES_USER=llm_user \
  -e POSTGRES_PASSWORD=llm_password \
  -p 5432:5432 postgres:15
alembic upgrade head
```

Run frontend locally (optional):

```bash
cd frontend
npm install
npm start
```

Run backend locally:

```bash
uvicorn llm_pkg.app:app --reload --host 0.0.0.0 --port 8000
```

Visit frontend at http://localhost:3000 (when running `npm start`) and backend API at http://localhost:8000.

## First Steps

1. Upload a document (when using Docker + nginx host / proxied API):

```bash
curl -X POST "http://localhost:8080/api/upload" \
  -H "accept: application/json" \
  -F "file=@/path/to/document.pdf"
```

If you're talking directly to the backend (no nginx proxy):

```bash
curl -X POST "http://localhost:8000/upload" -F "file=@/path/to/document.pdf"
```

2. List documents (proxied and direct examples):

```bash
# via nginx proxy
curl http://localhost:8080/api/documents

# direct to backend
curl http://localhost:8000/documents
```

3. Query documents (RAG) — proxied and direct:

```bash
# via nginx proxy
curl -X POST "http://localhost:8080/api/query" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "question=What are the main topics?" -d "provider=openai"

# direct to backend
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "question=What are the main topics?" -d "provider=openai"
```

## Example Workflow (Docker)

```bash
# 1. Start all services
docker-compose up --build

# 2. Upload a document via nginx host (proxies to backend)
curl -X POST "http://localhost:8080/api/upload" -F "file=@research_paper.pdf"

# 3. Query the document
curl -X POST "http://localhost:8080/api/query" -d "question=What are the key findings?" -d "provider=openai"

# 4. View all documents
curl http://localhost:8080/api/documents
```

## Build args, environment and other notes

- `docker-compose.yml` forwards build args `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `AZURE_OPENAI_API_KEY` into the backend image build. Ensure these are present in your environment (or in a `.env` file) when running `docker-compose build`.
- The backend `command` runs `alembic upgrade head` on startup and then starts `uvicorn llm_pkg.app:app --host 0.0.0.0 --port 8000` inside the container.
- Host -> container port mappings in `docker-compose.yml`:
  - postgres: 5432:5432
  - backend: 8000:8000
  - nginx: 8080:80
- The host upload folder `./data/uploads` is mounted into the container at `/app/data/uploads`.

## Common Issues

- "API Key Not Found": ensure API keys are present in `.env` or `config/llm_config.toml` and that the backend container has access to them via environment or build args. `docker-compose.yml` forwards several BUILD args and environment variables; check `.env` for values used by compose.
- Ollama: start the daemon `ollama serve` and verify `curl http://localhost:11434` responds (if you enabled the optional ollama service).
- Database: verify Postgres connectivity and run `alembic upgrade head` if migrations are missing. The `backend` service runs `alembic upgrade head` on start (see docker-compose `command`).

## Next Steps

- Read `README.md` and `CONFIGURATION.md` for provider-specific instructions.
- Try different providers and models.
- Run the examples: `python examples.py`.

## Useful Commands

```bash
# Development
make dev
make test
make format
make lint

# Run
make run
make cli

# Docker
docker-compose up --build
docker-compose logs -f
```

---

**Happy building!**
