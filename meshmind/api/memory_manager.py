from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence
from uuid import UUID

from meshmind._compat.pydantic import BaseModel

from meshmind.core.types import Memory, Triplet


class MemoryManager:
    """Mid-level CRUD interface for ``Memory`` and ``Triplet`` objects."""

    def __init__(self, graph_driver: Any):  # pragma: no cover
        self.driver = graph_driver

    @staticmethod
    def _props(model: Any) -> Dict[str, Any]:
        if isinstance(model, BaseModel):
            return model.dict(exclude_none=True)
        if hasattr(model, "dict"):
            try:
                return model.dict(exclude_none=True)  # type: ignore[attr-defined]
            except TypeError:
                pass
        if isinstance(model, dict):
            return {k: v for k, v in model.items() if v is not None}
        return {k: v for k, v in model.__dict__.items() if v is not None}

    def add_memory(self, memory: Memory) -> UUID:
        """
        Add a new Memory object to the graph.

        :param memory: A Memory-like object to be stored.
        :return: The UUID of the newly added memory.
        """
        props = self._props(memory)
        self.driver.upsert_entity(memory.entity_label, memory.name, props)
        return memory.uuid

    def update_memory(self, memory: Memory) -> None:
        """
        Update an existing Memory object in the graph.

        :param memory: A Memory-like object with updated fields.
        """
        props = self._props(memory)
        self.driver.upsert_entity(memory.entity_label, memory.name, props)

    def delete_memory(self, memory_id: UUID) -> None:
        """
        Delete a Memory object by its UUID.

        :param memory_id: UUID of the memory to delete.
        """
        # Delete memory node or relationship by uuid
        self.driver.delete(str(memory_id))

    def get_memory(self, memory_id: UUID) -> Optional[Any]:
        """
        Retrieve a Memory object by its UUID.

        :param memory_id: UUID of the memory to retrieve.
        :return: Memory-like object or None if not found.
        """
        payload = self.driver.get_entity(str(memory_id))
        if not payload:
            return None
        try:
            return Memory(**payload)
        except Exception:
            return None

    def list_memories(
        self,
        namespace: Optional[str] = None,
        entity_labels: Optional[Sequence[str]] = None,
        *,
        offset: int = 0,
        limit: Optional[int] = None,
        query: Optional[str] = None,
        use_search: bool | None = None,
    ) -> List[Memory]:
        """
        List Memory objects, optionally filtered by namespace and entity label.

        :param namespace: If provided, only return memories in this namespace.
        :param entity_labels: Optional entity labels to restrict the results.
        :param offset: Offset into the result set for pagination.
        :param limit: Maximum number of memories to return.
        :param query: Optional search string to hint server-side filtering.
        :param use_search: Force enabling/disabling the driver's search routine.
        :return: List of Memory-like objects.
        """
        should_search = use_search if use_search is not None else bool(query)
        if should_search and hasattr(self.driver, "search_entities"):
            search_fn = getattr(self.driver, "search_entities")
            records = search_fn(  # type: ignore[operator]
                query=query,
                namespace=namespace,
                entity_labels=entity_labels,
                offset=offset,
                limit=limit,
            )
        else:
            records = self.driver.list_entities(
                namespace,
                entity_labels,
                offset=offset,
                limit=limit,
            )
        result: List[Memory] = []
        for data in records:
            try:
                result.append(Memory(**data))
            except Exception:
                continue
        return result

    def count_memories(self, namespace: Optional[str] = None) -> Dict[str, Dict[str, int]]:
        """Aggregate memory counts grouped by namespace and entity label."""

        if not hasattr(self.driver, "count_entities"):
            raise NotImplementedError("Graph driver does not implement count_entities")
        counter = getattr(self.driver, "count_entities")
        return counter(namespace)  # type: ignore[misc]

    def add_triplet(self, triplet: Triplet) -> None:
        """Persist or update a ``Triplet`` relationship."""

        props = self._props(triplet)
        namespace = props.pop("namespace", None)
        if namespace is not None:
            props["namespace"] = namespace
        self.driver.upsert_edge(
            triplet.subject,
            triplet.predicate,
            triplet.object,
            props,
        )

    def delete_triplet(self, subj: str, predicate: str, obj: str) -> None:
        """Remove a relationship identified by subject/predicate/object."""

        self.driver.delete_triplet(subj, predicate, obj)

    def list_triplets(self, namespace: Optional[str] = None) -> List[Triplet]:
        """Return stored ``Triplet`` objects, optionally filtered by namespace."""

        records = self.driver.list_triplets(namespace)
        result: List[Triplet] = []
        for record in records:
            data = {
                "subject": record.get("subject"),
                "predicate": record.get("predicate"),
                "object": record.get("object"),
                "namespace": record.get("namespace") or namespace,
                "entity_label": record.get("predicate", "Relation"),
                "metadata": record.get("metadata") or {},
                "reference_time": record.get("reference_time"),
            }
            try:
                result.append(Triplet(**data))
            except Exception:
                continue
        return result
