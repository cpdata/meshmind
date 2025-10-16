"""Ensure protobuf assets ship with the package."""
from __future__ import annotations

from pathlib import Path

from meshmind.protos import data_path


def test_proto_files_packaged() -> None:
    proto_path = Path(data_path("memory_service.proto"))
    assert proto_path.exists()
    text = proto_path.read_text(encoding="utf-8")
    assert "service MeshMindService" in text
