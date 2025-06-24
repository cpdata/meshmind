"""
Hybrid retrieval combining vector and lexical (BM25) scores.
"""
from typing import List, Tuple

from meshmind.core.types import Memory, SearchConfig
from meshmind.retrieval.bm25 import bm25_search
from meshmind.core.embeddings import EncoderRegistry
from meshmind.core.similarity import cosine_similarity


def hybrid_search(
    query: str,
    memories: List[Memory],
    config: SearchConfig,
) -> List[Tuple[Memory, float]]:
    """
    Perform hybrid search by fusing vector and BM25 scores.

    :param query: Query string.
    :param memories: List of Memory objects with precomputed embeddings.
    :param config: SearchConfig containing encoder, weights, top_k.
    :return: List of (Memory, hybrid_score) tuples.
    """
    # Vector search: compute cosine similarity between query embedding and memory embeddings
    encoder = EncoderRegistry.get(config.encoder)
    q_emb = encoder.encode([query])[0]
    vector_scores = {}
    for mem in memories:
        emb = getattr(mem, 'embedding', None)
        if emb is None:
            continue
        try:
            sim = cosine_similarity(q_emb, emb)
        except Exception:
            sim = 0.0
        vector_scores[mem.uuid] = float(sim)

    # Lexical BM25 search
    bm25_results = bm25_search(query, memories, top_k=config.top_k)
    bm25_scores = {mem.uuid: score for mem, score in bm25_results}

    # fusing scores
    combined: List[Tuple[Memory, float]] = []
    for mem in memories:
        vs = vector_scores.get(mem.uuid, 0.0)
        ls = bm25_scores.get(mem.uuid, 0.0)
        score = config.hybrid_weights[0] * vs + config.hybrid_weights[1] * ls
        combined.append((mem, score))
    # sort and return top_k
    combined.sort(key=lambda x: x[1], reverse=True)
    return combined[: config.top_k]