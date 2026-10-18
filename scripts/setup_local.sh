#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
export UV_CACHE_DIR="$root/.tools/cache"
export UV_PYTHON_INSTALL_DIR="$root/.tools/python"
if [[ -z "${UV_BIN:-}" ]]; then
  if command -v uv >/dev/null 2>&1; then
    UV_BIN="$(command -v uv)"
  else
    if [[ ! -x .tools/uv/bin/uv ]]; then
      python3 -m venv .tools/uv
      .tools/uv/bin/python -m pip install --quiet uv==0.9.5
    fi
    UV_BIN="$root/.tools/uv/bin/uv"
  fi
fi
if [[ ! -x .tools/harness/bin/python ]]; then
  "$UV_BIN" venv --python 3.13.15 .tools/harness
fi
PYTHONPATH="$root/src" .tools/harness/bin/python scripts/fetch_resources.py \
  --resource swegemma --resource adk_submission --resource adk_eval_core
"$UV_BIN" pip install --quiet --python .tools/harness/bin/python -r requirements-local.txt
echo "Ready: bash scripts/harness.sh --help"
