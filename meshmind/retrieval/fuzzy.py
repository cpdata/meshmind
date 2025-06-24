"""
Fuzzy string matching retrieval using rapidfuzz.
"""
from typing import List, Tuple
from rapidfuzz import process, fuzz

from meshmind.core.types import Memory


def fuzzy_search(
    query: str,
    memories: List[Memory],
    top_k: int = 10,
    score_cutoff: float = 0.0,
) -> List[Tuple[Memory, float]]:
    """
    Retrieve memories ranked by fuzzy string similarity of their names to the query.

    :param query: Query string.
    :param memories: List of Memory objects (must have 'name' attribute).
    :param top_k: Number of top results to return.
    :param score_cutoff: Minimum score (0-1) to include in results.
    :return: List of (Memory, normalized_score) tuples.
    """
    # Build choices mapping
    choices = [mem.name for mem in memories]
    # rapidfuzz returns scores in 0-100 range
    raw_results = process.extract(
        query,
        choices,
        scorer=fuzz.WRatio,
        limit=top_k,
        score_cutoff=score_cutoff * 100,
    )
    results: List[Tuple[Memory, float]] = []
    for match, score, idx in raw_results:
        # Normalize score to [0,1]
        norm = score / 100.0
        results.append((memories[idx], norm))
    return results