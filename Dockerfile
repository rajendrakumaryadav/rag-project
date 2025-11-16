# Dockerfile for LLM-PKG
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY llm_pkg/ llm_pkg/
COPY config/ config/
COPY data/ data/

# Install Python dependencies
RUN uv pip install --system .

# Create upload directory
RUN mkdir -p data/uploads

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "llm_pkg.app:app", "--host", "0.0.0.0", "--port", "8000"]
