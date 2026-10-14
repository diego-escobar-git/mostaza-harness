"""Read-only phase-2 compiler, historical integrity and readiness gate."""

from __future__ import annotations

import argparse
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Any

from check_evidence import check_real
from check_official import phase2_compiler_receipts, phase2_resource_review

from mostaza.evaluation.contracts import canonical_json, require
from mostaza.evaluation.phase2 import (
    EVIDENCE,
    comparison,
    readiness,
    report_markdown,
)
from mostaza.research.trace_diagnostics import check_diagnosis

LEGACY_COMMIT = "60ad0cec85bb36a1e65609ca2b1a743ba087384d"
LEGACY_ROOTS = (
    "submission",
    "experiments/E0-baseline",
    "experiments/E1-hybrid-retrieval",
    "experiments/cohort.json",
    "docs/implementation/evidence/mostaza-phase1-foundation",
)


def check_legacy_bytes(root: Path) -> None:
    """Bind original tracked bytes to the merged historical baseline."""
    paths = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", LEGACY_COMMIT, "--", *LEGACY_ROOTS],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.splitlines()
    require(len(paths) >= 12, "Immutable legacy inventory unavailable")
    for name in paths:
        actual = root / name
        require(
            actual.is_file() and not actual.is_symlink(), "Legacy input missing/unsafe"
        )
        original = subprocess.run(
            ["git", "show", f"{LEGACY_COMMIT}:{name}"],
            cwd=root,
            check=True,
            capture_output=True,
            timeout=30,
        ).stdout
        require(
            actual.read_bytes() == original, f"Immutable legacy bytes changed: {name}"
        )


def verify(root: Path, cohort: Path, evidence: Path) -> dict[str, Any]:
    require(
        cohort.resolve() == (root / "experiments/cohort.json").resolve(),
        "Use the frozen repository cohort",
    )
    check_legacy_bytes(root)
    check_real(
        cohort, root / "docs/implementation/evidence/mostaza-phase1-foundation", root
    )
    diagnosis = check_diagnosis(root, evidence / "trace-diagnosis.json")
    review = phase2_resource_review(root)
    require(
        json.loads((evidence / "resource-review.json").read_text()) == review,
        "Resource review differs from pinned source recomputation",
    )
    compiler = phase2_compiler_receipts(root, root / ".tools/official/bin/python")
    require(
        json.loads((evidence / "official-validation.json").read_text()) == compiler,
        "Compiler receipts differ from actual variant compilation",
    )
    ready = readiness(root)
    # This local-only checkpoint deliberately admits no acquisition assertions.
    # A future authorized acquisition requires native verification support and a
    # complete gate/audit; changing status or inserting fixture results fails closed.
    require(
        (evidence / "readiness.json").read_bytes() == canonical_json(ready),
        "Readiness differs from current notebook/config/source/NOT_RUN evidence",
    )
    compared = comparison(diagnosis)
    require(
        (evidence / "comparison.json").read_bytes() == canonical_json(compared),
        "Comparison differs from native historical diagnosis/pending phase2",
    )
    require(
        (evidence / "report.md").read_text() == report_markdown(ready, compared),
        "Report differs from deterministic evidence recomputation",
    )
    return ready


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, default=Path(EVIDENCE))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        verify(root, args.cohort, args.evidence_dir)
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        zipfile.BadZipFile,
        subprocess.SubprocessError,
    ) as error:
        parser.exit(1, f"Phase-2 readiness verification failed: {error}\n")
    print(
        "Verified local phase-2 readiness and compiler provenance; "
        "real evaluation NOT_RUN"
    )


if __name__ == "__main__":
    main()
