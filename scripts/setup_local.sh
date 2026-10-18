#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$root/src${PYTHONPATH:+:$PYTHONPATH}"
runtime_python="${MOSTAZA_PYTHON:-$root/.tools/harness/bin/python}"
if [[ -x "$runtime_python" ]]; then
  "$runtime_python" - <<'PY'
import importlib.metadata as metadata
from pathlib import Path
import mostaza.development as development
assert development.ROOT == Path.cwd().resolve(), development.ROOT
for name, version in (
    ('swegemma', '0.2.11'), ('adk-submission', '0.2.13'),
    ('adk-eval-core', '0.1.0'), ('google-adk', '1.36.1'),
):
    assert metadata.version(name) == version, f'Expected {name}=={version}'
from dotenv import load_dotenv
print('Existing official environment and worktree imports verified; no installation needed')
PY
  echo "Ready: bash scripts/harness.sh --help"
  exit 0
fi
if [[ -n "${MOSTAZA_PYTHON:-}" ]]; then
  echo 'MOSTAZA_PYTHON must name an existing executable interpreter.' >&2
  exit 1
fi
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
