"""Smoke tests for environment provisioning scripts."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize("script_name", ["install_setup.sh", "maintenance_setup.sh"])
def test_setup_scripts_validate_optional_packages(script_name: str) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    script_path = repo_root / "run" / script_name
    env = os.environ.copy()
    env.update({
        "MESH_SKIP_SYSTEM_PACKAGES": "1",
        "MESH_SKIP_PYTHON_SYNC": "1",
    })
    result = subprocess.run(
        ["bash", str(script_path)],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    stdout = result.stdout
    assert "Validated optional packages: fastapi, neo4j, pymgclient" in stdout
    assert "Skipping system package installation" in stdout
    assert "Skipping Python dependency sync" in stdout
