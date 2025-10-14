import pytest

from meshmind.pipeline.preprocess import deduplicate, score_importance, compress
from meshmind.pipeline.store import store_memories, store_triplets
from meshmind.api.memory_manager import MemoryManager
from meshmind.core.types import Memory, Triplet
from meshmind.models.registry import PredicateRegistry


class DummyDriver:
    def __init__(self):
        self.entities = []
        self.deleted = []
        self.edges = []
        self.deleted_edges = []

    def upsert_entity(self, label, name, props):
        self.entities.append((label, name, props))

    def upsert_edge(self, subj, pred, obj, props):
        self.edges.append((subj, pred, obj, props))

    def delete(self, uuid):
        self.deleted.append(uuid)

    def delete_triplet(self, subj, pred, obj):
        self.deleted_edges.append((subj, pred, obj))

    def find(self, cypher, params):
        # Return empty for simplicity
        return []

    def list_triplets(self, namespace=None):
        return []


def make_memory(name: str) -> Memory:
    return Memory(namespace="ns", name=name, entity_label="Test")


def test_deduplicate_removes_duplicates():
    m1 = make_memory("a")
    m2 = make_memory("b")
    m3 = make_memory("a")
    result = deduplicate([m1, m2, m3])
    assert len(result) == 2
    assert {m.name for m in result} == {"a", "b"}


def test_score_importance_sets_default():
    m = make_memory("x")
    m.importance = None
    scored = score_importance([m])
    assert scored[0].importance == pytest.approx(1.0)


def test_compress_noop():
    m = make_memory("x")
    assert compress([m])[0] is m


def test_store_memories_calls_driver():
    d = DummyDriver()
    m1 = make_memory("node1")
    m2 = make_memory("node2")
    store_memories([m1, m2], d)
    assert len(d.entities) == 2
    assert d.entities[0][0] == "Test"
    assert d.entities[0][1] == "node1"


def test_store_triplets_registers_predicate():
    PredicateRegistry.clear()
    d = DummyDriver()
    triplet = Triplet(
        subject="s",
        predicate="RELATES",
        object="o",
        namespace="ns",
        entity_label="Relation",
    )
    store_triplets([triplet], d)
    assert d.edges and d.edges[0][1] == "RELATES"
    assert "RELATES" in PredicateRegistry.all()


def test_memory_manager_add_update_delete():
    d = DummyDriver()
    mgr = MemoryManager(d)
    m = make_memory("item")
    # add
    uuid = mgr.add_memory(m)
    assert uuid == m.uuid
    assert d.entities
    # update
    mgr.update_memory(m)
    assert len(d.entities) >= 2
    # delete
    mgr.delete_memory(m.uuid)
    assert str(m.uuid) in d.deleted
    # get returns None (driver.find returns empty)
    assert mgr.get_memory(m.uuid) is None
    # list returns empty or list
    lst = mgr.list_memories()
    assert isinstance(lst, list)


def test_memory_manager_triplet_roundtrip():
    d = DummyDriver()
    mgr = MemoryManager(d)
    triplet = Triplet(
        subject="s",
        predicate="RELATES",
        object="o",
        namespace="ns",
        entity_label="Relation",
    )
    mgr.add_triplet(triplet)
    assert d.edges
    mgr.delete_triplet(triplet.subject, triplet.predicate, triplet.object)
    assert d.deleted_edges
    assert mgr.list_triplets() == []
    
def test_deduplicate_by_embedding_similarity():
    # Two memories with similar embeddings should be deduplicated
    m1 = make_memory("first")
    m1.embedding = [1.0, 0.0]
    m2 = make_memory("second")
    # Very similar vector to m1
    m2.embedding = [0.99, 0.01]
    # With high threshold, treat as duplicates
    result_high = deduplicate([m1, m2], threshold=0.9)
    assert len(result_high) == 1
    # With low threshold, keep both
    result_low = deduplicate([m1, m2], threshold=0.1)
    assert len(result_low) == 2
