#!/usr/bin/env bash
set -euo pipefail

# Refresh an existing MeshMind environment restored from cache.
# Installs missing system packages, syncs Python dependencies, and
# prepares the workspace for end-to-end testing.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

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

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --install-dir /usr/local/bin --force
fi

cd "${REPO_ROOT}"

if [ -f "${REPO_ROOT}/uv.lock" ]; then
  uv pip sync --system "${REPO_ROOT}/uv.lock"
else
  uv pip install --system ".[dev,docs,testing]"
fi

# Update git submodules (if any) to keep tooling consistent.
if [ -f .gitmodules ]; then
  git submodule update --init --recursive
fi

