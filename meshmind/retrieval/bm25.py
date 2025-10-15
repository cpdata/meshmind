"""TF-IDF based retrieval (approximate BM25) using scikit-learn or fallbacks."""
from __future__ import annotations

import math
import re
from collections import Counter
from typing import List, Tuple

try:  # pragma: no cover - optional dependency
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:  # pragma: no cover - exercised when sklearn is unavailable
    TfidfVectorizer = None  # type: ignore
    cosine_similarity = None  # type: ignore

from meshmind.core.types import Memory


def bm25_search(
    query: str,
    memories: List[Memory],
    top_k: int = 10,
) -> List[Tuple[Memory, float]]:
    """
    Retrieve memories ranked by TF-IDF cosine similarity to the query.

    :param query: Query string.
    :param memories: List of Memory objects (must have 'name' attribute).
    :param top_k: Number of top results to return.
    :return: List of (Memory, similarity_score) tuples.
    """
    docs = [mem.name for mem in memories]

    if TfidfVectorizer is not None and cosine_similarity is not None:
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(docs)
        query_vec = vectorizer.transform([query])
        scores = cosine_similarity(query_vec, tfidf_matrix)[0]
        ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
        results: List[Tuple[Memory, float]] = []
        for idx, score in ranked:
            if score <= 0:
                break
            results.append((memories[idx], float(score)))
            if len(results) >= top_k:
                break
        return results

    tokens = [_tokenize(doc) for doc in docs]
    query_tokens = Counter(_tokenize(query))
    doc_freq: Counter[str] = Counter()
    for tok_set in map(set, tokens):
        for token in tok_set:
            doc_freq[token] += 1

    scores: List[Tuple[int, float]] = []
    total_docs = max(len(tokens), 1)
    for idx, doc_tokens in enumerate(tokens):
        doc_count = Counter(doc_tokens)
        doc_len = len(doc_tokens) or 1
        score = 0.0
        for token, q_tf in query_tokens.items():
            tf = doc_count.get(token, 0) / doc_len
            idf = math.log((total_docs + 1) / (doc_freq.get(token, 0) + 1)) + 1.0
            score += tf * idf * q_tf
        scores.append((idx, score))

    ranked = sorted(scores, key=lambda x: x[1], reverse=True)
    results: List[Tuple[Memory, float]] = []
    for idx, score in ranked:
        if score <= 0:
            continue
        results.append((memories[idx], float(score)))
        if len(results) >= top_k:
            break
    return results


def _tokenize(text: str) -> List[str]:
    return re.findall(r"\w+", text.lower())
