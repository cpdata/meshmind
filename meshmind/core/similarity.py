"""
Similarity and distance metrics for MeshMind.
"""
from typing import Sequence
import numpy as np


def cosine_similarity(vec1: Sequence[float], vec2: Sequence[float]) -> float:
    """
    Compute the cosine similarity between two vectors.
    Returns 0.0 if either vector has zero magnitude.
    """
    a = np.array(vec1, dtype=float)
    b = np.array(vec2, dtype=float)
    if a.shape != b.shape:
        raise ValueError("Vectors must be the same length")
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def euclidean_distance(vec1: Sequence[float], vec2: Sequence[float]) -> float:
    """
    Compute the Euclidean distance between two vectors.
    """
    a = np.array(vec1, dtype=float)
    b = np.array(vec2, dtype=float)
    if a.shape != b.shape:
        raise ValueError("Vectors must be the same length")
    return float(np.linalg.norm(a - b))