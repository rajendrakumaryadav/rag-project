# LLM-PKG: Document Processing & QA Platform

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.103+-green.svg)
![LangChain](https://img.shields.io/badge/LangChain-1.0+-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A full-featured document processing and question-answering platform that combines document scanning (Docling-like), LangChain, and LangGraph to create an intelligent document analysis system.

## 🌟 Features

- **📄 Document Upload & Processing**: Upload PDF, TXT, and Markdown files
- **🔍 Docling-like Document Scanning**: Advanced document parsing with text extraction, metadata, and structure analysis
- **💬 Intelligent Q&A**: Ask questions about your documents using RAG (Retrieval-Augmented Generation)
- **🔌 Multi-Provider Support**: Configurable LLM providers (OpenAI, Azure OpenAI, Ollama, OpenRouter)
- **🚀 FastAPI REST API**: Production-ready API with automatic documentation
- **💻 CLI Interface**: Interactive command-line tool for easy interaction
- **📊 LangGraph Workflows**: Structured AI workflows for complex document analysis
- **⚙️ Dynamic Configuration**: TOML-based configuration with hot-reload support

## 🏗️ Architecture

```
┌─────────────────┐
│  FastAPI Server │ ← REST API
└────────┬────────┘
         │
    ┌────┴────┐
    │   CLI   │ ← Command Line Interface
    └────┬────┘
         │
┌────────┴─────────────────────────┐
│     Application Layer             │
│  ┌──────────┐  ┌───────────┐    │
│  │ QA Engine│  │ Doc Proc  │    │
│  └──────────┘  └───────────┘    │
└────────┬─────────────────────────┘
         │
┌────────┴─────────────────────────┐
│   LangChain & LangGraph Layer    │
│  ┌──────┐ ┌────────┐ ┌────────┐ │
│  │ RAG  │ │ Chains │ │ Graphs │ │
│  └──────┘ └────────┘ └────────┘ │
└────────┬─────────────────────────┘
         │
┌────────┴─────────────────────────┐
│    LLM Providers Layer           │
│  ┌────────┐ ┌──────┐ ┌────────┐ │
│  │ OpenAI │ │ Azure│ │ Ollama │ │
│  └────────┘ └──────┘ └────────┘ │
└──────────────────────────────────┘
```

## 📋 Prerequisites

- Python 3.11 or higher
- uv (Python package manager)
- Optional: Ollama for local LLM inference

## 🚀 Quick Start

### 1. Install uv (if not already installed)

```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Setup

```bash
# Navigate to the project root
cd /home/rajendrayadav/Documents/projects/llm-pkg

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package in development mode
uv pip install -e .
```

### 3. Configure LLM Providers

Edit `config/llm_config.toml` to add your API keys and configuration:

```toml
[default]
provider = "openai"
model = "gpt-4o"
temperature = 0.2

[openai]
provider = "openai"
model = "gpt-4o"
api_key = "sk-your-openai-key-here"
base_url = "https://api.openai.com/v1"

[azure]
provider = "azure_openai"
resource_name = "your-azure-resource"
deployment_id = "your-deployment-id"
azure_api_key = "your-azure-key"
model = "gpt-4o"
temperature = 0.1

[ollama]
provider = "ollama"
model = "llama3"
host = "http://localhost:11434"
```

### 4. Run the Application

#### Option A: FastAPI Server

```bash
# Start the server
uvicorn llm_pkg.app:app --reload

# Or use the convenience script
llm-pkg-server
```

Visit:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

#### Option B: CLI Tool

```bash
# Interactive mode
llm-pkg

# Or use direct commands
llm-pkg upload document.pdf
llm-pkg list
llm-pkg query "What is this document about?"
llm-pkg config
```

## 📚 Usage Examples

### REST API Examples

#### Upload a Document

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

#### List Documents

```bash
curl -X GET "http://localhost:8000/documents"
```

#### Query Documents

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "question=What are the main topics in this document?" \
  -d "provider=openai"
```

#### Get Configuration

```bash
curl -X GET "http://localhost:8000/config"
```

#### Reload Configuration

```bash
curl -X POST "http://localhost:8000/config/reload"
```

### Python API Examples

```python
from llm_pkg.config import llm_loader, graph_manager
from llm_pkg.document_processor import DocumentProcessor
from llm_pkg.qa_engine import QAEngine
from pathlib import Path

# Initialize components
doc_processor = DocumentProcessor()
qa_engine = QAEngine(llm_loader, graph_manager)

# Process a document
async def process_doc():
    file_path = Path("document.pdf")
    processed = await doc_processor.process_document(file_path)
    print(f"Processed: {processed['summary']}")

# Query documents
async def ask_question():
    result = await qa_engine.query(
        question="What is the main topic?",
        provider="openai"
    )
    print(f"Answer: {result['answer']}")
```

### CLI Examples

```bash
# Start interactive mode
llm-pkg

# In interactive mode:
llm-pkg> upload research_paper.pdf
llm-pkg> list
llm-pkg> query What are the key findings?
llm-pkg> config
llm-pkg> exit

# Direct commands
llm-pkg upload report.pdf
llm-pkg query "Summarize the executive summary"
```

## 🔧 Configuration

### LLM Provider Configuration

The `config/llm_config.toml` file supports multiple providers:

#### OpenAI

```toml
[openai]
provider = "openai"
model = "gpt-4o"
api_key = "sk-..."
temperature = 0.7
max_tokens = 2000
```

#### Azure OpenAI

```toml
[azure]
provider = "azure_openai"
resource_name = "my-azure-resource"
deployment_id = "gpt-4-deployment"
azure_api_key = "..."
model = "gpt-4"
api_version = "2024-02-01"
```

#### Ollama (Local)

```toml
[ollama]
provider = "ollama"
model = "llama3"
host = "http://localhost:11434"
temperature = 0.5
```

#### OpenRouter (Multi-Provider)

```toml
[openrouter]
provider = "openai"
model = "openai/gpt-4o"  # Can use any OpenRouter model
api_key = "sk-or-v1-..."
base_url = "https://openrouter.ai/api/v1"
temperature = 0.7
```

**See [OPENROUTER_GUIDE.md](OPENROUTER_GUIDE.md) for detailed setup.**

### Application Settings

```toml
[metadata]
upload_dir = "data/uploads"
document_store = "pdfplumber"
doc_scan_tool = "docling-mimic"
max_file_size_mb = 50

[logging]
level = "INFO"
formatter = "rich"
```

## 📁 Project Structure

```
llm-pkg/
├── config/
│   └── llm_config.toml          # LLM provider configuration
├── data/
│   └── uploads/                 # Uploaded documents storage
├── examples/
│   └── examples.py              # Usage examples (scripts)
├── tools/
│   └── openrouter_test.py       # Utility script for OpenRouter testing
├── notebooks/                   # (optional) Jupyter notebooks
├── src/
│   └── llm_pkg/
│       ├── __init__.py
│       ├── app.py               # FastAPI application
│       ├── cli.py               # CLI interface
│       ├── config.py            # Configuration loader
│       ├── document_processor.py# Document scanning & processing
│       ├── qa_engine.py         # Q&A with LangChain/LangGraph
│       └── storage.py           # Document storage management
├── tests/
│   └── test_basic.py            # Unit tests
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## 🔍 Document Processing Features

### Supported Formats

- **PDF**: Full text extraction, table detection, metadata, page-by-page analysis
- **TXT**: Plain text processing with structure analysis
- **MD**: Markdown files with heading detection

### Extraction Capabilities

- **Text**: Complete text extraction with page awareness
- **Metadata**: Author, creation date, page count, file size
- **Structure**: Headings, lists, sections, tables
- **Layout**: Word positions, page dimensions
- **Tables**: Table detection and extraction

### Docling-like Features

The document processor mimics Docling's capabilities:

1. **Multi-layer extraction**: Text, structure, and metadata
2. **Layout analysis**: Position-aware text extraction
3. **Table detection**: Automatic table identification
4. **Semantic structure**: Heading and section detection
5. **Page-level processing**: Per-page analysis and chunking

## 💡 LangChain & LangGraph Integration

### RAG (Retrieval-Augmented Generation)

The QA engine implements RAG pattern:

1. **Document Loading**: Load and process documents
2. **Chunking**: Split documents into manageable chunks
3. **Embedding**: Create vector embeddings
4. **Retrieval**: Find relevant chunks for queries
5. **Generation**: Generate answers using LLM

### LangGraph Workflow

```python
# QA workflow structure
retrieve → generate → answer
    ↓
[documents] → [context] → [LLM] → [answer]
```

### Customization

Extend the QA engine with custom nodes:

```python
from llm_pkg.qa_engine import QAEngine

# Add custom processing nodes
workflow.add_node("summarize", summarize_node)
workflow.add_node("fact_check", fact_check_node)
```

## 🧪 Testing

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=llm_pkg --cov-report=html
```

## 🔒 Security Best Practices

1. **API Keys**: Never commit API keys to version control
2. **Environment Variables**: Use `.env` files for sensitive data
3. **File Upload**: Implement file size limits and type validation
4. **Authentication**: Add authentication for production deployments
5. **Rate Limiting**: Implement rate limiting for API endpoints

## 🚀 Production Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY . .

# Install dependencies
RUN uv pip install --system .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "llm_pkg.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables

```bash
export OPENAI_API_KEY="sk-..."
export AZURE_OPENAI_KEY="..."
export LOG_LEVEL="INFO"
```

### Systemd Service

```ini
[Unit]
Description=LLM-PKG Service
After=network.target

[Service]
Type=simple
User=llm-pkg
WorkingDirectory=/opt/llm-pkg
ExecStart=/opt/llm-pkg/.venv/bin/uvicorn llm_pkg.app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📊 Performance Tips

1. **Vector Store**: Use persistent vector stores (FAISS, Pinecone) for large datasets
2. **Caching**: Implement response caching for repeated queries
3. **Async**: All I/O operations are async for better performance
4. **Chunking**: Optimize chunk size based on your documents
5. **Batch Processing**: Process multiple documents in parallel

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain**: For the powerful LLM framework
- **LangGraph**: For workflow orchestration
- **FastAPI**: For the excellent web framework
- **Docling**: Inspiration for document processing
- **Rich**: For beautiful CLI output

## 📧 Contact

Rajendra Yadav - rajendra@example.com

Project Link: [https://github.com/rajendrayadav/llm-pkg](https://github.com/rajendrayadav/llm-pkg)

## 🗺️ Roadmap

- [ ] Support for more document formats (DOCX, HTML, etc.)
- [ ] Advanced table extraction and analysis
- [ ] Multi-modal support (images, charts)
- [ ] Document comparison and diff
- [ ] Batch processing API
- [ ] WebSocket support for streaming responses
- [ ] Integration with more vector databases
- [ ] Custom embedding models support
- [ ] Multi-language support
- [ ] Advanced caching strategies

---

**Built with ❤️ using uv, LangChain, and LangGraph**
