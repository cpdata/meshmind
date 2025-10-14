from meshmind.api.grpc import (
    GrpcServiceStub,
    IngestMemoriesRequest,
    IngestTripletsRequest,
    SearchRequest,
)
from meshmind.api.rest import RestAPIStub
from meshmind.api.service import MemoryPayload, SearchPayload, TripletPayload
from meshmind.core.types import Memory


def _memory(name: str) -> MemoryPayload:
    return MemoryPayload(namespace="test", name=name, entity_label="Note")


def test_memory_service_ingest_and_search(memory_service, dummy_encoder):
    payloads = [_memory("apple"), _memory("banana")]
    uuids = memory_service.ingest_memories(payloads)
    assert len(uuids) == 2

    request = SearchPayload(query="apple", namespace="test", encoder=dummy_encoder, top_k=1)
    results = memory_service.search(request)
    assert results and isinstance(results[0], Memory)


def test_rest_stub_routes(memory_service, dummy_encoder):
    app = RestAPIStub(memory_service)
    response = app.dispatch(
        "POST",
        "/memories",
        {"memories": [_memory("alpha").model_dump()]},
    )
    assert "uuids" in response

    search_response = app.dispatch(
        "POST",
        "/search",
        {"query": "alpha", "namespace": "test", "encoder": dummy_encoder, "top_k": 1},
    )
    assert search_response["results"]


def test_grpc_stub(memory_service, dummy_encoder):
    grpc = GrpcServiceStub(memory_service)
    request = IngestMemoriesRequest(memories=[_memory("cherry").model_dump()])
    resp = grpc.IngestMemories(request)
    assert resp.uuids

    search_resp = grpc.Search(
        SearchRequest(query="cherry", namespace="test", encoder=dummy_encoder, top_k=1)
    )
    assert search_resp.results

    triplet_resp = grpc.IngestTriplets(
        IngestTripletsRequest(
            triplets=[
                TripletPayload(
                    subject=resp.uuids[0],
                    predicate="linked_to",
                    object=resp.uuids[0],
                    namespace="test",
                    entity_label="Relation",
                ).model_dump()
            ]
        )
    )
    assert triplet_resp.stored == 1
