"""Unified dispatcher for various retrieval strategies."""
from __future__ import annotations

import re
from typing import Callable, List, Optional, Sequence

from meshmind.core.types import Memory, SearchConfig
from meshmind.retrieval.bm25 import bm25_search
from meshmind.retrieval.fuzzy import fuzzy_search
from meshmind.retrieval.hybrid import hybrid_search
from meshmind.retrieval.filters import (
    filter_by_namespace,
    filter_by_entity_labels,
    filter_by_metadata,
)
from meshmind.retrieval.rerank import apply_reranker
from meshmind.retrieval.vector import vector_search

Reranker = Callable[[str, Sequence[Memory], int], Sequence[Memory]]


def _apply_filters(
    memories: Sequence[Memory],
    namespace: Optional[str],
    entity_labels: Optional[List[str]],
    config: Optional[SearchConfig],
) -> List[Memory]:
    mems = filter_by_namespace(list(memories), namespace)
    mems = filter_by_entity_labels(mems, entity_labels)
    if config and config.filters:
        mems = filter_by_metadata(mems, config.filters)
    return mems


def search(
    query: str,
    memories: List[Memory],
    namespace: Optional[str] = None,
    entity_labels: Optional[List[str]] = None,
    config: Optional[SearchConfig] = None,
    reranker: Reranker | None = None,
) -> List[Memory]:
    """Perform hybrid search with optional reranking."""
    cfg = config or SearchConfig()
    mems = _apply_filters(memories, namespace, entity_labels, cfg)
    ranked = hybrid_search(query, mems, cfg)
    ordered = [m for m, _ in ranked]
    if not ordered:
        return []
    return apply_reranker(query, ordered, cfg.rerank_k, reranker)


def search_bm25(
    query: str,
    memories: List[Memory],
    namespace: Optional[str] = None,
    entity_labels: Optional[List[str]] = None,
    top_k: int = 10,
) -> List[Memory]:
    mems = _apply_filters(memories, namespace, entity_labels, None)
    results = bm25_search(query, mems, top_k=top_k)
    return [m for m, _ in results]


def search_fuzzy(
    query: str,
    memories: List[Memory],
    namespace: Optional[str] = None,
    entity_labels: Optional[List[str]] = None,
    top_k: int = 10,
) -> List[Memory]:
    mems = _apply_filters(memories, namespace, entity_labels, None)
    results = fuzzy_search(query, mems, top_k=top_k)
    return [m for m, _ in results]


def search_vector(
    query: str,
    memories: List[Memory],
    namespace: Optional[str] = None,
    entity_labels: Optional[List[str]] = None,
    config: Optional[SearchConfig] = None,
) -> List[Memory]:
    cfg = config or SearchConfig()
    mems = _apply_filters(memories, namespace, entity_labels, cfg)
    results = vector_search(query, mems, cfg)
    return [m for m, _ in results]


def search_regex(
    pattern: str,
    memories: List[Memory],
    namespace: Optional[str] = None,
    entity_labels: Optional[List[str]] = None,
    flags: int | None = None,
    top_k: int = 10,
) -> List[Memory]:
    mems = _apply_filters(memories, namespace, entity_labels, None)
    regex = re.compile(pattern, flags or re.IGNORECASE)
    scored: List[tuple[Memory, int]] = []
    for mem in mems:
        haystacks = [mem.name] + [str(value) for value in mem.metadata.values()]
        matches = [len(regex.findall(h)) for h in haystacks]
        score = max(matches, default=0)
        if score > 0:
            scored.append((mem, score))
    scored.sort(key=lambda item: item[1], reverse=True)
    return [mem for mem, _ in scored[:top_k]]


def search_exact(
    query: str,
    memories: List[Memory],
    namespace: Optional[str] = None,
    entity_labels: Optional[List[str]] = None,
    fields: Optional[List[str]] = None,
    case_sensitive: bool = False,
    top_k: int = 10,
) -> List[Memory]:
    mems = _apply_filters(memories, namespace, entity_labels, None)
    needle = query if case_sensitive else query.lower()
    fields = fields or ["name"]

    def normalize(value: object) -> str:
        text = "" if value is None else str(value)
        return text if case_sensitive else text.lower()

    matched: List[Memory] = []
    for mem in mems:
        for field in fields:
            value = getattr(mem, field, None)
            if value is None and field == "metadata":
                for meta_val in mem.metadata.values():
                    if normalize(meta_val) == needle:
                        matched.append(mem)
                        break
                continue
            if normalize(value) == needle:
                matched.append(mem)
                break
    return matched[:top_k]
