"""Coverage and rejection tests for the approved post-B180 corrections."""

import json
from pathlib import Path

import pytest

from mostaza.evaluation.context_candidate import GUARD, build_notebook
from mostaza.evaluation.context_diagnostics import (
    context_fit,
    error_category,
    read_action,
    trace_coverage,
)
from mostaza.evaluation.context_variants import (
    CONFIGURATIONS,
    configuration_files,
    expected_manifest,
)
from mostaza.evaluation.supervision_monitor import ReadOnlyMonitor
from mostaza.evaluation.verification_origin import binding_readiness, observe_origin
from mostaza.packaging import PackagingError

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    "tokens,cap,lower,status",
    [
        (16385, 16384, False, "EXCEEDS_CONTEXT"),
        (16385, 8192, False, "FITS_OBSERVED_REQUEST"),
        (16385, 8192, True, "UNKNOWN"),
        (None, 8192, False, "UNKNOWN"),
        (24577, 8192, True, "EXCEEDS_CONTEXT"),
    ],
)
def test_context_counts_do_not_turn_unknown_lower_bounds_into_fit(
    tokens, cap, lower, status
):
    assert context_fit(tokens, cap, lower_bound=lower)["status"] == status


@pytest.mark.parametrize(
    "tokens,cap", [(-1, 8192), (True, 8192), (1, 0), (1, True), (1, 32769)]
)
def test_context_invalid_counts_fail_closed(tokens, cap):
    with pytest.raises(ValueError):
        context_fit(tokens, cap)


def test_native_outcomes_are_not_reclassified_and_omissions_are_not_zero():
    trace = {"steps": [{"step_id": 3, "source": "agent", "message": "ordinary text"}]}
    measured = trace_coverage(trace)
    assert measured["retrieval_decisions"] is None
    assert measured["backend_execution"] is None
    assert measured["context_requests"][0]["prompt_tokens"] is None
    assert measured["native_outcome_modified"] is False
    assert (
        error_category("ContextWindowExceededError", verification_exit=1)
        == "CONTEXT_REJECTION"
    )
    assert error_category(None, verification_exit=1) == "VERIFICATION_FAILURE"


def test_repeated_native_ranges_trigger_bounded_alternative():
    response = {
        "status": "ok",
        "content": "line1",
        "start_line": 1,
        "end_line": 150,
        "is_truncated": True,
    }
    step = {
        "source": "agent",
        "message": "Retrieval decision: no unresolved question",
        "tool_calls": [
            {
                "function_name": "read_file",
                "arguments": {"filepath": "x.py", 'start_line"': 300},
            }
        ],
        "observation": {"content": json.dumps(response)},
    }
    result = trace_coverage({"steps": [dict(step, step_id=3), dict(step, step_id=4)]})
    assert result["read_observations"][0]["action"] == "CHECK_ARGUMENT_KEYS"
    assert result["read_observations"][1]["action"] == "USE_BOUNDED_SHELL_READ"
    assert len(result["retrieval_decisions"]) == 2
    assert (
        read_action({"filepath": "x.py", "start_line": 300}, response, duplicate=False)
        == "CHECK_RETURNED_RANGE"
    )


@pytest.mark.parametrize("configuration", CONFIGURATIONS)
def test_context_manifests_and_closures_have_explicit_unrun_identity(configuration):
    files = configuration_files(ROOT, configuration)
    manifest = expected_manifest(ROOT, configuration)
    assert manifest["ready_for_evaluation"] is False
    assert manifest["real_evaluation"] == "NOT_RUN"
    assert manifest["generation_parameters"]["max_output_tokens"] == 8192
    assert manifest["shared_conditions"]["events_compaction_config"] is None
    assert len(files) == 3


def test_unregistered_context_and_incomparable_notebook_pairs_rejected():
    with pytest.raises(PackagingError):
        expected_manifest(ROOT, "E0-B300-Q1")
    with pytest.raises(ValueError):
        build_notebook(ROOT, ("E0-C8K", "E1-C8K-Q1-R1"))
    with pytest.raises(RuntimeError, match="verifier"):
        exec(compile(GUARD, "candidate_guard", "exec"), {})


def test_sibling_probe_and_failed_install_never_claim_exact_verification():
    records = [
        {
            "phase": phase,
            "workspace_binding_matches": True,
            "status": "OBSERVED",
            "coverage": "sibling_probe_not_actual_test_process",
        }
        for phase in ("agent", "verification")
    ]
    for code in (0, 1, None):
        assert (
            binding_readiness(records, editable_install_exit_code=code)[
                "ready_for_real_evaluation"
            ]
            is False
        )


def test_unsafe_origin_request_rejected_before_any_command():
    class NoExecution:
        def exec(self, *args, **kwargs):
            raise AssertionError("Unsafe input reached execution")

    with pytest.raises(ValueError):
        observe_origin(
            NoExecution(),
            "fixture",
            module="x;echo bad",
            expected_relative_file="../x.py",
            expected_sha256="0" * 64,
            phase="verification",
        )


def test_supervisor_rejects_long_or_missing_observation_envelope(tmp_path):
    for timeout, interval in ((55, 15), (0, 15), (float("nan"), 15), (25, -1)):
        with pytest.raises(ValueError):
            ReadOnlyMonitor(
                ["fixture"],
                tmp_path / "obs",
                timeout_seconds=timeout,
                interval_seconds=interval,
            )
    monitor = ReadOnlyMonitor(["fixture"], tmp_path / "obs")
    with pytest.raises(RuntimeError):
        monitor.prelaunch(0)


def test_mutated_context_manifest_rejected_without_touching_sources(monkeypatch):
    target = ROOT / "experiments/E1-C8K/manifest.json"
    original = Path.read_text
    value = json.loads(original(target))
    value["generation_parameters"]["max_output_tokens"] = 16384

    def read(path, *args, **kwargs):
        return json.dumps(value) if path == target else original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", read)
    with pytest.raises(PackagingError, match="manifest drift"):
        configuration_files(ROOT, "E1-C8K")


def test_origin_receipt_claim_cannot_upgrade_unsupported_adapter():
    records = [
        {
            "phase": p,
            "workspace_binding_matches": True,
            "status": "OBSERVED",
            "coverage": "actual_test_process",
        }
        for p in ("agent", "verification")
    ]
    result = binding_readiness(records, editable_install_exit_code=0)
    assert result["ready_for_real_evaluation"] is False
    assert any("unsupported" in reason for reason in result["blockers"])


def test_lost_monitor_stop_control_escalates_and_ignores_secret_fields(
    tmp_path, monkeypatch
):
    import time
    from types import SimpleNamespace

    from mostaza.evaluation import supervision_monitor as module
    from mostaza.evaluation.browser_supervision import VersionIdentity

    payload = {
        "ref": "owner/fixture",
        "script_version_id": 12,
        "sdk_status": None,
        "browser_status": "RUNNING",
        "model_ready": True,
        "version_cancel_available": True,
        "secret": "MUST_NOT_PERSIST",
    }
    monkeypatch.setattr(
        module.subprocess,
        "run",
        lambda *a, **kw: SimpleNamespace(returncode=0, stdout=json.dumps(payload)),
    )
    monitor = ReadOnlyMonitor(["synthetic-reader"], tmp_path / "observe.jsonl")
    monitor.bind(
        VersionIdentity(
            "owner/fixture",
            1,
            12,
            "https://www.kaggle.com/code/owner/fixture?scriptVersionId=12",
        )
    )
    monitor.sample()
    assert "MUST_NOT_PERSIST" not in monitor.output.read_text()
    assert monitor.action(10) == "SUPERVISE_EXACT_VERSION"
    payload["version_cancel_available"] = False
    monitor.sample()
    assert monitor.action(10) == "RESTORE_EXACT_VERSION_STOP_CONTROL"
    monitor._control_lost = time.monotonic() - 61
    assert monitor.action(71) == "ESCALATE_STOP_CONTROL"
