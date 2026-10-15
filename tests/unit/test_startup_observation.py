"""Local lifecycle fixtures exercise persistence, not model evaluations."""

import json
import logging
from types import SimpleNamespace

import pytest

from mostaza.evaluation.startup_observation import (
    StartupObserver,
    start_observed_server,
)


class FakeServer:
    def __init__(self, fail=False):
        self.process = None
        self.log_path = ""
        self.config = SimpleNamespace(startup_timeout=30)
        self.fail = fail
        self.probes = 0

    def build_cmd(self):
        return ["local-unit-fixture", "no-model"]

    def start(self):
        from pathlib import Path

        Path(self.log_path).write_text("weights loading\nengine startup\n")
        if self.fail:
            Path(self.log_path).unlink()  # Native failure cleanup unlinks its log.
            raise RuntimeError("fixture startup failure")
        self.process = SimpleNamespace(pid=123, poll=lambda: None)

    def is_healthy(self):
        self.probes += 1
        return False


def test_native_unlink_on_failure_cannot_erase_retained_output(tmp_path):
    observer = StartupObserver(tmp_path / "run", 0)
    try:
        with pytest.raises(RuntimeError, match="fixture startup failure"):
            start_observed_server(FakeServer(fail=True), observer)
        assert (
            observer.root / "server-retained.log"
        ).read_text() == "weights loading\nengine startup\n"
        events = [
            json.loads(x)
            for x in (observer.root / "startup-events.jsonl").read_text().splitlines()
        ]
        assert events[-1]["event"] == "server.start.failed"
        assert events[-1]["error_type"] == "RuntimeError"
    finally:
        observer.close()


def test_native_success_records_stage_and_no_extra_inference_or_health_probes(tmp_path):
    server = FakeServer()
    observer = StartupObserver(tmp_path / "run", 0)
    try:
        observer.sample()
        before = json.loads((observer.root / "startup-status.json").read_text())
        assert before["health_ready"] is None and before["server_pid"] is None
        start_observed_server(server, observer)
        ready = json.loads((observer.root / "startup-status.json").read_text())
        assert ready["phase"] == "server.ready" and ready["server_pid"] == 123
        assert ready["health_ready"] is None  # No health result was measured here.
        observer.stage("server.start.wait")
        observer.sample()
        assert (
            json.loads((observer.root / "startup-status.json").read_text())[
                "health_ready"
            ]
            is False
        )
        observer.stage("evaluation.task")
        probes = server.probes
        observer.sample()
        assert server.probes == probes
    finally:
        observer.close()


def test_close_restores_only_its_own_logging_handler_and_level(tmp_path):
    logger = logging.getLogger("adk_submission.server")
    before_level, before_handlers = logger.level, list(logger.handlers)
    observer = StartupObserver(tmp_path / "run", 0)
    observer.start()
    logger.info("native startup lifecycle fixture")
    observer.close()
    assert logger.level == before_level and logger.handlers == before_handlers
    assert (
        "native startup lifecycle fixture"
        in (observer.root / "server-lifecycle.log").read_text()
    )
    assert observer._thread is not None and not observer._thread.is_alive()


def test_missing_persistence_fails_before_start_and_observation_failure_is_visible(
    tmp_path, monkeypatch
):
    observer = StartupObserver(tmp_path / "run", 0)
    try:

        def denied(*args):
            raise OSError("local fixture filesystem lacks hard links")

        monkeypatch.setattr("mostaza.evaluation.startup_observation.os.link", denied)
        with pytest.raises(OSError):
            start_observed_server(FakeServer(), observer)
        observer.failure = "fixture telemetry failure"
        with pytest.raises(RuntimeError, match="telemetry failure"):
            observer.stage("evaluation.task")
    finally:
        observer.close()
