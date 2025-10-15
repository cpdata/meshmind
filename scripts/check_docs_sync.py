#!/usr/bin/env python3
"""Ensure documentation updates accompany relevant code changes."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Set

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DOC_MAP: Dict[str, List[str]] = {
    "meshmind/api": ["docs/api.md", "docs/operations.md"],
    "meshmind/retrieval": ["docs/retrieval.md"],
    "meshmind/db": ["docs/persistence.md"],
    "meshmind/pipeline": ["docs/pipelines.md"],
    "meshmind/core": ["docs/architecture.md", "docs/development.md"],
    "meshmind/llm_client.py": ["docs/architecture.md", "docs/configuration.md"],
    "meshmind/cli": ["docs/operations.md"],
    "meshmind/tasks": ["docs/operations.md", "docs/telemetry.md"],
    "meshmind/tests/docker": ["SETUP.md", "docs/operations.md"],
    "docker-compose": ["SETUP.md", "docs/operations.md", "ENVIRONMENT_NEEDS.md"],
    "Dockerfile": ["SETUP.md", "ENVIRONMENT_NEEDS.md"],
}

DOC_PREFIXES = ("docs/",)
ALWAYS_DOC_FILES = {
    "README.md",
    "PROJECT.md",
    "SOT.md",
    "PLAN.md",
    "RECOMMENDATIONS.md",
    "RESUME_NOTES.md",
    "SETUP.md",
    "ENVIRONMENT_NEEDS.md",
    "NEEDED_FOR_TESTING.md",
}


def _git_diff(base: str) -> List[str]:
    cmd = ["git", "diff", "--name-only", f"{base}..HEAD"]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _docs_touched(files: Iterable[str]) -> Set[str]:
    docs: Set[str] = set()
    for path in files:
        if path.startswith(DOC_PREFIXES) or path in ALWAYS_DOC_FILES:
            docs.add(path)
    return docs


def check_docs(base: str) -> int:
    changed = _git_diff(base)
    if not changed:
        return 0

    docs_changed = _docs_touched(changed)
    missing: Dict[str, Dict[str, Iterable[str]]] = {}

    for prefix, required_docs in DOC_MAP.items():
        touched = [path for path in changed if path.startswith(prefix)]
        if not touched:
            continue
        if any(doc in docs_changed for doc in required_docs):
            continue
        missing[prefix] = {"files": touched, "docs": required_docs}

    if missing:
        print("Documentation updates required for the following areas:", file=sys.stderr)
        for prefix, info in missing.items():
            print(f"- {prefix}", file=sys.stderr)
            print(f"  touched: {', '.join(info['files'])}", file=sys.stderr)
            print(f"  expected docs: {', '.join(info['docs'])}", file=sys.stderr)
        return 1

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        default="origin/main",
        help="Git reference to diff against (default: origin/main)",
    )
    args = parser.parse_args()

    try:
        return check_docs(args.base)
    except RuntimeError as exc:  # pragma: no cover - git errors depend on CI setup
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
