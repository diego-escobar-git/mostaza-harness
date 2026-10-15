"""Stop observed owned groups and verify exit; transient signal errors are evidence."""

from __future__ import annotations

import json
import signal
import subprocess
import time
import traceback
from collections.abc import Callable
from pathlib import Path
from typing import Any


def read_process_table(
    deadline: float, measurements: list[dict[str, Any]]
) -> dict[int, tuple[int, int, str]]:
    """Read once within the shared deadline; absence must be observed."""
    started = time.monotonic()
    remaining = deadline - started
    if remaining <= 0:
        raise TimeoutError("No process observation budget remains")
    timeout = min(5.0, remaining)
    record: dict[str, Any] = {
        "timeout_seconds": timeout,
        "duration_seconds": None,
        "table_available": False,
        "process_count": None,
        "process_count_reason": "Observation not completed",
    }
    try:
        output = subprocess.run(
            ["/bin/ps", "-ww", "-axo", "pid=,ppid=,pgid=,command="],
            check=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        ).stdout
        if time.monotonic() > deadline:
            raise TimeoutError("Process observation exceeded its shared deadline")
        table = {}
        for line in output.splitlines():
            if not line.strip():
                continue
            parts = line.strip().split(maxsplit=3)
            if len(parts) != 4:
                raise ValueError("Malformed process observation")
            pid, parent, group = (int(value) for value in parts[:3])
            if pid < 0 or parent < 0 or group < 0 or pid in table:
                raise ValueError("Invalid or duplicate process identity")
            table[pid] = (parent, group, parts[3])
        if not table:
            raise ValueError("Empty process observation is unavailable, not exit proof")
        record.update(
            table_available=True,
            process_count=len(table),
            process_count_reason=None,
            outcome="observed",
        )
        return table
    except Exception as error:
        record.update(outcome=type(error).__name__, process_count_reason=str(error))
        raise
    finally:
        record["duration_seconds"] = time.monotonic() - started
        measurements.append(record)


def survivors(
    table: dict[int, tuple[int, int, str]],
    known: dict[int, tuple[int, int, str]],
) -> dict[int, tuple[int, int, str]]:
    return {
        pid: current
        for pid, current in table.items()
        if pid in known and current[1:] == known[pid][1:]
    }


def stop_group(
    process: subprocess.Popen[bytes],
    known: dict[int, tuple[int, int, str]],
    watchdog: Any,
) -> dict[str, Any]:
    """Never turn a vanished group into failure or suppress a live survivor."""
    import os

    errors = []
    table = watchdog.process_table()
    if process.poll() is None:
        watchdog.remember_descendants(process.pid, table, known)
    for sig in (signal.SIGTERM, signal.SIGKILL):
        live = survivors(table, known)
        groups = {entry[1] for entry in live.values()}
        if process.poll() is None:
            groups.add(process.pid)
        for group in sorted(groups):
            try:
                os.killpg(group, sig)
            except ProcessLookupError:
                pass
            except PermissionError as error:
                # A setuid read-only ps descendant may outlive its ordinary
                # parent briefly. Do not infer exit from this error: verify it.
                errors.append(
                    {
                        "group": group,
                        "signal": int(sig),
                        "error": str(error),
                    }
                )
        try:
            process.wait(timeout=3 if sig == signal.SIGTERM else 5)
        except subprocess.TimeoutExpired:
            pass
        table = watchdog.process_table()
        if process.poll() is None:
            watchdog.remember_descendants(process.pid, table, known)
    # Bounded grace for already exiting monitor helpers; no command/case retry.
    deadline = time.monotonic() + 2
    while survivors(table, known) and time.monotonic() < deadline:
        time.sleep(0.05)
        table = watchdog.process_table()
    live = survivors(table, known)
    if live or process.poll() is None:
        raise PermissionError(
            f"Owned process cleanup incomplete; pids={sorted(live)}; "
            f"signal_errors={errors}"
        )
    return {"complete": True, "signal_errors": errors, "survivors": []}


class CleanupIncomplete(PermissionError):
    """Carry truthful partial cleanup evidence even when observation fails."""

    def __init__(self, receipt: dict[str, Any]) -> None:
        self.receipt = receipt
        super().__init__(f"Owned process cleanup incomplete: {receipt}")


def stop_group_bounded(
    process: subprocess.Popen[bytes],
    known: dict[int, tuple[int, int, str]],
    watchdog: Any,
    deadline: float,
    measurements: list[dict[str, Any]],
) -> dict[str, Any]:
    """Bound cleanup; never skip owned-root signals on read error."""
    import os

    errors: list[dict[str, Any]] = []
    observation_errors: list[str] = []
    table: dict[int, tuple[int, int, str]] = {}

    def observe() -> None:
        nonlocal table
        try:
            table = read_process_table(deadline, measurements)
            if process.poll() is None:
                watchdog.remember_descendants(process.pid, table, known)
            for pid in list(survivors(table, known)):
                if pid != process.pid:
                    watchdog.remember_descendants(pid, table, known)
        except Exception as error:
            observation_errors.append(f"{type(error).__name__}: {error}")
            # A stale table cannot justify signals to possibly reused child PIDs.
            table = {}

    observe()
    for sig, wait_seconds in ((signal.SIGTERM, 3.0), (signal.SIGKILL, 5.0)):
        groups = {
            entry[1] for entry in survivors(table, known).values() if entry[1] > 0
        }
        # Popen is our still-live session leader; this ownership does not depend
        # on successful ps. Never skip its termination because discovery failed.
        if process.poll() is None:
            groups.add(process.pid)
        for group in sorted(groups):
            try:
                os.killpg(group, sig)
            except ProcessLookupError:
                pass
            except PermissionError as error:
                errors.append({"group": group, "signal": int(sig), "error": str(error)})
        try:
            process.wait(
                timeout=max(0.0, min(wait_seconds, deadline - time.monotonic()))
            )
        except subprocess.TimeoutExpired:
            pass
        observe()
    grace = min(deadline, time.monotonic() + 2.0)
    while survivors(table, known) and time.monotonic() < grace:
        time.sleep(min(0.05, max(0.0, grace - time.monotonic())))
        observe()
    live = survivors(table, known)
    verifiable = not observation_errors
    receipt = {
        "complete": verifiable
        and not live
        and process.poll() is not None
        and time.monotonic() <= deadline,
        "signal_errors": errors,
        "observation_errors": observation_errors,
        "survivors": sorted(live) if verifiable else None,
        "survivors_reason": None
        if verifiable
        else "One or more cleanup observations unavailable; absence not proven",
        "root_exited": process.poll() is not None,
    }
    if not receipt["complete"]:
        raise CleanupIncomplete(receipt)
    return receipt


class SupervisionFailure(ValueError):
    """Preserve independent work and cleanup errors in one durable receipt."""

    def __init__(self, receipt: dict[str, Any]) -> None:
        self.receipt = receipt
        super().__init__(
            f"Work: {receipt['work_error']}; cleanup: {receipt['cleanup_error']}; "
            f"persistence: {receipt.get('persistence_errors', [])}"
        )


def supervise(
    process: subprocess.Popen[bytes],
    known: dict[int, tuple[int, int, str]],
    watchdog: Any,
    work_deadline: float,
    cleanup_deadline: float,
    check: Callable[[], None],
    receipt_path: Path,
) -> dict[str, Any]:
    """Observe at most1Hz, check caps at0.2s, and retain every termination outcome."""
    measurements: list[dict[str, Any]] = []
    result: dict[str, Any] = {
        "status": "RUNNING",
        "work_deadline": work_deadline,
        "cleanup_deadline": cleanup_deadline,
        "discovery_interval_seconds": 1.0,
        "cap_check_interval_seconds": 0.2,
        "read_timeout_maximum_seconds": 5.0,
        "work_error": None,
        "work_traceback": None,
        "cleanup_error": None,
        "cleanup_traceback": None,
        "process_cleanup": None,
        "observations": measurements,
        "persistence_errors": [],
    }

    def persist() -> None:
        try:
            receipt_path.write_text(json.dumps(result, indent=2) + "\n")
        except Exception as error:
            result["persistence_errors"].append(f"{type(error).__name__}: {error}")
            raise

    next_observation = 0.0
    try:
        persist()
        while process.poll() is None:
            now = time.monotonic()
            if now >= work_deadline:
                raise TimeoutError("Work deadline exhausted; cleanup reserve preserved")
            if now >= next_observation:
                try:
                    table = read_process_table(work_deadline, measurements)
                    if process.poll() is None:
                        watchdog.remember_descendants(process.pid, table, known)
                    for pid in list(survivors(table, known)):
                        if pid != process.pid:
                            watchdog.remember_descendants(pid, table, known)
                finally:
                    if measurements:
                        measurements[-1]["phase"] = "work"
                    next_observation = time.monotonic() + 1.0
                    persist()
            check()
            if time.monotonic() >= work_deadline:
                raise TimeoutError("Work deadline exhausted; cleanup reserve preserved")
            time.sleep(min(0.2, max(0.0, work_deadline - time.monotonic())))
        if time.monotonic() > work_deadline:
            raise TimeoutError("Work completion observed after its deadline")
    except Exception as error:
        result["work_error"] = f"{type(error).__name__}: {error}"
        result["work_traceback"] = traceback.format_exc()
    finally:
        first_cleanup = len(measurements)
        try:
            result["process_cleanup"] = stop_group_bounded(
                process, known, watchdog, cleanup_deadline, measurements
            )
        except Exception as error:
            result["cleanup_error"] = f"{type(error).__name__}: {error}"
            result["cleanup_traceback"] = traceback.format_exc()
            result["process_cleanup"] = (
                error.receipt
                if isinstance(error, CleanupIncomplete)
                else {
                    "complete": False,
                    "survivors": None,
                    "survivors_reason": "Cleanup failed without verified exit receipt",
                }
            )
        finally:
            for entry in measurements[first_cleanup:]:
                entry["phase"] = "cleanup"
            result["exit_code"] = process.poll()
            result["status"] = (
                "FAILED"
                if result["work_error"]
                or result["cleanup_error"]
                or result["persistence_errors"]
                else "COMPLETE"
            )
            try:
                persist()
            except Exception:
                result["status"] = "FAILED"
    if result["status"] == "FAILED":
        raise SupervisionFailure(result)
    return result
