"""
Filtering utilities for Memory lists.
"""
from typing import Any, Dict, List, Optional

from meshmind.core.types import Memory


def filter_by_namespace(
    memories: List[Memory], namespace: Optional[str]
) -> List[Memory]:
    if namespace is None:
        return memories
    return [m for m in memories if m.namespace == namespace]


def filter_by_entity_labels(
    memories: List[Memory], labels: Optional[List[str]]
) -> List[Memory]:
    if not labels:
        return memories
    return [m for m in memories if m.entity_label in labels]


def filter_by_metadata(
    memories: List[Memory], filters: Optional[Dict[str, Any]]
) -> List[Memory]:
    if not filters:
        return memories
    result: List[Memory] = []
    for m in memories:
        ok = True
        for k, v in filters.items():
            if m.metadata.get(k) != v:
                ok = False
                break
        if ok:
            result.append(m)
    return result