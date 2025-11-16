# Configuration Guide for LLM-PKG

This guide will help you configure the LLM-PKG application with different LLM providers.

## Table of Contents

1. [OpenAI Configuration](#openai-configuration)
2. [Azure OpenAI Configuration](#azure-openai-configuration)
3. [Ollama Configuration](#ollama-configuration)
4. [Advanced Configuration](#advanced-configuration)

## OpenAI Configuration

### Step 1: Get API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

### Step 2: Configure

Edit `config/llm_config.toml`:

```toml
[openai]
provider = "openai"
model = "gpt-4o"  # or "gpt-3.5-turbo", "gpt-4-turbo"
api_key = "sk-your-actual-api-key-here"
base_url = "https://api.openai.com/v1"
temperature = 0.7
max_tokens = 2000
```

### Supported Models

- `gpt-4o` - Latest GPT-4 Optimized
- `gpt-4-turbo` - Fast GPT-4
- `gpt-3.5-turbo` - Cost-effective option

## Azure OpenAI Configuration

### Step 1: Set Up Azure OpenAI

1. Create an Azure account
2. Create an Azure OpenAI resource
3. Deploy a model (e.g., GPT-4)
4. Get your endpoint and API key

### Step 2: Configure

Edit `config/llm_config.toml`:

```toml
[azure]
provider = "azure_openai"
resource_name = "your-resource-name"
deployment_id = "your-deployment-name"
azure_api_key = "your-azure-api-key"
model = "gpt-4"
temperature = 0.1
api_version = "2024-02-01"
```

### Finding Your Values

- **Resource Name**: In Azure Portal, your resource name
- **Deployment ID**: Name of your deployed model
- **API Key**: Keys and Endpoint section in Azure Portal

## Ollama Configuration

### Step 1: Install Ollama

```bash
# On macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# On Windows
# Download from https://ollama.com/download
```

### Step 2: Pull a Model

```bash
ollama pull llama3
ollama pull mistral
ollama pull codellama
```

### Step 3: Configure

Edit `config/llm_config.toml`:

```toml
[ollama]
provider = "ollama"
model = "llama3"  # or "mistral", "codellama"
host = "http://localhost:11434"
temperature = 0.5
```

### Popular Ollama Models

- `llama3` - Meta's Llama 3
- `mistral` - Mistral AI
- `codellama` - Code-focused
- `phi` - Small but capable

## Advanced Configuration

### Multiple Provider Setup

You can configure multiple providers and switch between them:

```toml
[default]
provider = "openai"
model = "gpt-4o"

[openai]
provider = "openai"
model = "gpt-4o"
api_key = "sk-..."

[azure]
provider = "azure_openai"
deployment_id = "gpt-4-deployment"
azure_api_key = "..."

[ollama]
provider = "ollama"
model = "llama3"
host = "http://localhost:11434"
```

### Custom Parameters

```toml
[openai_creative]
provider = "openai"
model = "gpt-4o"
api_key = "sk-..."
temperature = 0.9  # More creative
max_tokens = 4000
top_p = 0.95

[openai_precise]
provider = "openai"
model = "gpt-4o"
api_key = "sk-..."
temperature = 0.1  # More precise
max_tokens = 1000
```

### Using Different Providers in Code

```python
from llm_pkg.config import llm_loader

# Use default provider
model = llm_loader.build_model()

# Use specific provider
openai_model = llm_loader.build_model("openai")
azure_model = llm_loader.build_model("azure")
ollama_model = llm_loader.build_model("ollama")
```

### API Endpoint

```bash
# Use specific provider
curl -X POST "http://localhost:8000/query" \
  -F "question=What is AI?" \
  -F "provider=ollama"
```

## Environment Variables

For security, use environment variables for API keys:

1. Create `.env` file:

```bash
OPENAI_API_KEY=sk-your-key
AZURE_OPENAI_API_KEY=your-azure-key
```

2. Update `config/llm_config.toml`:

```toml
[openai]
provider = "openai"
model = "gpt-4o"
api_key = "${OPENAI_API_KEY}"  # Will be replaced
```

## Troubleshooting

### OpenAI Issues

**Error: Invalid API Key**
- Check your API key is correct
- Ensure you have credits/billing set up

**Error: Rate Limit**
- Reduce request frequency
- Upgrade your OpenAI plan

### Azure Issues

**Error: Resource Not Found**
- Verify resource name and deployment ID
- Check API version compatibility

**Error: Authentication Failed**
- Confirm API key is correct
- Check Azure region settings

### Ollama Issues

**Error: Connection Refused**
- Ensure Ollama is running: `ollama serve`
- Check host URL is correct

**Error: Model Not Found**
- Pull the model: `ollama pull llama3`
- Verify model name spelling

## Testing Configuration

Test your configuration:

```bash
# Using CLI
llm-pkg config

# Using Python
python -c "from llm_pkg.config import llm_loader; print(llm_loader.providers)"

# Using API
curl http://localhost:8000/config
```

## Best Practices

1. **Security**: Never commit API keys to version control
2. **Cost**: Start with cheaper models for development
3. **Performance**: Use Ollama for local development
4. **Production**: Use Azure OpenAI for enterprise deployments
5. **Fallback**: Configure multiple providers for redundancy

## Support

For more help:
- Check the main [README.md](README.md)
- Visit [LangChain Documentation](https://python.langchain.com/)
- See [OpenAI API Reference](https://platform.openai.com/docs)
- Read [Azure OpenAI Docs](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
