import pytest

from meshmind.core.types import Memory, SearchConfig
from meshmind.retrieval.bm25 import bm25_search
from meshmind.retrieval.fuzzy import fuzzy_search
from meshmind.retrieval.hybrid import hybrid_search
from meshmind.retrieval.search import search, search_bm25, search_fuzzy


def make_memory(name: str) -> Memory:
    return Memory(namespace="ns", name=name, entity_label="Test")


@pytest.fixture(autouse=True)
def add_embeddings():
    # Assign dummy embeddings equal to length of name
    def _hook(mem: Memory):
        mem.embedding = [len(mem.name)]
        return mem
    Memory.pre_init = _hook
    yield
    delattr(Memory, 'pre_init')


def test_bm25_search():
    docs = [make_memory("apple pie"), make_memory("banana split"), make_memory("cherry tart")]
    results = bm25_search("apple", docs, top_k=2)
    # Expect 'apple pie' first
    assert results and results[0][0].name == "apple pie"
    assert results[0][1] > 0


def test_fuzzy_search():
    docs = [make_memory("apple pie"), make_memory("banana split")]
    results = fuzzy_search("apple pie", docs, top_k=2)
    assert results and results[0][0].name == "apple pie"
    assert 0 < results[0][1] <= 1.0


def test_hybrid_search():
    # Setup memories
    m1 = make_memory("apple")
    m2 = make_memory("banana")
    m1.embedding = [1.0]
    m2.embedding = [0.0]
    docs = [m1, m2]
    config = SearchConfig(encoder="dummy", top_k=2, hybrid_weights=(0.5, 0.5))
    # Register dummy encoder that returns [1] for 'apple' and [0] for 'banana'
    class DummyEncoder:
        def encode(self, texts):
            return [[1.0] if "apple" in t else [0.0] for t in texts]
    from meshmind.core.embeddings import EncoderRegistry
    EncoderRegistry.register("dummy", DummyEncoder())
    results = hybrid_search("apple", docs, config)
    # apple should have highest hybrid score
    assert results[0][0].name == "apple"


def test_search_dispatcher():
    m1 = make_memory("apple")
    m2 = make_memory("banana")
    m1.embedding = [1.0]
    m2.embedding = [0.0]
    docs = [m1, m2]
    from meshmind.core.embeddings import EncoderRegistry
    class DummyEncoder:
        def encode(self, texts): return [[1.0] if "apple" in t else [0.0] for t in texts]
    EncoderRegistry.register("dummy", DummyEncoder())
    config = SearchConfig(encoder="dummy", top_k=1, hybrid_weights=(0.5,0.5))
    res = search("apple", docs, namespace="ns", entity_labels=["Test"], config=config)
    assert len(res) == 1 and res[0].name == "apple"
    # BM25 and fuzzy via dispatcher
    res2 = search_bm25("banana", docs)
    assert res2 and res2[0].name == "banana"
    res3 = search_fuzzy("banana", docs)
    assert res3 and res3[0].name == "banana"