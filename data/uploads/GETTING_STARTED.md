# 🚀 LLM-PKG: Complete Setup Guide

## Project Overview

**LLM-PKG** is a production-ready document processing and Q&A platform that combines:
- **Document Upload & Processing** (Docling-like scanning)
- **LangChain** for LLM operations
- **LangGraph** for workflow orchestration
- **FastAPI** for REST API
- **Multi-Provider Support** (OpenAI, Azure OpenAI, Ollama)

---

## ✨ What's Included

### 📚 Core Features
- ✅ Document upload (PDF, TXT, Markdown)
- ✅ Docling-like document scanning
- ✅ RAG-based question answering
- ✅ Multi-provider LLM support
- ✅ REST API with FastAPI
- ✅ CLI interface
- ✅ Hot-reloadable configuration
- ✅ Production-ready deployment

### 🛠️ Development Tools
- ✅ Automated setup script
- ✅ Makefile for common tasks
- ✅ Docker & Docker Compose
- ✅ Test suite
- ✅ Code formatting & linting
- ✅ Comprehensive documentation

---

## 📦 Installation Methods

### Method 1: Quick Setup (Recommended)

```bash
cd /home/rajendrayadav/Documents/projects/llm-pkg/src

# Run automated setup
./setup.sh

# Verify installation
python verify_install.py
```

### Method 2: Using Makefile

```bash
cd /home/rajendrayadav/Documents/projects/llm-pkg/src

# Full setup
make setup

# Verify
python verify_install.py
```

### Method 3: Manual Setup

```bash
cd /home/rajendrayadav/Documents/projects/llm-pkg/src

# Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
uv pip install -e .

# Verify
python verify_install.py
```

### Method 4: Docker

```bash
cd /home/rajendrayadav/Documents/projects/llm-pkg/src

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f
```

---

## ⚙️ Configuration

### Step 1: Choose Your LLM Provider

#### Option A: OpenAI (Cloud)
```toml
# Edit config/llm_config.toml
[openai]
provider = "openai"
model = "gpt-4o"
api_key = "sk-your-actual-key-here"
```

Get API key: https://platform.openai.com/api-keys

#### Option B: Azure OpenAI (Enterprise)
```toml
# Edit config/llm_config.toml
[azure]
provider = "azure_openai"
resource_name = "your-resource"
deployment_id = "your-deployment"
azure_api_key = "your-key"
model = "gpt-4"
```

#### Option C: Ollama (Local/Free)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3

# Config is already set for localhost:11434
```

### Step 2: Verify Configuration

```bash
# Using CLI
llm-pkg config

# Using verification script
python verify_install.py

# Using API
curl http://localhost:8000/config
```

---

## 🎯 Running the Application

### Option 1: Web Server (API)

```bash
# Development mode
make run
# or
uvicorn llm_pkg.app:app --reload

# Production mode
make run-prod
```

Access:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Option 2: CLI Interface

```bash
# Interactive mode
make cli
# or
llm-pkg

# Direct commands
llm-pkg upload document.pdf
llm-pkg list
llm-pkg query "What is this about?"
llm-pkg config
```

### Option 3: Python API

```python
import asyncio
from llm_pkg import DocumentProcessor, QAEngine, llm_loader, graph_manager

async def main():
    # Initialize
    processor = DocumentProcessor()
    qa = QAEngine(llm_loader, graph_manager)
    
    # Process document
    from pathlib import Path
    result = await processor.process_document(Path("document.pdf"))
    print(f"Processed: {result['summary']}")
    
    # Ask question
    answer = await qa.query("What are the key points?")
    print(f"Answer: {answer['answer']}")

asyncio.run(main())
```

---

## 📝 Usage Examples

### Example 1: Upload & Query via API

```bash
# Start server
make run

# Upload document
curl -X POST http://localhost:8000/upload \
  -F "file=@research_paper.pdf"

# Query document
curl -X POST http://localhost:8000/query \
  -F "question=What are the main findings?" \
  -F "provider=openai"

# List documents
curl http://localhost:8000/documents
```

### Example 2: CLI Workflow

```bash
# Start interactive CLI
llm-pkg

# In interactive mode:
llm-pkg> upload research_paper.pdf
llm-pkg> list
llm-pkg> query What are the key findings?
llm-pkg> config
llm-pkg> exit
```

### Example 3: Python Script

```python
# Save as my_script.py
import asyncio
from llm_pkg import save_document, DocumentProcessor, QAEngine
from llm_pkg import llm_loader, graph_manager

async def analyze_document():
    # Upload
    with open("paper.pdf", "rb") as f:
        path = save_document(f.read(), "paper.pdf")
    
    # Process
    processor = DocumentProcessor()
    result = await processor.process_document(path)
    print(f"Pages: {result['summary']['total_pages']}")
    
    # Query
    qa = QAEngine(llm_loader, graph_manager)
    answer = await qa.query(
        "Summarize the key findings",
        provider="openai"
    )
    print(f"Answer: {answer['answer']}")

asyncio.run(analyze_document())
```

### Example 4: Batch Processing

```python
# Run the included examples
python examples.py
```

---

## 🧪 Testing & Development

### Run Tests

```bash
# Basic tests
make test

# With coverage
make test-cov

# Specific test
pytest tests/test_basic.py -v
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Full dev workflow
make dev  # Format + Lint + Test
```

### Development Workflow

```bash
# 1. Make changes
# 2. Format code
make format

# 3. Check linting
make lint

# 4. Run tests
make test

# 5. Run application
make run
```

---

## 📚 Documentation Reference

| Document | Purpose |
|----------|---------|
| `README.md` | Main documentation |
| `QUICKSTART.md` | 5-minute setup guide |
| `CONFIGURATION.md` | Provider configuration |
| `PROJECT_SUMMARY.md` | Project overview |
| `GETTING_STARTED.md` | This file |
| API Docs | http://localhost:8000/docs |

---

## 🐳 Docker Deployment

### Quick Start

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f llm-pkg

# Stop
docker-compose down
```

### With Ollama

```bash
# Start both services
docker-compose up -d

# The Ollama service will be available at localhost:11434
# Configure in config/llm_config.toml to use it
```

### Custom Build

```bash
# Build image
docker build -t llm-pkg .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY=sk-your-key \
  llm-pkg
```

---

## 🔍 Troubleshooting

### Common Issues

#### "Module not found"
```bash
# Activate virtual environment
source .venv/bin/activate

# Reinstall
uv pip install -e .
```

#### "API key not found"
```bash
# Check configuration
cat config/llm_config.toml

# Edit with your keys
nano config/llm_config.toml
```

#### "Port already in use"
```bash
# Change port
uvicorn llm_pkg.app:app --port 8001

# Or kill existing process
lsof -ti:8000 | xargs kill
```

#### "Ollama connection refused"
```bash
# Start Ollama
ollama serve

# Or install Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

### Verification

```bash
# Run verification script
python verify_install.py

# Check specific component
python -c "from llm_pkg import __version__; print(__version__)"

# Test API
curl http://localhost:8000/health
```

---

## 🚀 Next Steps

### For Development
1. Explore `examples.py` for usage patterns
2. Read `llm_pkg/qa_engine.py` to understand RAG
3. Customize workflows in LangGraph
4. Add new document formats
5. Extend API endpoints

### For Production
1. Set up environment variables
2. Configure reverse proxy (nginx)
3. Enable HTTPS/SSL
4. Add authentication
5. Set up monitoring
6. Configure rate limiting

### Learning Resources
- [LangChain Docs](https://python.langchain.com/)
- [LangGraph Guide](https://langchain-ai.github.io/langgraph/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/)
- [uv Documentation](https://github.com/astral-sh/uv)

---

## 📞 Getting Help

### Built-in Help

```bash
# Makefile commands
make help

# CLI help
llm-pkg --help

# API documentation
# Visit http://localhost:8000/docs
```

### Resources
- Check `README.md` for detailed docs
- See `examples.py` for code samples
- Review `tests/` for test examples
- Read `CONFIGURATION.md` for provider setup

---

## ✅ Quick Checklist

Before you start:
- [ ] Python 3.11+ installed
- [ ] uv installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] API keys configured
- [ ] Verification script passed

Ready to use:
- [ ] Server starts successfully
- [ ] Can upload documents
- [ ] Can query documents
- [ ] CLI works
- [ ] Tests pass

---

## 🎉 You're Ready!

Your LLM-PKG installation is complete. Choose your preferred interface:

```bash
# Web API
make run
# → http://localhost:8000/docs

# CLI
make cli
# → Interactive terminal

# Python
python examples.py
# → See code samples
```

**Happy building! 🚀**

---

*For more information, see README.md or visit the API docs at http://localhost:8000/docs*
