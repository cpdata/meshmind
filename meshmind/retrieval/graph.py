"""Graph-backed retrieval helpers that fetch memories directly from a driver."""
from __future__ import annotations

from typing import Callable, Iterable, List, Optional, Sequence

from meshmind.api.memory_manager import MemoryManager
from meshmind.core.embeddings import EncoderRegistry
from meshmind.core.types import Memory, SearchConfig
from meshmind.db.base_driver import GraphDriver
from meshmind.retrieval.search import (
    search as hybrid_search,
    search_bm25,
    search_exact,
    search_fuzzy,
    search_regex,
)
from meshmind.retrieval.vector import vector_search_from_embeddings

Reranker = Callable[[str, Sequence[Memory], int], Sequence[Memory]]


def _load_memories(
    driver: GraphDriver,
    namespace: Optional[str] = None,
    entity_labels: Optional[Iterable[str]] = None,
    *,
    query: Optional[str] = None,
    config: Optional[SearchConfig] = None,
    top_k: Optional[int] = None,
    use_search: bool = True,
) -> List[Memory]:
    manager = MemoryManager(driver)
    labels = _ensure_sequence(entity_labels)
    candidate_limit: Optional[int] = None
    if use_search:
        limit_hint = 0
        if config is not None:
            limit_hint = max(limit_hint, config.top_k * 5)
            if config.rerank_k:
                limit_hint = max(limit_hint, config.rerank_k * 2)
        if top_k:
            limit_hint = max(limit_hint, top_k * 5)
        candidate_limit = limit_hint or None
    return manager.list_memories(
        namespace,
        labels,
        limit=candidate_limit,
        query=query if use_search else None,
        use_search=use_search,
    )


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
    memories = _load_memories(
        driver,
        namespace,
        labels,
        query=query,
        config=config,
        use_search=True,
    )
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

    cfg = config or SearchConfig()
    labels = _ensure_sequence(entity_labels)
    encoder = EncoderRegistry.get(cfg.encoder)
    query_embedding = encoder.encode([query])[0]

    results: List[Memory] = []
    try:
        scored = driver.vector_search(
            query_embedding,
            namespace=namespace,
            entity_labels=labels,
            top_k=cfg.top_k,
        )
    except Exception:
        scored = []

    for record, _score in scored:
        try:
            results.append(Memory(**record))
        except Exception:
            continue

    if results:
        return results[: cfg.top_k]

    memories = _load_memories(
        driver,
        namespace,
        labels,
        query=query,
        config=config,
        use_search=True,
    )
    reranked = vector_search_from_embeddings(query_embedding, memories, cfg.top_k)
    return [mem for mem, _ in reranked]


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
    memories = _load_memories(
        driver,
        namespace,
        labels,
        top_k=top_k,
        use_search=False,
    )
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
    memories = _load_memories(
        driver,
        namespace,
        labels,
        query=query,
        top_k=top_k,
        use_search=True,
    )
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
    memories = _load_memories(
        driver,
        namespace,
        labels,
        query=query,
        top_k=top_k,
        use_search=True,
    )
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
    memories = _load_memories(
        driver,
        namespace,
        labels,
        query=query,
        top_k=top_k,
        use_search=True,
    )
    return search_fuzzy(
        query,
        memories,
        namespace=namespace,
        entity_labels=labels,
        top_k=top_k,
    )
