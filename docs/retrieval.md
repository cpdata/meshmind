# Retrieval Strategies

MeshMind ships with multiple retrieval strategies that operate on `Memory` collections. Each strategy can run purely in
memory (provided via argument) or load candidates directly from the configured graph driver.

## Hybrid Search

`meshmind.retrieval.search.search`

- Combines BM25 (text), vector similarity, regex, exact-match, and fuzzy signals.
- Accepts `SearchConfig` to tune weights, top-k counts, embedding encoder, and rerank parameters.
- Optional rerank step calls `meshmind.retrieval.llm_rerank.llm_rerank` using the active LLM client.

Graph wrapper: `graph_hybrid_search(query, driver, namespace=None, entity_labels=None, config=None, reranker=None)`
leans on `MemoryManager.list_memories(..., query=query, use_search=True)` so Memgraph/Neo4j filter and paginate on the
server. The helper automatically expands the candidate window (`top_k * 5`, `rerank_k * 2`) to balance recall with
efficiency.

## Vector Search

`meshmind.retrieval.vector.search_vector`

- Uses cosine similarity between query embedding and stored embeddings.
- Graph wrapper `graph_vector_search` now requests driver-side filtering (`query=<search string>`) and pagination, reducing
  the number of memories materialised before vector scoring.

## Textual Search

- **Regex** (`search_regex` / `graph_regex_search`): applies compiled regular expressions against string fields.
- **Exact** (`search_exact` / `graph_exact_search`): equality comparisons with optional case sensitivity, field
  selection, and top-k truncation.
- **Fuzzy** (`search_fuzzy` / `graph_fuzzy_search`): Levenshtein distance using `rapidfuzz` if installed.
- **BM25** (`search_bm25` / `graph_bm25_search`): rank text fields using BM25 weighting.

## Entity Label Filtering & Pagination

All graph-backed helpers accept `entity_labels`. The labels and pagination hints (`offset`, `limit`) are forwarded to
`MemoryManager` and ultimately to the graph driver so only relevant entity types are hydrated into Python. This prevents
unnecessary deserialization when a graph contains many heterogeneous memory types and unlocks efficient infinite-scroll or
batch processing patterns.

## Search Configuration

`SearchConfig` (`meshmind.core.types.SearchConfig`) controls:

- `top_k`: maximum results to return.
- `encoder`: embedding model name (default comes from settings and the MeshMind client).
- `rerank_k`: number of documents to rerank with LLM.
- `fields`: optional mapping for textual searches (regex, exact, fuzzy) to target metadata keys.

## Extending Retrieval

1. Add a new module under `meshmind/retrieval` with a function that accepts `(query, memories, **kwargs)`.
2. Update `meshmind/retrieval/__init__.py` and the MeshMind client to expose the helper.
3. Create graph wrappers if the strategy benefits from driver-backed loading.
4. Add unit tests in `meshmind/tests/test_retrieval.py` or a dedicated module to ensure determinism.
5. Document the feature here and in `README.md`.
