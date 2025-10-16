"""Similarity and distance metrics for MeshMind."""
from __future__ import annotations

from math import sqrt
from typing import Sequence

try:  # pragma: no cover - optional dependency
    import numpy as np
except ImportError:  # pragma: no cover - fallback path for test sandboxes
    np = None  # type: ignore


def cosine_similarity(vec1: Sequence[float], vec2: Sequence[float]) -> float:
    """
    Compute the cosine similarity between two vectors.
    Returns 0.0 if either vector has zero magnitude.
    """
    if np is not None:
        a = np.array(vec1, dtype=float)
        b = np.array(vec2, dtype=float)
        if a.shape != b.shape:
            raise ValueError("Vectors must be the same length")
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    if len(vec1) != len(vec2):
        raise ValueError("Vectors must be the same length")
    dot = sum(float(a) * float(b) for a, b in zip(vec1, vec2))
    norm_a = sqrt(sum(float(a) ** 2 for a in vec1))
    norm_b = sqrt(sum(float(b) ** 2 for b in vec2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(dot / (norm_a * norm_b))


def euclidean_distance(vec1: Sequence[float], vec2: Sequence[float]) -> float:
    """
    Compute the Euclidean distance between two vectors.
    """
    if np is not None:
        a = np.array(vec1, dtype=float)
        b = np.array(vec2, dtype=float)
        if a.shape != b.shape:
            raise ValueError("Vectors must be the same length")
        return float(np.linalg.norm(a - b))

    if len(vec1) != len(vec2):
        raise ValueError("Vectors must be the same length")
    return float(sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(vec1, vec2))))