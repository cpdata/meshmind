from meshmind.api.memory_manager import MemoryManager
from meshmind.client import MeshMind
from meshmind.db.in_memory_driver import InMemoryGraphDriver


def test_meshmind_list_memories_forwards_filters(monkeypatch):
    driver = InMemoryGraphDriver()
    client = MeshMind(llm_client=object(), graph_driver=driver)

    captured: dict[str, object] = {}

    def fake_list_memories(self, namespace=None, entity_labels=None, **kwargs):  # noqa: ANN001
        captured["namespace"] = namespace
        captured["entity_labels"] = entity_labels
        captured["kwargs"] = kwargs
        return []

    monkeypatch.setattr(MemoryManager, "list_memories", fake_list_memories)

    client.list_memories(
        namespace="demo",
        entity_labels=["Note"],
        offset=5,
        limit=10,
        query="alpha",
        use_search=True,
    )

    assert captured["namespace"] == "demo"
    assert captured["entity_labels"] == ["Note"]
    assert captured["kwargs"] == {"offset": 5, "limit": 10, "query": "alpha", "use_search": True}


def test_meshmind_memory_counts_delegates(monkeypatch):
    driver = InMemoryGraphDriver()
    client = MeshMind(llm_client=object(), graph_driver=driver)

    monkeypatch.setattr(MemoryManager, "count_memories", lambda self, namespace=None: {"ns": {"Note": 1}})

    counts = client.memory_counts(namespace="ns")
    assert counts["ns"]["Note"] == 1
