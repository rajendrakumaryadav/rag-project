#!/bin/bash

# LLM-PKG Setup Script
# ====================
# Automated setup for the LLM-PKG project

set -e

echo "🚀 LLM-PKG Setup Script"
echo "======================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed"
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ ! -d ".venv" ]; then
    uv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
uv pip install -e .

# Install dev dependencies
echo ""
read -p "Install development dependencies? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    uv pip install -e ".[dev]"
    echo "✅ Development dependencies installed"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p data/uploads
mkdir -p data/faiss_index
echo "✅ Directories created"

# Copy configuration template
echo ""
if [ ! -f ".env" ]; then
    read -p "Create .env file from template? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp .env.example .env
        echo "✅ .env file created. Please edit it with your API keys."
    fi
else
    echo "ℹ️  .env file already exists"
fi

# Check config file
echo ""
if [ ! -f "config/llm_config.toml" ]; then
    echo "⚠️  Warning: config/llm_config.toml not found"
    echo "   Please configure your LLM providers before running the application"
else
    echo "✅ Configuration file found"
fi

# Summary
echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your API keys"
echo "  2. Update config/llm_config.toml with your LLM provider settings"
echo "  3. Activate virtual environment: source .venv/bin/activate"
echo "  4. Run the server: uvicorn llm_pkg.app:app --reload"
echo "  5. Or use the CLI: llm-pkg"
echo ""
echo "For more information, see README.md"
