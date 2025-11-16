# OpenRouter Integration Guide

## What is OpenRouter?

**OpenRouter** is a unified API that provides access to multiple LLM providers through a single interface:
- Use one API key for multiple models (GPT-4, Claude, Llama, Gemini, etc.)
- Automatic fallbacks and routing
- Pay-as-you-go pricing
- No need for multiple API keys

**Website:** https://openrouter.ai

---

## Quick Setup

### Step 1: Get Your OpenRouter API Key

1. Visit [OpenRouter](https://openrouter.ai)
2. Sign up or log in
3. Go to [Keys](https://openrouter.ai/keys)
4. Create a new API key
5. Add credits to your account

### Step 2: Configure LLM-PKG

Edit `config/llm_config.toml` and add your OpenRouter key:

```toml
[openrouter]
provider = "openai"  # OpenRouter uses OpenAI-compatible API
model = "openai/gpt-4o"
api_key = "sk-or-v1-your-actual-key-here"
base_url = "https://openrouter.ai/api/v1"
temperature = 0.7
```

### Step 3: Use OpenRouter

**Via API:**
```bash
curl -X POST "http://localhost:8000/query" \
  -F "question=What is machine learning?" \
  -F "provider=openrouter"
```

**Via CLI:**
```bash
llm-pkg query "What is machine learning?"
# Edit default provider in config to use openrouter
```

**Via Python:**
```python
from llm_pkg.config import llm_loader

# Build OpenRouter model
model = llm_loader.build_model("openrouter")

# Use it
response = model.invoke("What is machine learning?")
print(response.content)
```

---

## Available Models on OpenRouter

### Popular Models (Updated Configuration)

The configuration includes several pre-configured OpenRouter profiles:

#### 1. **OpenRouter with GPT-4o** (`openrouter`)
```toml
[openrouter]
provider = "openai"
model = "openai/gpt-4o"
api_key = "<SET_OPENROUTER_KEY>"
base_url = "https://openrouter.ai/api/v1"
```
- **Best for:** General purpose, complex reasoning
- **Cost:** Moderate

#### 2. **OpenRouter with Claude** (`openrouter_claude`)
```toml
[openrouter_claude]
provider = "openai"
model = "anthropic/claude-3.5-sonnet"
api_key = "<SET_OPENROUTER_KEY>"
base_url = "https://openrouter.ai/api/v1"
```
- **Best for:** Long-context tasks, analysis, writing
- **Cost:** Moderate to high

#### 3. **OpenRouter with Llama** (`openrouter_llama`)
```toml
[openrouter_llama]
provider = "openai"
model = "meta-llama/llama-3.1-70b-instruct"
api_key = "<SET_OPENROUTER_KEY>"
base_url = "https://openrouter.ai/api/v1"
```
- **Best for:** Cost-effective, good performance
- **Cost:** Low to moderate

#### 4. **OpenRouter with Gemini** (`openrouter_gemini`)
```toml
[openrouter_gemini]
provider = "openai"
model = "google/gemini-pro-1.5"
api_key = "<SET_OPENROUTER_KEY>"
base_url = "https://openrouter.ai/api/v1"
```
- **Best for:** Multimodal tasks, large contexts
- **Cost:** Moderate

### Other Available Models

You can use any model from OpenRouter's catalog:

```toml
# GPT-4 Turbo
[openrouter_gpt4_turbo]
provider = "openai"
model = "openai/gpt-4-turbo"
api_key = "<SET_OPENROUTER_KEY>"
base_url = "https://openrouter.ai/api/v1"

# GPT-3.5 Turbo (Cost-effective)
[openrouter_gpt35]
provider = "openai"
model = "openai/gpt-3.5-turbo"
api_key = "<SET_OPENROUTER_KEY>"
base_url = "https://openrouter.ai/api/v1"

# Mistral Large
[openrouter_mistral]
provider = "openai"
model = "mistralai/mistral-large"
api_key = "<SET_OPENROUTER_KEY>"
base_url = "https://openrouter.ai/api/v1"

# Perplexity
[openrouter_perplexity]
provider = "openai"
model = "perplexity/llama-3.1-sonar-large-128k-online"
api_key = "<SET_OPENROUTER_KEY>"
base_url = "https://openrouter.ai/api/v1"
```

**Full model list:** https://openrouter.ai/models

---

## Usage Examples

### Example 1: Query with Different Models

```bash
# Using GPT-4o via OpenRouter
curl -X POST "http://localhost:8000/query" \
  -F "question=Explain quantum computing" \
  -F "provider=openrouter"

# Using Claude via OpenRouter
curl -X POST "http://localhost:8000/query" \
  -F "question=Explain quantum computing" \
  -F "provider=openrouter_claude"

# Using Llama via OpenRouter
curl -X POST "http://localhost:8000/query" \
  -F "question=Explain quantum computing" \
  -F "provider=openrouter_llama"
```

### Example 2: Python Script

```python
from llm_pkg.config import llm_loader

# Test different models
models_to_test = [
    "openrouter",
    "openrouter_claude",
    "openrouter_llama",
    "openrouter_gemini"
]

question = "What are the benefits of renewable energy?"

for model_name in models_to_test:
    print(f"\n{'='*50}")
    print(f"Testing: {model_name}")
    print('='*50)
    
    model = llm_loader.build_model(model_name)
    response = model.invoke(question)
    
    print(f"Response: {response.content[:200]}...")
```

### Example 3: Document Q&A with OpenRouter

```python
import asyncio
from llm_pkg import QAEngine, llm_loader, graph_manager

async def query_with_openrouter():
    qa_engine = QAEngine(llm_loader, graph_manager)
    
    # Query using Claude via OpenRouter
    result = await qa_engine.query(
        question="Summarize the main points",
        provider="openrouter_claude"
    )
    
    print(f"Answer: {result['answer']}")
    print(f"Sources: {len(result['sources'])}")

asyncio.run(query_with_openrouter())
```

---

## Advanced Configuration

### Custom Headers and Parameters

```toml
[openrouter_custom]
provider = "openai"
model = "openai/gpt-4o"
api_key = "<SET_OPENROUTER_KEY>"
base_url = "https://openrouter.ai/api/v1"
temperature = 0.7
max_tokens = 4000
top_p = 0.9
```

### Using Environment Variables

```bash
# Set in .env file
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

```toml
# Reference in config
[openrouter]
provider = "openai"
model = "openai/gpt-4o"
api_key = "${OPENROUTER_API_KEY}"
base_url = "https://openrouter.ai/api/v1"
```

### Setting Default Provider

```toml
[default]
provider = "openai"
model = "openai/gpt-4o"
temperature = 0.7

# This will make OpenRouter the default
# Just copy the openrouter section here
```

Or reference a provider:

```toml
[default]
provider_name = "openrouter"  # References [openrouter] section
```

---

## Benefits of Using OpenRouter

### 1. **Single API Key**
- No need to manage multiple provider accounts
- Simplified billing and usage tracking

### 2. **Access to Multiple Models**
- GPT-4, GPT-3.5 (OpenAI)
- Claude 3.5 (Anthropic)
- Llama 3.1 (Meta)
- Gemini Pro (Google)
- Mistral, Perplexity, and more

### 3. **Automatic Fallbacks**
```python
# OpenRouter can automatically fall back to alternative models
# if the primary model is unavailable
```

### 4. **Cost Optimization**
- Compare prices across models
- Use cheaper models for simple tasks
- Reserve expensive models for complex queries

### 5. **Pay-As-You-Go**
- No monthly subscriptions
- Only pay for what you use

---

## Pricing Comparison

Approximate costs per 1M tokens (as of Nov 2025):

| Model | Input | Output | Provider |
|-------|-------|--------|----------|
| GPT-4o | $5 | $15 | OpenAI |
| GPT-3.5 Turbo | $0.50 | $1.50 | OpenAI |
| Claude 3.5 Sonnet | $3 | $15 | Anthropic |
| Llama 3.1 70B | $0.50 | $0.75 | Meta |
| Gemini Pro 1.5 | $1.25 | $5 | Google |

**Check current prices:** https://openrouter.ai/models

---

## Cost-Effective Strategy

### Development
```toml
[default]
provider = "openai"
model = "openai/gpt-3.5-turbo"  # Cheap for testing
api_key = "<SET_OPENROUTER_KEY>"
base_url = "https://openrouter.ai/api/v1"
```

### Production
```toml
[default]
provider = "openai"
model = "openai/gpt-4o"  # Best quality
api_key = "<SET_OPENROUTER_KEY>"
base_url = "https://openrouter.ai/api/v1"
```

### Dynamic Selection in Code
```python
from llm_pkg.config import llm_loader

# Use cheap model for simple queries
simple_model = llm_loader.build_model("openrouter_gpt35")

# Use powerful model for complex queries
complex_model = llm_loader.build_model("openrouter_claude")
```

---

## Troubleshooting

### Error: "Invalid API Key"
```bash
# Check your key
echo $OPENROUTER_API_KEY

# Verify in config
cat config/llm_config.toml | grep api_key
```

### Error: "Model not found"
- Check model name at https://openrouter.ai/models
- Use exact format: `provider/model-name`

### Error: "Insufficient credits"
- Add credits at https://openrouter.ai/credits
- Minimum: $5

### Rate Limits
```toml
# Reduce concurrent requests
[openrouter]
provider = "openai"
model = "openai/gpt-4o"
api_key = "<SET_OPENROUTER_KEY>"
base_url = "https://openrouter.ai/api/v1"
max_retries = 3
request_timeout = 30
```

---

## Testing Your Configuration

### CLI Test
```bash
# View configuration
llm-pkg config

# Should show openrouter provider
```

### API Test
```bash
# Start server
make run

# Test OpenRouter endpoint
curl -X POST "http://localhost:8000/query" \
  -F "question=Hello, how are you?" \
  -F "provider=openrouter"
```

### Python Test
```python
from llm_pkg.config import llm_loader

# Test OpenRouter connection
try:
    model = llm_loader.build_model("openrouter")
    response = model.invoke("Say hello")
    print(f"✅ OpenRouter working: {response.content}")
except Exception as e:
    print(f"❌ Error: {e}")
```

---

## Best Practices

### 1. **Start with Free Credits**
- OpenRouter often provides free credits for new users
- Test different models before committing

### 2. **Monitor Usage**
- Check dashboard: https://openrouter.ai/activity
- Set up usage alerts

### 3. **Use Model Routing**
```python
# Smart routing based on task complexity
def choose_model(task_complexity):
    if task_complexity == "simple":
        return "openrouter_gpt35"
    elif task_complexity == "medium":
        return "openrouter_llama"
    else:
        return "openrouter_claude"
```

### 4. **Cache Responses**
- Implement caching for repeated queries
- Reduces API calls and costs

### 5. **Test Locally First**
- Use Ollama for development
- Switch to OpenRouter for production

---

## Migration Guide

### From Direct OpenAI
```toml
# Before
[openai]
provider = "openai"
model = "gpt-4o"
api_key = "sk-..."
base_url = "https://api.openai.com/v1"

# After (using OpenRouter)
[openrouter]
provider = "openai"
model = "openai/gpt-4o"  # Add "openai/" prefix
api_key = "sk-or-v1-..."  # OpenRouter key
base_url = "https://openrouter.ai/api/v1"  # OpenRouter endpoint
```

### From Azure OpenAI
```toml
# Before
[azure]
provider = "azure_openai"
deployment_id = "gpt-4"
azure_api_key = "..."

# After (using OpenRouter)
[openrouter]
provider = "openai"
model = "openai/gpt-4o"
api_key = "sk-or-v1-..."
base_url = "https://openrouter.ai/api/v1"
```

---

## Summary

**OpenRouter Benefits:**
- ✅ One API key for all models
- ✅ Access to GPT-4, Claude, Llama, Gemini, etc.
- ✅ Cost-effective pay-as-you-go
- ✅ Easy to switch between models
- ✅ No monthly subscriptions

**Quick Setup:**
1. Get API key from https://openrouter.ai/keys
2. Edit `config/llm_config.toml`
3. Replace `<SET_OPENROUTER_KEY>` with your key
4. Use `provider=openrouter` in queries

**For more info:** https://openrouter.ai/docs

---

**Ready to use OpenRouter with LLM-PKG! 🚀**
