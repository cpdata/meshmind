"""Fuzzy string matching retrieval with optional ``rapidfuzz`` acceleration."""
from __future__ import annotations

from difflib import SequenceMatcher
from typing import Callable, List, Tuple

try:  # pragma: no cover - optional dependency
    from rapidfuzz import fuzz, process
except ImportError:  # pragma: no cover - fallback for environments without rapidfuzz
    fuzz = None  # type: ignore
    process = None  # type: ignore

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
    choices = [mem.name for mem in memories]

    if process is not None and fuzz is not None:
        raw_results = process.extract(
            query,
            choices,
            scorer=fuzz.WRatio,
            limit=top_k,
            score_cutoff=score_cutoff * 100,
        )
        results: List[Tuple[Memory, float]] = []
        for match, score, idx in raw_results:
            results.append((memories[idx], score / 100.0))
        return results

    scorer: Callable[[str, str], float] = _sequence_ratio
    results: List[Tuple[Memory, float]] = []
    for idx, name in enumerate(choices):
        score = scorer(query, name)
        if score < score_cutoff:
            continue
        results.append((memories[idx], score))
    results.sort(key=lambda item: item[1], reverse=True)
    return results[:top_k]


def _sequence_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()
