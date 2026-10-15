"""Static integration contracts; no native verifier, agent loop or GPU execution."""

from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from mostaza.evaluation.notebook_import_candidate import (
    MODULE,
    NOTEBOOK,
    build_notebook,
    payload_of,
)
from mostaza.evaluation.notebook_import_cpu import candidate_contract

ROOT = Path(__file__).resolve().parents[2]


def load_script(name: str, monkeypatch: pytest.MonkeyPatch) -> Any:
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(
        name, ROOT / "scripts" / (name + ".py")
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_blocked_candidate_contract(historical_phase2_root: Path) -> None:
    # Positive historical admission never authorizes this combined checkout.
    assert candidate_contract(historical_phase2_root)["status"] == (
        "PASS_BLOCKED_NOTEBOOK_CONTRACT"
    )
    with pytest.raises(ValueError, match=r"Immutable file changed: README\.md"):
        candidate_contract(ROOT)


def test_current_notebook_rebuilds_from_unchanged_git_payload() -> None:
    committed = subprocess.check_output(
        ["git", "show", "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:" + NOTEBOOK],
        cwd=ROOT,
        timeout=10,
    )
    actual = (ROOT / NOTEBOOK).read_bytes()
    assert actual == committed == build_notebook(ROOT)
    notebook = json.loads(actual)
    assert notebook["metadata"]["kaggle"] == {
        "isGpuEnabled": False,
        "isInternetEnabled": False,
    }
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            assert cell["outputs"] == [] and cell["execution_count"] is None
            ast.parse("".join(cell["source"]), feature_version=(3, 12))
    for name, payload in payload_of(notebook).items():
        if name.endswith(".py"):
            ast.parse(payload.decode(), feature_version=(3, 12))
        if name == MODULE:
            source = subprocess.check_output(
                ["git", "show", "1b86b19f7654212c1d9f95eeca84d0e2a05db16b:" + name],
                cwd=ROOT,
                timeout=10,
            )
            assert payload == source == (ROOT / name).read_bytes()


def test_preflight_root_available_without_later_cell() -> None:
    notebook = json.loads((ROOT / NOTEBOOK).read_bytes())
    tree = ast.parse("".join(notebook["cells"][3]["source"]))
    view = next(
        n
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "LAYOUT_VIEW" for t in n.targets)
    )
    assert "STARTUP_OBSERVER.root" in ast.unparse(view)
    assert "RUN_ROOT" not in ast.unparse(view)


def test_gate_preserves_exact_regressions_and_new_budgets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    previous = load_script("run_requests_import_cpu_gate", monkeypatch)
    commands = gate.commands(1)
    assert commands[:10] == previous.COMMANDS
    assert len(commands) == 12
    assert "gate-1/matrix" in commands[10]
    assert "-I -S" in commands[11]
    assert gate.commands(2)[10:] == [
        c.replace("gate-1", "gate-2") for c in commands[10:]
    ]


def test_cleanup_refuses_unowned_or_symlink_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    sentinel = tmp_path / "user-file"
    sentinel.write_text("preserve")
    link = tmp_path / "link"
    link.symlink_to(tmp_path, target_is_directory=True)
    with pytest.raises(ValueError, match="unowned"):
        gate.cleanup_scratch(link, {"token": "bad"})
    assert sentinel.read_text() == "preserve"


def test_native_agent_prefix_and_tuple_forwarding_are_pinned() -> None:
    prefix = ROOT / ".tools/official/lib/python3.13/site-packages/swegemma"
    # Source-only compatibility evidence, not execution of the agent loop.
    agent = (prefix / "harness/agent_runner.py").read_text()
    evaluator = (prefix / "evaluate.py").read_text()
    assert "base_snapshot_path=base_snapshot_path" in agent
    assert "patch_path=patch_path" in agent
    assert agent.index("            extract_snapshot,") < agent.index(
        "setup_baseline_commit, docker, sandbox_id"
    )
    assert "run_kwargs['base_snapshot_path'] = base_snapshot_path" in evaluator
    assert "run_kwargs['patch_path'] = patch_path" in evaluator
    assert "verify_kwargs['base_snapshot_path'] = base_snapshot_path" in evaluator
    assert "verify_kwargs['patch_path'] = patch_path" in evaluator


def test_stop_group_verifies_exit_after_signal_permission_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import os
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)

    class Process:
        pid = 111

        def poll(self) -> int:
            return 0

        def wait(self, timeout: int) -> int:
            return 0

    tables = iter([{222: (111, 111, "/bin/ps -ww -axo pid=")}, {}, {}, {}])
    watchdog = types.SimpleNamespace(
        process_table=lambda: next(tables),
        remember_descendants=lambda pid, table, known: known.update(table),
    )

    def denied(group: int, sig: int) -> None:
        raise PermissionError("simulated transient group permission")

    monkeypatch.setattr(os, "killpg", denied)
    receipt = helper.stop_group(
        Process(), {222: (111, 111, "/bin/ps -ww -axo pid=")}, watchdog
    )
    assert receipt["complete"] is True
    assert len(receipt["signal_errors"]) == 1
    assert not receipt["survivors"]


def test_stop_group_never_suppresses_live_owned_survivor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import os
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)

    class Process:
        pid = 111

        def poll(self) -> int:
            return 0

        def wait(self, timeout: int) -> int:
            return 0

    watchdog = types.SimpleNamespace(
        process_table=lambda: {222: (111, 111, "owned-worker")},
        remember_descendants=lambda pid, table, known: known.update(table),
    )

    def denied(group: int, sig: int) -> None:
        raise PermissionError("simulated live worker")

    monkeypatch.setattr(os, "killpg", denied)
    moments = iter([0.0, 3.0])
    monkeypatch.setattr(helper.time, "monotonic", lambda: next(moments))
    with pytest.raises(PermissionError, match="cleanup incomplete"):
        helper.stop_group(Process(), {222: (111, 111, "owned-worker")}, watchdog)


def test_stop_group_does_not_signal_reused_pid(monkeypatch: pytest.MonkeyPatch) -> None:
    import os
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)

    class Process:
        pid = 111

        def poll(self) -> int:
            return 0

        def wait(self, timeout: int) -> int:
            return 0

    signals = []
    watchdog = types.SimpleNamespace(
        process_table=lambda: {222: (1, 999, "unrelated-process")},
        remember_descendants=lambda *args: pytest.fail("Rediscovered a dead root"),
    )
    monkeypatch.setattr(os, "killpg", lambda group, sig: signals.append((group, sig)))
    result = helper.stop_group(Process(), {222: (111, 111, "owned-worker")}, watchdog)
    assert result["complete"] is True
    assert signals == []


def test_stop_group_does_not_rediscover_a_finished_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)

    class Process:
        pid = 111

        def poll(self) -> int:
            return 0

        def wait(self, timeout: int) -> int:
            return 0

    watchdog = types.SimpleNamespace(
        process_table=lambda: {},
        remember_descendants=lambda *args: pytest.fail("Rediscovered a dead root"),
    )
    assert helper.stop_group(Process(), {}, watchdog)["complete"]


def test_gate_requires_complete_real_count_records(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    output = tmp_path / "gate"
    legacy = set()
    for name, number in (("verify-task-cpu", 11), ("requests-import-cpu", 9)):
        raw = tmp_path / name / "owned-run"
        raw.mkdir(parents=True)
        legacy.add(raw)
        (raw / "summary.json").write_text(
            json.dumps(
                {
                    "failure": None,
                    "invocations_started": number,
                    "invocations_assessed": number,
                }
            )
        )
        for index in range(number):
            case = raw / str(index)
            case.mkdir()
            (case / "result.json").write_text("{}")
            if name == "requests-import-cpu":
                (case / "native-started.json").write_text("{}")
    for index in range(6):
        case = output / "matrix" / str(index)
        case.mkdir(parents=True)
        for name in (
            "native-started",
            "native-completed",
            "assessed",
            "setup-started",
            "setup-completed",
        ):
            (case / (name + ".json")).write_text("{}")
    portable = output / "portability"
    portable.mkdir()
    for index in range(2):
        for name in ("started", "completed", "assessed"):
            (portable / f"{index}-{name}.json").write_text("{}")
    counts = gate.actual_counts(output, legacy)
    assert gate.counts_satisfy_gate(counts)
    assert counts["native_total"]["assessed_reason"] is None
    (output / "matrix/0/native-completed.json").unlink()
    assert not gate.counts_satisfy_gate(gate.actual_counts(output, legacy))


def test_gate_routes_host_temporary_files_into_owned_scratch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import tempfile

    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    scratch = tmp_path / "owned"
    scratch.mkdir()
    env = gate.execution_environment(scratch, 1234.5)
    assert env["MOSTAZA_NOTEBOOK_IMPORT_SCRATCH"] == str(scratch)
    assert env["MOSTAZA_CPU_DEADLINE"] == "1234.5"
    assert Path(env["TMPDIR"]) == scratch / "host-tmp"
    monkeypatch.setenv("TMPDIR", env["TMPDIR"])
    monkeypatch.setattr(tempfile, "tempdir", None)
    with tempfile.TemporaryDirectory() as directory:
        assert Path(directory).is_relative_to(scratch)
    assert not list((scratch / "host-tmp").iterdir())


def admission_fixture(tmp_path: Path, gate: Any) -> tuple[Path, dict[str, Any]]:
    import hashlib

    evidence = tmp_path / gate.EVIDENCE
    evidence.mkdir(parents=True)
    proposal = evidence / "additional-gate-plan.md"
    repair = evidence / "post-gate-repair.json"
    proposal.write_text("Owned proposal")
    repair.write_text("Owned repair")
    pins = []
    for number in (1, 2):
        relative = f"results/notebook-import-cpu/gate-{number}/receipt.json"
        path = tmp_path / relative
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps(
                {
                    "attempt": number,
                    "maximum_attempts": 2,
                    "passed": False,
                }
            )
        )
        pins.append(
            {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        )
    approval = {
        "status": "APPROVED",
        "proposal_sha256": hashlib.sha256(proposal.read_bytes()).hexdigest(),
        "repair_sha256": hashlib.sha256(repair.read_bytes()).hexdigest(),
        "prior_receipts": pins,
        "limits": {
            "attempt": 3,
            "maximum_additional_attempts": 1,
            "native_verifications": 26,
            "setup_probes": 6,
            "stdlib_probes": 2,
            "wall_seconds": 1200,
            "artifact_bytes": 1024**3,
            "automatic_retries": False,
        },
    }
    path = evidence / "additional-gate-approval.json"
    path.write_text(json.dumps(approval))
    return path, approval


def test_extra_gate_requires_explicit_matching_approval(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    path, approval = admission_fixture(tmp_path, gate)
    assert gate.additional_admission(tmp_path, 3)["attempt"] == 3
    approval["status"] = "PROPOSED"
    path.write_text(json.dumps(approval))
    with pytest.raises(ValueError, match="approval"):
        gate.additional_admission(tmp_path, 3)


@pytest.mark.parametrize(
    "tamper", ("limits", "proposal", "repair", "receipt", "missing")
)
def test_extra_gate_cannot_reset_or_expand_consumed_allowance(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tamper: str
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    path, approval = admission_fixture(tmp_path, gate)
    if tamper == "limits":
        approval["limits"]["maximum_additional_attempts"] = 2
        path.write_text(json.dumps(approval))
    elif tamper == "proposal":
        (path.parent / "additional-gate-plan.md").write_text("Changed")
    elif tamper == "repair":
        (path.parent / "post-gate-repair.json").write_text("Changed")
    elif tamper == "receipt":
        (tmp_path / approval["prior_receipts"][0]["path"]).write_text("{}")
    else:
        path.unlink()
    with pytest.raises((ValueError, FileNotFoundError)):
        gate.additional_admission(tmp_path, 3)


def test_ordinary_allowance_is_not_reopened(monkeypatch: pytest.MonkeyPatch) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    assert gate.additional_admission(Path("/unused"), 1) is None
    assert gate.additional_admission(Path("/unused"), 2) is None
    with pytest.raises(ValueError, match="Unapproved"):
        gate.additional_admission(Path("/unused"), 7)


def test_host_retention_configuration_is_confined_to_command_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    base = {"TMPDIR": "/owned/tmp", "PATH": "/bin"}
    original = dict(base)
    assert gate.host_test_environment(base, 1)["PYTEST_ADDOPTS"] == (
        "-o tmp_path_retention_policy=failed"
    )
    for index in range(2, 13):
        assert gate.host_test_environment(base, index) == original
    assert base == original


def test_host_retention_rejects_unreviewed_existing_options(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    with pytest.raises(ValueError, match="existing host pytest"):
        gate.host_test_environment({"PYTEST_ADDOPTS": "-k selected"}, 1)


@pytest.mark.parametrize("passing", (True, False))
def test_official_pytest_retention_cleans_passed_and_preserves_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, passing: bool
) -> None:
    import os
    import subprocess
    import sys

    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    source = tmp_path / "test_owned_retention.py"
    source.write_text(
        "def test_owned(tmp_path):\n"
        "    (tmp_path / 'probe.txt').write_text('small owned fixture')\n"
        f"    assert {passing!r}\n"
    )
    env = gate.host_test_environment(
        {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}, 1
    )
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    base = tmp_path / "pytest-base"
    run = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "-c",
            "/dev/null",
            "--basetemp",
            str(base),
            str(source),
        ],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert run.returncode == (0 if passing else 1), run.stdout + run.stderr
    retained = [
        p for p in base.glob("test_owned*/probe.txt") if not p.parent.is_symlink()
    ]
    assert len(retained) == (0 if passing else 1)


def resource_admission_fixture(
    tmp_path: Path, gate: Any
) -> tuple[Path, dict[str, Any]]:
    import hashlib

    evidence = tmp_path / gate.EVIDENCE
    evidence.mkdir(parents=True)
    for name in ("resource-gate-plan.md", "resource-repair.json"):
        (evidence / name).write_text("Owned fourth attempt proposal")
    pins = []
    for number in (1, 2, 3):
        relative = f"results/notebook-import-cpu/gate-{number}/receipt.json"
        path = tmp_path / relative
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps(
                {
                    "attempt": number,
                    "maximum_attempts": 3 if number == 3 else 2,
                    "passed": False,
                }
            )
        )
        pins.append(
            {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        )
    approval = {
        "status": "APPROVED",
        "proposal_sha256": hashlib.sha256(
            (evidence / "resource-gate-plan.md").read_bytes()
        ).hexdigest(),
        "repair_sha256": hashlib.sha256(
            (evidence / "resource-repair.json").read_bytes()
        ).hexdigest(),
        "prior_receipts": pins,
        "limits": {
            "attempt": 4,
            "maximum_additional_attempts": 1,
            "native_verifications": 26,
            "setup_probes": 6,
            "stdlib_probes": 2,
            "wall_seconds": 1200,
            "artifact_bytes": 1024**3,
            "automatic_retries": False,
        },
    }
    path = evidence / "resource-gate-approval.json"
    path.write_text(json.dumps(approval))
    return path, approval


def test_fourth_gate_admission_pins_three_consumed_attempts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    resource_admission_fixture(tmp_path, gate)
    admitted = gate.additional_admission(tmp_path, 4)
    assert admitted["attempt"] == 4
    assert len(admitted["prior_receipts"]) == 3
    assert not (tmp_path / "results/notebook-import-cpu/gate-4").exists()


@pytest.mark.parametrize(
    "tamper", ("limits", "proposal", "repair", "receipt", "missing", "count")
)
def test_fourth_gate_rejects_missing_or_changed_authorization(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    tamper: str,
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    path, approval = resource_admission_fixture(tmp_path, gate)
    if tamper == "limits":
        approval["limits"]["artifact_bytes"] *= 2
        path.write_text(json.dumps(approval))
    elif tamper == "proposal":
        (path.parent / "resource-gate-plan.md").write_text("Changed")
    elif tamper == "repair":
        (path.parent / "resource-repair.json").write_text("Changed")
    elif tamper == "receipt":
        (tmp_path / approval["prior_receipts"][2]["path"]).write_text("{}")
    elif tamper == "count":
        approval["prior_receipts"].pop()
        path.write_text(json.dumps(approval))
    else:
        path.unlink()
    with pytest.raises((ValueError, FileNotFoundError)):
        gate.additional_admission(tmp_path, 4)


def test_outer_controller_wires_retention_only_for_approved_resource_gates() -> None:
    tree = ast.parse((ROOT / "scripts/run_notebook_import_cpu_gate.py").read_text())
    run = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "run"
    )
    assignment = next(
        node
        for node in ast.walk(run)
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "command_env" for t in node.targets)
    )
    assert (
        ast.unparse(assignment.value)
        == "host_test_environment(env, index) if attempt in (4, 5, 6) else dict(env)"
    )
    popen = next(
        node
        for node in ast.walk(run)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "Popen"
    )
    assert (
        next(ast.unparse(k.value) for k in popen.keywords if k.arg == "env")
        == "command_env"
    )


def source_filter_admission_fixture(
    tmp_path: Path, gate: Any
) -> tuple[Path, dict[str, Any]]:
    import hashlib

    evidence = tmp_path / gate.EVIDENCE
    evidence.mkdir(parents=True)
    for name in ("source-filter-gate-plan.md", "gate4-source-diagnosis.json"):
        (evidence / name).write_text("Owned fifth attempt proposal")
    pins = []
    for number in (1, 2, 3, 4):
        relative = f"results/notebook-import-cpu/gate-{number}/receipt.json"
        path = tmp_path / relative
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps(
                {
                    "attempt": number,
                    "maximum_attempts": number if number >= 3 else 2,
                    "passed": False,
                }
            )
        )
        pins.append(
            {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        )
    approval = {
        "status": "APPROVED",
        "proposal_sha256": hashlib.sha256(
            (evidence / "source-filter-gate-plan.md").read_bytes()
        ).hexdigest(),
        "repair_sha256": hashlib.sha256(
            (evidence / "gate4-source-diagnosis.json").read_bytes()
        ).hexdigest(),
        "prior_receipts": pins,
        "limits": {
            "attempt": 5,
            "maximum_additional_attempts": 1,
            "native_verifications": 26,
            "setup_probes": 6,
            "stdlib_probes": 2,
            "wall_seconds": 1200,
            "artifact_bytes": 1024**3,
            "automatic_retries": False,
        },
    }
    path = evidence / "source-filter-gate-approval.json"
    path.write_text(json.dumps(approval))
    return path, approval


def test_fifth_gate_admission_pins_four_consumed_attempts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    source_filter_admission_fixture(tmp_path, gate)
    admitted = gate.additional_admission(tmp_path, 5)
    assert admitted["attempt"] == 5
    assert len(admitted["prior_receipts"]) == 4
    assert not (tmp_path / "results/notebook-import-cpu/gate-5").exists()


@pytest.mark.parametrize(
    "tamper", ("limits", "proposal", "repair", "receipt", "missing", "count")
)
def test_fifth_gate_rejects_missing_or_changed_authorization(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    tamper: str,
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    path, approval = source_filter_admission_fixture(tmp_path, gate)
    if tamper == "limits":
        approval["limits"]["artifact_bytes"] *= 2
        path.write_text(json.dumps(approval))
    elif tamper == "proposal":
        (path.parent / "source-filter-gate-plan.md").write_text("Changed")
    elif tamper == "repair":
        (path.parent / "gate4-source-diagnosis.json").write_text("Changed")
    elif tamper == "receipt":
        (tmp_path / approval["prior_receipts"][3]["path"]).write_text("{}")
    elif tamper == "count":
        approval["prior_receipts"].pop()
        path.write_text(json.dumps(approval))
    else:
        path.unlink()
    with pytest.raises((ValueError, FileNotFoundError)):
        gate.additional_admission(tmp_path, 5)


def test_prepared_process_observer_binds_timeout_to_shared_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)
    calls = []
    moments = iter([10.0, 10.1, 10.2])
    monkeypatch.setattr(helper.time, "monotonic", lambda: next(moments))

    def read(argv: list[str], **kwargs: Any) -> Any:
        calls.append((argv, kwargs))
        return types.SimpleNamespace(stdout="111 1 111 owned worker with spaces\n")

    monkeypatch.setattr(helper.subprocess, "run", read)
    evidence: list[dict[str, Any]] = []
    assert helper.read_process_table(11.25, evidence) == {
        111: (1, 111, "owned worker with spaces")
    }
    assert calls[0][0][0] == "/bin/ps"
    assert calls[0][1]["timeout"] == 1.25
    assert evidence[0]["process_count"] == 1
    assert evidence[0]["table_available"] is True


def test_prepared_process_observer_does_not_retry_or_infer_exit_on_timeout(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import subprocess

    helper = load_script("notebook_import_supervision", monkeypatch)
    calls = []
    monkeypatch.setattr(helper.time, "monotonic", lambda: 10.0)

    def slow(argv: list[str], **kwargs: Any) -> Any:
        calls.append(kwargs)
        raise subprocess.TimeoutExpired(argv, kwargs["timeout"])

    monkeypatch.setattr(helper.subprocess, "run", slow)
    evidence: list[dict[str, Any]] = []
    with pytest.raises(subprocess.TimeoutExpired):
        helper.read_process_table(100.0, evidence)
    assert len(calls) == 1 and calls[0]["timeout"] == 5.0
    assert evidence[0]["table_available"] is False
    assert evidence[0]["process_count"] is None
    assert evidence[0]["process_count_reason"]


@pytest.mark.parametrize(
    "output",
    ("", "bad line", "111 1 111 worker\n111 1 111 duplicate", "111 -1 111 worker"),
)
def test_prepared_process_observer_rejects_unavailable_or_malformed_tables(
    monkeypatch: pytest.MonkeyPatch,
    output: str,
) -> None:
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)
    monkeypatch.setattr(helper.time, "monotonic", lambda: 10.0)
    monkeypatch.setattr(
        helper.subprocess,
        "run",
        lambda *args, **kwargs: types.SimpleNamespace(stdout=output),
    )
    evidence: list[dict[str, Any]] = []
    with pytest.raises(ValueError):
        helper.read_process_table(20.0, evidence)
    assert evidence[0]["table_available"] is False
    assert evidence[0]["process_count"] is None


def test_prepared_process_observer_never_dispatches_after_deadline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    helper = load_script("notebook_import_supervision", monkeypatch)
    monkeypatch.setattr(helper.time, "monotonic", lambda: 10.0)
    monkeypatch.setattr(
        helper.subprocess, "run", lambda *args, **kwargs: pytest.fail("Late dispatch")
    )
    with pytest.raises(TimeoutError, match="No process observation budget"):
        helper.read_process_table(9.0, [])


def test_prepared_process_observer_rejects_a_late_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)
    moments = iter([10.0, 12.0, 12.1])
    monkeypatch.setattr(helper.time, "monotonic", lambda: next(moments))
    monkeypatch.setattr(
        helper.subprocess,
        "run",
        lambda *args, **kwargs: types.SimpleNamespace(stdout="111 1 111 worker"),
    )
    evidence: list[dict[str, Any]] = []
    with pytest.raises(TimeoutError, match="exceeded its shared deadline"):
        helper.read_process_table(11.0, evidence)
    assert evidence[0]["table_available"] is False
    assert evidence[0]["process_count"] is None


def test_prepared_cleanup_still_signals_owned_root_when_observation_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import os
    import subprocess
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)

    class Process:
        pid = 111
        done = False

        def poll(self) -> int | None:
            return 0 if self.done else None

        def wait(self, timeout: float) -> int:
            assert timeout <= 5.0
            self.done = True
            return 0

    def unavailable(deadline: float, measurements: Any) -> Any:
        raise subprocess.TimeoutExpired("owned ps", 5.0)

    signals = []
    monkeypatch.setattr(helper, "read_process_table", unavailable)
    monkeypatch.setattr(helper.time, "monotonic", lambda: 10.0)
    monkeypatch.setattr(os, "killpg", lambda group, sig: signals.append((group, sig)))
    watchdog = types.SimpleNamespace(remember_descendants=lambda *args: None)
    with pytest.raises(helper.CleanupIncomplete) as caught:
        helper.stop_group_bounded(
            Process(), {222: (111, 222, "stale child")}, watchdog, 20.0, []
        )
    assert signals and signals[0][0] == 111
    assert all(group != 222 for group, _ in signals)
    assert caught.value.receipt["complete"] is False
    assert caught.value.receipt["survivors"] is None
    assert caught.value.receipt["root_exited"] is True


def test_prepared_cleanup_waits_within_total_deadline_and_preserves_pid_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import os
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)
    waits = []

    class Process:
        pid = 111

        def poll(self) -> int:
            return 0

        def wait(self, timeout: float) -> int:
            waits.append(timeout)
            return 0

    monkeypatch.setattr(helper.time, "monotonic", lambda: 10.0)
    monkeypatch.setattr(
        helper, "read_process_table", lambda *args: {222: (1, 999, "unrelated")}
    )
    monkeypatch.setattr(
        os, "killpg", lambda *args: pytest.fail("Unrelated group signaled")
    )
    watchdog = types.SimpleNamespace(
        remember_descendants=lambda *args: pytest.fail("Reused PID rediscovered")
    )
    result = helper.stop_group_bounded(
        Process(), {222: (111, 222, "old child")}, watchdog, 10.5, []
    )
    assert result["complete"] is True
    assert waits == [0.5, 0.5]


def test_prepared_cleanup_never_accepts_persistent_owned_survivor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import os
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)

    class Process:
        pid = 111

        def poll(self) -> int:
            return 0

        def wait(self, timeout: float) -> int:
            return 0

    monkeypatch.setattr(helper.time, "monotonic", lambda: 10.0)
    monkeypatch.setattr(
        helper, "read_process_table", lambda *args: {222: (111, 222, "owned child")}
    )
    monkeypatch.setattr(os, "killpg", lambda *args: None)
    watchdog = types.SimpleNamespace(remember_descendants=lambda *args: None)
    with pytest.raises(helper.CleanupIncomplete) as caught:
        helper.stop_group_bounded(
            Process(), {222: (111, 222, "owned child")}, watchdog, 10.0, []
        )
    assert caught.value.receipt["survivors"] == [222]
    assert caught.value.receipt["complete"] is False


def test_prepared_observer_accepts_kernel_rows_without_treating_them_as_owned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)
    monkeypatch.setattr(helper.time, "monotonic", lambda: 10.0)
    monkeypatch.setattr(
        helper.subprocess,
        "run",
        lambda *args, **kwargs: types.SimpleNamespace(
            stdout="0 0 0 kernel_task\n1 0 1 launchd\n111 1 111 owned"
        ),
    )
    result = helper.read_process_table(20.0, [])
    assert result[0] == (0, 0, "kernel_task")
    assert helper.survivors(result, {111: (1, 111, "owned")}) == {
        111: (1, 111, "owned")
    }


def test_prepared_cleanup_never_signals_group_zero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import os
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)

    class Process:
        pid = 111

        def poll(self) -> int:
            return 0

        def wait(self, timeout: float) -> int:
            return 0

    monkeypatch.setattr(helper.time, "monotonic", lambda: 10.0)
    monkeypatch.setattr(
        helper,
        "read_process_table",
        lambda *args: {222: (111, 0, "anomalous owned child")},
    )
    monkeypatch.setattr(os, "killpg", lambda *args: pytest.fail("Group zero signaled"))
    watchdog = types.SimpleNamespace(remember_descendants=lambda *args: None)
    with pytest.raises(helper.CleanupIncomplete):
        helper.stop_group_bounded(
            Process(), {222: (111, 0, "anomalous owned child")}, watchdog, 10.0, []
        )


def test_prepared_cleanup_terminates_own_benign_process_if_ps_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import os
    import signal
    import subprocess
    import sys
    import time
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)
    process = subprocess.Popen(
        [sys.executable, "-I", "-c", "import time; time.sleep(30)"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    def unavailable(*args: Any) -> Any:
        raise subprocess.TimeoutExpired("owned observation fixture", 5.0)

    monkeypatch.setattr(helper, "read_process_table", unavailable)
    watchdog = types.SimpleNamespace(remember_descendants=lambda *args: None)
    try:
        with pytest.raises(helper.CleanupIncomplete) as caught:
            helper.stop_group_bounded(
                process, {}, watchdog, time.monotonic() + 10.0, []
            )
        assert process.poll() is not None
        assert caught.value.receipt["root_exited"] is True
        assert caught.value.receipt["complete"] is False
        assert caught.value.receipt["survivors"] is None
    finally:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=5)


def supervision_admission_fixture(
    tmp_path: Path, gate: Any
) -> tuple[Path, dict[str, Any]]:
    import hashlib

    evidence = tmp_path / gate.EVIDENCE
    evidence.mkdir(parents=True)
    for name in ("supervision-gate-plan.md", "supervision-repair.json"):
        (evidence / name).write_text("Owned sixth attempt proposal")
    pins = []
    for number in (1, 2, 3, 4, 5):
        relative = f"results/notebook-import-cpu/gate-{number}/receipt.json"
        path = tmp_path / relative
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps(
                {
                    "attempt": number,
                    "maximum_attempts": number if number >= 3 else 2,
                    "passed": False,
                }
            )
        )
        pins.append(
            {"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        )
    approval = {
        "status": "APPROVED",
        "proposal_sha256": hashlib.sha256(
            (evidence / "supervision-gate-plan.md").read_bytes()
        ).hexdigest(),
        "repair_sha256": hashlib.sha256(
            (evidence / "supervision-repair.json").read_bytes()
        ).hexdigest(),
        "prior_receipts": pins,
        "limits": {
            "attempt": 6,
            "maximum_additional_attempts": 1,
            "native_verifications": 26,
            "setup_probes": 6,
            "stdlib_probes": 2,
            "wall_seconds": 1200,
            "artifact_bytes": 1024**3,
            "automatic_retries": False,
        },
    }
    path = evidence / "supervision-gate-approval.json"
    path.write_text(json.dumps(approval))
    return path, approval


def test_sixth_gate_admission_pins_five_consumed_attempts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    supervision_admission_fixture(tmp_path, gate)
    admitted = gate.additional_admission(tmp_path, 6)
    assert admitted["attempt"] == 6
    assert len(admitted["prior_receipts"]) == 5
    assert not (tmp_path / "results/notebook-import-cpu/gate-6").exists()


@pytest.mark.parametrize(
    "tamper", ("limits", "proposal", "repair", "receipt", "missing", "count")
)
def test_sixth_gate_rejects_missing_or_changed_authorization(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    tamper: str,
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    path, approval = supervision_admission_fixture(tmp_path, gate)
    if tamper == "limits":
        approval["limits"]["artifact_bytes"] *= 2
        path.write_text(json.dumps(approval))
    elif tamper == "proposal":
        (path.parent / "supervision-gate-plan.md").write_text("Changed")
    elif tamper == "repair":
        (path.parent / "supervision-repair.json").write_text("Changed")
    elif tamper == "receipt":
        (tmp_path / approval["prior_receipts"][4]["path"]).write_text("{}")
    elif tamper == "count":
        approval["prior_receipts"].pop()
        path.write_text(json.dumps(approval))
    else:
        path.unlink()
    with pytest.raises((ValueError, FileNotFoundError)):
        gate.additional_admission(tmp_path, 6)


def test_supervision_throttles_discovery_but_keeps_cap_checks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)
    clock = [0.0]
    reads = []
    checks = []
    monkeypatch.setattr(helper.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        helper.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds)
    )

    class Process:
        pid = 111

        def poll(self) -> int | None:
            return 0 if clock[0] >= 1.2 else None

    def read(deadline: float, measurements: Any) -> Any:
        reads.append(clock[0])
        return {111: (1, 111, "owned")}

    monkeypatch.setattr(helper, "read_process_table", read)
    monkeypatch.setattr(helper, "stop_group_bounded", lambda *args: {"complete": True})
    watchdog = types.SimpleNamespace(remember_descendants=lambda *args: None)
    result = helper.supervise(
        Process(),
        {},
        watchdog,
        10.0,
        40.0,
        lambda: checks.append(clock[0]),
        tmp_path / "receipt.json",
    )
    assert reads == [0.0, 1.0]
    assert len(checks) == 6
    assert result["status"] == "COMPLETE"


def test_supervision_persists_both_work_and_cleanup_errors(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)

    class Process:
        pid = 111

        def poll(self) -> None:
            return None

    monkeypatch.setattr(
        helper, "read_process_table", lambda *args: {111: (1, 111, "owned")}
    )

    def broken_work() -> None:
        raise ValueError("work evidence")

    def broken_cleanup(*args: Any) -> Any:
        raise helper.CleanupIncomplete(
            {"complete": False, "survivors": None, "survivors_reason": "unknown"}
        )

    monkeypatch.setattr(helper, "stop_group_bounded", broken_cleanup)
    path = tmp_path / "receipt.json"
    watchdog = types.SimpleNamespace(remember_descendants=lambda *args: None)
    import time

    with pytest.raises(helper.SupervisionFailure):
        helper.supervise(
            Process(),
            {},
            watchdog,
            time.monotonic() + 10,
            time.monotonic() + 40,
            broken_work,
            path,
        )
    saved = json.loads(path.read_text())
    assert "work evidence" in saved["work_error"]
    assert "CleanupIncomplete" in saved["cleanup_error"]
    assert saved["process_cleanup"]["survivors"] is None
    assert saved["status"] == "FAILED"


def test_supervision_uses_total_cleanup_budget_after_work_deadline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)

    class Process:
        pid = 111

        def poll(self) -> None:
            return None

    monkeypatch.setattr(helper.time, "monotonic", lambda: 1171.0)
    calls = []

    def cleanup(
        process: Any, known: Any, watchdog: Any, deadline: float, observations: Any
    ) -> Any:
        calls.append(deadline)
        return {"complete": True}

    monkeypatch.setattr(helper, "stop_group_bounded", cleanup)
    watchdog = types.SimpleNamespace(remember_descendants=lambda *args: None)
    with pytest.raises(helper.SupervisionFailure):
        helper.supervise(
            Process(),
            {},
            watchdog,
            1170.0,
            1200.0,
            lambda: pytest.fail("Late work"),
            tmp_path / "receipt.json",
        )
    assert calls == [1200.0]


def test_attempt6_outer_and_inner_wiring_preserves_cleanup_reserves() -> None:
    outer = (ROOT / "scripts/run_notebook_import_cpu_gate.py").read_text()
    inner = (ROOT / "scripts/check_notebook_import_cpu.py").read_text()
    assert "started + 1170" in outer and "started + 1200" in outer
    assert 'active["supervision"] = error.receipt' in outer
    assert 'active.get("process_cleanup")' in outer
    assert 'bounded = output.parent.name == "gate-6"' in inner
    assert "min(deadline, case_deadline - 30)" in inner
    assert "case_started + 90" in inner


@pytest.mark.parametrize("always_fail", (False, True))
def test_supervision_cleans_owned_root_when_initial_receipt_write_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    always_fail: bool,
) -> None:
    import time
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)

    class Process:
        pid = 111
        done = False

        def poll(self) -> int | None:
            return 0 if self.done else None

    process = Process()
    calls = []
    path = tmp_path / "receipt.json"
    original_write = Path.write_text
    writes = []

    def write(target: Path, contents: str, *args: Any, **kwargs: Any) -> int:
        if target == path:
            writes.append(True)
            if always_fail or len(writes) == 1:
                raise OSError("initial receipt I/O failure")
        return original_write(target, contents, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", write)

    def cleanup(*args: Any) -> Any:
        process.done = True
        calls.append(True)
        return {"complete": True, "root_exited": True}

    monkeypatch.setattr(helper, "stop_group_bounded", cleanup)
    watchdog = types.SimpleNamespace(remember_descendants=lambda *args: None)
    with pytest.raises(helper.SupervisionFailure) as caught:
        helper.supervise(
            process,
            {},
            watchdog,
            time.monotonic() + 10,
            time.monotonic() + 40,
            lambda: pytest.fail("Work started after persistence failure"),
            path,
        )
    receipt = caught.value.receipt
    assert calls == [True] and process.poll() == 0
    assert "initial receipt I/O failure" in receipt["work_error"]
    assert receipt["persistence_errors"] and receipt["status"] == "FAILED"
    if not always_fail:
        assert json.loads(path.read_text())["process_cleanup"]["root_exited"] is True


def test_supervision_never_rediscovers_root_reused_during_ps(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import os
    import time
    import types

    helper = load_script("notebook_import_supervision", monkeypatch)

    class Process:
        pid = 111
        done = False

        def poll(self) -> int | None:
            return 0 if self.done else None

        def wait(self, timeout: float) -> int:
            return 0

    process = Process()

    def read(*args: Any) -> Any:
        process.done = True
        return {111: (1, 999, "unrelated reused PID")}

    monkeypatch.setattr(helper, "read_process_table", read)
    monkeypatch.setattr(helper.time, "sleep", lambda *args: None)
    monkeypatch.setattr(
        os, "killpg", lambda *args: pytest.fail("Unrelated process signaled")
    )
    watchdog = types.SimpleNamespace(
        remember_descendants=lambda *args: pytest.fail("Reused root rediscovered")
    )
    known: dict[int, tuple[int, int, str]] = {}
    result = helper.supervise(
        process,
        known,
        watchdog,
        time.monotonic() + 10,
        time.monotonic() + 40,
        lambda: None,
        tmp_path / "receipt.json",
    )
    assert result["status"] == "COMPLETE" and not known


@pytest.mark.parametrize("late_stage", ("assessment", "fixture_cleanup", "export"))
def test_row_acceptance_includes_assessment_cleanup_and_export_deadline(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    late_stage: str,
) -> None:
    matrix = load_script("check_notebook_import_cpu", monkeypatch)
    clock = [0.0]
    home = tmp_path / "owned-home"
    home.mkdir()
    output = tmp_path / "row"
    output.mkdir()

    def assess(*args: Any) -> Any:
        if late_stage == "assessment":
            clock[0] = 91.0
        return {"id": "own"}

    def cleanup(path: Path) -> None:
        if late_stage == "fixture_cleanup":
            clock[0] = 91.0

    monkeypatch.setattr(matrix, "assess_case", assess)
    monkeypatch.setattr(matrix.shutil, "rmtree", cleanup)
    monkeypatch.setattr(matrix, "immutable_inputs", lambda *args: None)
    monkeypatch.setattr(matrix.time, "monotonic", lambda: clock[0])
    original_write = Path.write_text

    def write(path: Path, contents: str, *args: Any, **kwargs: Any) -> int:
        result = original_write(path, contents, *args, **kwargs)
        if late_stage == "export":
            clock[0] = 91.0
        return result

    monkeypatch.setattr(Path, "write_text", write)
    with pytest.raises(TimeoutError):
        matrix.finish_row(tmp_path, {}, home, output, {"complete": True}, 90.0)
    assert not (output / "assessed.json").exists()


@pytest.mark.parametrize("late_stage", ("counts", "export"))
def test_gate_closeout_includes_counters_and_final_receipt_export(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    late_stage: str,
) -> None:
    gate = load_script("run_notebook_import_cpu_gate", monkeypatch)
    clock = [1201.0 if late_stage == "counts" else 1199.0]
    monkeypatch.setattr(gate.time, "monotonic", lambda: clock[0])
    original = Path.write_text

    def write(path: Path, contents: str, *args: Any, **kwargs: Any) -> int:
        result = original(path, contents, *args, **kwargs)
        clock[0] = 1201.0
        return result

    monkeypatch.setattr(Path, "write_text", write)
    result: dict[str, Any] = {
        "passed": True,
        "failure": None,
        "duration_seconds": 1.0,
        "wall_limit_seconds": 1200,
    }
    receipt = tmp_path / "receipt.json"
    gate.export_receipt(result, receipt, 0.0)
    saved = json.loads(receipt.read_text())
    assert saved["passed"] is False
    assert saved["duration_seconds"] >= 1201.0
    assert saved["final_export_checked_within_wall_limit"] is False
    assert "deadline" in saved["failure"]
