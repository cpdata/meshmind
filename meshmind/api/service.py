"""Service layer abstractions for REST and gRPC adapters."""
from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

from pydantic import BaseModel, Field

from meshmind.api.memory_manager import MemoryManager
from meshmind.core.types import Memory, SearchConfig, Triplet
from meshmind.retrieval import llm_rerank, search as retrieval_search


class MemoryPayload(BaseModel):
    """Serializable payload for creating or updating a memory."""

    uuid: str | None = None
    namespace: str
    name: str
    entity_label: str = "Memory"
    embedding: List[float] | None = None
    metadata: dict[str, object] = Field(default_factory=dict)
    reference_time: str | None = None
    importance: float | None = None
    ttl_seconds: int | None = None

    def to_memory(self) -> Memory:
        payload = self.model_dump(exclude_none=True)
        if self.uuid:
            payload["uuid"] = self.uuid
        return Memory(**payload)


class TripletPayload(BaseModel):
    subject: str
    predicate: str
    object: str
    namespace: str
    entity_label: str = "Relation"
    metadata: dict[str, object] = Field(default_factory=dict)
    reference_time: str | None = None

    def to_triplet(self) -> Triplet:
        return Triplet(**self.model_dump(exclude_none=True))


class SearchPayload(BaseModel):
    query: str
    namespace: str | None = None
    top_k: int = 10
    encoder: str | None = None
    rerank_k: int | None = None
    entity_labels: Sequence[str] | None = None
    rerank_model: str | None = None
    use_llm_rerank: bool = False
    llm_models: Dict[str, str] | None = None
    llm_base_urls: Dict[str, Optional[str]] | None = None
    llm_api_key: str | None = None

    def to_config(self) -> SearchConfig:
        config = SearchConfig(top_k=self.top_k)
        if self.encoder:
            config.encoder = self.encoder
        if self.rerank_k is not None:
            config.rerank_k = self.rerank_k
        if self.rerank_model:
            config.rerank_model = self.rerank_model
        elif self.llm_models and self.llm_models.get("rerank"):
            config.rerank_model = self.llm_models["rerank"]
        return config

    def llm_override_kwargs(self) -> Dict[str, Any]:
        return {
            "models": self.llm_models,
            "base_urls": self.llm_base_urls,
            "api_key": self.llm_api_key,
        }


class MemoryService:
    """Business logic for ingestion, retrieval, and triplet persistence."""

    def __init__(
        self,
        manager: MemoryManager,
        *,
        llm_client: Any | None = None,
        llm_client_factory: Callable[[], Any] | None = None,
    ) -> None:
        self.manager = manager
        self._llm_client: Any | None = llm_client
        self._llm_client_factory = llm_client_factory

    @property
    def llm_client(self) -> Any | None:
        """Expose the cached LLM client (mainly for tests)."""

        return self._llm_client

    def _resolve_llm_client(self) -> Any | None:
        if self._llm_client is not None:
            return self._llm_client
        if self._llm_client_factory is None:
            return None
        try:
            self._llm_client = self._llm_client_factory()
        except Exception:
            return None
        return self._llm_client

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------
    def ingest_memories(self, payloads: Sequence[MemoryPayload]) -> List[str]:
        uuids: List[str] = []
        for payload in payloads:
            memory = payload.to_memory()
            self.manager.add_memory(memory)
            uuids.append(str(memory.uuid))
        return uuids

    def ingest_triplets(self, payloads: Iterable[TripletPayload]) -> int:
        count = 0
        for payload in payloads:
            self.manager.add_triplet(payload.to_triplet())
            count += 1
        return count

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------
    def search(self, request: SearchPayload) -> List[Memory]:
        config = request.to_config()
        candidate_limit = max(config.top_k * 5, (config.rerank_k or 0) * 2)
        limit = candidate_limit or None
        memories = self.manager.list_memories(
            namespace=request.namespace,
            entity_labels=request.entity_labels,
            limit=limit,
            query=request.query,
            use_search=True,
        )
        reranker = None
        if request.use_llm_rerank:
            llm_client = self._resolve_llm_client()
            if llm_client is not None:
                overrides = request.llm_override_kwargs()
                if any(overrides.values()):
                    with_overrides = getattr(llm_client, "with_overrides", None)
                    if callable(with_overrides):
                        llm_client = with_overrides(**overrides)
                endpoint_override = None
                if request.llm_base_urls:
                    endpoint_override = (
                        request.llm_base_urls.get("rerank")
                        or request.llm_base_urls.get("default")
                    )
                rerank_model = config.rerank_model

                def _reranker(
                    query: str,
                    candidates: Sequence[Memory],
                    top_k: int,
                    *,
                    client: Any = llm_client,
                    model: str | None = rerank_model,
                    endpoint: str | None = endpoint_override,
                ) -> Sequence[Memory]:
                    return llm_rerank(
                        query,
                        candidates,
                        client,
                        top_k,
                        model=model,
                        endpoint=endpoint,
                    )

                reranker = _reranker
        return retrieval_search(
            request.query,
            memories,
            config=config,
            reranker=reranker,
        )

    # ------------------------------------------------------------------
    # CRUD proxies
    # ------------------------------------------------------------------
    def list_memories(
        self,
        namespace: str | None = None,
        entity_labels: Sequence[str] | None = None,
        *,
        offset: int = 0,
        limit: int | None = None,
        query: str | None = None,
        use_search: bool | None = None,
    ) -> List[Memory]:
        return self.manager.list_memories(
            namespace,
            entity_labels,
            offset=offset,
            limit=limit,
            query=query,
            use_search=use_search,
        )

    def list_triplets(self, namespace: str | None = None) -> List[Triplet]:
        return self.manager.list_triplets(namespace)

    def memory_counts(self, namespace: str | None = None) -> Dict[str, Dict[str, int]]:
        return self.manager.count_memories(namespace)
