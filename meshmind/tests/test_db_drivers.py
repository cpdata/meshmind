from uuid import uuid4

from meshmind.core.types import Memory, Triplet
from meshmind.db.in_memory_driver import InMemoryGraphDriver
from meshmind.db.sqlite_driver import SQLiteGraphDriver


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
