#!/usr/bin/env bash
set -euo pipefail

# Provision a fresh MeshMind development environment with full optional coverage.
# This script assumes outbound internet access and root privileges.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

if [[ "${MESH_SKIP_SYSTEM_PACKAGES:-0}" == "1" ]]; then
  echo "[${SCRIPT_NAME}] Skipping system package installation (MESH_SKIP_SYSTEM_PACKAGES=1)"
else
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    cmake \
    curl \
    git \
    pkg-config \
    python3 \
    python3-dev \
    python3-venv \
    python3-pip \
    libssl-dev \
    libffi-dev \
    libkrb5-dev \
    libsasl2-dev \
    libpq-dev \
    libopenblas-dev \
    liblapack-dev
fi

if [[ "${MESH_SKIP_PYTHON_SYNC:-0}" != "1" ]]; then
  if ! command -v uv >/dev/null 2>&1; then
    curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --install-dir /usr/local/bin --force
  fi
fi

cd "${REPO_ROOT}"

python - <<'PY'
import sys
from pathlib import Path

try:
    import tomllib  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - Python <3.11 fallback
    import tomli as tomllib  # type: ignore

data = tomllib.loads(Path("pyproject.toml").read_text())
extras = data.get("project", {}).get("optional-dependencies", {})
required = {"neo4j", "pymgclient", "fastapi"}
available: set[str] = set()
for group in ("dev", "docs", "testing"):
    for dep in extras.get(group, []):
        normalized = dep.split(";", 1)[0].split("[", 1)[0]
        normalized = normalized.split("==", 1)[0].split(">=", 1)[0].strip()
        if normalized:
            available.add(normalized)
missing = required - available
if missing:
    sys.stderr.write(f"Missing optional packages in extras: {', '.join(sorted(missing))}\n")
    sys.exit(1)
print("Validated optional packages: " + ", ".join(sorted(required)))
PY

if [[ "${MESH_SKIP_PYTHON_SYNC:-0}" == "1" ]]; then
  echo "[${SCRIPT_NAME}] Skipping Python dependency sync (MESH_SKIP_PYTHON_SYNC=1)"
else
  if [ -f "${REPO_ROOT}/uv.lock" ]; then
    uv pip sync --system "${REPO_ROOT}/uv.lock"
  else
    uv pip install --system ".[dev,docs,testing]"
  fi
fi

# Ensure scripts are executable for convenience.
chmod +x run/*.sh || true

