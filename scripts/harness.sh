#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
if [[ ! -x .tools/harness/bin/python ]]; then
  echo 'Run bash scripts/setup_local.sh first.' >&2
  exit 1
fi
export PYTHONDONTWRITEBYTECODE=1
exec .tools/harness/bin/python -m mostaza.development "$@"
