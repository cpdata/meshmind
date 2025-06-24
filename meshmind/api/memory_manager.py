from typing import Any, List, Optional
from uuid import UUID

class MemoryManager:
    """
    Mid-level CRUD interface for Memory objects, delegating to an underlying graph driver.
    """
    def __init__(self, graph_driver: Any):  # pragma: no cover
        self.driver = graph_driver

    def add_memory(self, memory: Any) -> UUID:
        """
        Add a new Memory object to the graph.

        :param memory: A Memory-like object to be stored.
        :return: The UUID of the newly added memory.
        """
        # Upsert the memory object into the graph
        try:
            props = memory.dict(exclude_none=True)
        except Exception:
            props = memory.__dict__
        self.driver.upsert_entity(memory.entity_label, memory.name, props)
        return memory.uuid

    def update_memory(self, memory: Any) -> None:
        """
        Update an existing Memory object in the graph.

        :param memory: A Memory-like object with updated fields.
        """
        # Update an existing memory via upsert
        try:
            props = memory.dict(exclude_none=True)
        except Exception:
            props = memory.__dict__
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
        # Retrieve a memory by UUID
        from meshmind.core.types import Memory

        cypher = "MATCH (m) WHERE m.uuid = $uuid RETURN m"
        params = {"uuid": str(memory_id)}
        records = self.driver.find(cypher, params)
        if not records:
            return None
        # Extract node properties
        record = records[0]
        data = record.get('m', record)
        try:
            return Memory(**data)
        except Exception:
            return None

    def list_memories(self, namespace: Optional[str] = None) -> List[Any]:
        """
        List Memory objects, optionally filtered by namespace.

        :param namespace: If provided, only return memories in this namespace.
        :return: List of Memory-like objects.
        """
        # List memories, optionally filtered by namespace
        from meshmind.core.types import Memory

        if namespace:
            cypher = "MATCH (m) WHERE m.namespace = $namespace RETURN m"
            params = {"namespace": namespace}
        else:
            cypher = "MATCH (m) RETURN m"
            params = {}
        records = self.driver.find(cypher, params)
        result: List[Any] = []
        for record in records:
            data = record.get('m', record)
            try:
                result.append(Memory(**data))
            except Exception:
                continue
        return result