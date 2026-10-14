"""Run eleven native CPU diagnostics with an owned process-group watchdog."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mostaza.evaluation.verify_task_cpu import (
    CASES,
    LIMIT_BYTES,
    assess,
    digest,
    validate_pins,
)


def used_bytes(path: Path) -> int:
    def walk_error(error: OSError) -> None:
        # Native finally may remove an owned directory during the walk.
        if not isinstance(error, FileNotFoundError):
            raise error

    total = 0
    for directory, _, names in os.walk(path, followlinks=False, onerror=walk_error):
        for name in names:
            try:
                info = (Path(directory) / name).lstat()
            except FileNotFoundError:
                # A missing temporary file consumes no retained bytes. Do not
                # hide permission/I/O errors or follow links outside this run.
                continue
            if stat.S_ISREG(info.st_mode):
                total += info.st_size
    return total


def process_table() -> dict[int, tuple[int, int, str]]:
    output = subprocess.run(
        ["ps", "-ww", "-axo", "pid=,ppid=,pgid=,command="],
        check=True,
        capture_output=True,
        text=True,
        timeout=2,
    ).stdout
    table = {}
    for line in output.splitlines():
        parts = line.strip().split(maxsplit=3)
        if len(parts) == 4:
            table[int(parts[0])] = (int(parts[1]), int(parts[2]), parts[3])
    return table


def remember_descendants(
    pid: int,
    table: dict[int, tuple[int, int, str]],
    known: dict[int, tuple[int, int, str]],
) -> None:
    descendants = {pid}
    while True:
        added = {
            child for child, (parent, _, _) in table.items() if parent in descendants
        } - descendants
        if not added:
            break
        descendants.update(added)
    for child in descendants:
        if child in table:
            known[child] = table[child]


def stop_group(
    process: subprocess.Popen[bytes],
    known: dict[int, tuple[int, int, str]],
) -> None:
    # Native commands create independent sessions; remember descendants while
    # their parent is alive instead of assuming one inherited process group.
    table = process_table()
    remember_descendants(process.pid, table, known)
    groups = {
        entry[1]
        for pid, entry in known.items()
        if pid in table and table[pid][1:] == entry[1:]
    }
    if process.poll() is None:
        groups.add(process.pid)
    for group in groups:
        try:
            os.killpg(group, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        pass
    for group in groups:
        try:
            os.killpg(group, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait(timeout=5)


def run(root: Path) -> dict[str, Any]:
    evidence = root / "docs/implementation/evidence/mostaza-verify-task-cpu"
    manifest = json.loads((evidence / "prerequisites.json").read_text())
    validate_pins(root, manifest)
    for name, version in manifest["native_environment_versions"].items():
        if importlib.metadata.version(name) != version:
            raise ValueError(f"CPU dependency changed: {name}")
    approval = json.loads((evidence / "approval.json").read_text())
    if approval["plan_sha256"] != digest(evidence / "plan-for-approval.md"):
        raise ValueError("Plan differs from approved proposal")
    if shutil.disk_usage(root).free < LIMIT_BYTES:
        raise ValueError("Insufficient free local disk budget")
    output_root = root / "results/verify-task-cpu"
    output_root.mkdir(exist_ok=True)
    if used_bytes(output_root) > LIMIT_BYTES:
        raise ValueError("Retained CPU evidence already exceeds budget")
    raw = output_root / str(uuid.uuid4())
    raw.mkdir()
    start = time.monotonic()
    results: list[dict[str, Any]] = []
    invocations_started = 0
    status = "BLOCKED"
    failure = None
    try:
        for case in CASES:
            case_dir = raw / case
            with (raw / (case + ".log")).open("wb") as log:
                command = [
                    sys.executable,
                    str(root / "scripts/verify_task_cpu_fixtures.py"),
                    "--case",
                    case,
                    "--output",
                    str(case_dir),
                ]
                process = subprocess.Popen(
                    command,
                    cwd=root,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                invocations_started += 1
                known: dict[int, tuple[int, int, str]] = {}
                deadline = min(time.monotonic() + 90, start + 1200)
                try:
                    while process.poll() is None:
                        remember_descendants(process.pid, process_table(), known)
                        if time.monotonic() > deadline:
                            raise TimeoutError(
                                "Owned CPU case/total wall budget exhausted"
                            )
                        if used_bytes(output_root) > LIMIT_BYTES:
                            raise ValueError("Owned CPU disk budget exhausted")
                        time.sleep(0.2)
                    if process.returncode != 0:
                        raise ValueError(
                            f"Native case worker failed: {case}; "
                            f"see {raw / (case + '.log')}"
                        )
                finally:
                    stop_group(process, known)
            row = json.loads((case_dir / "result.json").read_text())
            expected = json.loads((case_dir / "expected.json").read_text())
            results.append(assess(row, expected, case_dir))
            validate_pins(root, manifest)
        mismatches = any(
            r["workspace_binding"] is False for r in results if r["id"].startswith("R")
        )
        status = (
            "CPU_E2E_CONTROLS_PASS_REQUESTS_BINDING_MISMATCH"
            if mismatches
            else "CPU_E2E_CONTROLS_PASS_REQUESTS_OBSERVED"
        )
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
    finally:
        # Only this invocation's disposable fixtures/sandboxes; never source caches.
        for case in CASES:
            for name in ("fixture", "sandboxes"):
                shutil.rmtree(raw / case / name, ignore_errors=True)
        summary = {
            "schema_version": 1,
            "status": status,
            "failure": failure,
            "results": results,
            "duration_seconds": time.monotonic() - start,
            "raw_path": str(raw),
            "gpu_readiness": False,
            "actual_scorer_runtime_parity": None,
            "actual_scorer_runtime_parity_reason": (
                "Owned local CPU diagnostics only; no private scorer execution"
            ),
            "native_verifier_changed": False,
            "gpu_starts": 0,
            "invocations_started": invocations_started,
            "native_results_present": len(list(raw.glob("*/result.json"))),
            "invocations_assessed": len(results),
            "inventory": [
                {
                    "path": str(p.relative_to(root)),
                    "bytes": p.stat().st_size,
                    "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                }
                for p in sorted(raw.rglob("*"))
                if p.is_file()
            ],
        }
        (raw / "summary.json").write_text(
            json.dumps(summary, indent=2, sort_keys=True) + "\n"
        )
    if failure:
        raise ValueError(f"{failure}; evidence: {raw}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", required=True, action="store_true")
    parser.parse_args()
    print(json.dumps(run(Path(__file__).resolve().parents[1]), sort_keys=True))


if __name__ == "__main__":
    main()
