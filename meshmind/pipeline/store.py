"""Persistence helpers for storing memories and triplets."""
from __future__ import annotations

from typing import Any, Iterable

from pydantic import BaseModel

from meshmind.core.observability import log_event, telemetry
from meshmind.core.types import Triplet
from meshmind.db.base_driver import GraphDriver
from meshmind.models.registry import EntityRegistry, PredicateRegistry


def _props(obj: Any) -> dict[str, Any]:
    if isinstance(obj, BaseModel):
        return obj.model_dump(exclude_none=True)
    if hasattr(obj, "dict") or hasattr(obj, "model_dump"):
        try:
            return obj.model_dump(exclude_none=True)  # type: ignore[attr-defined]
        except (TypeError, AttributeError):
            pass
    if isinstance(obj, dict):
        return {k: v for k, v in obj.items() if v is not None}
    return {k: v for k, v in obj.__dict__.items() if v is not None}


def store_memories(
    memories: Iterable[Any],
    graph_driver: GraphDriver,
    *,
    entity_registry: type[EntityRegistry] | None = None,
) -> None:
    """Persist a sequence of Memory objects into the graph database."""

    registry = entity_registry or EntityRegistry
    stored = 0
    with telemetry.track_duration("pipeline.store.memories.duration"):
        for mem in memories:
            props = _props(mem)
            label = getattr(mem, "entity_label", None)
            if label and registry.model_for_label(label) is None and isinstance(mem, BaseModel):
                registry.register(type(mem))
            graph_driver.upsert_entity(label or "Memory", getattr(mem, "name", ""), props)
            stored += 1
    telemetry.increment("pipeline.store.memories.stored", stored)
    log_event("pipeline.store.memories", count=stored)


def store_triplets(
    triplets: Iterable[Triplet],
    graph_driver: GraphDriver,
    *,
    predicate_registry: type[PredicateRegistry] | None = None,
) -> None:
    """Persist a collection of ``Triplet`` relationships."""

    registry = predicate_registry or PredicateRegistry
    stored = 0
    with telemetry.track_duration("pipeline.store.triplets.duration"):
        for triplet in triplets:
            registry.add(triplet.predicate)
            props = _props(triplet)
            graph_driver.upsert_edge(
                triplet.subject,
                triplet.predicate,
                triplet.object,
                props,
            )
            stored += 1
    telemetry.increment("pipeline.store.triplets.stored", stored)
    log_event("pipeline.store.triplets", count=stored)
