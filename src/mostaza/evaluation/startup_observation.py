"Persistent startup observations; no model or accelerator operations."

from __future__ import annotations

import json
import logging
import os
import sys
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class StartupObserver:
    "Keep events and native subprocess output even if cleanup unlinks its log."

    def __init__(self, root: Path, launch_epoch: float, interval: float = 5.0):
        if interval <= 0:
            raise ValueError("Observation interval must be positive")
        root.mkdir(parents=True, exist_ok=False)
        self.root = root
        self.launch_epoch = launch_epoch
        self.interval = interval
        self.started = time.monotonic()
        self.phase = "observer.ready"
        self.server: Any = None
        self.failure: str | None = None
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._log_offset = 0
        self._logger = logging.getLogger("adk_submission.server")
        self._old_level = self._logger.level
        self._handler = logging.FileHandler(root / "server-lifecycle.log")
        self._handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        self._logger.addHandler(self._handler)
        self._logger.setLevel(logging.INFO)
        (root / "startup-schema.json").write_text(
            json.dumps(
                {
                    "since_launch_seconds": (
                        "seconds from external UTC epoch; in"
                        "cludes queue/startup, not pure mode"
                        "l time"
                    ),
                    "observer_monotonic_seconds": (
                        "seconds since observer initialization, not allocation start"
                    ),
                    "server_log_bytes": (
                        "bytes in retained native subprocess output at sampling time"
                    ),
                    "health_ready": (
                        "Native health probe Boolean only du"
                        "ring startup; False does not distin"
                        "guish refusal/timeout/non-200"
                    ),
                    "server_return_code": (
                        "Native process poll exit code; null"
                        " while running or without a process"
                        " handle; see server_process_state"
                    ),
                    "new_log_text": (
                        "Up to4096 newly read bytes decoded "
                        "as UTF8 replacement; full bytes ret"
                        "ained in server-retained.log"
                    ),
                    "coverage": (
                        "Heartbeat snapshots every5seconds p"
                        "lus native probe latency; not exhau"
                        "stive process or model timing"
                    ),
                },
                sort_keys=True,
            )
            + "\n"
        )
        self.event("observer.ready", physical_gpu_release_confirmed=None)

    def event(self, kind: str, **details: Any) -> None:
        with self._lock:
            now = time.time()
            record = {
                "event": kind,
                "phase": self.phase,
                "timestamp_utc": datetime.fromtimestamp(now, UTC).isoformat(),
                "since_launch_seconds": now - self.launch_epoch,
                "observer_monotonic_seconds": time.monotonic() - self.started,
                **details,
            }
            text = json.dumps(record, sort_keys=True)
            with (self.root / "startup-events.jsonl").open("a") as stream:
                stream.write(text + "\n")
                stream.flush()
            pending = self.root / ".startup-status.tmp"
            pending.write_text(text + "\n")
            pending.replace(self.root / "startup-status.json")
            print("MOSTAZA_OBSERVATION " + text, flush=True)

    def stage(self, name: str) -> None:
        self.check()
        self.phase = name
        self.event("stage")

    def start(self) -> None:
        if self._thread is not None:
            raise ValueError("Observer already started")
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def bind_server(self, server: Any) -> None:
        "Hard link on one filesystem: native stop can unlink only its own name."
        self.check()
        source = self.root / "server-source.log"
        retained = self.root / "server-retained.log"
        with source.open("xb"):
            pass
        os.link(source, retained)  # Fail before model startup if persistence fails.
        server.log_path = str(source)
        self.server = server
        self.event("server.log.bound", retained_log=retained.name)

    def sample(self) -> None:
        details: dict[str, Any] = {
            "server_pid": None,
            "server_return_code": None,
            "health_ready": None,
            "server_log_bytes": None,
            "new_log_text": None,
            "server_process_state": "UNBOUND",
            "health_probe_reason": "not_probed_no_process",
            "server_log_reason": "server_not_bound",
            "new_log_reason": "server_not_bound",
        }
        with self._lock:
            if self.server is not None:
                details["server_process_state"] = "NOT_SPAWNED_OR_HANDLE_CLEARED"
                process = self.server.process
                if process is not None:
                    details["server_pid"] = process.pid
                    details["server_return_code"] = process.poll()
                    details["server_process_state"] = (
                        "RUNNING" if details["server_return_code"] is None else "EXITED"
                    )
                    details["health_probe_reason"] = "not_probed_outside_startup"
                    if self.phase == "server.start.wait":
                        # Native health probe: two-second timeout, no inference.
                        details["health_ready"] = self.server.is_healthy()
                        details["health_probe_reason"] = None
                path = self.root / "server-retained.log"
                if path.exists():
                    details["server_log_reason"] = None
                    details["new_log_reason"] = "no_new_bytes"
                    details["server_log_bytes"] = path.stat().st_size
                    with path.open("rb") as stream:
                        stream.seek(self._log_offset)
                        data = stream.read(4096)
                    self._log_offset += len(data)
                    if data:
                        details["new_log_text"] = data.decode(errors="replace")
                        details["new_log_reason"] = None
                else:
                    details["server_log_reason"] = "retained_log_missing"
                    details["new_log_reason"] = "retained_log_missing"
            self.event("heartbeat", **details)

    def check(self) -> None:
        if self.failure is not None:
            raise RuntimeError("Startup observation failed: " + self.failure)

    def _run(self) -> None:
        while not self._stop.wait(self.interval):
            try:
                self.sample()
            except Exception as error:
                self.failure = type(error).__name__ + ": " + str(error)
                print(
                    "MOSTAZA_OBSERVATION_ERROR " + self.failure,
                    file=sys.stderr,
                    flush=True,
                )
                return

    def close(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=4)
        self._logger.removeHandler(self._handler)
        self._handler.close()
        self._logger.setLevel(self._old_level)
        self.event("observer.closed", observation_failure=self.failure)


def start_observed_server(server: Any, observer: StartupObserver) -> None:
    "Use the unchanged native start method, with durable context on either exit."
    observer.bind_server(server)
    observer.stage("server.start.wait")
    observer.event(
        "server.start.requested",
        startup_timeout_seconds=server.config.startup_timeout,
        command=server.build_cmd(),
    )
    try:
        server.start()
    except BaseException as error:
        observer.event(
            "server.start.failed",
            error_type=type(error).__name__,
            error_message=str(error)[-4096:],
        )
        raise
    observer.check()
    observer.stage("server.ready")
    observer.sample()
