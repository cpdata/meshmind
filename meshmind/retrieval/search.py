"""
Unified dispatcher for various retrieval strategies.
"""
from typing import List, Optional

from meshmind.core.types import Memory, SearchConfig
from meshmind.retrieval.bm25 import bm25_search
from meshmind.retrieval.fuzzy import fuzzy_search
from meshmind.retrieval.hybrid import hybrid_search
from meshmind.retrieval.filters import (
    filter_by_namespace,
    filter_by_entity_labels,
    filter_by_metadata,
)


def search(
    query: str,
    memories: List[Memory],
    namespace: Optional[str] = None,
    entity_labels: Optional[List[str]] = None,
    config: Optional[SearchConfig] = None,
) -> List[Memory]:
    """
    Perform hybrid search over memories with optional filters.

    :param query: Query string.
    :param memories: List of Memory objects.
    :param namespace: Filter by namespace.
    :param entity_labels: Filter by entity labels.
    :param config: SearchConfig overriding defaults.
    :return: Ranked list of Memory objects.
    """
    # Apply filters
    mems = filter_by_namespace(memories, namespace)
    mems = filter_by_entity_labels(mems, entity_labels)
    if config and config.filters:
        mems = filter_by_metadata(mems, config.filters)

    # Use hybrid search by default
    cfg = config or SearchConfig()
    ranked = hybrid_search(query, mems, cfg)
    # Return only Memory objects
    return [m for m, _ in ranked]


def search_bm25(
    query: str,
    memories: List[Memory],
    namespace: Optional[str] = None,
    entity_labels: Optional[List[str]] = None,
    top_k: int = 10,
) -> List[Memory]:
    mems = filter_by_namespace(memories, namespace)
    mems = filter_by_entity_labels(mems, entity_labels)
    results = bm25_search(query, mems, top_k=top_k)
    return [m for m, _ in results]


def search_fuzzy(
    query: str,
    memories: List[Memory],
    namespace: Optional[str] = None,
    entity_labels: Optional[List[str]] = None,
    top_k: int = 10,
) -> List[Memory]:
    mems = filter_by_namespace(memories, namespace)
    mems = filter_by_entity_labels(mems, entity_labels)
    results = fuzzy_search(query, mems, top_k=top_k)
    return [m for m, _ in results]