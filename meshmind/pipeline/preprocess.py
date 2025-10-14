from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

import math
import re

from meshmind.core.observability import log_event, telemetry

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

def _text_from_memory(mem: Any) -> str:
    chunks: List[str] = []
    name = getattr(mem, "name", None)
    if isinstance(name, str):
        chunks.append(name)
    metadata = getattr(mem, "metadata", None) or {}
    if isinstance(metadata, dict):
        for value in metadata.values():
            if isinstance(value, str):
                chunks.append(value)
    return " ".join(chunks)


def _recent_bonus(reference_time: Any, now: datetime) -> float:
    if reference_time is None:
        return 0.0
    try:
        if isinstance(reference_time, datetime):
            ref = reference_time
        else:
            ref = datetime.fromisoformat(str(reference_time))
    except Exception:
        return 0.0
    if ref.tzinfo is None:
        ref = ref.replace(tzinfo=timezone.utc)
    delta = now - ref
    seconds = max(delta.total_seconds(), 0.0)
    week = 7 * 24 * 60 * 60
    return max(0.0, 1.0 - min(seconds / week, 1.0))


def score_importance(memories: List[Any]) -> List[Any]:
    """Assign a heuristic importance score for each memory."""

    now = datetime.now(timezone.utc)
    for mem in memories:
        try:
            if getattr(mem, "importance", None) not in (None, 0):
                continue

            text = _text_from_memory(mem)
            tokens = re.findall(r"\w+", text.lower())
            unique_ratio = len(set(tokens)) / max(len(tokens), 1)
            length_factor = min(len(tokens) / 25.0, 1.5)
            digit_bonus = 0.3 if any(ch.isdigit() for ch in text) else 0.0
            recency_bonus = _recent_bonus(getattr(mem, "reference_time", None), now)
            metadata_size = len(getattr(mem, "metadata", {}) or {})
            metadata_bonus = min(metadata_size * 0.05, 0.25)

            embedding = getattr(mem, "embedding", None) or []
            magnitude = math.sqrt(sum((float(x) ** 2 for x in embedding))) if embedding else 0.0
            magnitude_bonus = min(magnitude / 10.0, 0.4)

            score = 0.5 + (0.8 * unique_ratio) + length_factor + digit_bonus
            score += recency_bonus + metadata_bonus + magnitude_bonus
            mem.importance = round(min(score, 5.0), 3)
        except Exception:
            continue
    metrics = summarize_importance(memories)
    telemetry.gauge("importance.mean", metrics["mean"])
    telemetry.gauge("importance.stddev", metrics["stddev"])
    telemetry.gauge("importance.count", float(metrics["count"]))
    log_event(
        "importance.scored",
        mean=metrics["mean"],
        stddev=metrics["stddev"],
        count=metrics["count"],
        recent=metrics["recent_bonus"],
    )
    return memories


def summarize_importance(memories: List[Any]) -> Dict[str, float]:
    """Return descriptive statistics about importance assignments."""

    values: List[float] = []
    recency_bonus_total = 0.0
    now = datetime.now(timezone.utc)
    for mem in memories:
        val = getattr(mem, "importance", None)
        if val is None:
            continue
        try:
            values.append(float(val))
            recency_bonus_total += _recent_bonus(getattr(mem, "reference_time", None), now)
        except Exception:
            continue
    count = len(values)
    if not values:
        return {"mean": 0.0, "stddev": 0.0, "count": 0.0, "recent_bonus": 0.0}
    mean_value = sum(values) / count
    variance = sum((value - mean_value) ** 2 for value in values) / count
    stddev = math.sqrt(variance)
    return {
        "mean": round(mean_value, 3),
        "stddev": round(stddev, 3),
        "count": float(count),
        "recent_bonus": round(recency_bonus_total / count, 3),
    }

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