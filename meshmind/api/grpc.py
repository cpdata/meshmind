"""gRPC-style adapters for MeshMind."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional

from meshmind.api.service import MemoryPayload, MemoryService, SearchPayload, TripletPayload


@dataclass
class IngestMemoriesRequest:
    memories: List[dict] = field(default_factory=list)


@dataclass
class IngestMemoriesResponse:
    uuids: List[str] = field(default_factory=list)


@dataclass
class IngestTripletsRequest:
    triplets: List[dict] = field(default_factory=list)


@dataclass
class IngestTripletsResponse:
    stored: int = 0


@dataclass
class SearchRequest:
    query: str
    namespace: str | None = None
    top_k: int = 10
    encoder: str | None = None
    rerank_k: int | None = None
    entity_labels: List[str] | None = None
    rerank_model: str | None = None
    use_llm_rerank: bool = False
    llm_models: Dict[str, str] | None = None
    llm_base_urls: Dict[str, Optional[str]] | None = None
    llm_api_key: str | None = None


@dataclass
class SearchResponse:
    results: List[dict] = field(default_factory=list)


@dataclass
class MemoryCountsRequest:
    namespace: str | None = None


@dataclass
class MemoryCountsResponse:
    counts: Dict[str, Dict[str, int]] = field(default_factory=dict)


class GrpcServiceStub:
    """Simple callable object that mirrors gRPC service behaviour for tests."""

    def __init__(self, service: MemoryService) -> None:
        self.service = service

    def IngestMemories(self, request: IngestMemoriesRequest) -> IngestMemoriesResponse:  # noqa: N802
        payloads = [MemoryPayload(**item) for item in request.memories]
        uuids = self.service.ingest_memories(payloads)
        return IngestMemoriesResponse(uuids=uuids)

    def IngestTriplets(self, request: IngestTripletsRequest) -> IngestTripletsResponse:  # noqa: N802
        payloads = [TripletPayload(**item) for item in request.triplets]
        stored = self.service.ingest_triplets(payloads)
        return IngestTripletsResponse(stored=stored)

    def Search(self, request: SearchRequest) -> SearchResponse:  # noqa: N802
        payload = SearchPayload(
            query=request.query,
            namespace=request.namespace,
            top_k=request.top_k,
            encoder=request.encoder,
            rerank_k=request.rerank_k,
            entity_labels=request.entity_labels,
            rerank_model=request.rerank_model,
            use_llm_rerank=request.use_llm_rerank,
            llm_models=request.llm_models,
            llm_base_urls=request.llm_base_urls,
            llm_api_key=request.llm_api_key,
        )
        results = self.service.search(payload)
        return SearchResponse(results=[mem.dict() for mem in results])

    def MemoryCounts(self, request: MemoryCountsRequest) -> MemoryCountsResponse:  # noqa: N802
        counts = self.service.memory_counts(namespace=request.namespace)
        return MemoryCountsResponse(counts=counts)


__all__ = [
    "GrpcServiceStub",
    "IngestMemoriesRequest",
    "IngestMemoriesResponse",
    "IngestTripletsRequest",
    "IngestTripletsResponse",
    "SearchRequest",
    "SearchResponse",
    "MemoryCountsRequest",
    "MemoryCountsResponse",
]
