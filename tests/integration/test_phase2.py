"""AC-7/AC-9/AC-10: authentic local readiness, compiler and tamper rejection."""

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from mostaza.evaluation.contracts import canonical_json
from mostaza.evaluation.phase2 import (
    EVIDENCE,
    NOTEBOOK,
    build_notebook,
    check_notebook,
    operator_commands,
    readiness,
)

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


@pytest.mark.historical_evidence
def test_ac10_actual_recompute_rejects_historical_readiness_identity(
    historical_phase2_root,
    tmp_path,
):
    # search-code:AC-8 / phase-2 AC-10: original verification stays authentic;
    # active readiness remains bound to the current source and operator paths.
    root = historical_phase2_root
    frozen = json.loads((root / EVIDENCE / "readiness.json").read_text())
    paths = [
        base / name
        for base in (ROOT, root)
        for name in (
            frozen["notebook"]["path"],
            *frozen["source_sha256"],
        )
    ] + [
        ROOT / NOTEBOOK,
        *[path for base in (ROOT, root) for path in (base / EVIDENCE).iterdir()],
    ]
    before = {p: p.read_bytes() for p in paths}
    child = r"""
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

root = Path.cwd().resolve()
assert os.environ["PYTHONPATH"] == str(root / "src")
sys.path.insert(0, str(root / "scripts"))
import check_phase2
from mostaza.evaluation.contracts import canonical_json
from mostaza.evaluation.phase2 import EVIDENCE, operator_commands

assert Path(check_phase2.__file__).resolve() == root / "scripts/check_phase2.py"
evidence = root / EVIDENCE
ready = check_phase2.verify(root, root / "experiments/cohort.json", evidence)
assert ready["operator_commands"] == operator_commands(root)
for name, expected in ready["source_sha256"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected

# A real verifier run must reject current operator paths in historical evidence.
# Only the disposable copy changes; compiler/resource/trace checks run again.
tampered = Path(sys.argv[1])
tampered.mkdir()
for source in evidence.iterdir():
    shutil.copyfile(source, tampered / source.name)
forged = json.loads((tampered / "readiness.json").read_text())
forged["operator_commands"] = operator_commands(Path(sys.argv[2]))
assert forged["operator_commands"] != ready["operator_commands"]
(tampered / "readiness.json").write_bytes(canonical_json(forged))
try:
    check_phase2.verify(root, root / "experiments/cohort.json", tampered)
except ValueError as error:
    assert str(error) == (
        "Readiness differs from current notebook/config/source/NOT_RUN evidence"
    ), str(error)
else:
    raise AssertionError("Historical verifier accepted different operator paths")

bindings = {
    name: str(Path(module.__file__).resolve())
    for name, module in sys.modules.items()
    if (name == "mostaza" or name.startswith("mostaza."))
    and getattr(module, "__file__", None)
}
assert bindings
assert all(Path(path).is_relative_to(root / "src") for path in bindings.values())
print(json.dumps({
    "ready": ready, "bindings": bindings, "operator_tamper_rejected": True
}))
"""
    result = subprocess.run(
        [
            str(root / ".venv/bin/python"),
            "-c",
            child,
            str(tmp_path / "tampered-evidence"),
            str(ROOT),
        ],
        cwd=root,
        env={**os.environ, "PYTHONPATH": str(root / "src")},
        capture_output=True,
        text=True,
        timeout=240,
    )
    assert result.returncode == 0, (
        f"Historical phase-2 verifier exited {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    receipt = json.loads(result.stdout)
    assert receipt["ready"] == frozen
    assert receipt["operator_tamper_rejected"] is True
    for module in ("mostaza", "mostaza.packaging", "mostaza.evaluation.phase2"):
        relative = module.replace(".", "/")
        if module == "mostaza":
            relative += "/__init__"
        assert receipt["bindings"][module] == str(root / "src" / (relative + ".py"))

    assert Path(readiness.__code__.co_filename).resolve() == (
        ROOT / "src/mostaza/evaluation/phase2.py"
    )
    ready = readiness(ROOT)
    assert ready["operator_commands"] == operator_commands(ROOT)
    assert frozen["operator_commands"] == operator_commands(root)
    assert ready["operator_commands"] != frozen["operator_commands"]
    assert ready != frozen  # Current candidate cannot claim the historical receipt.
    assert (
        ready["source_sha256"]["src/mostaza/packaging.py"]
        != (frozen["source_sha256"]["src/mostaza/packaging.py"])
    )
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
        if path == ROOT / NOTEBOOK:
            return canonical_json(forged)
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", read)
    with pytest.raises(ValueError, match="provenance mismatch"):
        check_notebook(ROOT)
