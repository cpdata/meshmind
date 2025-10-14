from uuid import uuid4

from meshmind.core.types import Triplet
from meshmind.db.in_memory_driver import InMemoryGraphDriver
from meshmind.db.sqlite_driver import SQLiteGraphDriver
from meshmind.testing import FakeEmbeddingEncoder, FakeMemgraphDriver, FakeRedisBroker


def _memory_payload(name: str) -> dict:
    return {
        "uuid": str(uuid4()),
        "namespace": "test",
        "name": name,
        "entity_label": "Note",
        "metadata": {"content": name},
    }


def test_in_memory_driver_roundtrip():
    driver = InMemoryGraphDriver()
    payload = _memory_payload("alpha")
    driver.upsert_entity("Note", payload["name"], payload)

    entity = driver.get_entity(payload["uuid"])
    assert entity and entity["name"] == "alpha"

    triplet = Triplet(
        subject=payload["uuid"],
        predicate="related_to",
        object=str(uuid4()),
        namespace="test",
        entity_label="Relation",
    )
    driver.upsert_edge(triplet.subject, triplet.predicate, triplet.object, triplet.dict())
    records = driver.list_triplets("test")
    assert records and records[0]["predicate"] == "related_to"

    driver.delete(uuid4())  # deleting unknown should not error
    driver.delete_triplet(triplet.subject, triplet.predicate, triplet.object)
    assert not driver.list_triplets("test")

    driver.delete(payload["uuid"])
    assert driver.get_entity(payload["uuid"]) is None


def test_sqlite_driver_roundtrip():
    driver = SQLiteGraphDriver(":memory:")
    payload = _memory_payload("beta")
    driver.upsert_entity("Note", payload["name"], payload)

    entity = driver.get_entity(payload["uuid"])
    assert entity and entity["name"] == "beta"

    triplet = Triplet(
        subject=payload["uuid"],
        predicate="mentions",
        object=str(uuid4()),
        namespace="test",
        entity_label="Relation",
    )
    driver.upsert_edge(triplet.subject, triplet.predicate, triplet.object, triplet.dict())
    records = driver.list_triplets("test")
    assert records and records[0]["predicate"] == "mentions"

    driver.delete(payload["uuid"])
    assert driver.get_entity(payload["uuid"]) is None
    assert not driver.list_triplets("test")


def test_sqlite_list_entities_filters_namespace_and_label():
    driver = SQLiteGraphDriver(":memory:")
    note = _memory_payload("note")
    task = _memory_payload("task")
    task["entity_label"] = "Task"
    driver.upsert_entity("Note", note["name"], note)
    driver.upsert_entity("Task", task["name"], task)

    filtered = driver.list_entities(namespace="test", entity_labels=["Note"])
    assert len(filtered) == 1
    assert filtered[0]["entity_label"] == "Note"

    everything = driver.list_entities(namespace="test")
    assert len(everything) == 2


def test_fake_memgraph_driver_behaviour():
    driver = FakeMemgraphDriver()
    payload = _memory_payload("gamma")
    driver.upsert_entity("Note", payload["name"], payload)
    records = driver.find("MATCH (m) RETURN m", {})
    assert records
    assert driver.cypher_calls


def test_fake_memgraph_entity_label_filtering():
    driver = FakeMemgraphDriver()
    note = _memory_payload("alpha")
    other = _memory_payload("beta")
    other["entity_label"] = "Task"
    driver.upsert_entity("Note", note["name"], note)
    driver.upsert_entity("Task", other["name"], other)

    filtered = driver.list_entities(namespace="test", entity_labels=["Note"])
    assert len(filtered) == 1
    assert filtered[0]["entity_label"] == "Note"


def test_fake_redis_broker_roundtrip():
    broker = FakeRedisBroker()
    broker.set("key", "value")
    assert broker.get("key") == "value"
    broker.lpush("queue", "a", "b")
    assert broker.lrange("queue", 0, -1) == ["b", "a"]
    broker.publish("events", {"message": "hello"})
    assert broker.delete("key") == 1


def test_fake_embedding_encoder_hashing():
    encoder = FakeEmbeddingEncoder(scale=2.0)
    vec = encoder.encode(["alpha"])
    assert isinstance(vec, list) and isinstance(vec[0][0], float)
