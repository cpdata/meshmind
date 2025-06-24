"""Utility functions for MeshMind."""
import uuid
from datetime import datetime
import hashlib
from typing import Any
import tiktoken
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
    """Returns the number of tokens in a text string.
    Args:
        string: The text string to count tokens for.
        encoding_name: The name of the encoding to use. Defaults to "o200k_base".
    Returns:
        The number of tokens in the text string.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens