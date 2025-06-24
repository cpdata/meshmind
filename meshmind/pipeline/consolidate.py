"""
Pipeline for consolidating and summarizing duplicate memories.
"""
from typing import List, Any

from meshmind.core.types import Memory


def consolidate_memories(memories: List[Memory]) -> List[Memory]:
    """
    Consolidate duplicate memories by name, preferring high importance.

    :param memories: List of Memory objects.
    :return: List of consolidated Memory objects.
    """
    # Group memories by name
    grouped: dict[str, List[Memory]] = {}
    for mem in memories:
        grouped.setdefault(mem.name, []).append(mem)

    consolidated: List[Memory] = []
    for name, group in grouped.items():
        # Choose the memory with highest importance (fallback to first)
        selected = max(
            group,
            key=lambda m: (m.importance or 0.0),
        )
        consolidated.append(selected)
    return consolidated