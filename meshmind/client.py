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
from meshmind.core.types import Memory, Triplet, SearchConfig
from meshmind.db.base_driver import GraphDriver
from meshmind.db.factory import graph_driver_factory as make_graph_driver_factory
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
            self._graph_driver_factory = make_graph_driver_factory()

        self._memory_manager: Optional[MemoryManager] = (
            MemoryManager(self._graph_driver) if self._graph_driver else None
        )
        self.entity_registry = EntityRegistry
        self.predicate_registry = PredicateRegistry
        bootstrap_entities([Memory])
        bootstrap_encoders()

    @property
    def graph_driver(self) -> GraphDriver:
        """Expose the active graph driver, creating it on demand."""
        return self._ensure_driver()

    @property
    def driver(self) -> GraphDriver:
        """Backward compatible alias for :attr:`graph_driver`."""
        return self.graph_driver

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

    # ------------------------------------------------------------------
    # Retrieval helpers
    # ------------------------------------------------------------------
    def search(
        self,
        query: str,
        memories: Sequence[Memory] | None = None,
        namespace: str | None = None,
        entity_labels: Sequence[str] | None = None,
        config: SearchConfig | None = None,
        use_llm_rerank: bool = False,
        reranker: Callable[[str, Sequence[Memory], int], Sequence[Memory]] | None = None,
    ) -> List[Memory]:
        from meshmind.retrieval import llm_rerank, search as hybrid_search
        from meshmind.retrieval.graph import graph_hybrid_search

        cfg = config or SearchConfig(encoder=self.embedding_model)
        active_reranker = reranker
        if use_llm_rerank:
            active_reranker = lambda q, c, k: llm_rerank(
                q, c, self.llm_client, k, model=cfg.rerank_model
            )

        if memories is None:
            return graph_hybrid_search(
                query,
                self._ensure_driver(),
                namespace=namespace,
                entity_labels=entity_labels,
                config=cfg,
                reranker=active_reranker,
            )

        return hybrid_search(
            query,
            list(memories),
            namespace=namespace,
            entity_labels=list(entity_labels) if entity_labels else None,
            config=cfg,
            reranker=active_reranker,
        )

    def search_vector(
        self,
        query: str,
        memories: Sequence[Memory] | None = None,
        namespace: str | None = None,
        entity_labels: Sequence[str] | None = None,
        config: SearchConfig | None = None,
    ) -> List[Memory]:
        from meshmind.retrieval import search_vector
        from meshmind.retrieval.graph import graph_vector_search

        cfg = config or SearchConfig(encoder=self.embedding_model)
        if memories is None:
            return graph_vector_search(
                query,
                self._ensure_driver(),
                namespace=namespace,
                entity_labels=entity_labels,
                config=cfg,
            )
        return search_vector(
            query,
            list(memories),
            namespace=namespace,
            entity_labels=list(entity_labels) if entity_labels else None,
            config=cfg,
        )

    def search_regex(
        self,
        pattern: str,
        memories: Sequence[Memory] | None = None,
        namespace: str | None = None,
        entity_labels: Sequence[str] | None = None,
        flags: int | None = None,
        top_k: int = 10,
    ) -> List[Memory]:
        from meshmind.retrieval import search_regex
        from meshmind.retrieval.graph import graph_regex_search

        if memories is None:
            return graph_regex_search(
                pattern,
                self._ensure_driver(),
                namespace=namespace,
                entity_labels=entity_labels,
                flags=flags,
                top_k=top_k,
            )
        return search_regex(
            pattern,
            list(memories),
            namespace=namespace,
            entity_labels=list(entity_labels) if entity_labels else None,
            flags=flags,
            top_k=top_k,
        )

    def search_exact(
        self,
        query: str,
        memories: Sequence[Memory] | None = None,
        namespace: str | None = None,
        entity_labels: Sequence[str] | None = None,
        fields: Sequence[str] | None = None,
        case_sensitive: bool = False,
        top_k: int = 10,
    ) -> List[Memory]:
        from meshmind.retrieval import search_exact
        from meshmind.retrieval.graph import graph_exact_search

        if memories is None:
            return graph_exact_search(
                query,
                self._ensure_driver(),
                namespace=namespace,
                entity_labels=entity_labels,
                fields=fields,
                case_sensitive=case_sensitive,
                top_k=top_k,
            )
        return search_exact(
            query,
            list(memories),
            namespace=namespace,
            entity_labels=list(entity_labels) if entity_labels else None,
            fields=list(fields) if fields else None,
            case_sensitive=case_sensitive,
            top_k=top_k,
        )

