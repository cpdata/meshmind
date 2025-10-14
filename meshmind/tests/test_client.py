from meshmind.api.memory_manager import MemoryManager
from meshmind.client import MeshMind
from meshmind.db.in_memory_driver import InMemoryGraphDriver


def test_meshmind_list_memories_forwards_entity_labels(monkeypatch):
    driver = InMemoryGraphDriver()
    client = MeshMind(llm_client=object(), graph_driver=driver)

    captured: dict[str, object] = {}

    def fake_list_memories(self, namespace=None, entity_labels=None):  # noqa: ANN001
        captured["namespace"] = namespace
        captured["entity_labels"] = entity_labels
        return []

    monkeypatch.setattr(MemoryManager, "list_memories", fake_list_memories)

    client.list_memories(namespace="demo", entity_labels=["Note"])

    assert captured["namespace"] == "demo"
    assert captured["entity_labels"] == ["Note"]
