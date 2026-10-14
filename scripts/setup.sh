#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd -- "$PROJECT_ROOT"
export UV_CACHE_DIR="${UV_CACHE_DIR:-$PROJECT_ROOT/.tools/cache}"
export UV_PYTHON_INSTALL_DIR="${UV_PYTHON_INSTALL_DIR:-$PROJECT_ROOT/.tools/python}"
if [[ -x "$PROJECT_ROOT/.tools/uv/bin/uv" ]]; then
  export PATH="$PROJECT_ROOT/.tools/uv/bin:$PATH"
fi
if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required. See README.md for the scoped installation instructions." >&2
  exit 1
fi
uv sync --locked --group dev
uv run --frozen --no-sync python -c 'import sys, mostaza; assert sys.version_info[:2] == (3, 13), sys.version; print(f"Python {sys.version.split()[0]}; mostaza {mostaza.__version__}")'
