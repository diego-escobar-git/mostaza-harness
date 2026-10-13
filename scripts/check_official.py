"""Read-only official prerequisites, compiler, ZIP and package-build checks."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from mostaza.packaging import PackagingError, build_submission
from mostaza.resources import ResourceError, require_resources


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.add_argument("--experiments", choices=["E0", "E1"], nargs="+", required=True)
    parser.add_argument("--compiler-python", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    compiler = args.compiler_python or root / ".tools/official/bin/python"
    try:
        require_resources(
            root,
            [
                "notebook",
                "swegemma",
                "adk_submission",
                "adk_eval_core",
                "harness_readme",
                "starter_agent",
                "tasks",
            ],
        )
        with tempfile.TemporaryDirectory(prefix="mostaza-official-check-") as temporary:
            for experiment in args.experiments:
                first = Path(temporary) / f"{experiment}-1.zip"
                second = Path(temporary) / f"{experiment}-2.zip"
                first_hash = build_submission(root, experiment, first, compiler)
                second_hash = build_submission(root, experiment, second, compiler)
                if (
                    first_hash != second_hash
                    or first.read_bytes() != second.read_bytes()
                ):
                    raise PackagingError("Archive reproduction differs")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "build",
                    "--no-isolation",
                    "--outdir",
                    temporary,
                    str(root),
                ],
                check=True,
                timeout=180,
            )
    except (
        ResourceError,
        PackagingError,
        OSError,
        subprocess.SubprocessError,
    ) as error:
        parser.exit(1, f"Official validation prerequisite failed: {error}\n")
    print(
        "Official compiler-only validation and reproducible archives passed. "
        "Real Kaggle evidence is separate."
    )


if __name__ == "__main__":
    main()
