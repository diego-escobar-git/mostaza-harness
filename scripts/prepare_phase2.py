"""Generate only the approved notebook and declared local phase-2 evidence."""

from __future__ import annotations

import json
from pathlib import Path

from check_official import phase2_compiler_receipts, phase2_resource_review
from check_phase2 import check_legacy_bytes

from mostaza.evaluation.contracts import canonical_json, require
from mostaza.evaluation.phase2 import (
    EVIDENCE,
    NOTEBOOK,
    build_notebook,
    comparison,
    readiness,
    report_markdown,
)
from mostaza.research.trace_diagnostics import check_diagnosis


def prepare(root: Path) -> None:
    evidence = root / EVIDENCE
    check_legacy_bytes(root)
    diagnosis = check_diagnosis(root, evidence / "trace-diagnosis.json")
    for name, actual in (
        ("resource-review.json", phase2_resource_review(root)),
        (
            "official-validation.json",
            phase2_compiler_receipts(root, root / ".tools/official/bin/python"),
        ),
    ):
        require(
            json.loads((evidence / name).read_text()) == actual,
            "Prior-stage evidence must match actual pinned inputs/compiler",
        )
    # A local preparation never erases real acquisition evidence.
    target = evidence / "readiness.json"
    if target.exists():
        old = json.loads(target.read_text())
        require(
            old.get("real_evaluation") == "NOT_RUN"
            and old.get("real_acquisition") is None,
            "Refusing to overwrite real or unrecognized acquisition evidence",
        )
    notebook = root / NOTEBOOK
    require(not notebook.is_symlink(), "Notebook symlink forbidden")
    notebook.parent.mkdir(parents=True, exist_ok=True)
    notebook.write_bytes(build_notebook(root))
    ready = readiness(root)
    compared = comparison(diagnosis)
    for name, data in (
        ("readiness.json", canonical_json(ready)),
        ("comparison.json", canonical_json(compared)),
        ("report.md", report_markdown(ready, compared).encode()),
    ):
        path = evidence / name
        require(not path.is_symlink(), "Evidence symlink forbidden")
        path.write_bytes(data)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    prepare(root)
    print(
        "Prepared private offline notebook; GPU disabled; "
        "phase-2 real evaluation NOT_RUN"
    )


if __name__ == "__main__":
    main()
