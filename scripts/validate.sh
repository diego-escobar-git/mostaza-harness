#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$PROJECT_ROOT"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$PROJECT_ROOT/.tools/cache}"
export UV_PYTHON_INSTALL_DIR="${UV_PYTHON_INSTALL_DIR:-$PROJECT_ROOT/.tools/python}"
if [[ -x "$PROJECT_ROOT/.tools/uv/bin/uv" ]]; then
  export PATH="$PROJECT_ROOT/.tools/uv/bin:$PATH"
fi
uv run --frozen --no-sync ruff format --check .
uv run --frozen --no-sync ruff check .
uv run --frozen --no-sync mypy src scripts
uv run --frozen --no-sync pytest -q -p no:cacheprovider tests/unit
uv run --frozen --no-sync pytest -q -p no:cacheprovider tests/integration
BUILD_DIR="$(mktemp -d)"
trap 'rm -rf -- "$BUILD_DIR"' EXIT
mkdir -p "$BUILD_DIR/project/src"
cp pyproject.toml README.md LICENSE "$BUILD_DIR/project/"
cp -R src/mostaza "$BUILD_DIR/project/src/"
uv run --frozen --no-sync python -m build "$BUILD_DIR/project" --no-isolation --outdir "$BUILD_DIR/dist"
uv run --frozen --no-sync python scripts/check_official.py --check --experiments E0 E1
uv run --frozen --no-sync python scripts/check_evidence.py --require-real-paired --cohort experiments/cohort.json --evidence-dir docs/implementation/evidence/mostaza-phase1-foundation
