"""End-to-end MeshMind example covering extraction, storage, and retrieval."""
from __future__ import annotations

from meshmind.client import MeshMind
from meshmind.core.types import Memory, Triplet


def main() -> None:
    mm = MeshMind()

    texts = [
        "The Eiffel Tower is located in Paris and was built in 1889.",
        "Python is a programming language created by Guido van Rossum.",
    ]

    memories = mm.extract_memories(
        instructions="Extract key facts as Memory objects.",
        namespace="demo",
        entity_types=[Memory],
        content=texts,
    )
    memories = mm.deduplicate(memories)
    memories = mm.score_importance(memories)
    memories = mm.compress(memories)
    mm.store_memories(memories)
    print(f"Stored {len(memories)} memories.")

    if len(memories) >= 2:
        relation = Triplet(
            subject=str(memories[0].uuid),
            predicate="RELATED_TO",
            object=str(memories[1].uuid),
            namespace="demo",
            entity_label="Knowledge",
            metadata={"confidence": 0.9},
        )
        mm.store_triplets([relation])
        print("Stored relationship between first two memories.")

    hits = mm.search("Eiffel Tower", memories, namespace="demo")
    print("Hybrid search results:")
    for mem in hits:
        print(f"- {mem.name} (importance={mem.importance})")

    vector_hits = mm.search_vector("programming", memories, namespace="demo")
    print("Vector-only search results:")
    for mem in vector_hits:
        print(f"- {mem.name}")

    regex_hits = mm.search_regex(r"Paris", memories, namespace="demo")
    print("Regex search results:")
    for mem in regex_hits:
        print(f"- {mem.name}")

    exact_hits = mm.search_exact("Python", memories, fields=["name"], namespace="demo")
    print("Exact match search results:")
    for mem in exact_hits:
        print(f"- {mem.name}")


if __name__ == "__main__":
    main()
