"""Bounded external read-only observation; no session start/cancel implementation."""

from __future__ import annotations

import json
import math
import subprocess
import threading
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from mostaza.evaluation.browser_supervision import VersionIdentity, supervisor_action


class ReadOnlyMonitor:
    """Run an explicitly supplied metadata reader with a hard subprocess timeout.

    The caller owns the read-only reader, audited source hash and browser controls.
    No shell is used. Each observation command must emit one JSON object.
    """

    def __init__(
        self,
        command: Sequence[str],
        output: Path,
        *,
        timeout_seconds: float = 25,
        interval_seconds: float = 15,
    ):
        if (
            not command
            or not all(isinstance(v, str) and v for v in command)
            or not math.isfinite(timeout_seconds)
            or not math.isfinite(interval_seconds)
            or timeout_seconds <= 0
            or interval_seconds < 0
            or timeout_seconds + interval_seconds > 50
        ):
            raise ValueError("Observation command must fit the sixty-second envelope")
        self.command = list(command)
        self.output = output
        self.timeout = timeout_seconds
        self.interval = interval_seconds
        self.started: float | None = None
        self.last_observed: float | None = None
        self.last_success: float | None = None
        self.last_record: dict[str, Any] | None = None
        self.identity: VersionIdentity | None = None
        self._control_lost: float | None = None
        self._stop = threading.Event()
        self._first = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.RLock()

    def sample(self) -> dict[str, Any]:
        begin = time.monotonic()
        try:
            result = subprocess.run(
                self.command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
            if result.returncode != 0:
                raise ValueError("Metadata reader failed")
            observation = json.loads(result.stdout)
            if not isinstance(observation, dict):
                raise ValueError("Invalid observation")
            allowed = {
                "ref",
                "script_version_id",
                "sdk_status",
                "browser_status",
                "model_ready",
                "version_cancel_available",
                "active_event_visible",
            }
            observation = {k: v for k, v in observation.items() if k in allowed}
            if not observation:
                raise ValueError("No usable metadata fields")
            status, reason = "OBSERVED", None
        except subprocess.TimeoutExpired:
            observation, status, reason = (
                {},
                "UNAVAILABLE",
                "Metadata reader exceeded bounded timeout",
            )
        except (OSError, ValueError):
            observation, status, reason = (
                {},
                "UNAVAILABLE",
                "Metadata reader failed or returned invalid JSON",
            )
        ended = time.monotonic()
        record = {
            "started_monotonic": begin,
            "ended_monotonic": ended,
            "timestamp_epoch": time.time(),
            "status": status,
            "reason": reason,
            "observation": observation,
            "physical_gpu_release_confirmed": None,
        }
        with self._lock:
            self.last_observed, self.last_record = ended, record
            if status == "OBSERVED":
                self.last_success = ended
            self.output.parent.mkdir(parents=True, exist_ok=True)
            with self.output.open("a") as stream:
                stream.write(json.dumps(record, sort_keys=True) + "\n")
        self._first.set()
        return record

    def start(self) -> None:
        if self._thread is not None:
            raise ValueError("Monitor already started")
        self.started = time.monotonic()

        def run() -> None:
            while not self._stop.is_set():
                self.sample()
                if self._stop.wait(self.interval):
                    return

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
        if not self._first.wait(self.timeout + 2):
            self.close()
            raise RuntimeError("Observer failed to initialize before launch")

    def prelaunch(self, t0_monotonic: float) -> dict[str, Any]:
        with self._lock:
            if (
                self._thread is None
                or not self._thread.is_alive()
                or self._stop.is_set()
                or self.started is None
                or self.last_record is None
                or self.last_record["status"] != "OBSERVED"
                or self.last_success is None
                or not math.isfinite(t0_monotonic)
                or not self.started <= self.last_success <= t0_monotonic
                or not 0 <= t0_monotonic - self.last_success <= 60
            ):
                raise RuntimeError(
                    "A live successfully initialized observer must precede external T0"
                )
            return {
                "started_monotonic": self.started,
                "first_success_precedes_t0": True,
                "t0_monotonic": t0_monotonic,
                "last_success_monotonic": self.last_success,
                "physical_release_guaranteed": False,
            }

    def bind(self, identity: VersionIdentity) -> None:
        with self._lock:
            if self.identity is not None and self.identity != identity:
                raise ValueError("Cannot retarget a monitor to another session")
            self.identity = identity

    def action(self, elapsed_seconds: float) -> str:
        with self._lock:
            if self.identity is None:
                return "RESTORE_EXACT_VERSION_STOP_CONTROL"
            record = self.last_record
            obs = {} if record is None else record["observation"]
            stale = (
                self.last_observed is None or time.monotonic() - self.last_observed > 60
            )
            if stale or record is None or record["status"] != "OBSERVED":
                return "ESCALATE_STOP_CONTROL"
            if elapsed_seconds >= 6240 and (
                obs.get("ref") != self.identity.ref
                or obs.get("script_version_id") != self.identity.script_version_id
            ):
                return "ESCALATE_STOP_CONTROL"
            now = time.monotonic()
            if obs.get("version_cancel_available") is True:
                self._control_lost = None
            elif self._control_lost is None:
                self._control_lost = now
            return supervisor_action(
                elapsed_seconds,
                expected_ref=self.identity.ref,
                expected_script_version_id=self.identity.script_version_id,
                observed_ref=obs.get("ref"),
                observed_script_version_id=obs.get("script_version_id"),
                sdk_status=obs.get("sdk_status"),
                browser_status=obs.get("browser_status"),
                version_cancel_available=obs.get("version_cancel_available") is True,
                model_ready=obs.get("model_ready"),
                active_event_visible=obs.get("active_event_visible") is True,
                control_unavailable_seconds=(
                    0 if self._control_lost is None else now - self._control_lost
                ),
                observation_failed=stale
                or record is None
                or record["status"] != "OBSERVED",
            )

    def close(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(self.timeout + 2)
