from uuid import uuid4

from meshmind.api.memory_manager import MemoryManager
from meshmind.core.types import Memory, Triplet
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


def test_in_memory_driver_pagination_and_search():
    driver = InMemoryGraphDriver()
    for idx in range(5):
        payload = _memory_payload(f"item-{idx}")
        payload["metadata"]["description"] = f"important note {idx}"
        driver.upsert_entity("Note", payload["name"], payload)

    limited = driver.list_entities(namespace="test", offset=1, limit=2)
    assert len(limited) == 2

    searched = driver.search_entities(query="important note 3", namespace="test")
    assert len(searched) == 1
    assert searched[0]["name"].endswith("3")


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


def test_sqlite_search_entities_and_pagination():
    driver = SQLiteGraphDriver(":memory:")
    for idx in range(6):
        payload = _memory_payload(f"row-{idx}")
        payload["metadata"]["summary"] = "lorem ipsum"
        driver.upsert_entity("Note", payload["name"], payload)

    chunk = driver.list_entities(namespace="test", limit=3)
    assert len(chunk) == 3

    second_page = driver.list_entities(namespace="test", offset=3, limit=3)
    assert len(second_page) == 3

    match = driver.search_entities(query="ipsum", namespace="test")
    assert len(match) == 6

    none = driver.search_entities(query="missing", namespace="test", limit=1)
    assert none == []


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


def test_fake_memgraph_counts():
    driver = FakeMemgraphDriver()
    alpha = _memory_payload("alpha")
    beta = _memory_payload("beta")
    beta["entity_label"] = "Task"
    driver.upsert_entity("Note", alpha["name"], alpha)
    driver.upsert_entity("Task", beta["name"], beta)

    counts = driver.count_entities()
    assert counts["test"]["Note"] == 1
    assert counts["test"]["Task"] == 1


def test_memory_manager_count_memories():
    driver = InMemoryGraphDriver()
    manager = MemoryManager(driver)
    first = _memory_payload("first")
    second = _memory_payload("second")
    second["entity_label"] = "Task"
    manager.add_memory(Memory(**first))
    manager.add_memory(Memory(**second))

    counts = manager.count_memories()
    assert counts["test"]["Note"] == 1
    assert counts["test"]["Task"] == 1


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
