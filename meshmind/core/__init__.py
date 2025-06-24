"""Core components of MeshMind."""
from .config import settings
from .errors import MeshMindError, ConfigError, StorageError, NotFoundError, ValidationError
from .utils import generate_uuid, current_timestamp, hash_string, hash_dict
from .embeddings import OpenAIEmbeddingEncoder, SentenceTransformerEncoder, EncoderRegistry
from .similarity import cosine_similarity, euclidean_distance

__all__ = [
    "settings",
    "MeshMindError", "ConfigError", "StorageError", "NotFoundError", "ValidationError",
    "generate_uuid", "current_timestamp", "hash_string", "hash_dict",
    "OpenAIEmbeddingEncoder", "SentenceTransformerEncoder", "EncoderRegistry",
    "cosine_similarity", "euclidean_distance",
]