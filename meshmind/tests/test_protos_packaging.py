"""Ensure protobuf assets ship with the package."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from meshmind.protos import data_path


def test_proto_files_packaged() -> None:
    proto_path = Path(data_path("memory_service.proto"))
    assert proto_path.exists()
    text = proto_path.read_text(encoding="utf-8")
    assert "service MeshMindService" in text


def test_check_protos_script_runs_successfully() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [sys.executable, "scripts/check_protos.py"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Protobuf bindings are up to date." in result.stderr
