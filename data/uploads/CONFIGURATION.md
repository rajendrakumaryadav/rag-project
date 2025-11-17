# Configuration Guide for LLM-PKG

This guide explains how to configure LLM-PKG with different LLM providers and key application settings.

## Overview

- Primary provider configuration lives in `config/llm_config.toml`.
- Sensitive values (API keys, secrets) should be provided via environment variables or a local `.env` file (see `.env.example`).
- The project uses PostgreSQL with the `pgvector` extension as the primary vector store for embeddings and retrieval.

## Table of Contents

1. OpenAI
2. Azure OpenAI
3. Ollama (local)
4. OpenRouter
5. Advanced configuration
6. Environment variables
7. Troubleshooting

## OpenAI

1. Get an API key at https://platform.openai.com/
2. Edit `config/llm_config.toml` or use an environment variable:

```toml
[openai]
provider = "openai"
model = "gpt-4o"
api_key = "${OPENAI_API_KEY}"
base_url = "https://api.openai.com/v1"
temperature = 0.7
max_tokens = 2000
```

Use the `.env` file to set `OPENAI_API_KEY` for local development.

## Azure OpenAI

1. Create an Azure OpenAI resource, deploy a model and get your key and endpoint.
2. Example configuration in `config/llm_config.toml`:

```toml
[azure]
provider = "azure_openai"
resource_name = "your-resource-name"
deployment_id = "gpt-4-deployment"
azure_api_key = "${AZURE_OPENAI_API_KEY}"
model = "gpt-4"
api_version = "2024-02-01"
```

## Ollama (local)

Ollama provides an easy way to run models locally for development.

```bash
# Install on Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh
# Start the Ollama daemon
ollama serve
# Pull a model
ollama pull llama3
```

Configuration:

```toml
[ollama]
provider = "ollama"
model = "llama3"
host = "http://localhost:11434"
temperature = 0.5
```

## OpenRouter

OpenRouter can act as a multi-provider gateway. Example config:

```toml
[openrouter]
provider = "openai"
model = "openai/gpt-4o"
api_key = "${OPENROUTER_API_KEY}"
base_url = "https://openrouter.ai/api/v1"
temperature = 0.7
```

See `OPENROUTER_GUIDE.md` for more details.

## Advanced configuration

- You can define multiple named provider sections (e.g., `openai_creative`, `openai_precise`) and pick them at runtime.
- Common custom parameters: `temperature`, `max_tokens`, `top_p`, `stop`.
- The loader in `llm_pkg.config` will interpolate environment variables when building provider clients.

## Environment variables

Create a `.env` (local, do not commit) using `.env.example` as a template. Typical variables:

```bash
OPENAI_API_KEY=sk-...
AZURE_OPENAI_API_KEY=...
OLLAMA_HOST=http://localhost:11434
SECRET_KEY=your-super-secret-key (min 32 chars)
DATABASE_URL=postgresql://llm_user:llm_password@localhost:5432/llm_pkg
```

In `config/llm_config.toml` you can reference these variables with `${NAME}` and the config loader will replace them at runtime.

## Troubleshooting

- Invalid API key / Authentication errors: verify keys in `.env` and `config/llm_config.toml`, ensure backend has access to environment variables.
- Ollama connection refused: start the server with `ollama serve` and verify `curl http://localhost:11434` returns a response.
- Database errors: verify `DATABASE_URL` and that the `pgvector` extension is installed in your Postgres instance. Run migrations:

```bash
alembic upgrade head
```

- When running with Docker Compose, check `docker-compose logs -f` and inspect individual container logs (e.g., `docker logs <container>`).

## Testing configuration

- From Python:

```bash
python -c "from llm_pkg.config import llm_loader; print(llm_loader.providers)"
```

- From the running API:

```bash
curl http://localhost/api/config
```

## Best practices

- Keep secrets out of version control.
- For local development use Ollama for faster iterations.
- For production use robust provider accounts (Azure/OpenAI) with monitoring and cost controls.
- Configure multiple providers for redundancy and failover.

## Support

See the main README (`README.md`) and the OpenRouter guide (`OPENROUTER_GUIDE.md`) for more provider-specific details.
