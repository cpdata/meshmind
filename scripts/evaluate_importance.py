#!/usr/bin/env python3
"""Evaluate MeshMind's importance heuristic across sample datasets."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, List

sys.path.append(str(Path(__file__).resolve().parents[1]))

from meshmind.core.types import Memory
from meshmind.pipeline.preprocess import score_importance, summarize_importance


def _load_memories_from_path(path: Path) -> List[Memory]:
    text = path.read_text(encoding="utf-8")
    try:
        payload = json.loads(text)
        if isinstance(payload, list):
            items = payload
        else:
            items = payload.get("memories", []) if isinstance(payload, dict) else []
    except json.JSONDecodeError:
        # Try JSON lines fallback
        items = [json.loads(line) for line in text.splitlines() if line.strip()]
    memories = []
    for item in items:
        if not isinstance(item, dict):
            continue
        memories.append(Memory(**item))
    return memories


def _generate_synthetic(count: int, namespace: str) -> List[Memory]:
    memories: List[Memory] = []
    for idx in range(count):
        memories.append(
            Memory(
                namespace=namespace,
                name=f"Synthetic memory {idx}",
                entity_label="Memory",
                metadata={
                    "content": f"Synthetic content block {idx}",
                    "summary": f"Auto summary {idx}",
                },
            )
        )
    return memories


def _memories_from_args(args: argparse.Namespace) -> List[Memory]:
    if args.input:
        return _load_memories_from_path(Path(args.input))
    return _generate_synthetic(args.synthetic_count, args.namespace)


def evaluate(memories: Iterable[Memory]) -> dict[str, float]:
    scored = score_importance(list(memories))
    return summarize_importance(scored)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        help="Path to JSON/JSONL payload containing memories (falls back to synthetic data)",
    )
    parser.add_argument(
        "--synthetic-count",
        type=int,
        default=100,
        help="Number of synthetic memories to generate when --input is omitted",
    )
    parser.add_argument(
        "--namespace",
        default="analysis",
        help="Namespace assigned to synthetic memories",
    )
    parser.add_argument(
        "--output",
        help="Optional file path to store the evaluation summary as JSON",
    )
    args = parser.parse_args()

    memories = _memories_from_args(args)
    summary = evaluate(memories)
    payload = {"count": summary["count"], "mean": summary["mean"], "stddev": summary["stddev"], "recent_bonus": summary["recent_bonus"]}
    text = json.dumps(payload, indent=2, sort_keys=True)

    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
