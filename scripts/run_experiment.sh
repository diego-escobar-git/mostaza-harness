#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"
if [[ -x "$project_root/.tools/uv/bin/uv" ]]; then
  export PATH="$project_root/.tools/uv/bin:$PATH"
fi
case "${1:-}" in
  import) shift; exec uv run --frozen --no-sync python -m mostaza.evaluation.import_results "$@" ;;
  report) shift; exec uv run --frozen --no-sync python -m mostaza.research.report "$@" ;;
  *) echo 'Usage: scripts/run_experiment.sh {import|report} [arguments]' >&2; exit 2 ;;
esac
