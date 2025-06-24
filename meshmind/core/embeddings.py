"""
Embedding encoders and registry for MeshMind.
"""
from typing import List, Dict, Any
import time

_OPENAI_AVAILABLE = True
try:
    from openai import OpenAI
    from openai.error import RateLimitError
except ImportError:
    _OPENAI_AVAILABLE = False
    openai = None  # type: ignore
    class RateLimitError(Exception):  # type: ignore
        pass

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
    ):
        if not _OPENAI_AVAILABLE:
            raise ImportError(
                "openai package is required for OpenAIEmbeddingEncoder"
            )
        try:
            openai.api_key = settings.OPENAI_API_KEY
        except Exception:
            pass

        self.llm_client = OpenAI()
        self.RateLimitError = RateLimitError
        self.model_name = model_name
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
                    model=self.model_name,
                    input=texts,
                )
                return [item['embedding'] for item in response['data']]
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
        from sentence_transformers import SentenceTransformer

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