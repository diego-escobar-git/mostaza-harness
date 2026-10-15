"""Prepare approved CPU-only context variants and a blocked private notebook."""

import argparse
import json
from pathlib import Path

from mostaza.evaluation.context_candidate import (
    EVIDENCE,
    NOTEBOOK,
    build_notebook,
    readiness,
)
from mostaza.evaluation.context_variants import (
    CONFIGURATIONS,
    configuration_files,
    prepare_manifests,
)
from mostaza.packaging import archive_bytes


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    prepare_manifests(root)
    notebook = root / NOTEBOOK
    data = build_notebook(root)
    if notebook.exists() and notebook.read_bytes() != data:
        raise ValueError("Existing candidate differs; review rather than overwrite")
    notebook.write_bytes(data)
    evidence = root / EVIDENCE
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "readiness.json").write_text(
        json.dumps(readiness(root), indent=2, sort_keys=True) + "\n"
    )
    if args.output_dir:
        output = args.output_dir.resolve()
        if not output.is_relative_to(root / "results"):
            parser.error("Archives must stay in a new ignored results directory")
        for configuration in CONFIGURATIONS:
            archive_bytes(
                configuration_files(root, configuration),
                output / (configuration + ".zip"),
            )
    print(
        "Prepared five variants and private notebook; verifier "
        "binding blocks GPU readiness"
    )


if __name__ == "__main__":
    main()
