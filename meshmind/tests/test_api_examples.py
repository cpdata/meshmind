from __future__ import annotations

from fastapi.testclient import TestClient

from meshmind.api.grpc import GrpcServiceStub
from meshmind.api.memory_manager import MemoryManager
from meshmind.api.rest import create_app
from meshmind.api.service import MemoryPayload, MemoryService
from meshmind.db.in_memory_driver import InMemoryGraphDriver
from meshmind.core.embeddings import EncoderRegistry
from meshmind.protos import memory_service_pb2 as pb2


def _service_with_sample_data() -> MemoryService:
    driver = InMemoryGraphDriver()
    manager = MemoryManager(driver)
    service = MemoryService(manager)
    if not EncoderRegistry.is_registered("text-embedding-3-small"):
        class _DummyEncoder:
            def encode(self, texts):
                return [[0.0, 0.0, 0.0] for _ in texts]

        EncoderRegistry.register("text-embedding-3-small", _DummyEncoder())
    payload = MemoryPayload(
        namespace="demo",
        name="MeshMind architecture overview",
        entity_label="Memory",
        metadata={
            "content": "MeshMind combines hybrid retrieval with graph persistence.",
            "summary": "Architecture overview",
        },
        importance=1.2,
    )
    service.ingest_memories([payload])
    return service


def test_rest_curl_example_matches_service() -> None:
    service = _service_with_sample_data()
    app = create_app(service)
    client = TestClient(app)

    search_payload = {
        "query": "architecture",
        "namespace": "demo",
        "top_k": 5,
        "entity_labels": ["Memory"],
    }
    response = client.post("/search", json=search_payload)
    data = response.json()
    assert response.status_code == 200
    assert data["results"]

    counts_response = client.get("/memories/counts", params={"namespace": "demo"})
    assert counts_response.status_code == 200
    counts = counts_response.json()["counts"]
    assert counts["demo"]["Memory"] >= 1


def test_grpcurl_example_matches_stub() -> None:
    service = _service_with_sample_data()
    stub = GrpcServiceStub(service)

    request = pb2.SearchPayload(query="architecture", namespace="demo", top_k=5)
    response = stub.Search(request)
    assert response.results

    counts_request = pb2.MemoryCountsRequest(namespace="demo")
    counts_response = stub.MemoryCounts(counts_request)
    assert counts_response.counts["demo"].entity_counts["Memory"] >= 1
