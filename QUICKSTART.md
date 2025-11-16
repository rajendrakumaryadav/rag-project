# Quick Start Guide

Get up and running with LLM-PKG in 5 minutes!

## Prerequisites

- Python 3.11+
- Git (optional)
- API key for at least one LLM provider (OpenAI, Azure, or Ollama)

## Installation

### Option 1: Automated Setup (Recommended)

```bash
cd /home/rajendrayadav/Documents/projects/llm-pkg/src
./setup.sh
```

### Option 2: Manual Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

## Configuration

### 1. Set Up API Keys

**For OpenAI:**
```bash
# Edit config/llm_config.toml
# Add your OpenAI API key
api_key = "sk-your-actual-key-here"
```

**For Ollama (Free, Local):**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3

# Config is already set for localhost
```

### 2. Verify Configuration

```bash
# Check configuration
make config

# Or using Python
python -c "from llm_pkg.config import llm_loader; print(llm_loader.providers)"
```

## Running the Application

### Option 1: Web Server (Recommended)

```bash
# Start the server
make run

# Or manually
uvicorn llm_pkg.app:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

### Option 2: CLI Interface

```bash
# Interactive mode
make cli

# Or manually
python -m llm_pkg.cli

# Direct commands
llm-pkg upload document.pdf
llm-pkg query "What is this about?"
```

### Option 3: Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## First Steps

### 1. Upload a Document

**Using API:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/document.pdf"
```

**Using CLI:**
```bash
llm-pkg upload document.pdf
```

### 2. List Documents

**Using API:**
```bash
curl http://localhost:8000/documents
```

**Using CLI:**
```bash
llm-pkg list
```

### 3. Ask Questions

**Using API:**
```bash
curl -X POST "http://localhost:8000/query" \
  -F "question=What are the main topics?" \
  -F "provider=openai"
```

**Using CLI:**
```bash
llm-pkg query "What are the main topics?"
```

## Example Workflow

```bash
# 1. Start the server
make run

# 2. In another terminal, upload a document
curl -X POST "http://localhost:8000/upload" \
  -F "file=@research_paper.pdf"

# 3. Query the document
curl -X POST "http://localhost:8000/query" \
  -F "question=What are the key findings?" \
  -F "provider=openai"

# 4. View all documents
curl http://localhost:8000/documents
```

## Interactive Examples

Run the included examples:

```bash
python examples.py
```

This will demonstrate:
- Document upload and processing
- Querying with different providers
- Custom LangGraph workflows
- Batch processing

## Common Issues

### "API Key Not Found"
- Check `config/llm_config.toml` has your API key
- Ensure quotes are correct: `api_key = "sk-..."`

### "Connection Refused" (Ollama)
- Start Ollama: `ollama serve`
- Verify it's running: `curl http://localhost:11434`

### "Module Not Found"
- Activate virtual environment: `source .venv/bin/activate`
- Reinstall: `uv pip install -e .`

## Next Steps

1. **Read the full documentation**: See [README.md](README.md)
2. **Configure multiple providers**: See [CONFIGURATION.md](CONFIGURATION.md)
3. **Explore the API**: Visit http://localhost:8000/docs
4. **Run tests**: `make test`
5. **Customize workflows**: Edit `llm_pkg/qa_engine.py`

## Useful Commands

```bash
# Development
make dev          # Full dev workflow (format, lint, test)
make test         # Run tests
make format       # Format code
make lint         # Lint code

# Running
make run          # Start server (dev mode)
make run-prod     # Start server (production)
make cli          # Start CLI

# Maintenance
make clean        # Clean temp files
make install-dev  # Install dev dependencies
```

## Getting Help

- **Documentation**: Check [README.md](README.md) and [CONFIGURATION.md](CONFIGURATION.md)
- **API Docs**: http://localhost:8000/docs (when server is running)
- **Examples**: See `examples.py`
- **Tests**: Check `tests/` directory

## What's Next?

Try these features:
1. Upload different document types (PDF, TXT, MD)
2. Use different LLM providers
3. Build custom LangGraph workflows
4. Integrate with your own applications
5. Deploy to production

---

**Happy building! 🚀**
