import pytest

from datetime import datetime, timezone
from random import Random

from meshmind.pipeline.consolidate import ConsolidationSettings, consolidate_memories
from meshmind.pipeline.preprocess import (
    compress,
    deduplicate,
    score_importance,
)
from meshmind.pipeline.store import store_memories, store_triplets
from meshmind.api.memory_manager import MemoryManager
from meshmind.core.types import Memory, Triplet
from meshmind.models.registry import PredicateRegistry
from meshmind.core.observability import telemetry


class DummyDriver:
    def __init__(self):
        self.entities = []
        self.deleted = []
        self.edges = []
        self.deleted_edges = []

    def upsert_entity(self, label, name, props):
        self.entities.append((label, name, dict(props)))

    def upsert_edge(self, subj, pred, obj, props):
        self.edges.append((subj, pred, obj, props))

    def delete(self, uuid):
        self.deleted.append(uuid)
        self.entities = [entry for entry in self.entities if str(entry[2].get("uuid")) != str(uuid)]

    def delete_triplet(self, subj, pred, obj):
        self.deleted_edges.append((subj, pred, obj))

    def find(self, cypher, params):
        # Return empty for simplicity
        return []

    def list_triplets(self, namespace=None):
        return []

    def get_entity(self, uuid):
        for _, _, props in self.entities:
            if str(props.get("uuid")) == str(uuid):
                return dict(props)
        return None

    def list_entities(self, namespace=None, entity_labels=None, *, offset=0, limit=None):
        results = []
        for _, _, props in self.entities:
            if namespace is None or props.get("namespace") == namespace:
                if entity_labels and props.get("entity_label") not in set(entity_labels):
                    continue
                results.append(dict(props))
        if limit is None:
            return results[offset:]
        if limit <= 0:
            return []
        return results[offset : offset + limit]


def make_memory(name: str) -> Memory:
    return Memory(namespace="ns", name=name, entity_label="Test")


def test_deduplicate_removes_duplicates():
    m1 = make_memory("a")
    m2 = make_memory("b")
    m3 = make_memory("a")
    result = deduplicate([m1, m2, m3])
    assert len(result) == 2
    assert {m.name for m in result} == {"a", "b"}


def test_score_importance_heuristic_variation():
    recent = make_memory("Urgent server outage 500 error")
    recent.metadata = {"content": "Service unavailable 500"}
    recent.reference_time = datetime.now(timezone.utc)

    mundane = make_memory("Note")
    mundane.metadata = {"content": "write unit tests"}

    scored = score_importance([recent, mundane])
    values = [mem.importance for mem in scored]
    assert all(val is not None for val in values)
    assert scored[0].importance != scored[1].importance
    assert max(values) <= 5.0


def test_score_importance_records_metrics():
    telemetry.reset()
    m1 = make_memory("Outage 500")
    m1.metadata = {"content": "Service returned 500 error"}
    m1.reference_time = datetime.now(timezone.utc)
    score_importance([m1])
    snapshot = telemetry.snapshot()
    gauges = snapshot["gauges"]
    assert "importance.mean" in gauges
    assert gauges["importance.count"] >= 1.0


def test_compress_noop():
    m = make_memory("x")
    assert compress([m])[0] is m


def test_consolidate_memories_merges_duplicates():
    base = make_memory("Alice")
    duplicate = make_memory("Alice")
    duplicate.metadata = {"content": "Alice likes tea"}
    base.metadata = {"content": "Alice likes coffee"}
    duplicate.importance = 0.2
    base.importance = 0.9

    plan = consolidate_memories([base, duplicate])
    assert len(plan.outcomes) == 1
    outcome = plan.outcomes[0]
    assert "consolidated_summary" in outcome.updated.metadata
    assert outcome.removed_ids


def test_consolidate_memories_scales_with_large_dataset():
    rng = Random(42)
    memories: list[Memory] = []
    for namespace_idx in range(3):
        namespace = f"bulk-{namespace_idx}"
        for group_idx in range(10):
            base_name = f"Entity {namespace_idx}-{group_idx}"
            primary = make_memory(base_name)
            primary.namespace = namespace
            primary.metadata = {"content": f"{base_name} base description"}
            primary.importance = round(rng.random() + 0.5, 3)
            memories.append(primary)
            for dup_idx in range(7):
                duplicate = make_memory(base_name)
                duplicate.namespace = namespace
                duplicate.metadata = {
                    "content": f"{base_name} duplicate {dup_idx}",
                    "summary": f"{base_name} summary {dup_idx}",
                }
                duplicate.importance = max(primary.importance - 0.1, 0.1)
                memories.append(duplicate)

    settings = ConsolidationSettings(
        max_group_size=25,
        max_updates=400,
        max_updates_per_namespace=150,
    )
    plan = consolidate_memories(memories, settings=settings)

    assert len(plan.outcomes) == 30
    removed_total = sum(len(outcome.removed_ids) for outcome in plan)
    assert removed_total == len(memories) - len(plan.outcomes)
    for outcome in plan:
        assert outcome.updated.metadata.get("consolidated_summary")
        assert outcome.updated.importance is not None
        assert all(uid for uid in outcome.removed_ids)


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
    assert mgr.list_memories(entity_labels=["Other"]) == []


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
