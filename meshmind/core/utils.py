"""Utility helpers for MeshMind with optional dependency guards."""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime
from functools import lru_cache
from typing import Any, Optional

_TIKTOKEN = None


def _ensure_tiktoken() -> Any:
    """Return the ``tiktoken`` module if it is installed."""

    global _TIKTOKEN
    if _TIKTOKEN is None:
        try:
            import tiktoken  # type: ignore
        except ImportError as exc:  # pragma: no cover - exercised in minimal envs
            raise RuntimeError(
                "tiktoken is required for token counting but is not installed."
                " Install the optional 'tiktoken' extra to enable compression features."
            ) from exc
        _TIKTOKEN = tiktoken
    return _TIKTOKEN


@lru_cache(maxsize=8)
def get_token_encoder(encoding_name: str = "o200k_base", optional: bool = False) -> Optional[Any]:
    """Return a cached tiktoken encoder or ``None`` when optional."""

    try:
        module = _ensure_tiktoken()
    except RuntimeError:
        if optional:
            return None
        raise
    return module.get_encoding(encoding_name)


def generate_uuid() -> str:
    """Generate a UUID4 string."""
    return str(uuid.uuid4())

def current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.utcnow()

def hash_string(value: str) -> str:
    """Hash a string using SHA-256 and return the hex digest."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def hash_dict(data: Any) -> str:
    """Hash a dictionary by converting it to its string representation."""
    return hash_string(str(data))

def num_tokens_from_string(string: str, encoding_name: str = "o200k_base") -> int:
    """Return the number of tokens in ``string`` for ``encoding_name``."""

    encoder = get_token_encoder(encoding_name, optional=False)
    return len(encoder.encode(string))
