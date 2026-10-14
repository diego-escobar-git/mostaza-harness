#!/bin/sh
set -eu
project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_root"
if [ -x "$project_root/.tools/uv/bin/uv" ]; then
  export PATH="$project_root/.tools/uv/bin:$PATH"
fi
exec uv run --frozen --no-sync python -m mostaza.packaging "$@"
