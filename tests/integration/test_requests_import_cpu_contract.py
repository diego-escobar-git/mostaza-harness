"""Static integration and byte-identical own tests; no native matrix here."""

import importlib.util
import re
import sys
from pathlib import Path

import pytest

from mostaza.evaluation.requests_import_cpu import EVIDENCE, immutable_inputs

ROOT = Path(__file__).resolve().parents[2]


def load_script(name, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / (name + ".py")
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_frozen_native_and_vcpu01_inputs_and_exact_gate(
    monkeypatch, historical_phase2_root
):
    immutable_inputs(historical_phase2_root)
    with pytest.raises(
        ValueError,
        match=(
            r"Missing/changed immutable input: docs/specs/plans/closed/"
            r"mostaza-phase2-budget-retrieval\.md"
        ),
    ):
        immutable_inputs(ROOT)
    gate = load_script("run_requests_import_cpu_gate", monkeypatch)
    plan = (ROOT / EVIDENCE / "plan-for-approval.md").read_text()
    commands = re.search(r"```sh\n(.*?)```", plan, re.S).group(1).strip().splitlines()
    assert gate.COMMANDS == commands


def test_requests_test_bodies_preserved_and_have_no_stage_switch(tmp_path, monkeypatch):
    new = load_script("requests_import_cpu_fixtures", monkeypatch)
    old = load_script("verify_task_cpu_fixtures", monkeypatch)
    expected = {"pair": "R01", "package": "requests"}
    path = tmp_path / "pair-current.json"
    source = new.test_source(expected, path)
    old_source = old.diagnostic_source("R00", path, expected)
    assert (
        source[source.index("\ndef test_origin_binding():") :]
        == old_source[old_source.index("\ndef test_origin_binding():") :]
    )
    assert "-U" not in source and "-B" not in source
    assert "sys.path.insert" not in source
    assert "os.readlink" in source
    compile(source, "owned-test", "exec")


def test_outer_cleanup_only_removes_observed_owned_temporaries(tmp_path, monkeypatch):
    gate = load_script("run_requests_import_cpu_gate", monkeypatch)
    current = (
        tmp_path
        / "results/requests-import-cpu/matrix-00000000-0000-0000-0000-000000000001"
    )
    previous = current.with_name("matrix-00000000-0000-0000-0000-000000000002")
    legacy = tmp_path / "results/verify-task-cpu/00000000-0000-0000-0000-000000000003"
    for raw, case in [(current, "R00-B"), (previous, "R00-B"), (legacy, "V01")]:
        (raw / case / "fixture").mkdir(parents=True)
        (raw / case / "sandboxes").mkdir()
        (raw / case / "result.json").write_text("preserve evidence")
    known = {
        100: (
            1,
            100,
            (
                f"python {tmp_path}/scripts/requests_import_cpu_fixtures.py "
                f"--case R00-B --output {current}/R00-B"
            ),
        ),
        101: (
            1,
            101,
            (
                f"python {tmp_path}/scripts/verify_task_cpu_fixtures.py "
                f"--case V01 --output {legacy}/V01"
            ),
        ),
    }
    owned = gate.observed_roots(tmp_path, known)
    assert owned == {current, legacy}
    result = gate.cleanup_owned(tmp_path, owned)
    assert result["attempted"] and result["complete_for_observed_roots"]
    assert not (current / "R00-B/fixture").exists()
    assert not (legacy / "V01/sandboxes").exists()
    assert (previous / "R00-B/fixture").is_dir()
    assert (current / "R00-B/result.json").read_text() == "preserve evidence"


def test_outer_cleanup_rejects_outside_roots_and_preserves_link_targets(
    tmp_path, monkeypatch
):
    import pytest

    gate = load_script("run_requests_import_cpu_gate", monkeypatch)
    with pytest.raises(ValueError):
        gate.cleanup_owned(tmp_path, {tmp_path / "outside"})
    raw = (
        tmp_path
        / "results/requests-import-cpu/matrix-00000000-0000-0000-0000-000000000001"
    )
    (raw / "L01").mkdir(parents=True)
    outside = tmp_path / "user-directory"
    outside.mkdir()
    (outside / "keep").write_text("safe")
    (raw / "L01/fixture").symlink_to(outside, target_is_directory=True)
    assert gate.cleanup_owned(tmp_path, {raw})["complete_for_observed_roots"]
    assert (outside / "keep").read_text() == "safe"
