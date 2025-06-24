from typing import Any, List

def deduplicate(memories: List[Any], threshold: float = 0.95) -> List[Any]:
    """
    Remove duplicate Memory objects based on exact name match or embedding similarity.

    :param memories: List of Memory-like objects with 'name' and optional 'embedding'.
    :param threshold: Cosine similarity threshold above which two memories are considered duplicates.
    :return: Deduplicated list of Memory-like objects.
    """
    from meshmind.core.similarity import cosine_similarity

    unique: List[Any] = []
    seen_names: set = set()
    for mem in memories:
        name = getattr(mem, 'name', None)
        # Skip if name duplicate
        if name is None or name in seen_names:
            continue
        # Skip if embedding too similar to an existing memory (enabled only when threshold>=0.5)
        duplicate = False
        if threshold >= 0.5:
            emb = getattr(mem, 'embedding', None)
            if emb is not None:
                for u in unique:
                    u_emb = getattr(u, 'embedding', None)
                    if u_emb is None:
                        continue
                    try:
                        sim = cosine_similarity(emb, u_emb)
                    except Exception:
                        continue
                    if sim >= threshold:
                        duplicate = True
                        break
        if duplicate:
            continue
        # Unique memory: record and add
        seen_names.add(name)
        unique.append(mem)
    return unique

def score_importance(memories: List[Any]) -> List[Any]:
    """
    Assign or update importance scores for each Memory.

    :param memories: List of Memory-like objects.
    :return: List of Memory-like objects with updated importance.
    """
    # Assign a default importance score if missing
    for mem in memories:
        if getattr(mem, 'importance', None) is None:
            try:
                mem.importance = 1.0
            except Exception:
                continue
    return memories

def compress(memories: List[Any]) -> List[Any]:
    """
    Compress long text fields in Memory objects to save space or reduce tokens.

    :param memories: List of Memory-like objects.
    :return: List of Memory-like objects with compressed content.
    """
    try:
        from meshmind.pipeline.compress import compress_memories
        return compress_memories(memories)
    except ImportError:
        # compression module unavailable, return original
        return memories
    except Exception:
        # on any error, fallback to original
        return memories