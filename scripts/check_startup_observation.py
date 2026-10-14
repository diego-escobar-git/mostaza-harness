"""Native lifecycle checks with CPU-only local fixtures; no model evaluation."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import socket
import sys
import tempfile
import time
from importlib.metadata import version
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mostaza.evaluation.startup_observation import (
    StartupObserver,
    start_observed_server,
)


def check() -> dict[str, Any]:
    native = importlib.import_module("adk_submission")
    source = importlib.import_module("adk_submission.server")
    if version("adk-submission") != "0.2.13":
        raise ValueError("Pinned native lifecycle required")
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    http = (
        "from http.server import HTTPServer,BaseHTTPRequestHandler\n"
        "print('LOCAL_CPU_FIXTURE_STARTED',flush=True)\n"
        "class Handler(BaseHTTPRequestHandler):\n"
        " def do_GET(self):\n"
        "  self.send_response(200);self.end_headers()\n"
        f"HTTPServer(('127.0.0.1',{port}),Handler).serve_forever()\n"
    )
    source_path = source.__file__
    if source_path is None:
        raise ValueError("Native source file is unavailable")
    outcomes = []
    with tempfile.TemporaryDirectory(prefix="mostaza-local-observer-") as temporary:
        for name, command in (
            ("healthy", [sys.executable, "-u", "-c", http]),
            (
                "timeout",
                [
                    sys.executable,
                    "-u",
                    "-c",
                    http.replace("send_response(200)", "send_response(503)"),
                ],
            ),
            (
                "exits",
                [
                    sys.executable,
                    "-u",
                    "-c",
                    "print('LOCAL_CPU_EXIT_FIXTURE',flush=True);raise SystemExit(7)",
                ],
            ),
        ):
            server = native.VllmServer(
                native.VllmConfig(
                    model="LOCAL_CPU_FIXTURE_NO_MODEL",
                    port=port,
                    startup_timeout=1,
                    health_check_interval=0.05,
                )
            )
            server.build_cmd = lambda command=command: command
            observer = StartupObserver(
                Path(temporary) / name, time.time(), interval=0.05
            )
            observer.start()
            observed_failure = False
            try:
                try:
                    start_observed_server(server, observer)
                except native.ServerStartupError:
                    observed_failure = True
                if observed_failure != (name != "healthy"):
                    raise AssertionError("Unexpected native fixture outcome")
            finally:
                server.stop(timeout=1)
                observer.close()
            retained = (observer.root / "server-retained.log").read_text()
            expected = (
                "LOCAL_CPU_FIXTURE_STARTED"
                if name != "exits"
                else "LOCAL_CPU_EXIT_FIXTURE"
            )
            if expected not in retained:
                raise AssertionError("Native stop erased captured output")
            if name in {"healthy", "timeout"} and Path(server.log_path).exists():
                raise AssertionError("Native cleanup did not exercise unlink")
            outcomes.append(
                {
                    "fixture": name,
                    "expected_failure_observed": observed_failure,
                    "retained_after_native_stop": True,
                }
            )
    return {
        "kind": "local_cpu_native_lifecycle_fixtures",
        "gpu_used": False,
        "model_evaluations": 0,
        "native_version": version("adk-submission"),
        "native_server_source_sha256": hashlib.sha256(
            Path(source_path).read_bytes()
        ).hexdigest(),
        "outcomes": outcomes,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = check()
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
