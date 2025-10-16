"""Helpers for reranking retrieval results."""
from __future__ import annotations

from typing import Callable, List, Sequence

from meshmind.core.types import Memory

Reranker = Callable[[str, Sequence[Memory], int], Sequence[Memory]]


def llm_rerank(
    query: str,
    memories: Sequence[Memory],
    llm_client: object | None,
    top_k: int,
    model: str | None = None,
    endpoint: str | None = None,
) -> List[Memory]:
    """Rerank results using an LLM client that supports the Responses API."""
    if llm_client is None or not memories:
        return list(memories)[:top_k]

    model_name = model or "gpt-5-nano"
    prompt = "\n".join(
        [
            "You are a ranking assistant.",
            "Given the query and numbered memory summaries, return a JSON array of memory indexes",
            "sorted from best to worst match.",
            f"Query: {query}",
            "Memories:",
        ]
    )
    for idx, memory in enumerate(memories):
        prompt += f"\n{idx}: {memory.name}"

    try:  # pragma: no cover - network interaction mocked in tests
        response = llm_client.responses.create(  # type: ignore[attr-defined]
            operation="rerank",
            model=model_name,
            base_url=endpoint,
            input=[{"role": "user", "content": prompt}],
            response_format={"type": "json_schema", "json_schema": {
                "name": "rankings",
                "schema": {
                    "type": "object",
                    "properties": {
                        "order": {
                            "type": "array",
                            "items": {"type": "integer"},
                        }
                    },
                    "required": ["order"],
                },
            }},
        )
        content = response.output[0].content[0].text  # type: ignore[index]
    except Exception:
        return list(memories)[:top_k]

    try:
        import json

        data = json.loads(content)
        indexes = [idx for idx in data.get("order", []) if 0 <= idx < len(memories)]
    except Exception:
        return list(memories)[:top_k]

    ranked = [memories[idx] for idx in indexes]
    remaining = [mem for mem in memories if mem not in ranked]
    ranked.extend(remaining)
    return ranked[:top_k]


def apply_reranker(
    query: str,
    candidates: Sequence[Memory],
    top_k: int,
    reranker: Reranker | None = None,
) -> List[Memory]:
    if reranker is None:
        return list(candidates)[:top_k]
    ranked = reranker(query, candidates, top_k)
    return list(ranked)[:top_k]
