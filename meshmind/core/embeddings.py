"""Embedding encoder implementations and registry utilities."""
from __future__ import annotations

import time
from typing import Any, Dict, List

from meshmind.llm_client import (
    LLMClient,
    LLMConfig,
    RateLimitError,
    build_llm_config_from_settings,
)

from .config import settings


class OpenAIEmbeddingEncoder:
    """
    Encoder that uses OpenAI's embedding API with retry on rate limits.
    """
    def __init__(
        self,
        model_name: str = settings.EMBEDDING_MODEL,
        max_retries: int = 5,
        backoff_factor: float = 1.0,
        llm_client: LLMClient | None = None,
        llm_config: LLMConfig | None = None,
    ):
        config = llm_config or build_llm_config_from_settings(settings)
        if model_name:
            config = config.override(models={"embedding": model_name})
        resolved_model = config.model_for("embedding", fallback=model_name)
        self.llm_client = llm_client or LLMClient(config)
        self.RateLimitError = RateLimitError
        self.model_name = resolved_model
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def encode(self, texts: List[str] | str) -> List[List[float]]:
        """
        Generate embeddings for a text or list of texts using OpenAI API.
        Retries on rate limit errors with exponential backoff.
        """
        if isinstance(texts, str):
            texts = [texts]

        for attempt in range(self.max_retries):
            try:
                response = self.llm_client.embeddings.create(
                    operation="embedding",
                    model=self.model_name,
                    input=texts,
                )
                data = getattr(response, "data", None)
                if data is None:
                    data = response.get("data", [])  # type: ignore[assignment]
                embeddings: List[List[float]] = []
                for item in data:
                    if hasattr(item, "embedding"):
                        embeddings.append(list(getattr(item, "embedding")))
                    else:
                        embeddings.append(list(item["embedding"]))
                return embeddings
            except self.RateLimitError:
                time.sleep(self.backoff_factor * (2 ** attempt))
            except Exception:
                raise
        raise RuntimeError(
            f"OpenAI embedding request failed after {self.max_retries} retries"
        )


class SentenceTransformerEncoder:
    """
    Encoder that uses a local SentenceTransformer model.
    """
    def __init__(self, model_name: str):
        try:  # pragma: no cover - optional dependency
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError(
                "sentence-transformers is required for SentenceTransformerEncoder."
                " Install the optional 'sentence-transformers' extra to enable this encoder."
            ) from exc

        self.model = SentenceTransformer(model_name)

    def encode(self, texts: List[str] | str) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using SentenceTransformer.
        """
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = self.model.encode(texts)
        try:
            return embeddings.tolist()
        except AttributeError:
            return embeddings  # assume already a list


class EncoderRegistry:
    """
    Registry mapping encoder names to encoder instances.
    """
    _encoders: Dict[str, Any] = {}

    @classmethod
    def register(cls, name: str, encoder: Any) -> None:
        """Register an encoder under a given name."""
        cls._encoders[name] = encoder

    @classmethod
    def get(cls, name: str) -> Any:
        """Retrieve a registered encoder by name."""
        encoder = cls._encoders.get(name)
        if encoder is None:
            raise KeyError(f"Encoder '{name}' not found in registry")
        return encoder

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Return True if an encoder ``name`` has been registered."""

        return name in cls._encoders

    @classmethod
    def available(cls) -> List[str]:
        """Return the list of registered encoder identifiers."""

        return list(cls._encoders.keys())

    @classmethod
    def clear(cls) -> None:
        """Remove all registered encoders. Intended for testing."""

        cls._encoders.clear()
