"""Run the exact approved CPU gate under one outer deadline; never retry a step."""

from __future__ import annotations

import argparse
import importlib
import json
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mostaza.evaluation.requests_import_cpu import CASES, EVIDENCE, immutable_inputs
from mostaza.evaluation.verify_task_cpu import CASES as OLD_CASES
from mostaza.evaluation.verify_task_cpu import LIMIT_BYTES, digest

COMMANDS = [
    "bash scripts/validate.sh",
    ".venv/bin/python scripts/check_phase2.py --check --cohort experiments/cohort.json",
    ".venv/bin/python scripts/prepare_startup_phase2.py --check",
    ".tools/official/bin/python scripts/check_startup_configuration.py",
    (
        ".venv/bin/python docs/implementation/evidence/"
        "mostaza-phase2-startup-run/recompute.py --check"
    ),
    ".venv/bin/python scripts/check_context_verification.py --check",
    ".venv/bin/python scripts/check_pcv01.py --check",
    ".venv/bin/python scripts/check_pcv01_scorer_contract.py --check",
    ".tools/official/bin/python scripts/check_verify_task_cpu.py --check",
    ".tools/official/bin/python scripts/check_requests_import_cpu.py --check",
]


def run_scope(root: Path, raw: Path) -> tuple[str, ...]:
    if raw.parent == root / "results/requests-import-cpu" and raw.name.startswith(
        "matrix-"
    ):
        identifier, cases = raw.name.removeprefix("matrix-"), CASES
    elif raw.parent == root / "results/verify-task-cpu":
        identifier, cases = raw.name, OLD_CASES
    else:
        raise ValueError("Not an owned CPU matrix root")
    if str(uuid.UUID(identifier)) != identifier or raw.resolve() != raw:
        raise ValueError("Noncanonical CPU matrix root")
    return cases


def observed_roots(
    root: Path,
    known: dict[int, tuple[int, int, str]],
) -> set[Path]:
    result = set()
    workers = ("requests_import_cpu_fixtures.py", "verify_task_cpu_fixtures.py")
    for _, _, command in known.values():
        if not any(str(root / "scripts" / worker) in command for worker in workers):
            continue
        _, separator, output = command.rpartition(" --output ")
        if not separator:
            continue
        case_dir = Path(output.strip().strip("\"'"))
        try:
            cases = run_scope(root, case_dir.parent)
        except ValueError:
            continue
        if case_dir.name in cases:
            result.add(case_dir.parent)
    return result


def cleanup_owned(root: Path, owned: set[Path]) -> dict[str, Any]:
    records = []
    for raw in sorted(owned):
        cases = run_scope(root, raw)
        for case in cases:
            parent = raw / case
            if parent.is_symlink() or parent.resolve() != parent:
                records.append(
                    {
                        "path": str(parent),
                        "complete": False,
                        "error": "Noncanonical case directory; not removed",
                    }
                )
                continue
            for name in ("fixture", "sandboxes"):
                path = parent / name
                try:
                    if path.is_symlink():
                        path.unlink()
                    elif path.exists():
                        shutil.rmtree(path)
                    records.append({"path": str(path), "complete": not path.exists()})
                except OSError as error:
                    records.append(
                        {"path": str(path), "complete": False, "error": str(error)}
                    )
    return {
        "attempted": True,
        "complete_for_observed_roots": all(r["complete"] for r in records),
        "scope": "Only temporary fixture/sandboxes in observed worker output roots",
        "roots": [str(p) for p in sorted(owned)],
        "records": records,
    }


def run(root: Path, attempt: int) -> dict[str, Any]:
    immutable_inputs(root)
    output = root / "results/requests-import-cpu" / f"gate-{attempt}"
    if attempt == 2:
        prior = output.parent / "gate-1/receipt.json"
        repair = root / EVIDENCE / "corrective-attempt.json"
        if not prior.exists() or not repair.exists():
            raise ValueError("Corrective attempt requires prior evidence and repair")
        record = json.loads(repair.read_text())
        if not all(record.get(key) for key in ("reason", "repair", "focused_checks")):
            raise ValueError(
                "Corrective record must identify finding, repair and checks"
            )
        if (
            json.loads(prior.read_text())["passed"]
            and record["reason"] != "audit_finding"
        ):
            raise ValueError("A passed gate may repeat only for an actual audit repair")
    output.mkdir(parents=True, exist_ok=False)
    watchdog = importlib.import_module("check_verify_task_cpu")
    started = time.monotonic()
    receipts: list[dict[str, Any]] = []
    failure = None
    owned: set[Path] = set()
    active: dict[str, Any] | None = None
    try:
        for index, command in enumerate(COMMANDS, 1):
            logfile = output / f"{index:02}.log"
            step = time.monotonic()
            active = {
                "command": command,
                "argv": command.split(),
                "step": step,
                "logfile": logfile,
            }
            with logfile.open("wb") as log:
                process = subprocess.Popen(
                    command.split(),
                    cwd=root,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                known: dict[int, tuple[int, int, str]] = {}
                try:
                    while process.poll() is None:
                        watchdog.remember_descendants(
                            process.pid, watchdog.process_table(), known
                        )
                        owned.update(observed_roots(root, known))
                        if time.monotonic() > started + 1200:
                            raise TimeoutError("Whole CPU gate1200s deadline exhausted")
                        used = watchdog.used_bytes(output.parent) + watchdog.used_bytes(
                            root / "results/verify-task-cpu"
                        )
                        if used > LIMIT_BYTES:
                            raise ValueError("Whole CPU gate artifact cap exceeded")
                        time.sleep(0.2)
                finally:
                    try:
                        watchdog.stop_group(process, known)
                    finally:
                        owned.update(observed_roots(root, known))
            receipts.append(
                {
                    "command": command,
                    "argv": command.split(),
                    "exit_code": process.returncode,
                    "duration_seconds": time.monotonic() - step,
                    "log": str(logfile.relative_to(root)),
                    "log_sha256": digest(logfile),
                }
            )
            print(
                json.dumps(
                    {
                        "step": index,
                        "exit_code": process.returncode,
                        "duration_seconds": receipts[-1]["duration_seconds"],
                    }
                ),
                flush=True,
            )
            active = None
            if process.returncode:
                raise ValueError(f"Gate command failed: {command}")
        immutable_inputs(root)
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
        if active is not None:
            logfile = active["logfile"]
            receipts.append(
                {
                    "command": active["command"],
                    "argv": active["argv"],
                    "exit_code": None,
                    "exit_code_reason": failure,
                    "duration_seconds": time.monotonic() - active["step"],
                    "log": str(logfile.relative_to(root)),
                    "log_sha256": digest(logfile) if logfile.exists() else None,
                }
            )
    cleanup = cleanup_owned(root, owned)
    if not cleanup["complete_for_observed_roots"]:
        failure = failure or "Owned temporary cleanup incomplete"
    if failure and receipts:
        receipts[-1]["cleanup"] = cleanup
    result = {
        "cleanup": cleanup,
        "attempt": attempt,
        "maximum_attempts": 2,
        "commands": receipts,
        "failure": failure,
        "passed": failure is None and len(receipts) == 10,
        "duration_seconds": time.monotonic() - started,
        "wall_limit_seconds": 1200,
        "automatic_retries": False,
        "maximum_native_invocations": 20,
        "plan_sha256": digest(root / EVIDENCE / "plan-for-approval.md"),
    }
    (output / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    if failure:
        raise ValueError(f"{failure}; evidence: {output}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", required=True, action="store_true")
    parser.add_argument("--attempt", required=True, type=int, choices=(1, 2))
    args = parser.parse_args()
    run(Path(__file__).resolve().parents[1], args.attempt)


if __name__ == "__main__":
    main()
