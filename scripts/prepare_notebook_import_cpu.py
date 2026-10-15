"""Prepare only a GPU-disabled notebook, host manifests and CPU readiness record."""

import argparse
import json
from pathlib import Path

from mostaza.evaluation.contracts import canonical_json
from mostaza.evaluation.notebook_import_candidate import (
    EVIDENCE,
    NOTEBOOK,
    build_notebook,
    experiment_manifest,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    outputs = {NOTEBOOK: build_notebook(root)}
    for arm in ("E0", "E1"):
        outputs[f"experiments/{arm}-C8K-L1/manifest.json"] = canonical_json(
            experiment_manifest(root, arm)
        )
    outputs[EVIDENCE + "/readiness.json"] = canonical_json(
        {
            "candidate": "N-IMPORT-CPU-01",
            "ready_for_gpu": False,
            "gpu_authorization": None,
            "real_evaluations": "NOT_RUN",
            "linux_runtime_portability": "NOT_TESTED",
            "private_scorer_parity": None,
            "private_scorer_parity_reason": "No real Kaggle/private scorer execution",
        }
    )
    for name, data in outputs.items():
        path = root / name
        if args.check:
            if path.read_bytes() != data:
                raise ValueError("Prepared file differs: " + name)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    print(json.dumps({"prepared_files": list(outputs), "gpu_readiness": False}))


if __name__ == "__main__":
    main()
