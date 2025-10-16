#!/usr/bin/env python3
"""Benchmark consolidation heuristics across synthetic workloads."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from statistics import mean, stdev
from typing import List

sys.path.append(str(Path(__file__).resolve().parents[1]))

from meshmind.core.types import Memory
from meshmind.pipeline.consolidate import (
    ConsolidationOutcome,
    ConsolidationSettings,
    consolidate_memories,
)


def _generate_dataset(namespaces: int, groups_per_namespace: int, duplicates: int) -> List[Memory]:
    memories: List[Memory] = []
    for ns_idx in range(namespaces):
        namespace = f"benchmark-{ns_idx}"
        for group_idx in range(groups_per_namespace):
            label = f"Entity {ns_idx}-{group_idx}"
            primary = Memory(
                namespace=namespace,
                name=label,
                entity_label="Memory",
                metadata={"content": f"{label} canonical"},
                importance=1.0,
            )
            memories.append(primary)
            for dup_idx in range(duplicates):
                memories.append(
                    Memory(
                        namespace=namespace,
                        name=label,
                        entity_label="Memory",
                        metadata={
                            "content": f"{label} duplicate {dup_idx}",
                            "summary": f"Summary {dup_idx}",
                        },
                        importance=max(0.1, 0.9 - (dup_idx * 0.05)),
                    )
                )
    return memories


def _summarize(plan: List[ConsolidationOutcome]) -> dict[str, float]:
    removed = sum(len(outcome.removed_ids) for outcome in plan)
    summaries = sum(
        1 for outcome in plan if outcome.updated.metadata.get("consolidated_summary")
    )
    return {
        "groups": float(len(plan)),
        "removed": float(removed),
        "summaries": float(summaries),
    }


def run_benchmark(args: argparse.Namespace) -> dict[str, float]:
    dataset = _generate_dataset(args.namespaces, args.groups, args.duplicates)
    settings = ConsolidationSettings(
        max_group_size=max(args.duplicates + 1, args.max_group_size),
        max_updates=args.max_updates,
        max_updates_per_namespace=args.max_updates_per_namespace,
    )
    durations = []
    for _ in range(args.iterations):
        start = time.perf_counter()
        plan = consolidate_memories(dataset, settings=settings)
        durations.append(time.perf_counter() - start)
    stats = _summarize(plan.outcomes)
    stats.update(
        {
            "duration_mean": round(mean(durations), 6),
            "duration_stddev": round(stdev(durations) if len(durations) > 1 else 0.0, 6),
            "iterations": float(len(durations)),
        }
    )
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--namespaces", type=int, default=3, help="Synthetic namespaces")
    parser.add_argument("--groups", type=int, default=10, help="Groups per namespace")
    parser.add_argument("--duplicates", type=int, default=7, help="Duplicates per group")
    parser.add_argument("--iterations", type=int, default=5, help="Benchmark iterations")
    parser.add_argument(
        "--max-group-size",
        type=int,
        default=25,
        help="Override ConsolidationSettings.max_group_size",
    )
    parser.add_argument(
        "--max-updates",
        type=int,
        default=400,
        help="Override ConsolidationSettings.max_updates",
    )
    parser.add_argument(
        "--max-updates-per-namespace",
        type=int,
        default=150,
        help="Override ConsolidationSettings.max_updates_per_namespace",
    )
    parser.add_argument(
        "--output",
        help="Optional JSON file path to persist benchmark metrics",
    )
    args = parser.parse_args()

    metrics = run_benchmark(args)
    payload = json.dumps(metrics, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
