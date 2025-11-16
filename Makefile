# Makefile for LLM-PKG
# ====================
# Convenient commands for development and deployment

.PHONY: help install install-dev setup clean test run cli docs format lint

help:
	@echo "LLM-PKG Development Commands"
	@echo "============================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup        - Run full setup (venv + install)"
	@echo "  make install      - Install dependencies"
	@echo "  make install-dev  - Install with dev dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run          - Run FastAPI server"
	@echo "  make cli          - Run CLI in interactive mode"
	@echo "  make test         - Run tests"
	@echo "  make format       - Format code with black"
	@echo "  make lint         - Lint code with ruff"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        - Clean temporary files"
	@echo "  make docs         - Generate documentation"
	@echo ""

setup:
	@echo "🚀 Running setup..."
	@bash setup.sh

install:
	@echo "📦 Installing dependencies..."
	uv pip install -e .

install-dev:
	@echo "📦 Installing with dev dependencies..."
	uv pip install -e ".[dev]"

clean:
	@echo "🧹 Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.log" -delete
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf .coverage
	@rm -rf dist
	@rm -rf build
	@rm -rf *.egg-info
	@echo "✅ Cleanup complete"

test:
	@echo "🧪 Running tests..."
	pytest -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest --cov=llm_pkg --cov-report=html --cov-report=term

run:
	@echo "🚀 Starting FastAPI server..."
	uvicorn llm_pkg.app:app --reload --host 0.0.0.0 --port 8000

run-prod:
	@echo "🚀 Starting FastAPI server (production)..."
	uvicorn llm_pkg.app:app --host 0.0.0.0 --port 8000 --workers 4

cli:
	@echo "💻 Starting CLI..."
	python -m llm_pkg.cli

format:
	@echo "✨ Formatting code..."
	black src/llm_pkg/
	@echo "✅ Code formatted"

lint:
	@echo "🔍 Linting code..."
	ruff check src/llm_pkg/

docs:
	@echo "📚 Generating documentation..."
	@echo "Documentation available in README.md"

example:
	@echo "🎯 Running examples..."
	python examples/examples.py

# Development workflow
dev: clean install-dev format lint test
	@echo "✅ Development workflow complete"

# Production build
build: clean install test
	@echo "✅ Production build complete"
