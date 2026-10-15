"""Scope/source contract only; dedicated ninth gate runs native matrix once."""

import ast
import json
from pathlib import Path

import pytest

from mostaza.evaluation.verify_task_cpu import CASES, validate_pins

ROOT = Path(__file__).resolve().parents[2]


def test_cpu_driver_retains_direct_native_backend_and_pinned_inputs(
    historical_phase2_root,
):
    manifest = json.loads(
        (
            ROOT
            / "docs/implementation/evidence/mostaza-verify-task-cpu/prerequisites.json"
        ).read_text()
    )
    validate_pins(historical_phase2_root, manifest)
    with pytest.raises(
        ValueError,
        match=(
            r"Missing/changed immutable input: docs/specs/plans/closed/"
            r"mostaza-phase2-budget-retrieval\.md"
        ),
    ):
        validate_pins(ROOT, manifest)
    source = (ROOT / "scripts/verify_task_cpu_fixtures.py").read_text()
    tree = ast.parse(source)
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    assert any(
        isinstance(call.func, ast.Attribute) and call.func.attr == "verify_task"
        for call in calls
    )
    assert not any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
    assert "monkeypatch" not in source
    assert "mostaza/owned_cpu_fixture" in source
    assert len(CASES) == 11


def test_supervisor_tracks_native_detached_descendant_groups():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "cpu_supervisor", ROOT / "scripts/check_verify_task_cpu.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    known = {}
    # Child has its own session/group, as native execute_subprocess_command does.
    module.remember_descendants(
        100,
        {
            100: (1, 100, "owned worker"),
            101: (100, 101, "native command"),
            102: (101, 101, "native pytest"),
            200: (1, 200, "unrelated"),
        },
        known,
    )
    assert set(known) == {100, 101, 102}
    assert {row[1] for row in known.values()} == {100, 101}


def test_disk_meter_tolerates_native_cleanup_race(tmp_path, monkeypatch):
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "cpu_disk_meter", ROOT / "scripts/check_verify_task_cpu.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    disappearing = tmp_path / "native-temporary"
    disappearing.write_bytes(b"temporary")
    (tmp_path / "retained").write_bytes(b"keep")
    original = Path.lstat

    def delete_before_stat(path, *args, **kwargs):
        if path == disappearing:
            disappearing.unlink(missing_ok=True)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "lstat", delete_before_stat)
    assert module.used_bytes(tmp_path) == 4


def test_disk_meter_does_not_follow_links_or_hide_io_errors(tmp_path, monkeypatch):
    import importlib.util

    import pytest

    spec = importlib.util.spec_from_file_location(
        "cpu_disk_meter", ROOT / "scripts/check_verify_task_cpu.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    actual = tmp_path / "retained"
    actual.write_bytes(b"keep")
    (tmp_path / "alias").symlink_to(actual)
    assert module.used_bytes(tmp_path) == 4
    original = Path.lstat

    def denied(path, *args, **kwargs):
        if path == actual:
            raise PermissionError("owned failure injection")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "lstat", denied)
    with pytest.raises(PermissionError):
        module.used_bytes(tmp_path)
