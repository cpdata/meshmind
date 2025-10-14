"""Vector-only retrieval helpers."""
from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

from meshmind.core.embeddings import EncoderRegistry
from meshmind.core.similarity import cosine_similarity
from meshmind.core.types import Memory, SearchConfig


def vector_search(
    query: str,
    memories: Sequence[Memory],
    config: SearchConfig | None = None,
) -> List[Tuple[Memory, float]]:
    """Rank memories using cosine similarity against the query embedding."""
    if not memories:
        return []

    cfg = config or SearchConfig()
    encoder = EncoderRegistry.get(cfg.encoder)
    query_embedding = encoder.encode([query])[0]

    scored: List[Tuple[Memory, float]] = []
    for memory in memories:
        embedding = getattr(memory, "embedding", None)
        if embedding is None:
            continue
        try:
            score = cosine_similarity(query_embedding, embedding)
        except Exception:
            score = 0.0
        scored.append((memory, float(score)))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[: cfg.top_k]


def vector_search_from_embeddings(
    query_embedding: Sequence[float],
    memories: Iterable[Memory],
    top_k: int = 10,
) -> List[Tuple[Memory, float]]:
    """Rank memories when the query embedding is precomputed."""
    scored: List[Tuple[Memory, float]] = []
    for memory in memories:
        embedding = getattr(memory, "embedding", None)
        if embedding is None:
            continue
        try:
            score = cosine_similarity(query_embedding, embedding)
        except Exception:
            score = 0.0
        scored.append((memory, float(score)))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:top_k]
