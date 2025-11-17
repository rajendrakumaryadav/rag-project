from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Any, Mapping, NamedTuple

import tomli

# Guard heavy third-party imports so the package can be imported in minimal dev
# environments (tests, linters, docs) even if provider integrations are not
# installed. If those integrations are missing, we provide informative stubs
# that raise if used at runtime.
try:
    from langchain.chat_models import init_chat_model
except Exception:  # ImportError or other
    def init_chat_model(*args, **kwargs):
        raise ImportError(
            "langchain.chat_models.init_chat_model is not available. "
            "Install the required provider-specific runtime (e.g. `pip install langchain`)"
        )

try:
    from langchain_core.runnables import RunnableConfig
except Exception:
    # Lightweight fallback so type hints and code paths that reference
    # RunnableConfig don't fail at import time. Using a simple class wrapper
    # is sufficient for our usage in this module.
    class RunnableConfig:
        def __init__(self, **kwargs: Any):
            self.__dict__.update(kwargs)

try:
    from langgraph import config as lg_config
    from langgraph.runtime import Runtime
except Exception:
    # Provide a minimal lg_config with set_config and a Runtime placeholder.
    class _LGConfigStub:
        @staticmethod
        def set_config(_: dict[str, Any]) -> None:
            # no-op in environments without langgraph
            return
    
    
    lg_config = _LGConfigStub()
    
    
    class Runtime:  # type: ignore
        pass

logger = logging.getLogger(__name__)

# Resolve configuration path with sensible fallbacks for local dev and Docker.
# Priority: environment variable -> project/config/llm_config.toml -> /app/config/llm_config.toml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_CONFIG = os.getenv("LLM_PKG_CONFIG") or os.getenv("LLM_CONFIG_PATH")
LOCAL_CONFIG = PROJECT_ROOT / "config" / "llm_config.toml"
DOCKER_CONFIG = Path("/app/config/llm_config.toml")

if ENV_CONFIG:
    CONFIG_FILE = Path(ENV_CONFIG)
elif LOCAL_CONFIG.exists():
    CONFIG_FILE = LOCAL_CONFIG
elif DOCKER_CONFIG.exists():
    CONFIG_FILE = DOCKER_CONFIG
else:
    # Default to the local config path so instructions and tools point to the repo layout.
    # Do not fail import if the file is missing; LLMLoader.reload() will handle missing file gracefully.
    CONFIG_FILE = LOCAL_CONFIG


class ProviderConfig(NamedTuple):
    provider: str
    model: str
    meta: dict[str, Any]


class LLMLoader:
    """Load provider configurations from TOML and build LangChain/Graph clients.

    Behavior notes:
    - On import, the loader will attempt to load a configuration file but will not raise
      if the file is missing; instead it logs a warning and leaves `providers` empty.
    - Use the environment variable `LLM_PKG_CONFIG` or `LLM_CONFIG_PATH` to point to a
      custom TOML file.
    """
    
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or CONFIG_FILE
        self.providers: dict[str, ProviderConfig] = {}
        self.default: ProviderConfig | None = None
        # Attempt to load configuration, but handle missing/malformed files gracefully.
        try:
            self.reload()
        except Exception as exc:
            # Log and continue with empty config so importing the package in dev
            # environments doesn't fail if the config isn't present yet.
            logger.warning(
                "Failed to load LLM config from %s: %s. Continuing with empty provider set.",
                self.config_path,
                exc,
            )
    
    def reload(self) -> None:
        # If the config file doesn't exist, do not raise; set empty providers.
        if not self.config_path.exists():
            logger.warning(
                "LLM config file not found at %s. Tried env var, local project config, and docker path.\n"
                "Set LLM_PKG_CONFIG or create %s to provide provider configurations.",
                self.config_path,
                LOCAL_CONFIG,
            )
            self.providers.clear()
            self.default = None
            return
        
        # Read and parse TOML, with helpful error messages on parse failure.
        try:
            raw_text = self.config_path.read_text(encoding="utf-8")
            raw = tomli.loads(raw_text)
        except Exception as e:
            raise RuntimeError(
                f"Failed to read or parse LLM config at {self.config_path}: {e}"
            )(e)
        
        self.providers.clear()
        default_section = raw.get("default", {})
        for name, section in raw.items():
            if name in {"default", "metadata", "logging"}:
                continue
            provider = section.get("provider")
            if not provider:
                raise ValueError(f"Provider section '{name}' must declare `provider`.")
            model = section.get("model", section.get("deployment_id") or "gpt-4o")
            meta = {k: v for k, v in section.items() if k not in {"provider", "model"}}
            self.providers[name] = ProviderConfig(
                provider=provider, model=model, meta=meta
            )
        
        self.default = None
        if default_section:
            provider_name = default_section.get("provider_name")
            if provider_name and provider_name in self.providers:
                self.default = self.providers[provider_name]
            else:
                fallback_provider = default_section.get("provider")
                fallback_model = default_section.get("model")
                if fallback_provider and fallback_model:
                    self.default = ProviderConfig(
                        provider=fallback_provider, model=fallback_model, meta={}
                    )
        
        if not self.default and "openai" in self.providers:
            self.default = self.providers["openai"]
    
    def get_provider_config(self, name: str | None = None) -> ProviderConfig:
        if name:
            if name not in self.providers:
                raise KeyError(f"No provider section named '{name}'")
            return self.providers[name]
        if self.default:
            return self.default
        raise ValueError("No default provider configured.")
    
    def build_model(self, name: str | None = None, **kwargs: Any):
        cfg = self.get_provider_config(name)
        config_kwargs = {**cfg.meta}
        # Merge kwargs passed to function invocation and config.
        config_kwargs.update(kwargs)
        
        # Replace placeholder API keys with environment variables
        if "api_key" in config_kwargs:
            api_key_value = config_kwargs["api_key"]
            # Check if it's a placeholder (starts with < and ends with >)
            if (
                    isinstance(api_key_value, str)
                    and api_key_value.startswith("<")
                    and api_key_value.endswith(">")
            ):
                # Extract the env var name and try to get from environment
                env_var_name = api_key_value.strip("<>")
                env_value = os.getenv(env_var_name)
                if env_value:
                    config_kwargs["api_key"] = env_value
                else:
                    # Try common environment variable names
                    if cfg.provider in {"google_genai", "google", "vertexai"}:
                        config_kwargs["api_key"] = os.getenv(
                            "GOOGLE_API_KEY", api_key_value
                        )
                    elif cfg.provider == "openai":
                        config_kwargs["api_key"] = os.getenv(
                            "OPENAI_API_KEY", api_key_value
                        )
                    elif cfg.provider == "azure_openai":
                        config_kwargs["api_key"] = os.getenv(
                            "AZURE_OPENAI_API_KEY", api_key_value
                        )
        
        # Map generic "api_key"/"base_url" to provider-specific names for
        # the OpenAI-compatible provider so the underlying client recognizes
        # them (e.g. openai_api_key, openai_api_base). This ensures OpenRouter
        # base URLs and API keys are used instead of trying to hit platform
        # OpenAI endpoints.
        if cfg.provider == "openai":
            if "api_key" in config_kwargs:
                config_kwargs.setdefault("openai_api_key", config_kwargs.pop("api_key"))
            if "base_url" in config_kwargs:
                config_kwargs.setdefault(
                    "openai_api_base", config_kwargs.pop("base_url")
                )
        
        # Vertex AI (Google Gemini) provider-specific mapping. LangChain's
        # VertexAI/Google provider accepts values like project_id, location
        # and credentials; make it convenient to specify an `api_key` or
        # `google_credentials` in the provider section of the TOML.
        if cfg.provider in {"vertexai", "google", "google_genai"}:
            # map common keys to what the runtime often expects
            if "api_key" in config_kwargs:
                config_kwargs.setdefault("google_api_key", config_kwargs.pop("api_key"))
            if "project" in config_kwargs:
                config_kwargs.setdefault("project_id", config_kwargs.pop("project"))
            if "location" in config_kwargs:
                config_kwargs.setdefault("location", config_kwargs.pop("location"))
            if "credentials" in config_kwargs:
                config_kwargs.setdefault(
                    "google_credentials", config_kwargs.pop("credentials")
                )
        
        if cfg.provider == "azure_openai":
            config_kwargs.setdefault("deployment_id", cfg.meta.get("deployment_id"))
        
        # Normalize any provider aliases to the provider names expected by
        # `init_chat_model` (for example: vertexai -> google_vertexai).
        provider_aliases = {
            "vertexai": "google_genai",
            "google": "google_genai",
        }
        model_provider = provider_aliases.get(cfg.provider, cfg.provider)
        
        # Avoid passing duplicate keyword arguments. init_chat_model accepts the
        # model_provider and other keyword args; pass the resolved config_kwargs
        # which have provider-mapped values.
        try:
            return init_chat_model(
                model=cfg.model,
                model_provider=model_provider,
                config_prefix=None,
                configurable_fields=None,
                **config_kwargs,
            )
        except ImportError as e:
            hint = (
                f"Missing provider runtime: {model_provider}. "
                "Install provider-specific integration, e.g. `pip install -U langchain-google-genai`"
            )
            raise ImportError(hint) from e


class LangGraphManager:
    """Wire LangChain-loaded metadata into LangGraph runtime."""
    
    def __init__(self, loader: LLMLoader) -> None:
        self.loader = loader
        self.runtime: Runtime | None = None
    
    def apply_config(self, provider_name: str | None = None) -> RunnableConfig:
        model = self.loader.build_model(provider_name)
        metadata = {
            "langchain_provider": provider_name or self.loader.default.provider,
            "langchain_model": getattr(model, "model", "custom"),
        }
        lg_config.set_config({"metadata": metadata})
        return RunnableConfig(metadata=metadata)
    
    def runtime_context(self) -> Mapping[str, Any]:
        return {"langgraph_runtime": self.runtime} if self.runtime else {}


llm_loader = LLMLoader()
graph_manager = LangGraphManager(llm_loader)
