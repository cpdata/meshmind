from datetime import datetime, timedelta, timezone

import pytest

from meshmind.core.types import Memory
from meshmind.pipeline.consolidate import consolidate_memories
from meshmind.pipeline.expire import expire_memories


class DummyManager:
    def __init__(self, memories):
        self._memories = memories
        self.deleted: list[str] = []

    def list_memories(self):
        return list(self._memories)

    def delete_memory(self, memory_id):
        self.deleted.append(str(memory_id))

    def update_memory(self, memory):  # pragma: no cover - interface placeholder
        pass


def make_memory(name: str, created_at: datetime, ttl: int | None = None) -> Memory:
    mem = Memory(namespace="ns", name=name, entity_label="Test")
    mem.created_at = created_at
    mem.ttl_seconds = ttl
    return mem


def test_expire_memories(monkeypatch):
    now = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    expired = make_memory("old", now - timedelta(hours=2), ttl=1800)
    active = make_memory("fresh", now - timedelta(minutes=5), ttl=1800)
    manager = DummyManager([expired, active])

    class DummyDateTime:
        @classmethod
        def utcnow(cls):
            return now

        @classmethod
        def now(cls, tz=None):
            if tz is None:
                return now.replace(tzinfo=None)
            return now.astimezone(tz)

    monkeypatch.setattr("meshmind.pipeline.expire.datetime", DummyDateTime)

    removed = expire_memories(manager)

    assert str(expired.uuid) in removed
    assert str(active.uuid) not in removed
    assert str(expired.uuid) in manager.deleted


def test_consolidate_memories_returns_outcomes():
    primary = Memory(namespace="ns", name="Alice", entity_label="Test", metadata={"content": "likes tea"})
    duplicate = Memory(namespace="ns", name="Alice", entity_label="Test", metadata={"content": "likes coffee"})
    primary.importance = 0.8
    duplicate.importance = 0.2

    plan = consolidate_memories([primary, duplicate])
    assert len(plan.outcomes) == 1
    outcome = plan.outcomes[0]
    assert outcome.updated.metadata["consolidated_summary"]
    assert outcome.removed_ids
