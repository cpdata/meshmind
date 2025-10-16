#!/usr/bin/env python3
"""Measure pagination performance for MeshMind drivers using synthetic data."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from statistics import mean, stdev

sys.path.append(str(Path(__file__).resolve().parents[1]))

from meshmind.api.memory_manager import MemoryManager
from meshmind.core.types import Memory
from meshmind.db.factory import create_graph_driver


def _seed(manager: MemoryManager, namespace: str, entity_label: str, count: int) -> None:
    existing = manager.list_memories(namespace=namespace, entity_labels=[entity_label])
    if existing:
        return
    for idx in range(count):
        mem = Memory(
            namespace=namespace,
            name=f"Pagination {idx}",
            entity_label=entity_label,
            metadata={"content": f"Synthetic payload {idx}"},
        )
        manager.add_memory(mem)


def run_benchmark(args: argparse.Namespace) -> dict[str, float]:
    driver = create_graph_driver(backend=args.backend)
    manager = MemoryManager(driver)
    try:
        _seed(manager, args.namespace, args.entity_label, args.count)
        durations = []
        total_fetched = 0
        for _ in range(args.iterations):
            start = time.perf_counter()
            offset = 0
            fetched = 0
            while True:
                batch = manager.list_memories(
                    namespace=args.namespace,
                    entity_labels=[args.entity_label],
                    offset=offset,
                    limit=args.page_size,
                )
                fetched += len(batch)
                if not batch:
                    break
                offset += args.page_size
            durations.append(time.perf_counter() - start)
            total_fetched = fetched
        return {
            "iterations": float(args.iterations),
            "duration_mean": round(mean(durations), 6),
            "duration_stddev": round(stdev(durations) if len(durations) > 1 else 0.0, 6),
            "page_size": float(args.page_size),
            "count": float(args.count),
            "fetched": float(total_fetched),
        }
    finally:
        closer = getattr(driver, "close", None)
        if callable(closer):
            closer()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="memory", help="Driver backend to benchmark")
    parser.add_argument("--count", type=int, default=2000, help="Synthetic memories to seed")
    parser.add_argument("--page-size", type=int, default=200, help="Page size for list_memories")
    parser.add_argument("--iterations", type=int, default=3, help="Number of benchmark repetitions")
    parser.add_argument("--namespace", default="pagination", help="Namespace for synthetic data")
    parser.add_argument("--entity-label", default="Memory", help="Entity label for seeded data")
    parser.add_argument("--output", help="Optional JSON output path")
    args = parser.parse_args()

    metrics = run_benchmark(args)
    payload = json.dumps(metrics, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
