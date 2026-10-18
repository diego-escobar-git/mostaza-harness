#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi
runtime_python="${MOSTAZA_PYTHON:-$root/.tools/harness/bin/python}"
if [[ ! -x "$runtime_python" ]]; then
  echo 'Run bash scripts/setup_local.sh first.' >&2
  exit 1
fi
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$root/src${PYTHONPATH:+:$PYTHONPATH}"
exec "$runtime_python" -m mostaza.development "$@"
