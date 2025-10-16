from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _run_script(script: str, *args: str) -> dict[str, float]:
    repo_root = _repo_root()
    script_path = repo_root / "scripts" / script
    result = subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_evaluate_importance_synthetic() -> None:
    data = _run_script("evaluate_importance.py", "--synthetic-count", "5")
    assert data["count"] >= 5.0
    assert data["mean"] >= 0.0


def test_consolidation_benchmark_quick_run() -> None:
    metrics = _run_script(
        "consolidation_benchmark.py",
        "--iterations",
        "2",
        "--namespaces",
        "1",
        "--groups",
        "2",
        "--duplicates",
        "2",
    )
    assert metrics["groups"] == 2.0
    assert metrics["iterations"] == 2.0


def test_pagination_benchmark_memory_backend() -> None:
    metrics = _run_script(
        "benchmark_pagination.py",
        "--backend",
        "memory",
        "--count",
        "50",
        "--page-size",
        "10",
        "--iterations",
        "1",
    )
    assert metrics["page_size"] == 10.0
    assert metrics["count"] == 50.0
    assert metrics["fetched"] <= 50.0
