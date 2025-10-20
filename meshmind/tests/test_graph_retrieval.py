from meshmind.api.memory_manager import MemoryManager
from meshmind.core.types import Memory, SearchConfig
from meshmind.db.in_memory_driver import InMemoryGraphDriver
from meshmind.retrieval.graph import (
    graph_exact_search,
    graph_hybrid_search,
    graph_regex_search,
    graph_vector_search,
)


class TrackingDriver(InMemoryGraphDriver):
    def __init__(self) -> None:
        super().__init__()
        self.search_calls: list[dict[str, object]] = []
        self.list_calls = 0
        self.vector_calls: list[dict[str, object]] = []

    def search_entities(self, *args, **kwargs):  # noqa: ANN002 - passthrough to super
        self.search_calls.append(dict(kwargs))
        return super().search_entities(*args, **kwargs)

    def list_entities(self, *args, **kwargs):  # noqa: ANN002 - passthrough to super
        self.list_calls += 1
        return super().list_entities(*args, **kwargs)

    def vector_search(self, *args, **kwargs):  # noqa: ANN002 - passthrough to super
        self.vector_calls.append(dict(kwargs))
        return super().vector_search(*args, **kwargs)


def test_graph_hybrid_search_uses_driver(dummy_encoder):
    driver = TrackingDriver()
    manager = MemoryManager(driver)
    memory = Memory(
        namespace="ns",
        name="Apple Pie",
        entity_label="Recipe",
        embedding=[1.0],
    )
    manager.add_memory(memory)
    config = SearchConfig(encoder=dummy_encoder, top_k=1)

    results = graph_hybrid_search("apple", driver, namespace="ns", config=config)

    assert results and results[0].name == "Apple Pie"
    assert driver.search_calls
    assert driver.search_calls[0]["query"] == "apple"


def test_graph_vector_search_filters_namespace(dummy_encoder):
    driver = TrackingDriver()
    manager = MemoryManager(driver)
    include = Memory(
        namespace="keep",
        name="Keep",
        entity_label="Note",
        embedding=[1.0],
    )
    exclude = Memory(
        namespace="skip",
        name="Skip",
        entity_label="Note",
        embedding=[0.0],
    )
    manager.add_memory(include)
    manager.add_memory(exclude)
    config = SearchConfig(encoder=dummy_encoder, top_k=5)

    results = graph_vector_search("keep", driver, namespace="keep", config=config)

    assert len(results) == 1
    assert results[0].name == include.name
    assert driver.vector_calls
    assert driver.vector_calls[0]["namespace"] == "keep"


def test_graph_exact_search_filters_entity_labels(dummy_encoder):
    driver = TrackingDriver()
    manager = MemoryManager(driver)
    keep = Memory(
        namespace="ns",
        name="Retain",
        entity_label="Note",
        metadata={"content": "keep me"},
    )
    skip = Memory(
        namespace="ns",
        name="Skip",
        entity_label="Task",
        metadata={"content": "ignore"},
    )
    manager.add_memory(keep)
    manager.add_memory(skip)

    results = graph_exact_search(
        "Retain",
        driver,
        namespace="ns",
        entity_labels=["Note"],
        fields=["name"],
        top_k=5,
    )

    assert len(results) == 1
    assert results[0].entity_label == "Note"


def test_graph_regex_search_falls_back_to_list(dummy_encoder):
    driver = TrackingDriver()
    manager = MemoryManager(driver)
    memory = Memory(
        namespace="ns",
        name="Alpha",
        entity_label="Note",
        metadata={"content": "Value"},
    )
    manager.add_memory(memory)

    results = graph_regex_search(
        "Alpha",
        driver,
        namespace="ns",
        entity_labels=["Note"],
    )
    assert results
    assert driver.list_calls >= 1
    assert not driver.search_calls  # regex skips driver search
