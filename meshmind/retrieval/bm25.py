"""
TF-IDF based retrieval (approximate BM25) using scikit-learn.
"""
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
    # Prepare document texts
    docs = [mem.name for mem in memories]
    # Vectorize documents and query
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(docs)
    query_vec = vectorizer.transform([query])
    # Compute cosine similarity scores
    scores = cosine_similarity(query_vec, tfidf_matrix)[0]
    # Rank scores
    ranked = sorted(
        enumerate(scores), key=lambda x: x[1], reverse=True
    )
    # Collect top_k non-zero scores
    results: List[Tuple[Memory, float]] = []
    for idx, score in ranked:
        if score <= 0:
            break
        results.append((memories[idx], float(score)))
        if len(results) >= top_k:
            break
    return results