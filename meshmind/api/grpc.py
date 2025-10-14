"""gRPC-style adapters for MeshMind."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

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


@dataclass
class SearchResponse:
    results: List[dict] = field(default_factory=list)


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
        )
        results = self.service.search(payload)
        return SearchResponse(results=[mem.dict() for mem in results])


__all__ = [
    "GrpcServiceStub",
    "IngestMemoriesRequest",
    "IngestMemoriesResponse",
    "IngestTripletsRequest",
    "IngestTripletsResponse",
    "SearchRequest",
    "SearchResponse",
]
