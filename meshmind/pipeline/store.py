from typing import Any, Iterable
from meshmind.db.base_driver import GraphDriver

def store_memories(
    memories: Iterable[Any],
    graph_driver: GraphDriver,
) -> None:
    """
    Persist a sequence of Memory objects into the graph database.

    :param memories: An iterable of Memory-like objects with attributes for upsert.
    :param graph_driver: An instance of GraphDriver to perform database operations.
    """
    # Iterate over Memory-like objects and upsert into graph
    for mem in memories:
        # Use Pydantic-like dict to extract properties
        try:
            props = mem.dict(exclude_none=True)
        except Exception:
            # Fallback for non-Pydantic objects
            props = mem.__dict__
        # Upsert entity node with label and name
        graph_driver.upsert_entity(mem.entity_label, mem.name, props)