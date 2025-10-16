import pytest

from meshmind.core.types import Memory
from meshmind.tasks import scheduled


class StubManager:
    def __init__(self, memories):
        self._memories = memories
        self.updated = []
        self.deleted = []

    def list_memories(self):
        return list(self._memories)

    def update_memory(self, memory):
        self.updated.append(memory)

    def delete_memory(self, memory_id):
        self.deleted.append(str(memory_id))


@pytest.fixture(autouse=True)
def reset_manager():
    scheduled._reset_manager()
    yield
    scheduled._reset_manager()


def test_consolidate_task_persists_updates(monkeypatch):
    mem_a = Memory(namespace="ns", name="Alice", entity_label="Person", metadata={"content": "Alice likes tea"})
    mem_b = Memory(namespace="ns", name="Alice", entity_label="Person", metadata={"content": "Alice likes coffee"})
    mem_b.importance = 0.9

    manager = StubManager([mem_a, mem_b])
    monkeypatch.setattr(scheduled, "_MANAGER", manager, raising=False)

    stats = scheduled.consolidate_task()

    assert stats["merged"] == 1
    assert stats["removed"] >= 1
    assert stats["failures"] == 0
    assert manager.updated
    assert manager.deleted


def test_consolidate_task_retries_conflicts(monkeypatch):
    mem_a = Memory(namespace="ns", name="Alice", entity_label="Person", metadata={"content": "tea"})
    mem_b = Memory(namespace="ns", name="Alice", entity_label="Person", metadata={"content": "coffee"})
    mem_b.importance = 0.9

    manager = StubManager([mem_a, mem_b])
    attempts = {"count": 0}

    def flaky_update(memory):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise RuntimeError("conflict")
        manager.updated.append(memory)

    monkeypatch.setattr(manager, "update_memory", flaky_update, raising=False)
    monkeypatch.setattr(scheduled, "_MANAGER", manager, raising=False)
    monkeypatch.setattr(scheduled.settings, "MAINTENANCE_MAX_ATTEMPTS", 3, raising=False)
    monkeypatch.setattr(scheduled.settings, "MAINTENANCE_BASE_DELAY_SECONDS", 0.0, raising=False)
    monkeypatch.setattr(scheduled, "_sleep", lambda *_: None, raising=False)

    stats = scheduled.consolidate_task()

    assert attempts["count"] == 3
    assert stats["failures"] == 0
    assert manager.deleted


def test_consolidate_task_reports_failures(monkeypatch):
    mem_a = Memory(namespace="ns", name="Alice", entity_label="Person", metadata={"content": "tea"})
    mem_b = Memory(namespace="ns", name="Alice", entity_label="Person", metadata={"content": "coffee"})
    mem_b.importance = 0.9

    manager = StubManager([mem_a, mem_b])

    def failing_update(memory):
        raise RuntimeError("conflict")

    monkeypatch.setattr(manager, "update_memory", failing_update, raising=False)
    monkeypatch.setattr(scheduled, "_MANAGER", manager, raising=False)
    monkeypatch.setattr(scheduled.settings, "MAINTENANCE_MAX_ATTEMPTS", 2, raising=False)
    monkeypatch.setattr(scheduled.settings, "MAINTENANCE_BASE_DELAY_SECONDS", 0.0, raising=False)
    monkeypatch.setattr(scheduled, "_sleep", lambda *_: None, raising=False)

    stats = scheduled.consolidate_task()

    assert stats["failures"] == 1
    assert manager.deleted == []
