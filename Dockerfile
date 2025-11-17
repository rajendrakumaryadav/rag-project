# Dockerfile for LLM-PKG
FROM python:3.11-slim

# Build arguments for API keys
ARG GOOGLE_API_KEY
ARG OPENAI_API_KEY
ARG AZURE_OPENAI_API_KEY

# Set environment variables from build args
ENV GOOGLE_API_KEY=${GOOGLE_API_KEY}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV AZURE_OPENAI_API_KEY=${AZURE_OPENAI_API_KEY}

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
COPY README.md .
COPY alembic.ini .
COPY alembic/ alembic/
COPY src/ src/
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
