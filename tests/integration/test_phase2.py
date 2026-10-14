"""AC-7/AC-9/AC-10: authentic local readiness, compiler and tamper rejection."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from mostaza.evaluation.contracts import canonical_json
from mostaza.evaluation.phase2 import EVIDENCE, build_notebook, check_notebook

ROOT = Path(__file__).resolve().parents[2]


def checker():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "phase2_checker", ROOT / "scripts/check_phase2.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_ac10_actual_readonly_gate_compiles_all_variants_and_replays_evidence():
    paths = [
        ROOT / "notebooks/mostaza-phase2-budget-retrieval.ipynb",
        *sorted((ROOT / EVIDENCE).iterdir()),
    ]
    before = {p: p.read_bytes() for p in paths}
    ready = checker().verify(ROOT, ROOT / "experiments/cohort.json", ROOT / EVIDENCE)
    assert ready["real_evaluation"] == "NOT_RUN"
    assert ready["platform_enforcement"]["status"] == "BLOCKED"
    assert {p: p.read_bytes() for p in paths} == before


@pytest.mark.parametrize("field", ["real_evaluation", "records", "real_acquisition"])
def test_ac9_forged_real_evidence_rejected(tmp_path, monkeypatch, field):
    module = checker()
    # Earlier heavyweight authentic checks are independently covered above.
    # Here a copied declared artifact changes, with no product-tree mutation.
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    for source in (ROOT / EVIDENCE).iterdir():
        (evidence / source.name).write_bytes(source.read_bytes())
    ready = json.loads((evidence / "readiness.json").read_text())
    ready[field] = "fabricated-real-outcome"
    (evidence / "readiness.json").write_bytes(canonical_json(ready))
    monkeypatch.setattr(module, "check_legacy_bytes", lambda *_: None)
    monkeypatch.setattr(module, "check_real", lambda *_: None)
    monkeypatch.setattr(
        module,
        "check_diagnosis",
        lambda *_: json.loads((ROOT / EVIDENCE / "trace-diagnosis.json").read_text()),
    )
    monkeypatch.setattr(
        module,
        "phase2_resource_review",
        lambda *_: json.loads((ROOT / EVIDENCE / "resource-review.json").read_text()),
    )
    monkeypatch.setattr(
        module,
        "phase2_compiler_receipts",
        lambda *_: json.loads(
            (ROOT / EVIDENCE / "official-validation.json").read_text()
        ),
    )
    with pytest.raises(ValueError, match="Readiness differs"):
        module.verify(ROOT, ROOT / "experiments/cohort.json", evidence)


def test_ac10_notebook_tamper_rejected_without_executing_cells(monkeypatch):
    original = Path.read_bytes
    notebook = build_notebook(ROOT)
    forged = json.loads(notebook)
    forged["cells"][1]["source"] = ["ALLOW_GPU = True\n"]

    def read(path):
        if path == ROOT / "notebooks/mostaza-phase2-budget-retrieval.ipynb":
            return canonical_json(forged)
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", read)
    with pytest.raises(ValueError, match="provenance mismatch"):
        check_notebook(ROOT)
