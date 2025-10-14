import pytest

from meshmind.client import MeshMind
from meshmind.core.types import SearchConfig
from meshmind.db.in_memory_driver import InMemoryGraphDriver
from meshmind.retrieval import (
    apply_reranker,
    llm_rerank,
    search,
    search_bm25,
    search_exact,
    search_fuzzy,
    search_regex,
    search_vector,
)
from meshmind.retrieval.hybrid import hybrid_search


def test_bm25_search(memory_factory):
    docs = [
        memory_factory("apple pie"),
        memory_factory("banana split"),
        memory_factory("cherry tart"),
    ]
    results = search_bm25("apple", docs, top_k=2)
    assert results and results[0].name == "apple pie"


def test_fuzzy_search(memory_factory):
    docs = [memory_factory("apple pie"), memory_factory("banana split")]
    results = search_fuzzy("apple pie", docs, top_k=2)
    assert results and results[0].name == "apple pie"


def test_hybrid_search(memory_factory, dummy_encoder):
    m1 = memory_factory("apple", embedding=[1.0])
    m2 = memory_factory("banana", embedding=[0.0])
    config = SearchConfig(encoder=dummy_encoder, top_k=2, hybrid_weights=(0.5, 0.5))
    ranked = hybrid_search("apple", [m1, m2], config)
    assert ranked[0][0].name == "apple"


def test_vector_search(memory_factory, dummy_encoder):
    m1 = memory_factory("apple", embedding=[1.0])
    m2 = memory_factory("banana", embedding=[0.0])
    config = SearchConfig(encoder=dummy_encoder, top_k=1)
    results = search_vector("apple", [m1, m2], config=config)
    assert results == [m1]


def test_regex_search(memory_factory):
    docs = [
        memory_factory("Visit Paris", metadata={"city": "Paris"}),
        memory_factory("Visit Berlin", metadata={"city": "Berlin"}),
    ]
    results = search_regex("paris", docs, top_k=5)
    assert len(results) == 1 and results[0].name == "Visit Paris"


def test_exact_search(memory_factory):
    docs = [
        memory_factory("Python"),
        memory_factory("Rust", metadata={"language": "Rust"}),
    ]
    results = search_exact("rust", docs, fields=["metadata"], case_sensitive=False)
    assert results and results[0].name == "Rust"


def test_search_dispatcher_with_rerank(memory_factory, dummy_encoder):
    m1 = memory_factory("apple", embedding=[1.0])
    m2 = memory_factory("banana", embedding=[0.1])
    docs = [m2, m1]
    config = SearchConfig(encoder=dummy_encoder, top_k=2, rerank_k=2)

    class DummyLLM:
        class responses:
            @staticmethod
            def create(**kwargs):
                return type(
                    "Resp",
                    (),
                    {
                        "output": [
                            type(
                                "Out",
                                (),
                                {
                                    "content": [
                                        type("Text", (), {"text": '{"order": [1, 0]}'})
                                    ]
                                },
                            )
                        ]
                    },
                )

    reranked = search(
        "apple",
        docs,
        config=config,
        reranker=lambda q, c, k: llm_rerank(q, c, DummyLLM(), k, model="dummy"),
    )
    assert reranked[0].name == "apple"


def test_apply_reranker_default(memory_factory):
    docs = [memory_factory("alpha"), memory_factory("beta")]
    ranked = apply_reranker("alpha", docs, top_k=1)
    assert ranked == [docs[0]]


def test_llm_rerank_failure(memory_factory):
    docs = [memory_factory("alpha"), memory_factory("beta")]
    result = llm_rerank("alpha", docs, llm_client=None, top_k=2)
    assert len(result) == 2


def test_client_search_uses_graph_when_memories_none(dummy_encoder, memory_factory):
    driver = InMemoryGraphDriver()
    client = MeshMind(llm_client=object(), embedding_model=dummy_encoder, graph_driver=driver)
    memory = memory_factory("apple", embedding=[1.0])
    client.create_memory(memory)
    config = SearchConfig(encoder=dummy_encoder, top_k=1)

    results = client.search("apple", memories=None, namespace="ns", config=config)

    assert results and results[0].name == "apple"
