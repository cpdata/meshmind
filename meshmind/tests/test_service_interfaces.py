from uuid import UUID

from meshmind.api.grpc import (
    GrpcServiceStub,
    IngestMemoriesRequest,
    IngestTripletsRequest,
    MemoryCountsRequest,
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

    captured: dict[str, object] = {}

    sample = Memory(
        uuid=UUID(uuids[0]),
        namespace="test",
        name="apple",
        entity_label="Note",
        content="apple",
    )

    def fake_list(namespace=None, entity_labels=None, **kwargs):  # noqa: ANN001
        captured["namespace"] = namespace
        captured["entity_labels"] = entity_labels
        captured["kwargs"] = kwargs
        return [sample]

    original = memory_service.manager.list_memories
    memory_service.manager.list_memories = fake_list  # type: ignore[assignment]

    request = SearchPayload(query="apple", namespace="test", encoder=dummy_encoder, top_k=1)
    results = memory_service.search(request)
    memory_service.manager.list_memories = original  # restore

    assert results and isinstance(results[0], Memory)
    assert captured["namespace"] == "test"
    assert captured["entity_labels"] is None or captured["entity_labels"] == []
    assert captured["kwargs"]["query"] == "apple"
    assert captured["kwargs"]["use_search"] is True
    assert captured["kwargs"]["limit"] is not None


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

    memory_service.llm_client.calls.clear()
    override_response = app.dispatch(
        "POST",
        "/search",
        {
            "query": "alpha",
            "namespace": "test",
            "encoder": dummy_encoder,
            "top_k": 1,
            "use_llm_rerank": True,
            "llm_models": {"rerank": "rerank-dev"},
            "llm_base_urls": {"rerank": "https://llm.example/rerank"},
            "llm_api_key": "override-key",
        },
    )
    assert override_response["results"]
    assert memory_service.llm_client.calls
    last_call = memory_service.llm_client.calls[-1]
    assert last_call["model"] == "rerank-dev"
    assert last_call["base_url"] == "https://llm.example/rerank"
    assert memory_service.llm_client.last_override["models"]["rerank"] == "rerank-dev"

    filtered = app.dispatch(
        "GET",
        "/memories",
        {"namespace": "test", "entity_labels": ["Note"]},
    )
    assert filtered["memories"]

    filtered_none = app.dispatch(
        "GET",
        "/memories",
        {"namespace": "test", "entity_labels": ["Task"]},
    )
    assert filtered_none["memories"] == []

    counts = app.dispatch("GET", "/memories/counts", {"namespace": "test"})
    assert counts["counts"]["test"]["Note"] >= 1


def test_memory_service_list_memories_forwards_kwargs(memory_service):
    captured: dict[str, object] = {}

    def fake_list(namespace=None, entity_labels=None, **kwargs):  # noqa: ANN001
        captured["namespace"] = namespace
        captured["entity_labels"] = entity_labels
        captured["kwargs"] = kwargs
        return []

    original = memory_service.manager.list_memories
    memory_service.manager.list_memories = fake_list  # type: ignore[assignment]

    memory_service.list_memories(
        namespace="demo",
        entity_labels=["Note"],
        offset=5,
        limit=10,
        query="python",
        use_search=False,
    )

    memory_service.manager.list_memories = original  # restore

    assert captured["namespace"] == "demo"
    assert captured["entity_labels"] == ["Note"]
    assert captured["kwargs"] == {"offset": 5, "limit": 10, "query": "python", "use_search": False}


def test_memory_service_search_applies_llm_overrides(memory_service, dummy_encoder):
    sample = Memory(
        uuid=UUID(int=1),
        namespace="test",
        name="apple",
        entity_label="Note",
        content="apple",
    )

    def fake_list(namespace=None, entity_labels=None, **kwargs):  # noqa: ANN001
        return [sample]

    original = memory_service.manager.list_memories
    memory_service.manager.list_memories = fake_list  # type: ignore[assignment]

    payload = SearchPayload(
        query="apple",
        namespace="test",
        encoder=dummy_encoder,
        top_k=1,
        use_llm_rerank=True,
        llm_models={"rerank": "direct-rerank"},
        llm_base_urls={"default": "https://llm.example/default"},
        llm_api_key="override-key",
    )

    memory_service.llm_client.calls.clear()
    results = memory_service.search(payload)
    memory_service.manager.list_memories = original

    assert results
    assert memory_service.llm_client.calls
    direct_call = memory_service.llm_client.calls[-1]
    assert direct_call["model"] == "direct-rerank"
    assert direct_call["base_url"] == "https://llm.example/default"
    assert memory_service.llm_client.last_override["base_urls"]["default"] == "https://llm.example/default"


def test_grpc_stub(memory_service, dummy_encoder):
    grpc = GrpcServiceStub(memory_service)
    request = IngestMemoriesRequest(memories=[_memory("cherry").model_dump()])
    resp = grpc.IngestMemories(request)
    assert resp.uuids

    search_resp = grpc.Search(
        SearchRequest(
            query="cherry",
            namespace="test",
            encoder=dummy_encoder,
            top_k=1,
            entity_labels=["Note"],
        )
    )
    assert search_resp.results

    memory_service.llm_client.calls.clear()
    override_resp = grpc.Search(
        SearchRequest(
            query="cherry",
            namespace="test",
            encoder=dummy_encoder,
            top_k=1,
            entity_labels=["Note"],
            use_llm_rerank=True,
            llm_models={"rerank": "rerank-grpc"},
            llm_base_urls={"rerank": "https://llm.example/grpc"},
            llm_api_key="override-key",
        )
    )
    assert override_resp.results
    assert memory_service.llm_client.calls
    grpc_call = memory_service.llm_client.calls[-1]
    assert grpc_call["model"] == "rerank-grpc"
    assert grpc_call["base_url"] == "https://llm.example/grpc"

    counts_resp = grpc.MemoryCounts(MemoryCountsRequest(namespace="test"))
    assert counts_resp.counts["test"]["Note"] >= 1

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
