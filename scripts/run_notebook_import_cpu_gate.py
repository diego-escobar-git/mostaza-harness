"""Approved twelve-command gate; whole-run deadline, owned cleanup, no retries."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
import time
import traceback
import uuid
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mostaza.evaluation.notebook_import_candidate import EVIDENCE
from mostaza.evaluation.notebook_import_cpu import immutable_inputs
from mostaza.evaluation.verify_task_cpu import LIMIT_BYTES, digest


def commands(attempt: int) -> list[str]:
    previous = importlib.import_module("run_requests_import_cpu_gate")
    prefix = f"results/notebook-import-cpu/gate-{attempt}"
    return [
        *previous.COMMANDS,
        (
            ".tools/official/bin/python scripts/check_notebook_import_cpu.py "
            f"--check --output {prefix}/matrix"
        ),
        (
            "/Users/diego/.pyenv/versions/3.12.8/bin/python3.12 -I -S "
            "scripts/check_notebook_import_portability.py --check "
            f"--receipt {prefix}/matrix/summary.json --output {prefix}/portability"
        ),
    ]


def cleanup_scratch(scratch: Path, owner: dict[str, str]) -> dict[str, Any]:
    if (
        scratch.parent != Path("/private/tmp")
        or scratch != scratch.resolve()
        or scratch.name != "mostaza-notebook-import-" + owner["token"]
        or str(uuid.UUID(owner["token"])) != owner["token"]
        or json.loads((scratch / "owner.json").read_text()) != owner
    ):
        raise ValueError("Refusing unowned scratch cleanup")
    shutil.rmtree(scratch)
    return {"path": str(scratch), "complete": not scratch.exists()}


def source_inventory(root: Path) -> list[dict[str, Any]]:
    result = []
    for pattern in (
        "src/mostaza/evaluation/notebook_import*.py",
        "scripts/*notebook_import*.py",
        "tests/unit/test_notebook_import*.py",
        "tests/integration/test_notebook_import*.py",
        "notebooks/mostaza-notebook-import-cpu.ipynb",
        "experiments/E?-C8K-L1/manifest.json",
        "docs/specs/notebook-import-cpu.md",
    ):
        for path in sorted(root.glob(pattern)):
            result.append(
                {
                    "path": str(path.relative_to(root)),
                    "bytes": path.stat().st_size,
                    "sha256": digest(path),
                }
            )
    return result


def actual_counts(output: Path, legacy_roots: set[Path]) -> dict[str, Any]:
    legacy: list[dict[str, Any]] = []
    for raw in sorted(legacy_roots):
        summary_path = raw / "summary.json"
        summary = json.loads(summary_path.read_text()) if summary_path.exists() else {}
        returned = len(list(raw.glob("*/result.json")))
        exact_start = len(list(raw.glob("*/native-started.json")))
        is_legacy_v = raw.parent.name == "verify-task-cpu"
        passed = not summary.get("failure") and summary_path.exists()
        # V-CPU-01's old "invocations_started" counts worker dispatches. Only a
        # completed assessed matrix establishes exact native-call counts.
        started = (
            returned
            if is_legacy_v and passed
            else (None if is_legacy_v else exact_start)
        )
        legacy.append(
            {
                "raw_path": str(raw),
                "started": started,
                "started_reason": (
                    "Frozen V-CPU-01 has worker starts, no native-start boundary marker"
                    if started is None
                    else None
                ),
                "native_start_lower_bound": returned,
                "worker_starts": summary.get("invocations_started"),
                "worker_starts_reason": None
                if "invocations_started" in summary
                else "Frozen controller summary unavailable",
                "completed": returned,
                "assessed": summary.get("invocations_assessed"),
                "assessed_reason": None
                if "invocations_assessed" in summary
                else "Frozen controller did not retain its assessment summary",
            }
        )
    matrix = output / "matrix"
    new = {
        "started": len(list(matrix.glob("*/native-started.json"))),
        "completed": len(list(matrix.glob("*/native-completed.json"))),
        "assessed": len(list(matrix.glob("*/assessed.json"))),
    }
    setup = {
        "started": len(list(matrix.glob("*/setup-started.json"))),
        "completed": len(list(matrix.glob("*/setup-completed.json"))),
        "assessed": len(list(matrix.glob("*/assessed.json"))),
    }
    portable = output / "portability"
    stdlib = {
        field: len(list(portable.glob("*-" + field + ".json")))
        for field in ("started", "completed", "assessed")
    }
    all_known = all(r["started"] is not None for r in legacy)
    totals = {
        "started": new["started"] + sum(r["started"] for r in legacy)
        if all_known
        else None,
        "started_reason": None
        if all_known
        else "Frozen legacy native-start telemetry absent",
        "completed": new["completed"] + sum(r["completed"] for r in legacy),
        "assessed": (
            new["assessed"] + sum(r["assessed"] for r in legacy)
            if all(r["assessed"] is not None for r in legacy)
            else None
        ),
    }
    totals["assessed_reason"] = (
        None
        if totals["assessed"] is not None
        else "A frozen legacy assessment summary is unavailable"
    )
    return {
        "legacy_native": legacy,
        "new_native": new,
        "native_total": totals,
        "setup": setup,
        "stdlib": stdlib,
    }


def counts_satisfy_gate(counts: dict[str, Any]) -> bool:
    return all(
        counts[scope][field] == maximum
        for scope, maximum in (("native_total", 26), ("setup", 6), ("stdlib", 2))
        for field in ("started", "completed", "assessed")
    )


def execution_environment(scratch: Path, deadline: float) -> dict[str, str]:
    temporary = scratch / "host-tmp"
    temporary.mkdir()
    env = dict(os.environ)
    env["TMPDIR"] = str(temporary)
    env["MOSTAZA_NOTEBOOK_IMPORT_SCRATCH"] = str(scratch)
    env["MOSTAZA_CPU_DEADLINE"] = str(deadline)
    return env


def additional_admission(root: Path, attempt: int) -> dict[str, Any] | None:
    if attempt == 6:
        return supervision_admission(root)
    if attempt == 5:
        return source_filter_admission(root)
    if attempt == 4:
        return resource_admission(root)
    if attempt not in (1, 2, 3):
        raise ValueError("Unapproved gate attempt")
    if attempt != 3:
        return None
    evidence = root / EVIDENCE
    approval_path = evidence / "additional-gate-approval.json"
    approval = json.loads(approval_path.read_text())
    proposal = evidence / "additional-gate-plan.md"
    repair = evidence / "post-gate-repair.json"
    expected_limits = {
        "attempt": 3,
        "maximum_additional_attempts": 1,
        "native_verifications": 26,
        "setup_probes": 6,
        "stdlib_probes": 2,
        "wall_seconds": 1200,
        "artifact_bytes": LIMIT_BYTES,
        "automatic_retries": False,
    }
    if (
        approval.get("status") != "APPROVED"
        or approval.get("proposal_sha256") != digest(proposal)
        or approval.get("repair_sha256") != digest(repair)
        or approval.get("limits") != expected_limits
    ):
        raise ValueError("Additional gate approval missing, changed or out of scope")
    receipts = approval.get("prior_receipts")
    if not isinstance(receipts, list) or len(receipts) != 2:
        raise ValueError("Both consumed gate receipts are required")
    for index, pin in enumerate(receipts, 1):
        expected = f"results/notebook-import-cpu/gate-{index}/receipt.json"
        path = root / expected
        if pin.get("path") != expected or digest(path) != pin.get("sha256"):
            raise ValueError("Consumed gate evidence changed")
        prior = json.loads(path.read_text())
        if (
            prior["attempt"] != index
            or prior["maximum_attempts"] != 2
            or prior["passed"]
        ):
            raise ValueError("Additional allowance requires both failed prior attempts")
    return {
        "attempt": 3,
        "approval_sha256": digest(approval_path),
        "proposal_sha256": approval["proposal_sha256"],
        "repair_sha256": approval["repair_sha256"],
        "prior_receipts": receipts,
        "ordinary_maximum_attempts": 2,
        "maximum_additional_attempts": 1,
    }


def resource_admission(root: Path) -> dict[str, Any]:
    """Admit the single fourth attempt without resetting consumed allowances."""
    evidence = root / EVIDENCE
    approval_path = evidence / "resource-gate-approval.json"
    approval = json.loads(approval_path.read_text())
    expected_limits = {
        "attempt": 4,
        "maximum_additional_attempts": 1,
        "native_verifications": 26,
        "setup_probes": 6,
        "stdlib_probes": 2,
        "wall_seconds": 1200,
        "artifact_bytes": LIMIT_BYTES,
        "automatic_retries": False,
    }
    if (
        approval.get("status") != "APPROVED"
        or approval.get("proposal_sha256") != digest(evidence / "resource-gate-plan.md")
        or approval.get("repair_sha256") != digest(evidence / "resource-repair.json")
        or approval.get("limits") != expected_limits
    ):
        raise ValueError("Resource gate approval missing, changed or out of scope")
    receipts = approval.get("prior_receipts")
    if not isinstance(receipts, list) or len(receipts) != 3:
        raise ValueError("Three consumed gate receipts are required")
    for index, pin in enumerate(receipts, 1):
        expected = f"results/notebook-import-cpu/gate-{index}/receipt.json"
        path = root / expected
        if pin.get("path") != expected or digest(path) != pin.get("sha256"):
            raise ValueError("Consumed gate evidence changed")
        prior = json.loads(path.read_text())
        if (
            prior["attempt"] != index
            or prior["maximum_attempts"] != (3 if index == 3 else 2)
            or prior["passed"]
        ):
            raise ValueError("Resource allowance requires three failed prior attempts")
    return {
        "attempt": 4,
        "approval_sha256": digest(approval_path),
        "proposal_sha256": approval["proposal_sha256"],
        "repair_sha256": approval["repair_sha256"],
        "prior_receipts": receipts,
        "ordinary_maximum_attempts": 2,
        "previous_additional_attempts": 1,
        "maximum_additional_attempts": 1,
    }


def source_filter_admission(root: Path) -> dict[str, Any]:
    """Admit the single fifth attempt without resetting consumed allowances."""
    evidence = root / EVIDENCE
    approval_path = evidence / "source-filter-gate-approval.json"
    approval = json.loads(approval_path.read_text())
    expected_limits = {
        "attempt": 5,
        "maximum_additional_attempts": 1,
        "native_verifications": 26,
        "setup_probes": 6,
        "stdlib_probes": 2,
        "wall_seconds": 1200,
        "artifact_bytes": LIMIT_BYTES,
        "automatic_retries": False,
    }
    if (
        approval.get("status") != "APPROVED"
        or approval.get("proposal_sha256")
        != digest(evidence / "source-filter-gate-plan.md")
        or approval.get("repair_sha256")
        != digest(evidence / "gate4-source-diagnosis.json")
        or approval.get("limits") != expected_limits
    ):
        raise ValueError("Source filter gate approval missing, changed or out of scope")
    receipts = approval.get("prior_receipts")
    if not isinstance(receipts, list) or len(receipts) != 4:
        raise ValueError("Four consumed gate receipts are required")
    for index, pin in enumerate(receipts, 1):
        expected = f"results/notebook-import-cpu/gate-{index}/receipt.json"
        path = root / expected
        if pin.get("path") != expected or digest(path) != pin.get("sha256"):
            raise ValueError("Consumed gate evidence changed")
        prior = json.loads(path.read_text())
        if (
            prior["attempt"] != index
            or prior["maximum_attempts"] != (index if index >= 3 else 2)
            or prior["passed"]
        ):
            raise ValueError(
                "Source filter allowance requires four failed prior attempts"
            )
    return {
        "attempt": 5,
        "approval_sha256": digest(approval_path),
        "proposal_sha256": approval["proposal_sha256"],
        "repair_sha256": approval["repair_sha256"],
        "prior_receipts": receipts,
        "ordinary_maximum_attempts": 2,
        "previous_additional_attempts": 2,
        "maximum_additional_attempts": 1,
    }


def supervision_admission(root: Path) -> dict[str, Any]:
    """Admit the single sixth attempt without resetting consumed allowances."""
    evidence = root / EVIDENCE
    approval_path = evidence / "supervision-gate-approval.json"
    approval = json.loads(approval_path.read_text())
    expected_limits = {
        "attempt": 6,
        "maximum_additional_attempts": 1,
        "native_verifications": 26,
        "setup_probes": 6,
        "stdlib_probes": 2,
        "wall_seconds": 1200,
        "artifact_bytes": LIMIT_BYTES,
        "automatic_retries": False,
    }
    if (
        approval.get("status") != "APPROVED"
        or approval.get("proposal_sha256")
        != digest(evidence / "supervision-gate-plan.md")
        or approval.get("repair_sha256") != digest(evidence / "supervision-repair.json")
        or approval.get("limits") != expected_limits
    ):
        raise ValueError("Supervision gate approval missing, changed or out of scope")
    receipts = approval.get("prior_receipts")
    if not isinstance(receipts, list) or len(receipts) != 5:
        raise ValueError("Five consumed gate receipts are required")
    for index, pin in enumerate(receipts, 1):
        expected = f"results/notebook-import-cpu/gate-{index}/receipt.json"
        path = root / expected
        if pin.get("path") != expected or digest(path) != pin.get("sha256"):
            raise ValueError("Consumed gate evidence changed")
        prior = json.loads(path.read_text())
        if (
            prior["attempt"] != index
            or prior["maximum_attempts"] != (index if index >= 3 else 2)
            or prior["passed"]
        ):
            raise ValueError(
                "Supervision allowance requires five failed prior attempts"
            )
    return {
        "attempt": 6,
        "approval_sha256": digest(approval_path),
        "proposal_sha256": approval["proposal_sha256"],
        "repair_sha256": approval["repair_sha256"],
        "prior_receipts": receipts,
        "ordinary_maximum_attempts": 2,
        "previous_additional_attempts": 3,
        "maximum_additional_attempts": 1,
    }


HOST_TEST_RETENTION = "-o tmp_path_retention_policy=failed"


def host_test_environment(base: dict[str, str], index: int) -> dict[str, str]:
    """Apply the approved host-only policy without mutating the base environment."""
    result = dict(base)
    if index == 1:
        if result.get("PYTEST_ADDOPTS"):
            raise ValueError("Review existing host pytest options before overriding")
        result["PYTEST_ADDOPTS"] = HOST_TEST_RETENTION
    return result


def export_receipt(result: dict[str, Any], path: Path, started: float) -> None:
    """Check the whole budget after counters/inventory and after receipt export."""
    elapsed = time.monotonic() - started
    result["duration_seconds"] = elapsed
    result["duration_measurement_scope"] = (
        "Through counters/inventory before final JSON write; export completion "
        "is checked separately against the same wall limit"
    )
    limit = result["wall_limit_seconds"]
    if elapsed > limit:
        result["passed"] = False
        result["failure"] = (
            result["failure"] or "Gate closeout exceeded total wall deadline"
        )
    result["final_export_checked_within_wall_limit"] = elapsed <= limit
    path.write_text(json.dumps(result, indent=2) + "\n")
    finished = time.monotonic() - started
    if finished > limit:
        result["passed"] = False
        result["failure"] = (
            result["failure"] or "Gate receipt export exceeded total wall deadline"
        )
        result["duration_seconds"] = finished
        result["duration_measurement_scope"] = (
            "Through first receipt export; failed closeout follows"
        )
        result["final_export_checked_within_wall_limit"] = False
        # A late failure may be exported after the bound, but can never be PASS.
        path.write_text(json.dumps(result, indent=2) + "\n")


def run(root: Path, attempt: int) -> dict[str, Any]:
    started = time.monotonic()
    immutable_inputs(root)
    admission = additional_admission(root, attempt)
    output = root / "results/notebook-import-cpu" / f"gate-{attempt}"
    if attempt == 2:
        prior = output.parent / "gate-1/receipt.json"
        repair = root / EVIDENCE / "corrective-attempt.json"
        if not prior.exists() or not repair.exists():
            raise ValueError(
                "Corrective attempt requires prior gate evidence and repair"
            )
        correction = json.loads(repair.read_text())
        if not all(correction.get(k) for k in ("reason", "repair", "focused_checks")):
            raise ValueError("Incomplete corrective attempt record")
        if (
            json.loads(prior.read_text())["passed"]
            and correction["reason"] != "audit_finding"
        ):
            raise ValueError("Passed gate may repeat only after an audit finding")
    output.mkdir(parents=True, exist_ok=False)
    token = str(uuid.uuid4())
    scratch = Path("/private/tmp") / ("mostaza-notebook-import-" + token)
    scratch.mkdir()
    owner = {"token": token, "project": str(root), "gate": str(output)}
    (scratch / "owner.json").write_text(json.dumps(owner))
    (output / "ownership.json").write_text(
        json.dumps(
            {"root": str(scratch), "host_tmpdir": str(scratch / "host-tmp"), **owner}
        )
    )
    inventory = source_inventory(root)
    (output / "source-inventory.json").write_text(
        json.dumps(inventory, indent=2) + "\n"
    )
    env = execution_environment(scratch, started + 1170)
    watchdog = importlib.import_module("check_verify_task_cpu")
    previous = importlib.import_module("run_requests_import_cpu_gate")
    owned: set[Path] = set()
    receipts = []
    failure = None
    failure_traceback = None
    sampled_peak = 0
    active: dict[str, Any] | None = None
    try:
        if shutil.disk_usage(root).free < LIMIT_BYTES:
            raise ValueError("Insufficient disk headroom")
        for index, command in enumerate(commands(attempt), 1):
            # Frozen legacy matrices cannot consult our deadline. Admit their
            # whole worst-case case allowance before starting the command.
            rows = {9: 11, 10: 9, 11: 6, 12: 2}.get(index, 1)
            if time.monotonic() + rows * 90 + 30 > started + 1200:
                raise TimeoutError("Insufficient step allowance before cleanup reserve")
            immutable_inputs(root)
            if source_inventory(root) != inventory:
                raise ValueError("Implementation changed during gate")
            step = time.monotonic()
            logfile = output / f"{index:02}.log"
            command_env = (
                host_test_environment(env, index) if attempt in (4, 5, 6) else dict(env)
            )
            environment_overrides = {
                key: value
                for key, value in command_env.items()
                if env.get(key) != value
            }
            active = {
                "command": command,
                "step": step,
                "logfile": logfile,
                "environment_overrides": environment_overrides,
            }
            with logfile.open("wb") as log:
                process = subprocess.Popen(
                    command.split(),
                    cwd=root,
                    env=command_env,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                known: dict[int, tuple[int, int, str]] = {}
                if attempt == 6:
                    helper = importlib.import_module("notebook_import_supervision")

                    def check_owned_caps(
                        observed: dict[int, tuple[int, int, str]] = known,
                    ) -> None:
                        nonlocal sampled_peak
                        owned.update(previous.observed_roots(root, observed))
                        used = sum(
                            watchdog.used_bytes(path)
                            for path in (
                                scratch,
                                root / "results/notebook-import-cpu",
                                root / "results/requests-import-cpu",
                                root / "results/verify-task-cpu",
                            )
                        )
                        sampled_peak = max(sampled_peak, used)
                        if used > LIMIT_BYTES:
                            raise ValueError("Whole CPU gate artifact ceiling")

                    try:
                        supervision = helper.supervise(
                            process,
                            known,
                            watchdog,
                            started + 1170,
                            started + 1200,
                            check_owned_caps,
                            output / f"{index:02}.supervision.json",
                        )
                        process_cleanup = supervision["process_cleanup"]
                        active["supervision"] = supervision
                        active["process_cleanup"] = process_cleanup
                    except helper.SupervisionFailure as error:
                        active["supervision"] = error.receipt
                        active["process_cleanup"] = error.receipt["process_cleanup"]
                        raise
                    finally:
                        owned.update(previous.observed_roots(root, known))
                else:
                    try:
                        while process.poll() is None:
                            watchdog.remember_descendants(
                                process.pid, watchdog.process_table(), known
                            )
                            owned.update(previous.observed_roots(root, known))
                            if time.monotonic() > started + 1170:
                                raise TimeoutError(
                                    "Gate work deadline;30s reserved for cleanup"
                                )
                            used = sum(
                                watchdog.used_bytes(path)
                                for path in (
                                    scratch,
                                    root / "results/notebook-import-cpu",
                                    root / "results/requests-import-cpu",
                                    root / "results/verify-task-cpu",
                                )
                            )
                            sampled_peak = max(sampled_peak, used)
                            if used > LIMIT_BYTES:
                                raise ValueError("Whole CPU gate artifact ceiling")
                            time.sleep(0.2)
                    finally:
                        try:
                            process_cleanup = importlib.import_module(
                                "notebook_import_supervision"
                            ).stop_group(process, known, watchdog)
                        finally:
                            owned.update(previous.observed_roots(root, known))
            receipts.append(
                {
                    "command": command,
                    "argv": command.split(),
                    "environment_overrides": environment_overrides,
                    "exit_code": process.returncode,
                    "process_cleanup": process_cleanup,
                    "supervision": active.get("supervision"),
                    "duration_seconds": time.monotonic() - step,
                    "log": str(logfile.relative_to(root)),
                    "log_sha256": digest(logfile),
                }
            )
            active = None
            print(
                json.dumps(
                    {
                        "step": index,
                        "exit_code": process.returncode,
                        "process_cleanup": process_cleanup,
                        "duration_seconds": receipts[-1]["duration_seconds"],
                    }
                ),
                flush=True,
            )
            if process.returncode:
                raise ValueError("Gate command failed: " + command)
        immutable_inputs(root)
        if source_inventory(root) != inventory:
            raise ValueError("Final source inventory changed")
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
        failure_traceback = traceback.format_exc()
        if active:
            logfile = active["logfile"]
            receipts.append(
                {
                    "command": active["command"],
                    "argv": active["command"].split(),
                    "environment_overrides": active["environment_overrides"],
                    "exit_code": None,
                    "exit_code_reason": failure,
                    "process_cleanup": active.get("process_cleanup"),
                    "supervision": active.get("supervision"),
                    "duration_seconds": time.monotonic() - active["step"],
                    "log": str(logfile.relative_to(root)),
                    "log_sha256": digest(logfile) if logfile.exists() else None,
                }
            )
    cleanups = []
    try:
        cleanups.append(previous.cleanup_owned(root, owned))
        cleanups.append(cleanup_scratch(scratch, owner))
        if not cleanups[0]["complete_for_observed_roots"]:
            raise ValueError("Regression cleanup incomplete")
    except Exception as error:
        failure = failure or f"Cleanup {type(error).__name__}: {error}"
    elapsed = time.monotonic() - started
    if elapsed > 1200:
        failure = failure or "Gate cleanup exceeded1200s total deadline"
    counts = actual_counts(output, owned)
    if failure is None and not counts_satisfy_gate(counts):
        failure = "Actual execution counts differ from approved gate"
    result = {
        "actual_counts": counts,
        "attempt": attempt,
        "maximum_attempts": attempt if admission is not None else 2,
        "additional_authorization": admission,
        "passed": failure is None and len(receipts) == 12,
        "failure": failure,
        "failure_traceback": failure_traceback,
        "commands": receipts,
        "cleanup": cleanups,
        "duration_seconds": elapsed,
        "wall_limit_seconds": 1200,
        "work_deadline_seconds": 1170,
        "cleanup_reserve_seconds": 30,
        "sampled_peak_bytes": sampled_peak,
        "host_temporary_root": env["TMPDIR"],
        "sampled_peak_scope": (
            "Polled owned output/scratch bytes; includes prior retained CPU results"
        ),
        "physical_instantaneous_peak_bytes": None,
        "physical_peak_reason": "Polling cannot guarantee instantaneous physical peak",
        "maximum_native_invocations": 26,
        "maximum_setup_probes": 6,
        "maximum_stdlib_probes": 2,
        "automatic_retries": False,
        "plan_sha256": digest(root / EVIDENCE / "plan-for-approval.md"),
    }
    export_receipt(result, output / "receipt.json", started)
    if not result["passed"]:
        raise ValueError(f"{result['failure']}; evidence: {output}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", required=True, action="store_true")
    parser.add_argument(
        "--attempt", required=True, type=int, choices=(1, 2, 3, 4, 5, 6)
    )
    args = parser.parse_args()
    run(Path(__file__).resolve().parents[1], args.attempt)


if __name__ == "__main__":
    main()
