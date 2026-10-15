"""Execute the approved nine-case layout matrix once, CPU only."""

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
from mostaza.evaluation.requests_import_cpu import (
    CASES,
    EVIDENCE,
    assess,
    immutable_inputs,
    runtime_versions,
    validate_pairs,
)
from mostaza.evaluation.verify_task_cpu import LIMIT_BYTES, digest


def run(root: Path) -> dict[str, Any]:
    manifest = immutable_inputs(root)
    runtime_versions(manifest)
    watchdog = importlib.import_module("check_verify_task_cpu")
    output_root = root / "results/requests-import-cpu"
    output_root.mkdir(exist_ok=True)
    raw = output_root / ("matrix-" + str(uuid.uuid4()))
    raw.mkdir()
    if shutil.disk_usage(root).free < LIMIT_BYTES:
        raise ValueError("Insufficient local disk budget")
    started = time.monotonic()
    rows: list[dict[str, Any]] = []
    assessments: list[dict[str, Any]] = []
    launched = 0
    status, failure = "BLOCKED", None
    try:
        for case in CASES:
            case_dir = raw / case
            with (raw / (case + ".log")).open("wb") as log:
                process = subprocess.Popen(
                    [
                        sys.executable,
                        str(root / "scripts/requests_import_cpu_fixtures.py"),
                        "--case",
                        case,
                        "--output",
                        str(case_dir),
                    ],
                    cwd=root,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                launched += 1
                known: dict[int, tuple[int, int, str]] = {}
                deadline = min(started + 1200, time.monotonic() + 90)
                try:
                    while process.poll() is None:
                        watchdog.remember_descendants(
                            process.pid, watchdog.process_table(), known
                        )
                        if time.monotonic() > deadline:
                            raise TimeoutError("CPU case/matrix wall deadline")
                        used = watchdog.used_bytes(output_root) + watchdog.used_bytes(
                            root / "results/verify-task-cpu"
                        )
                        if used > LIMIT_BYTES:
                            raise ValueError("Owned CPU artifact cap exceeded")
                        time.sleep(0.2)
                    if process.returncode:
                        raise ValueError(
                            f"Case worker failed: {case}; see {raw / (case + '.log')}"
                        )
                finally:
                    watchdog.stop_group(process, known)
            row = json.loads((case_dir / "result.json").read_text())
            assessments.append(assess(row, case_dir))
            rows.append(row)
            immutable_inputs(root)
        validate_pairs(rows)
        if list(raw.glob("*-current.*")):
            raise ValueError("Stale pair witness after final stage")
        status = "CPU_REQUESTS_IMPORT_BINDING_VALIDATED"
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
    finally:
        for case in CASES:
            for name in ("fixture", "sandboxes"):
                shutil.rmtree(raw / case / name, ignore_errors=True)
        result = {
            "status": status,
            "failure": failure,
            "worker_processes_started": launched,
            "invocations_started": len(list(raw.glob("*/native-started.json"))),
            "native_results_present": len(list(raw.glob("*/result.json"))),
            "invocations_assessed": len(assessments),
            "results": assessments,
            "raw_path": str(raw),
            "duration_seconds": time.monotonic() - started,
            "gpu_readiness": False,
            "actual_scorer_runtime_parity": None,
            "actual_scorer_runtime_parity_reason": (
                "Explicit local CPU layout variant only"
            ),
            "raw_junit": None,
            "raw_junit_reason": "Native cleanup removes internal JUnit",
            "peak_disk_bytes": None,
            "peak_disk_reason": "Polled cap enforced; peak value not retained",
            "cpu_time_seconds": None,
            "cpu_time_reason": "Elapsed wall-clock times only",
            "plan_sha256": digest(root / EVIDENCE / "plan-for-approval.md"),
        }
        (raw / "summary.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n"
        )
    if failure:
        raise ValueError(f"{failure}; raw evidence: {raw}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", required=True, action="store_true")
    parser.parse_args()
    print(json.dumps(run(Path(__file__).resolve().parents[1]), sort_keys=True))


if __name__ == "__main__":
    main()
