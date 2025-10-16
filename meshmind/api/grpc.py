"""gRPC adapters and helpers for MeshMind."""
from __future__ import annotations

from typing import Iterable, Sequence

from google.protobuf import json_format, struct_pb2, wrappers_pb2

from meshmind.api.service import MemoryPayload, MemoryService, SearchPayload, TripletPayload
from meshmind.core.types import Memory, Triplet
from meshmind.protos import memory_service_pb2 as pb2
from meshmind.protos import memory_service_pb2_grpc as pb2_grpc

__all__ = [
    "GrpcServiceStub",
    "memory_to_proto",
    "memory_proto_to_memory",
    "triplet_to_proto",
    "memory_from_proto",
    "triplet_from_proto",
]


def _dict_to_struct(data: dict[str, object] | None) -> struct_pb2.Struct:
    struct = struct_pb2.Struct()
    if data:
        struct.update(data)
    return struct


def _struct_to_dict(struct: struct_pb2.Struct | None) -> dict[str, object]:
    if not struct:
        return {}
    return json_format.MessageToDict(struct, preserving_proto_field_name=True)


def _maybe_wrapper(value: object | None, wrapper_cls):
    if value is None:
        return None
    return wrapper_cls(value=value)


def memory_to_proto(memory: Memory) -> pb2.MemoryPayload:
    return pb2.MemoryPayload(
        uuid=str(memory.uuid),
        namespace=memory.namespace,
        name=memory.name,
        entity_label=memory.entity_label,
        embedding=list(memory.embedding or []),
        metadata=_dict_to_struct(memory.metadata),
        reference_time=memory.reference_time.isoformat() if memory.reference_time else "",
        importance=_maybe_wrapper(memory.importance, wrappers_pb2.DoubleValue),
        ttl_seconds=_maybe_wrapper(memory.ttl_seconds, wrappers_pb2.Int64Value),
        created_at=memory.created_at.isoformat() if memory.created_at else "",
        updated_at=memory.updated_at.isoformat() if memory.updated_at else "",
    )


def memory_from_proto(message: pb2.MemoryPayload) -> MemoryPayload:
    data: dict[str, object] = {
        "uuid": message.uuid or None,
        "namespace": message.namespace,
        "name": message.name,
        "entity_label": message.entity_label or "Memory",
        "embedding": list(message.embedding),
        "metadata": _struct_to_dict(message.metadata),
        "reference_time": message.reference_time or None,
    }
    if message.HasField("importance"):
        data["importance"] = message.importance.value
    if message.HasField("ttl_seconds"):
        data["ttl_seconds"] = int(message.ttl_seconds.value)
    payload = MemoryPayload(**{k: v for k, v in data.items() if v is not None})
    return payload


def memory_proto_to_memory(message: pb2.MemoryPayload) -> Memory:
    payload = memory_from_proto(message)
    data = payload.model_dump(exclude_none=True)
    if message.created_at:
        data["created_at"] = message.created_at
    if message.updated_at:
        data["updated_at"] = message.updated_at
    return Memory(**data)


def triplet_to_proto(triplet: Triplet) -> pb2.TripletPayload:
    return pb2.TripletPayload(
        subject=triplet.subject,
        predicate=triplet.predicate,
        object=triplet.object,
        namespace=triplet.namespace,
        entity_label=triplet.entity_label,
        metadata=_dict_to_struct(triplet.metadata),
        reference_time=triplet.reference_time.isoformat() if triplet.reference_time else "",
    )


def triplet_from_proto(message: pb2.TripletPayload) -> TripletPayload:
    data: dict[str, object] = {
        "subject": message.subject,
        "predicate": message.predicate,
        "object": message.object,
        "namespace": message.namespace,
        "entity_label": message.entity_label or "Relation",
        "metadata": _struct_to_dict(message.metadata),
        "reference_time": message.reference_time or None,
    }
    return TripletPayload(**data)


def _search_payload_from_proto(message: pb2.SearchPayload) -> SearchPayload:
    data: dict[str, object] = {
        "query": message.query,
        "namespace": message.namespace or None,
        "top_k": message.top_k or 0,
        "encoder": message.encoder or None,
        "entity_labels": list(message.entity_labels) or None,
        "rerank_model": message.rerank_model or None,
        "use_llm_rerank": message.use_llm_rerank,
        "llm_models": dict(message.llm_models),
        "llm_base_urls": dict(message.llm_base_urls),
        "llm_api_key": message.llm_api_key or None,
    }
    if message.HasField("rerank_k"):
        data["rerank_k"] = message.rerank_k.value
    payload = SearchPayload(**{k: v for k, v in data.items() if v not in ({}, None)})
    if payload.top_k <= 0:
        payload.top_k = SearchPayload.model_fields["top_k"].default  # type: ignore[index]
    return payload


class GrpcServiceStub(pb2_grpc.MeshMindServiceServicer):
    """In-process service implementation mirroring the real gRPC server."""

    def __init__(self, service: MemoryService) -> None:
        self.service = service

    # The context parameter is optional to keep the signature compatible with grpc.Servicer methods.
    def IngestMemories(self, request: pb2.IngestMemoriesRequest, context=None) -> pb2.IngestMemoriesResponse:  # noqa: N802
        payloads = [memory_from_proto(memory) for memory in request.memories]
        uuids = self.service.ingest_memories(payloads)
        return pb2.IngestMemoriesResponse(uuids=uuids)

    def IngestTriplets(self, request: pb2.IngestTripletsRequest, context=None) -> pb2.IngestTripletsResponse:  # noqa: N802
        payloads = [triplet_from_proto(triplet) for triplet in request.triplets]
        stored = self.service.ingest_triplets(payloads)
        return pb2.IngestTripletsResponse(stored=stored)

    def Search(self, request: pb2.SearchPayload, context=None) -> pb2.SearchResponse:  # noqa: N802
        payload = _search_payload_from_proto(request)
        results = self.service.search(payload)
        return pb2.SearchResponse(results=[memory_to_proto(mem) for mem in results])

    def MemoryCounts(self, request: pb2.MemoryCountsRequest, context=None) -> pb2.MemoryCountsResponse:  # noqa: N802
        namespace = request.namespace or None
        counts = self.service.memory_counts(namespace)
        response = pb2.MemoryCountsResponse()
        for ns, labels in counts.items():
            entry = response.counts[ns]
            for label, value in labels.items():
                entry.entity_counts[label] = int(value)
        return response

    # Convenience helpers -------------------------------------------------
    def ingest_memories(self, payloads: Iterable[MemoryPayload]) -> Sequence[str]:
        request = pb2.IngestMemoriesRequest(memories=[memory_to_proto(p.to_memory()) for p in payloads])
        response = self.IngestMemories(request)
        return list(response.uuids)

    def ingest_triplets(self, payloads: Iterable[TripletPayload]) -> int:
        request = pb2.IngestTripletsRequest(triplets=[triplet_to_proto(p.to_triplet()) for p in payloads])
        response = self.IngestTriplets(request)
        return response.stored

    def search(self, payload: SearchPayload) -> Sequence[Memory]:
        proto = pb2.SearchPayload(
            query=payload.query,
            namespace=payload.namespace or "",
            top_k=payload.top_k,
            encoder=payload.encoder or "",
            entity_labels=list(payload.entity_labels or []),
            rerank_model=payload.rerank_model or "",
            use_llm_rerank=payload.use_llm_rerank,
            llm_models=dict(payload.llm_models or {}),
            llm_base_urls=dict(payload.llm_base_urls or {}),
            llm_api_key=payload.llm_api_key or "",
        )
        if payload.rerank_k is not None:
            proto.rerank_k.CopyFrom(wrappers_pb2.Int32Value(value=payload.rerank_k))
        response = self.Search(proto)
        memories = [memory_proto_to_memory(memory) for memory in response.results]
        return memories
