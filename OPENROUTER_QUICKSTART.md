# OpenRouter Quick Reference

## ⚡ Quick Setup (3 Steps)

1. **Get API Key**: https://openrouter.ai/keys
2. **Add Credits**: https://openrouter.ai/credits (minimum $5)
3. **Update Config**: Replace API key in `config/llm_config.toml`

## 🚀 Usage Examples

### CLI
```bash
# Interactive mode
llm-pkg

# Within CLI
llm-pkg> query What is machine learning?
```

### Python Script
```python
from llm_pkg import QAEngine, llm_loader, graph_manager
import asyncio

async def ask():
    qa = QAEngine(llm_loader, graph_manager)
    result = await qa.query(
        question="Explain Python",
        provider="openrouter"  # or openrouter_claude, openrouter_llama
    )
    print(result['answer'])

asyncio.run(ask())
```

### FastAPI
```bash
# Start server
llm-pkg-server

# Query endpoint
curl -X POST "http://localhost:8000/query" \
  -F "question=What is AI?" \
  -F "provider=openrouter"
```

## 🎯 Choose Your Model

| Provider | Model | Best For | Cost |
|----------|-------|----------|------|
| `openrouter` | GPT-4o | General purpose, reasoning | $$ |
| `openrouter_claude` | Claude 3.5 Sonnet | Analysis, long context | $$$ |
| `openrouter_llama` | Llama 3.1 70B | Cost-effective, coding | $ |
| `openrouter_gemini` | Gemini Pro 1.5 | Fast, multimodal | $$ |

## 📝 Common Tasks

### Change Default Provider
Edit `config/llm_config.toml`:
```toml
[default]
provider_name = "openrouter_llama"  # Use any configured provider
```

### Add New Model
```toml
[openrouter_mistral]
provider = "openai"
model = "mistralai/mixtral-8x7b-instruct"
api_key = "sk-or-v1-YOUR-KEY"
base_url = "https://openrouter.ai/api/v1"
temperature = 0.7
```

### Test Configuration
```bash
python tools/openrouter_test.py
```

## 🔧 Troubleshooting

| Error | Solution |
|-------|----------|
| "Authentication required" | Check API key in config |
| "Insufficient credits" | Add credits at openrouter.ai/credits |
| "Model not found" | Verify model name at openrouter.ai/models |
| "Rate limit" | Wait or upgrade plan |

## 💰 Cost Management

- Check usage: https://openrouter.ai/activity
- Set limits: https://openrouter.ai/settings
- Compare pricing: https://openrouter.ai/models

## 📚 Resources

- **Models**: https://openrouter.ai/models
- **Docs**: https://openrouter.ai/docs
- **Dashboard**: https://openrouter.ai/
- **Full Guide**: `OPENROUTER_USAGE.md`
