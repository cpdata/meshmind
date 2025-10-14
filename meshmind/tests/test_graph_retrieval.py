from meshmind.api.memory_manager import MemoryManager
from meshmind.core.types import Memory, SearchConfig
from meshmind.db.in_memory_driver import InMemoryGraphDriver
from meshmind.retrieval.graph import graph_hybrid_search, graph_vector_search


def test_graph_hybrid_search_uses_driver(dummy_encoder):
    driver = InMemoryGraphDriver()
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


def test_graph_vector_search_filters_namespace(dummy_encoder):
    driver = InMemoryGraphDriver()
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
