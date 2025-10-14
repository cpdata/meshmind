"""High-level MeshMind client orchestrating ingestion and storage flows."""
from __future__ import annotations

from typing import Any, Callable, Iterable, List, Optional, Sequence, Type
from uuid import UUID

try:  # pragma: no cover - optional dependency
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore

from meshmind.api.memory_manager import MemoryManager
from meshmind.core.bootstrap import bootstrap_entities, bootstrap_encoders
from meshmind.core.config import settings
from meshmind.core.types import Memory, Triplet
from meshmind.db.base_driver import GraphDriver
from meshmind.db.memgraph_driver import MemgraphDriver
from meshmind.models.registry import EntityRegistry, PredicateRegistry


class MeshMind:
    """High-level orchestration client for extraction, preprocessing, and persistence."""

    def __init__(
        self,
        llm_client: Any = None,
        embedding_model: str | None = None,
        graph_driver: Optional[GraphDriver] = None,
        graph_driver_factory: Callable[[], GraphDriver] | None = None,
    ):
        if llm_client is None:
            if OpenAI is None:
                raise ImportError(
                    "openai package is required to construct a default MeshMind LLM client."
                )
            client_kwargs: dict[str, Any] = {}
            if settings.OPENAI_API_KEY:
                client_kwargs["api_key"] = settings.OPENAI_API_KEY
            llm_client = OpenAI(**client_kwargs)

        self.llm_client = llm_client
        self.embedding_model = embedding_model or settings.EMBEDDING_MODEL

        self._graph_driver: Optional[GraphDriver] = graph_driver
        self._graph_driver_factory = graph_driver_factory
        if self._graph_driver is None and self._graph_driver_factory is None:
            self._graph_driver_factory = lambda: MemgraphDriver(  # type: ignore[assignment]
                settings.MEMGRAPH_URI,
                settings.MEMGRAPH_USERNAME,
                settings.MEMGRAPH_PASSWORD,
            )

        self._memory_manager: Optional[MemoryManager] = (
            MemoryManager(self._graph_driver) if self._graph_driver else None
        )
        self.entity_registry = EntityRegistry
        self.predicate_registry = PredicateRegistry
        bootstrap_entities([Memory])
        bootstrap_encoders()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_driver(self) -> GraphDriver:
        if self._graph_driver is None:
            if self._graph_driver_factory is None:
                raise RuntimeError("No graph driver factory available for MeshMind")
            self._graph_driver = self._graph_driver_factory()
        return self._graph_driver

    def _ensure_manager(self) -> MemoryManager:
        if self._memory_manager is None:
            self._memory_manager = MemoryManager(self._ensure_driver())
        return self._memory_manager

    # ------------------------------------------------------------------
    # Pipelines
    # ------------------------------------------------------------------
    def extract_memories(
        self,
        instructions: str,
        namespace: str,
        entity_types: Sequence[Type[Any]],
        content: Sequence[str],
    ) -> List[Any]:
        from meshmind.pipeline.extract import extract_memories

        return extract_memories(
            instructions=instructions,
            namespace=namespace,
            entity_types=list(entity_types),
            embedding_model=self.embedding_model,
            content=list(content),
            llm_client=self.llm_client,
        )

    def deduplicate(
        self,
        memories: Sequence[Any],
        threshold: float = 0.95,
    ) -> List[Any]:
        from meshmind.pipeline.preprocess import deduplicate

        return deduplicate(list(memories), threshold)

    def score_importance(
        self,
        memories: Sequence[Any],
    ) -> List[Any]:
        from meshmind.pipeline.preprocess import score_importance

        return score_importance(list(memories))

    def compress(
        self,
        memories: Sequence[Any],
    ) -> List[Any]:
        from meshmind.pipeline.preprocess import compress

        return compress(list(memories))

    def store_memories(
        self,
        memories: Iterable[Any],
    ) -> None:
        from meshmind.pipeline.store import store_memories

        store_memories(
            memories,
            self._ensure_driver(),
            entity_registry=self.entity_registry,
        )

    def store_triplets(
        self,
        triplets: Iterable[Triplet],
    ) -> None:
        from meshmind.pipeline.store import store_triplets

        store_triplets(
            triplets,
            self._ensure_driver(),
            predicate_registry=self.predicate_registry,
        )

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------
    def create_memory(self, memory: Memory) -> UUID:
        return self._ensure_manager().add_memory(memory)

    def update_memory(self, memory: Memory) -> None:
        self._ensure_manager().update_memory(memory)

    def delete_memory(self, memory_id: UUID) -> None:
        self._ensure_manager().delete_memory(memory_id)

    def get_memory(self, memory_id: UUID) -> Optional[Memory]:
        return self._ensure_manager().get_memory(memory_id)

    def list_memories(self, namespace: str | None = None) -> List[Memory]:
        return self._ensure_manager().list_memories(namespace)

    def create_triplet(self, triplet: Triplet) -> None:
        self.predicate_registry.add(triplet.predicate)
        self._ensure_manager().add_triplet(triplet)

    def delete_triplet(self, triplet: Triplet) -> None:
        self._ensure_manager().delete_triplet(
            triplet.subject, triplet.predicate, triplet.object
        )

    def list_triplets(self, namespace: str | None = None) -> List[Triplet]:
        return self._ensure_manager().list_triplets(namespace)

