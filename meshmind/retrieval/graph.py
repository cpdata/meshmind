"""Graph-backed retrieval helpers that fetch memories directly from a driver."""
from __future__ import annotations

from typing import Callable, Iterable, List, Optional, Sequence

from meshmind.api.memory_manager import MemoryManager
from meshmind.core.types import Memory, SearchConfig
from meshmind.db.base_driver import GraphDriver
from meshmind.retrieval.search import (
    search as hybrid_search,
    search_bm25,
    search_exact,
    search_fuzzy,
    search_regex,
    search_vector,
)

Reranker = Callable[[str, Sequence[Memory], int], Sequence[Memory]]


def _load_memories(
    driver: GraphDriver,
    namespace: Optional[str] = None,
    entity_labels: Optional[Iterable[str]] = None,
) -> List[Memory]:
    manager = MemoryManager(driver)
    labels = _ensure_sequence(entity_labels)
    return manager.list_memories(namespace, labels)


def _ensure_sequence(values: Iterable[str] | None) -> List[str] | None:
    if values is None:
        return None
    return list(values)


def graph_hybrid_search(
    query: str,
    driver: GraphDriver,
    namespace: Optional[str] = None,
    entity_labels: Optional[Iterable[str]] = None,
    config: Optional[SearchConfig] = None,
    reranker: Reranker | None = None,
) -> List[Memory]:
    """Run the standard hybrid search against memories fetched from the graph."""

    labels = _ensure_sequence(entity_labels)
    memories = _load_memories(driver, namespace, labels)
    return hybrid_search(
        query,
        memories,
        namespace=namespace,
        entity_labels=labels,
        config=config,
        reranker=reranker,
    )


def graph_vector_search(
    query: str,
    driver: GraphDriver,
    namespace: Optional[str] = None,
    entity_labels: Optional[Iterable[str]] = None,
    config: Optional[SearchConfig] = None,
) -> List[Memory]:
    """Run vector search against graph-backed memories."""

    labels = _ensure_sequence(entity_labels)
    memories = _load_memories(driver, namespace, labels)
    return search_vector(
        query,
        memories,
        namespace=namespace,
        entity_labels=labels,
        config=config,
    )


def graph_regex_search(
    pattern: str,
    driver: GraphDriver,
    namespace: Optional[str] = None,
    entity_labels: Optional[Iterable[str]] = None,
    flags: int | None = None,
    top_k: int = 10,
) -> List[Memory]:
    """Execute regex search with memories loaded from the graph."""

    labels = _ensure_sequence(entity_labels)
    memories = _load_memories(driver, namespace, labels)
    return search_regex(
        pattern,
        memories,
        namespace=namespace,
        entity_labels=labels,
        flags=flags,
        top_k=top_k,
    )


def graph_exact_search(
    query: str,
    driver: GraphDriver,
    namespace: Optional[str] = None,
    entity_labels: Optional[Iterable[str]] = None,
    fields: Optional[Iterable[str]] = None,
    case_sensitive: bool = False,
    top_k: int = 10,
) -> List[Memory]:
    """Execute exact-match search using graph-backed memories."""

    labels = _ensure_sequence(entity_labels)
    memories = _load_memories(driver, namespace, labels)
    target_fields = list(fields) if fields else None
    return search_exact(
        query,
        memories,
        namespace=namespace,
        entity_labels=labels,
        fields=target_fields,
        case_sensitive=case_sensitive,
        top_k=top_k,
    )


def graph_bm25_search(
    query: str,
    driver: GraphDriver,
    namespace: Optional[str] = None,
    entity_labels: Optional[Iterable[str]] = None,
    top_k: int = 10,
) -> List[Memory]:
    """Execute BM25 search using graph-backed memories."""

    labels = _ensure_sequence(entity_labels)
    memories = _load_memories(driver, namespace, labels)
    return search_bm25(
        query,
        memories,
        namespace=namespace,
        entity_labels=labels,
        top_k=top_k,
    )


def graph_fuzzy_search(
    query: str,
    driver: GraphDriver,
    namespace: Optional[str] = None,
    entity_labels: Optional[Iterable[str]] = None,
    top_k: int = 10,
) -> List[Memory]:
    """Execute fuzzy search against graph-backed memories."""

    labels = _ensure_sequence(entity_labels)
    memories = _load_memories(driver, namespace, labels)
    return search_fuzzy(
        query,
        memories,
        namespace=namespace,
        entity_labels=labels,
        top_k=top_k,
    )
