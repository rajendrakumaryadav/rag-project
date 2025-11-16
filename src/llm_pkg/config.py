from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, NamedTuple

import tomli
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langgraph import config as lg_config
from langgraph.runtime import Runtime

CONFIG_FILE = Path(__file__).resolve().parents[2] / "config" / "llm_config.toml"


class ProviderConfig(NamedTuple):
    provider: str
    model: str
    meta: dict[str, Any]


class LLMLoader:
    """Load provider configurations from TOML and build LangChain/Graph clients."""

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or CONFIG_FILE
        self.providers: dict[str, ProviderConfig] = {}
        self.default: ProviderConfig | None = None
        self.reload()

    def reload(self) -> None:
        raw = tomli.loads(self.config_path.read_text())
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
        config_kwargs = {**cfg.meta, "model": cfg.model}
        config_kwargs.update(kwargs)
        if cfg.provider == "azure_openai":
            config_kwargs.setdefault("deployment_id", cfg.meta.get("deployment_id"))
        return init_chat_model(
            model=cfg.model,
            model_provider=cfg.provider,
            config_prefix=None,
            configurable_fields=None,
            **cfg.meta,
            **kwargs,
        )


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
