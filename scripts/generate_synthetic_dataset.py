"""Generate synthetic datasets for MeshMind benchmarking."""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Iterable
from uuid import uuid4

import numpy as np

WORDS = [
    "agent",
    "memory",
    "context",
    "graph",
    "embedding",
    "retrieval",
    "knowledge",
    "triplet",
    "pipeline",
    "maintenance",
    "rerank",
]


def _random_text(word_count: int) -> str:
    return " ".join(random.choice(WORDS) for _ in range(word_count))


def _random_metadata() -> dict[str, object]:
    return {
        "summary": _random_text(random.randint(4, 10)),
        "tags": random.sample(WORDS, k=random.randint(2, 4)),
        "score": round(random.random(), 3),
        "source": random.choice(["ingest", "consolidation", "bootstrap"]),
    }


def _random_embedding(dim: int) -> list[float]:
    vector = np.random.normal(0, 1, size=dim)
    norm = np.linalg.norm(vector)
    if norm == 0:
        return [0.0 for _ in range(dim)]
    return (vector / norm).astype(float).tolist()


def _write_jsonl(path: Path, rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _write_triplets(path: Path, rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("subject,predicate,object,namespace,entity_label,metadata\n")
        for row in rows:
            metadata = json.dumps(row.get("metadata", {}), ensure_ascii=False)
            handle.write(
                (
                    f"{row['subject']},{row['predicate']},{row['object']},{row['namespace']},"
                    f"{row['entity_label']},{metadata}\n"
                )
            )


def generate_dataset(
    output_dir: Path,
    *,
    memories: int,
    triplets: int,
    embedding_dim: int,
    namespace: str,
) -> None:
    random.seed(42)
    np.random.seed(42)
    output_dir.mkdir(parents=True, exist_ok=True)

    memory_rows = []
    triplet_rows = []
    entity_ids: list[str] = []
    entity_labels: dict[str, str] = {}

    for _ in range(memories):
        uid = str(uuid4())
        entity_ids.append(uid)
        label = random.choice(["Note", "Task", "Observation"])
        entity_labels[uid] = label
        memory_rows.append(
            {
                "uuid": uid,
                "namespace": namespace,
                "name": _random_text(3).title(),
                "entity_label": label,
                "content": _random_text(random.randint(20, 60)),
                "embedding": _random_embedding(embedding_dim),
                "metadata": _random_metadata(),
            }
        )

    for _ in range(triplets):
        subj, obj = random.sample(entity_ids, k=2)
        triplet_rows.append(
            {
                "subject": subj,
                "predicate": random.choice(["references", "follows", "relates_to", "duplicates"]),
                "object": obj,
                "namespace": namespace,
                "entity_label": entity_labels[subj],
                "metadata": {
                    "confidence": round(random.uniform(0.5, 0.99), 2),
                    "notes": _random_text(6),
                },
            }
        )

    _write_jsonl(output_dir / "memories.jsonl", memory_rows)
    _write_triplets(output_dir / "triplets.csv", triplet_rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Directory to write dataset files")
    parser.add_argument("--memories", type=int, default=10000, help="Number of synthetic memories to generate")
    parser.add_argument("--triplets", type=int, default=20000, help="Number of synthetic triplets to generate")
    parser.add_argument("--embedding-dim", type=int, default=384, help="Embedding vector dimensionality")
    parser.add_argument("--namespace", type=str, default="benchmark", help="Namespace label for generated data")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    generate_dataset(
        args.output,
        memories=args.memories,
        triplets=args.triplets,
        embedding_dim=args.embedding_dim,
        namespace=args.namespace,
    )
    print(f"Synthetic dataset written to {args.output}")


if __name__ == "__main__":
    main()
