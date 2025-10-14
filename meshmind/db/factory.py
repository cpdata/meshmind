"""Factory helpers for constructing :class:`GraphDriver` instances."""
from __future__ import annotations

from typing import Callable, Dict, Type

from meshmind.core.config import settings
from meshmind.db.base_driver import GraphDriver
from meshmind.db.in_memory_driver import InMemoryGraphDriver
from meshmind.db.memgraph_driver import MemgraphDriver
from meshmind.db.neo4j_driver import Neo4jGraphDriver
from meshmind.db.sqlite_driver import SQLiteGraphDriver


def _normalize_backend(name: str) -> str:
    return name.replace("-", "_").lower()


def available_backends() -> Dict[str, Type[GraphDriver]]:
    """Return the mapping of backend names to driver classes."""

    return {
        "memory": InMemoryGraphDriver,
        "in_memory": InMemoryGraphDriver,
        "inmemory": InMemoryGraphDriver,
        "sqlite": SQLiteGraphDriver,
        "memgraph": MemgraphDriver,
        "neo4j": Neo4jGraphDriver,
    }


def create_graph_driver(backend: str | None = None, **kwargs) -> GraphDriver:
    """Instantiate a :class:`GraphDriver` for the requested backend."""

    backend_name = _normalize_backend(backend or settings.GRAPH_BACKEND)
    drivers = available_backends()
    if backend_name not in drivers:
        raise ValueError(f"Unsupported graph backend '{backend_name}'")

    driver_cls: Type[GraphDriver] = drivers[backend_name]
    if driver_cls is InMemoryGraphDriver:
        return driver_cls()
    if driver_cls is SQLiteGraphDriver:
        path = kwargs.get("path") or settings.SQLITE_PATH
        return driver_cls(path)
    if driver_cls is MemgraphDriver:
        return driver_cls(
            settings.MEMGRAPH_URI,
            settings.MEMGRAPH_USERNAME,
            settings.MEMGRAPH_PASSWORD,
        )
    if driver_cls is Neo4jGraphDriver:
        return driver_cls(
            settings.NEO4J_URI,
            settings.NEO4J_USERNAME,
            settings.NEO4J_PASSWORD,
        )
    return driver_cls(**kwargs)


def graph_driver_factory(backend: str | None = None, **kwargs) -> Callable[[], GraphDriver]:
    """Return a callable that lazily constructs the configured driver."""

    def _factory() -> GraphDriver:
        return create_graph_driver(backend=backend, **kwargs)

    return _factory
