"""Six bounded relocated CPU rows, only within the approved outer gate."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mostaza.evaluation.notebook_import_cpu import (
    CASES,
    assess_case,
    candidate_contract,
    immutable_inputs,
)
from mostaza.evaluation.verify_task_cpu import LIMIT_BYTES


def finish_row(
    root: Path,
    row: dict[str, Any],
    home: Path,
    output: Path,
    process_cleanup: dict[str, Any],
    deadline: float | None,
) -> dict[str, Any]:
    """Do not accept a row until assessment, export and fixture cleanup fit."""
    assessment = {**assess_case(row, home), "process_cleanup": process_cleanup}
    shutil.rmtree(home)
    immutable_inputs(root)
    if deadline is not None and time.monotonic() > deadline:
        raise TimeoutError("Row assessment/fixture cleanup exceeded90s total")
    marker = output / "assessed.json"
    marker.write_text(json.dumps({"native": True, "setup": True}))
    if deadline is not None and time.monotonic() > deadline:
        marker.unlink()
        raise TimeoutError("Row receipt export exceeded90s total")
    return assessment


def run(root: Path, output: Path) -> dict[str, Any]:
    immutable_inputs(root)
    contract = candidate_contract(root)
    scratch = Path(os.environ["MOSTAZA_NOTEBOOK_IMPORT_SCRATCH"])
    owner = json.loads((scratch / "owner.json").read_text())
    if (
        owner["project"] != str(root)
        or owner["gate"] != str(output.parent)
        or scratch != scratch.resolve()
        or scratch.parent != Path("/private/tmp")
        or not scratch.name.startswith("mostaza-notebook-import-")
    ):
        raise ValueError("Missing bounded gate ownership")
    if (
        Path(tempfile.gettempdir()).resolve() != scratch / "host-tmp"
        or Path(os.environ["TMPDIR"]).resolve() != scratch / "host-tmp"
    ):
        raise ValueError("Host temporaries escape the owned artifact ceiling")
    deadline = float(os.environ["MOSTAZA_CPU_DEADLINE"])
    bounded = output.parent.name == "gate-6"
    if bounded:
        importlib.import_module("run_notebook_import_cpu_gate").additional_admission(
            root, 6
        )
    output.mkdir()
    watchdog = importlib.import_module("check_verify_task_cpu")
    started = time.monotonic()
    assessments = []
    failure = None
    failure_traceback = None
    try:
        for case in CASES:
            if deadline - time.monotonic() < 90:
                raise TimeoutError("Insufficient case allowance before cleanup reserve")
            home = scratch / case
            case_started = time.monotonic()
            with (output / (case + ".log")).open("wb") as log:
                process = subprocess.Popen(
                    [
                        sys.executable,
                        str(root / "scripts/notebook_import_cpu_fixtures.py"),
                        "--case",
                        case,
                        "--output",
                        str(output / case),
                        "--home",
                        str(home),
                    ],
                    cwd=root,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
                known: dict[int, tuple[int, int, str]] = {}
                case_deadline = min(
                    deadline + 30 if bounded else deadline, case_started + 90
                )
                if bounded:
                    helper = importlib.import_module("notebook_import_supervision")

                    def check_caps() -> None:
                        if (
                            watchdog.used_bytes(scratch) + watchdog.used_bytes(output)
                            > LIMIT_BYTES
                        ):
                            raise ValueError("Relocated row artifact ceiling")

                    supervision = helper.supervise(
                        process,
                        known,
                        watchdog,
                        min(deadline, case_deadline - 30),
                        case_deadline,
                        check_caps,
                        output / (case + ".supervision.json"),
                    )
                    process_cleanup = supervision["process_cleanup"]
                    if process.returncode:
                        raise ValueError(
                            f"Worker failed: {case}; see {output / (case + '.log')}"
                        )
                else:
                    try:
                        while process.poll() is None:
                            watchdog.remember_descendants(
                                process.pid, watchdog.process_table(), known
                            )
                            if time.monotonic() > case_deadline:
                                raise TimeoutError("Relocated row deadline exhausted")
                            if (
                                watchdog.used_bytes(scratch)
                                + watchdog.used_bytes(output)
                                > LIMIT_BYTES
                            ):
                                raise ValueError("Relocated row artifact ceiling")
                            time.sleep(0.2)
                        if process.returncode:
                            raise ValueError(
                                f"Worker failed: {case}; see {output / (case + '.log')}"
                            )
                    finally:
                        process_cleanup = importlib.import_module(
                            "notebook_import_supervision"
                        ).stop_group(process, known, watchdog)
            row = json.loads((output / case / "result.json").read_text())
            assessments.append(
                finish_row(
                    root,
                    row,
                    home,
                    output / case,
                    process_cleanup,
                    case_deadline if bounded else None,
                )
            )
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
        failure_traceback = traceback.format_exc()
    finally:
        # The outer gate also sweeps this exact owned scratch root after a killed
        # controller. No retained raw evidence is in scratch.
        for case in CASES:
            path = scratch / case
            if path.exists():
                shutil.rmtree(path)
        result: dict[str, Any] = {
            "status": "BLOCKED"
            if failure
            else "CPU_NOTEBOOK_LAYOUT_INTEGRATION_VALIDATED",
            "failure": failure,
            "failure_traceback": failure_traceback,
            "results": assessments,
            "candidate_contract": contract,
            "duration_seconds": time.monotonic() - started,
            "native_started": len(list(output.glob("*/native-started.json"))),
            "native_results_present": len(list(output.glob("*/result.json"))),
            "setup_started": len(list(output.glob("*/setup-started.json"))),
            "setup_completed": len(list(output.glob("*/setup-completed.json"))),
            "setup_assessed": len(list(output.glob("*/assessed.json"))),
            "native_completed": len(list(output.glob("*/native-completed.json"))),
            "rows_assessed": len(assessments),
            "portable_inputs": [
                str(output / case / "portable/input.json") for case in ("L01", "R00")
            ],
            "gpu_readiness": False,
            "real_evaluations": "NOT_RUN",
            "linux_runtime_portability": "NOT_TESTED",
            "private_scorer_parity": None,
            "private_scorer_parity_reason": "No Kaggle/private scorer execution",
            "cpu_time_seconds": None,
            "cpu_time_reason": "Wall-clock measurements only",
        }
        (output / "summary.json").write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n"
        )
    if failure:
        raise ValueError(f"{failure}; evidence: {output}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", required=True, action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(Path(__file__).resolve().parents[1], args.output.resolve())))


if __name__ == "__main__":
    main()
