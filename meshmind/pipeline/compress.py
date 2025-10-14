"""Token-aware compression helpers for memory metadata."""
from __future__ import annotations

from typing import List

from meshmind.core.types import Memory
from meshmind.core.utils import get_token_encoder


def compress_memories(
    memories: List[Memory], max_tokens: int = 500
) -> List[Memory]:
    """
    Compress long memory metadata content to fit within max token budget.

    :param memories: List of Memory objects, potentially with metadata['content'].
    :param max_tokens: Maximum number of tokens allowed per memory.
    :return: List of Memory objects with content possibly shortened.
    """
    encoder = get_token_encoder("o200k_base", optional=True)
    if encoder is None:
        return memories
    compressed = []
    for mem in memories:
        content = mem.metadata.get('content')
        if not isinstance(content, str):
            compressed.append(mem)
            continue
        tokens = encoder.encode(content)
        if len(tokens) <= max_tokens:
            compressed.append(mem)
            continue
        # Truncate tokens and decode back to string
        truncated = encoder.decode(tokens[:max_tokens])
        mem.metadata['content'] = truncated
        compressed.append(mem)
    return compressed
