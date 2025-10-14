"""Pipeline helpers for consolidating and summarising duplicate memories."""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from meshmind.core.types import Memory


@dataclass
class ConsolidationOutcome:
    """Result of merging a group of related memories."""

    updated: Memory
    removed_ids: List[str]
    skipped_ids: List[str] = field(default_factory=list)


@dataclass
class ConsolidationSettings:
    """Constraints used when planning consolidation batches."""

    max_group_size: int = 50
    max_updates: int = 200
    max_updates_per_namespace: int = 40


@dataclass
class ConsolidationPlan:
    """Container for consolidation outcomes and any skipped groups."""

    outcomes: List[ConsolidationOutcome] = field(default_factory=list)
    skipped_groups: Dict[str, int] = field(default_factory=dict)

    def add_skipped(self, namespace: str, count: int) -> None:
        self.skipped_groups[namespace] = self.skipped_groups.get(namespace, 0) + count

    def __iter__(self):
        return iter(self.outcomes)

    def __len__(self) -> int:
        return len(self.outcomes)


def _merge_metadata(group: Iterable[Memory]) -> Dict[str, object]:
    merged: Dict[str, object] = {}
    for mem in group:
        metadata = getattr(mem, "metadata", {}) or {}
        if not isinstance(metadata, dict):
            continue
        for key, value in metadata.items():
            if key not in merged:
                merged[key] = value
                continue
            existing = merged[key]
            if existing == value:
                continue
            if not isinstance(existing, list):
                existing = [existing]
            if isinstance(value, list):
                for item in value:
                    if item not in existing:
                        existing.append(item)
            else:
                if value not in existing:
                    existing.append(value)
            merged[key] = existing
    return merged


def _combine_embeddings(group: Iterable[Memory]) -> List[float] | None:
    embeddings: List[List[float]] = []
    for mem in group:
        emb = getattr(mem, "embedding", None)
        if isinstance(emb, list) and emb:
            embeddings.append([float(x) for x in emb])
    if not embeddings:
        return None
    length = len(embeddings[0])
    sums = [0.0] * length
    for vector in embeddings:
        if len(vector) != length:
            continue
        for idx, value in enumerate(vector):
            sums[idx] += value
    count = max(len(embeddings), 1)
    return [round(total / count, 6) for total in sums]


def _summary_from_group(group: Iterable[Memory]) -> str:
    seen: List[str] = []
    for mem in group:
        text = ""
        metadata = getattr(mem, "metadata", {}) or {}
        if isinstance(metadata, dict):
            text = str(metadata.get("content") or metadata.get("summary") or "")
        if not text:
            text = getattr(mem, "name", "")
        text = text.strip()
        if text and text not in seen:
            seen.append(text)
    return " \n".join(seen[:3])


def consolidate_memories(
    memories: List[Memory],
    settings: Optional[ConsolidationSettings] = None,
) -> ConsolidationPlan:
    """Consolidate duplicate memories and describe the merge plan."""

    grouped: Dict[tuple[str, str, str], List[Memory]] = {}
    for mem in memories:
        key = (getattr(mem, "namespace", ""), getattr(mem, "entity_label", ""), getattr(mem, "name", ""))
        grouped.setdefault(key, []).append(mem)

    cfg = settings or ConsolidationSettings()
    plan = ConsolidationPlan()
    namespace_counts: Dict[str, int] = {}

    for group in grouped.values():
        if len(group) == 1:
            continue
        namespace = getattr(group[0], "namespace", "") or "default"
        if len(group) > cfg.max_group_size:
            plan.add_skipped(namespace, len(group))
            continue
        if len(plan) >= cfg.max_updates:
            plan.add_skipped(namespace, len(group))
            continue
        if namespace_counts.get(namespace, 0) >= cfg.max_updates_per_namespace:
            plan.add_skipped(namespace, len(group))
            continue

        primary = max(
            group,
            key=lambda m: (
                getattr(m, "importance", 0.0) or 0.0,
                getattr(m, "updated_at", getattr(m, "created_at", None)),
            ),
        )
        metadata = _merge_metadata(group)
        summary = _summary_from_group(group)
        if summary:
            metadata.setdefault("consolidated_summary", summary)
        embedding = _combine_embeddings(group)
        update: Dict[str, object] = {"metadata": metadata}
        if embedding is not None:
            update["embedding"] = embedding
        if metadata and "importance" not in metadata:
            importance_values = [getattr(mem, "importance", 0.0) or 0.0 for mem in group]
            update["importance"] = round(max(importance_values), 3)
        updated = primary.model_copy(update=update)
        removed_ids = [str(getattr(mem, "uuid", "")) for mem in group if mem is not primary]
        namespace_counts[namespace] = namespace_counts.get(namespace, 0) + 1
        plan.outcomes.append(ConsolidationOutcome(updated=updated, removed_ids=removed_ids))
    return plan
