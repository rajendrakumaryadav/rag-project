# OpenRouter Usage Guide

## What is OpenRouter?

OpenRouter provides a unified API to access multiple LLM providers (OpenAI, Anthropic, Google, Meta, etc.) through a single interface. You only need one API key to access dozens of models.

## Quick Start

### 1. Test Your Configuration

```bash
# Test OpenRouter setup
python tools/openrouter_test.py
```

### 2. Using OpenRouter in Different Ways

#### A. Via FastAPI Server

Start the server:
```bash
llm-pkg-server
# or
uvicorn llm_pkg.app:app --reload
```

Then make API calls:

```bash
# Query with GPT-4o via OpenRouter
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "question=What is machine learning?" \
  -d "provider=openrouter"

# Query with Claude 3.5 Sonnet
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "question=Explain neural networks" \
  -d "provider=openrouter_claude"

# Query with Llama 3.1
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "question=Summarize the document" \
  -d "provider=openrouter_llama"

# Query with Gemini Pro
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "question=Analyze this text" \
  -d "provider=openrouter_gemini"
```

#### B. Via CLI

```bash
# Interactive mode
llm-pkg

# Then within the CLI:
llm-pkg> query What is deep learning?
```

#### C. Via Python API

```python
import asyncio
from llm_pkg import QAEngine, llm_loader, graph_manager

async def query_with_openrouter():
    qa_engine = QAEngine(llm_loader, graph_manager)
    
    # Use GPT-4o via OpenRouter
    result = await qa_engine.query(
        question="What are transformers in AI?",
        provider="openrouter"
    )
    print(f"GPT-4o: {result['answer']}")
    
    # Use Claude 3.5 Sonnet
    result = await qa_engine.query(
        question="Explain attention mechanisms",
        provider="openrouter_claude"
    )
    print(f"Claude: {result['answer']}")
    
    # Use Llama 3.1
    result = await qa_engine.query(
        question="What is RAG?",
        provider="openrouter_llama"
    )
    print(f"Llama: {result['answer']}")

asyncio.run(query_with_openrouter())
```

#### D. Direct Model Building

```python
from llm_pkg import llm_loader

# Build OpenRouter GPT-4o model
model = llm_loader.build_model("openrouter")
response = model.invoke("What is the capital of France?")
print(response.content)

# Build Claude model
claude = llm_loader.build_model("openrouter_claude")
response = claude.invoke("Write a haiku about coding")
print(response.content)

# Build Llama model
llama = llm_loader.build_model("openrouter_llama")
response = llama.invoke("Explain Python in one sentence")
print(response.content)
```

## Available Models

Your current configured OpenRouter models:

| Provider Name | Model | Description |
|---------------|-------|-------------|
| `openrouter` | `openai/gpt-4o` | OpenAI's GPT-4o |
| `openrouter_claude` | `anthropic/claude-3.5-sonnet` | Anthropic's Claude 3.5 Sonnet |
| `openrouter_llama` | `meta-llama/llama-3.1-70b-instruct` | Meta's Llama 3.1 70B |
| `openrouter_gemini` | `google/gemini-pro-1.5` | Google's Gemini Pro 1.5 |

## Adding More Models

You can add any OpenRouter-supported model by adding a new section in `config/llm_config.toml`:

```toml
[openrouter_mistral]
provider = "openai"
model = "mistralai/mixtral-8x7b-instruct"
api_key = "sk-or-v1-YOUR-KEY-HERE"
base_url = "https://openrouter.ai/api/v1"
temperature = 0.7
```

Popular models available on OpenRouter:
- `anthropic/claude-3-opus`
- `anthropic/claude-3-haiku`
- `openai/gpt-4-turbo`
- `openai/gpt-3.5-turbo`
- `meta-llama/llama-3.1-405b-instruct`
- `google/gemini-2.0-flash-exp`
- `mistralai/mistral-large`
- `cohere/command-r-plus`

See all models at: https://openrouter.ai/models

## Setting as Default Provider

To make OpenRouter your default, update `config/llm_config.toml`:

```toml
[default]
provider_name = "openrouter"  # Use specific provider config
```

Or:

```toml
[default]
provider = "openai"
model = "openai/gpt-4o"
api_key = "sk-or-v1-YOUR-KEY"
base_url = "https://openrouter.ai/api/v1"
temperature = 0.7
```

## Cost Tracking

OpenRouter provides usage tracking at: https://openrouter.ai/activity

You can also pass tracking metadata:

```python
model = llm_loader.build_model("openrouter")
response = model.invoke(
    "What is AI?",
    config={
        "metadata": {
            "user_id": "user123",
            "app_name": "llm-pkg"
        }
    }
)
```

## Troubleshooting

### Issue: "Authentication required"
**Solution:** Check your API key is correct in `config/llm_config.toml`

### Issue: "Insufficient credits"
**Solution:** Add credits at https://openrouter.ai/credits

### Issue: "Model not found"
**Solution:** Verify model name at https://openrouter.ai/models

### Issue: "Rate limit exceeded"
**Solution:** Wait a moment or upgrade your plan

## Advanced Features

### Custom Headers

```python
from llm_pkg.config import llm_loader

# Add custom headers for OpenRouter
config = llm_loader.get_provider_config("openrouter")
model = llm_loader.build_model("openrouter", 
    default_headers={
        "HTTP-Referer": "https://your-app.com",
        "X-Title": "LLM-PKG"
    }
)
```

### Model Fallbacks

OpenRouter automatically falls back to alternative models if one fails (requires configuration in their dashboard).

### Streaming Responses

```python
model = llm_loader.build_model("openrouter")
for chunk in model.stream("Write a story"):
    print(chunk.content, end="", flush=True)
```

## Best Practices

1. **Start with smaller models** for testing (e.g., `openai/gpt-3.5-turbo`)
2. **Monitor costs** at https://openrouter.ai/activity
3. **Use appropriate temperatures**:
   - Creative tasks: 0.7-1.0
   - Analytical tasks: 0.2-0.5
   - Deterministic tasks: 0.0-0.2
4. **Set rate limits** in OpenRouter dashboard
5. **Use model-specific strengths**:
   - Claude: Long context, analysis
   - GPT-4: General purpose, reasoning
   - Llama: Cost-effective, open source
   - Gemini: Multimodal, fast

## Resources

- OpenRouter Dashboard: https://openrouter.ai/
- API Keys: https://openrouter.ai/keys
- Model Pricing: https://openrouter.ai/models
- Documentation: https://openrouter.ai/docs
- Activity/Usage: https://openrouter.ai/activity
