try:
    import pytest
except ImportError:
    # Define fallback for pytest.approx
    class pytest:
        @staticmethod
        def approx(x):
            return x
from datetime import datetime, timedelta

from meshmind.pipeline.expire import expire_memories
from meshmind.pipeline.consolidate import consolidate_memories
from meshmind.pipeline.compress import compress_memories
from meshmind.core.types import Memory


class DummyManager:
    def __init__(self, memories):
        self._memories = memories
        self.deleted = []

    def list_memories(self):
        return self._memories

    def delete_memory(self, memory_id):
        self.deleted.append(str(memory_id))

    # Methods to satisfy manager interface
    def update_memory(self, memory):
        pass


def make_memory(name, created_at, ttl):
    mem = Memory(namespace="ns", name=name, entity_label="Test")
    mem.created_at = created_at
    mem.reference_time = None
    mem.ttl_seconds = ttl
    return mem


def test_expire_memories(monkeypatch):
    now = datetime(2025, 1, 1, 12, 0, 0)
    # Create memories: one expired, one not
    m1 = make_memory("a", now - timedelta(seconds=3600), ttl=1800)
    m2 = make_memory("b", now - timedelta(seconds=600), ttl=1800)
    manager = DummyManager([m1, m2])
    # Monkeypatch datetime.utcnow
    class DummyDateTime:
        @classmethod
        def utcnow(cls):
            return now
    monkeypatch.setattr('meshmind.pipeline.expire.datetime', DummyDateTime)
    expired = expire_memories(manager)
    assert str(m1.uuid) in expired
    assert str(m2.uuid) not in expired
    assert str(m1.uuid) in manager.deleted


def test_consolidate_memories():
    # Two memories with same name, different importance
    m1 = Memory(namespace="ns", name="x", entity_label="Test")
    m2 = Memory(namespace="ns", name="x", entity_label="Test")
    m1.importance = 0.5
    m2.importance = 1.0
    m3 = Memory(namespace="ns", name="y", entity_label="Test")
    result = consolidate_memories([m1, m2, m3])
    # Expect one for 'x' with higher importance and one for 'y'
    names = {m.name for m in result}
    assert names == {"x", "y"}
    selected_x = next(m for m in result if m.name == "x")
    assert selected_x.importance == pytest.approx(1.0)
