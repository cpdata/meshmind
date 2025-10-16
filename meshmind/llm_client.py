"""Provider-agnostic wrapper around OpenAI-compatible SDKs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

DEFAULT_MODEL = "gpt-5-nano"

try:  # pragma: no cover - optional dependency import
    from openai import OpenAI as _OpenAI
    from openai import RateLimitError as _RateLimitError
except ImportError:  # pragma: no cover - exercised in tests without openai
    _OpenAI = None  # type: ignore[assignment]

    class _RateLimitError(Exception):
        """Fallback error used when the OpenAI SDK is unavailable."""

        pass


RateLimitError = _RateLimitError


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for an OpenAI-compatible client."""

    api_key: Optional[str] = None
    base_urls: Dict[str, Optional[str]] = field(
        default_factory=lambda: {"default": None}
    )
    models: Dict[str, str] = field(default_factory=lambda: {"default": DEFAULT_MODEL})
    default_model: str = DEFAULT_MODEL

    def model_for(self, operation: str, fallback: Optional[str] = None) -> str:
        """Return the preferred model for a given operation."""

        return (
            self.models.get(operation)
            or self.models.get("default")
            or fallback
            or self.default_model
        )

    def base_url_for(self, operation: str) -> Optional[str]:
        """Return the preferred base URL for a given operation."""

        base_url = self.base_urls.get(operation)
        if base_url:
            return base_url
        return self.base_urls.get("default") or None

    def override(
        self,
        *,
        models: Optional[Dict[str, Optional[str]]] = None,
        base_urls: Optional[Dict[str, Optional[str]]] = None,
        api_key: Optional[str] = None,
    ) -> "LLMConfig":
        """Return a copy of the config with overrides applied."""

        new_models = dict(self.models)
        if models:
            for key, value in models.items():
                if value:
                    new_models[key] = value
        new_base_urls = dict(self.base_urls)
        if base_urls:
            for key, value in base_urls.items():
                if value is not None:
                    new_base_urls[key] = value or None
        new_api_key = api_key if api_key not in (None, "") else self.api_key
        return LLMConfig(
            api_key=new_api_key,
            base_urls=new_base_urls,
            models=new_models,
            default_model=self.default_model,
        )


class _ResponsesProxy:
    def __init__(self, parent: "LLMClient") -> None:
        self._parent = parent

    def create(
        self,
        *,
        operation: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        return self._parent.responses_create(
            operation=operation or "extraction",
            model=model,
            base_url=base_url,
            **kwargs,
        )


class _EmbeddingsProxy:
    def __init__(self, parent: "LLMClient") -> None:
        self._parent = parent

    def create(
        self,
        *,
        operation: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        return self._parent.embeddings_create(
            operation=operation or "embedding",
            model=model,
            base_url=base_url,
            **kwargs,
        )


class LLMClient:
    """Thin wrapper around the OpenAI SDK that centralises configuration."""

    def __init__(
        self,
        config: LLMConfig,
        *,
        client_kwargs: Optional[Dict[str, Any]] = None,
    ) -> None:
        if _OpenAI is None:
            raise ImportError(
                "openai package is required to construct an LLM client."
            )

        self.config = config
        base_kwargs = dict(client_kwargs or {})
        if config.api_key:
            base_kwargs.setdefault("api_key", config.api_key)
        default_base = config.base_url_for("default")
        if default_base:
            base_kwargs.setdefault("base_url", default_base)
        self._default_kwargs = base_kwargs
        self._client_cache: Dict[Optional[str], Any] = {}

        self.responses = _ResponsesProxy(self)
        self.embeddings = _EmbeddingsProxy(self)

    def _client_for(self, base_url: Optional[str]) -> Any:
        key = base_url or self._default_kwargs.get("base_url") or "__default__"
        if key not in self._client_cache:
            kwargs = dict(self._default_kwargs)
            if base_url:
                kwargs["base_url"] = base_url
            self._client_cache[key] = _OpenAI(**kwargs)
        return self._client_cache[key]

    def responses_create(
        self,
        *,
        operation: str = "extraction",
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        resolved_model = model or self.config.model_for(operation)
        resolved_base = base_url if base_url not in ("", None) else None
        if resolved_base is None:
            resolved_base = self.config.base_url_for(operation)
        client = self._client_for(resolved_base)
        kwargs.setdefault("model", resolved_model)
        return client.responses.create(**kwargs)

    def embeddings_create(
        self,
        *,
        operation: str = "embedding",
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        resolved_model = model or self.config.model_for(operation)
        resolved_base = base_url if base_url not in ("", None) else None
        if resolved_base is None:
            resolved_base = self.config.base_url_for(operation)
        client = self._client_for(resolved_base)
        kwargs.setdefault("model", resolved_model)
        return client.embeddings.create(**kwargs)

    def with_overrides(
        self,
        *,
        models: Optional[Dict[str, Optional[str]]] = None,
        base_urls: Optional[Dict[str, Optional[str]]] = None,
        api_key: Optional[str] = None,
    ) -> "LLMClient":
        """Create a new client that applies the provided overrides."""

        return LLMClient(
            self.config.override(
                models=models, base_urls=base_urls, api_key=api_key
            ),
            client_kwargs=self._default_kwargs,
        )


def build_llm_config_from_settings(settings: Any) -> LLMConfig:
    """Construct an :class:`LLMConfig` instance from settings."""

    base_urls = {
        "default": settings.LLM_DEFAULT_BASE_URL or None,
        "extraction": settings.LLM_EXTRACTION_BASE_URL or None,
        "embedding": settings.LLM_EMBEDDING_BASE_URL or None,
        "rerank": settings.LLM_RERANK_BASE_URL or None,
    }
    models = {
        "default": settings.LLM_DEFAULT_MODEL or DEFAULT_MODEL,
        "extraction": settings.LLM_EXTRACTION_MODEL or None,
        "embedding": settings.LLM_EMBEDDING_MODEL,
        "rerank": settings.LLM_RERANK_MODEL or None,
    }
    cleaned_base_urls = {
        key: value for key, value in base_urls.items() if value is not None
    }
    cleaned_models = {
        key: value for key, value in models.items() if value
    }
    api_key = settings.LLM_API_KEY or settings.OPENAI_API_KEY or None
    return LLMConfig(
        api_key=api_key,
        base_urls={**{"default": cleaned_base_urls.get("default")}, **cleaned_base_urls},
        models={**{"default": cleaned_models.get("default", DEFAULT_MODEL)}, **cleaned_models},
        default_model=cleaned_models.get("default", DEFAULT_MODEL),
    )


def build_default_llm_client(
    settings: Any,
    *,
    models: Optional[Dict[str, Optional[str]]] = None,
    base_urls: Optional[Dict[str, Optional[str]]] = None,
    api_key: Optional[str] = None,
    client_kwargs: Optional[Dict[str, Any]] = None,
) -> LLMClient:
    """Helper to instantiate an :class:`LLMClient` using application settings."""

    config = build_llm_config_from_settings(settings)
    if any((models, base_urls, api_key)):
        config = config.override(models=models, base_urls=base_urls, api_key=api_key)
    return LLMClient(config, client_kwargs=client_kwargs)


__all__ = [
    "DEFAULT_MODEL",
    "LLMClient",
    "LLMConfig",
    "RateLimitError",
    "build_default_llm_client",
    "build_llm_config_from_settings",
]
