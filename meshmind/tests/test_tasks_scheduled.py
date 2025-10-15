import pytest
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
    assert manager.updated
    assert manager.deleted
