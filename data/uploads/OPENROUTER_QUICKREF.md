# OpenRouter Quick Reference

## 🚀 Quick Setup (3 Steps)

### 1. Get API Key
Visit: https://openrouter.ai/keys
- Sign up/Login
- Create new key
- Add $5+ credits

### 2. Configure
Edit `config/llm_config.toml`:
```toml
[openrouter]
provider = "openai"
model = "openai/gpt-4o"
api_key = "sk-or-v1-YOUR-KEY-HERE"
base_url = "https://openrouter.ai/api/v1"
```

### 3. Test
```bash
python test_openrouter.py
```

---

## 📋 Popular Models

| Model ID | Use Case | Cost |
|----------|----------|------|
| `openai/gpt-4o` | Best overall | $$$ |
| `openai/gpt-3.5-turbo` | Fast & cheap | $ |
| `anthropic/claude-3.5-sonnet` | Long context | $$$ |
| `meta-llama/llama-3.1-70b-instruct` | Open source | $$ |
| `google/gemini-pro-1.5` | Multimodal | $$ |

Full list: https://openrouter.ai/models

---

## 💻 Usage Examples

### API
```bash
curl -X POST http://localhost:8000/query \
  -F "question=Hello" \
  -F "provider=openrouter"
```

### CLI
```bash
llm-pkg query "Hello" --provider openrouter
```

### Python
```python
from llm_pkg.config import llm_loader
model = llm_loader.build_model("openrouter")
response = model.invoke("Hello")
print(response.content)
```

---

## 🔧 Multiple Models Setup

```toml
# GPT-4o
[openrouter]
provider = "openai"
model = "openai/gpt-4o"
api_key = "sk-or-v1-..."
base_url = "https://openrouter.ai/api/v1"

# Claude
[openrouter_claude]
provider = "openai"
model = "anthropic/claude-3.5-sonnet"
api_key = "sk-or-v1-..."
base_url = "https://openrouter.ai/api/v1"

# Llama (cheaper)
[openrouter_llama]
provider = "openai"
model = "meta-llama/llama-3.1-70b-instruct"
api_key = "sk-or-v1-..."
base_url = "https://openrouter.ai/api/v1"
```

---

## ✅ Testing

```bash
# Verify configuration
python test_openrouter.py

# Check config
llm-pkg config

# Simple test
curl -X POST http://localhost:8000/query \
  -F "question=What is 2+2?" \
  -F "provider=openrouter"
```

---

## 💡 Cost Tips

1. **Development**: Use `gpt-3.5-turbo` ($)
2. **Production**: Use `gpt-4o` ($$$)
3. **Budget**: Use `llama-3.1-70b` ($$)

Monitor usage: https://openrouter.ai/activity

---

## 🐛 Troubleshooting

| Error | Solution |
|-------|----------|
| Invalid API key | Check key at https://openrouter.ai/keys |
| Insufficient credits | Add credits at https://openrouter.ai/credits |
| Model not found | Check model ID at https://openrouter.ai/models |
| Rate limit | Wait or upgrade plan |

---

## 📚 More Info

- **Full Guide**: See `OPENROUTER_GUIDE.md`
- **Docs**: https://openrouter.ai/docs
- **Models**: https://openrouter.ai/models
- **Pricing**: https://openrouter.ai/models (per model)

---

**Ready to use OpenRouter! 🎉**
