"Exact-version fallback and offline notebook invariants; never use GPU."

import ast
import json
from pathlib import Path

import pytest

from mostaza.evaluation.browser_supervision import (
    NOTEBOOK,
    POLICY,
    VersionIdentity,
    build_observed_notebook,
    supervisor_action,
    validate_launch_receipt,
)

ROOT = Path(__file__).resolve().parents[2]


def decide(elapsed=600, **overrides):
    values = {
        "expected_ref": "owner/unique-notebook",
        "expected_script_version_id": 358123456,
        "observed_ref": "owner/unique-notebook",
        "observed_script_version_id": 358123456,
        "sdk_status": "RUNNING",
        "browser_status": "RUNNING",
        "version_cancel_available": True,
        "model_ready": False,
        "active_event_visible": False,
    }
    values.update(overrides)
    return supervisor_action(elapsed, **values)


def test_missing_active_event_never_aborts_an_identified_controllable_version():
    assert decide() == "SUPERVISE_EXACT_VERSION"
    assert decide(sdk_status=None) == "SUPERVISE_EXACT_VERSION"
    assert decide(active_event_visible=True) == "SUPERVISE_ACTIVE_EVENT"


@pytest.mark.parametrize(
    "overrides",
    [
        {"observed_script_version_id": 358123457},
        {"observed_ref": "owner/another-notebook"},
        {"observed_script_version_id": None},
    ],
)
def test_never_cancel_a_different_or_unidentified_version(overrides):
    assert decide(7000, **overrides) == "IDENTIFY_EXACT_VERSION_OR_ESCALATE"


@pytest.mark.parametrize(
    "elapsed,ready,expected",
    [
        (1799, False, "SUPERVISE_EXACT_VERSION"),
        (1800, False, "STOP_EXACT_VERSION"),
        (1800, None, "STOP_EXACT_VERSION"),
        (1800, True, "SUPERVISE_EXACT_VERSION"),
        (6239, True, "SUPERVISE_EXACT_VERSION"),
        (6240, True, "STOP_EXACT_VERSION"),
        (float("nan"), True, "STOP_EXACT_VERSION"),
    ],
)
def test_startup_and_stop_limits(elapsed, ready, expected):
    assert decide(elapsed, model_ready=ready) == expected


def test_quota_zero_or_missing_event_is_not_terminal_confirmation():
    assert decide(sdk_status="COMPLETE") == "RECONCILE_EXACT_VERSION_STATUS"
    assert decide(sdk_status="CANCEL_REQUESTED") == "WAIT_FOR_TERMINAL_CONFIRMATION"
    assert (
        decide(sdk_status="CANCEL_ACKNOWLEDGED", browser_status="CANCEL_ACKNOWLEDGED")
        == "VERIFY_QUOTA_STABILITY_AND_CLOSE"
    )
    assert (
        decide(version_cancel_available=False) == "RESTORE_EXACT_VERSION_STOP_CONTROL"
    )
    assert (
        decide(6240, model_ready=True, version_cancel_available=False)
        == "ESCALATE_STOP_CONTROL"
    )
    assert decide(observation_failed=True) == "STOP_EXACT_VERSION"


def test_observed_notebook_keeps_inputs_and_agent_settings_and_is_unapproved():
    nb = json.loads(build_observed_notebook(ROOT))
    base = json.loads(
        (ROOT / "notebooks/mostaza-phase2-budget-retrieval.ipynb").read_text()
    )
    assert (
        nb["metadata"]["mostaza"]["payload_sha256"]
        == base["metadata"]["mostaza"]["payload_sha256"]
    )
    assert nb["metadata"]["kaggle"] == {
        "isGpuEnabled": False,
        "isInternetEnabled": False,
    }
    assert nb["metadata"]["mostaza"]["observed_preparation"]["authorization"] is None
    guard = "".join(nb["cells"][1]["source"])
    with pytest.raises(RuntimeError, match="authorization is absent"):
        exec(guard, {})
    old = guard.replace(
        "BROWSER_AUTHORIZATION = None",
        (
            "BROWSER_AUTHORIZATION = {'approved': True, 'p"
            "olicy': {'batch': 'B180-initial'}}"
        ),
        1,
    )
    with pytest.raises(RuntimeError, match="authorization is absent"):
        exec(old, {})
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            ast.parse("".join(cell["source"]), feature_version=(3, 12))
    code = "".join(nb["cells"][-1]["source"])
    for setting in (
        "timeout_seconds=180",
        "verification_timeout_seconds=300",
        "max_tool_calls=30",
        "max_time_minutes=3",
        "max_turns=50",
        "concurrency=1",
    ):
        assert setting in code
    assert "start_observed_server" in code
    assert code.index("STARTUP_OBSERVER.close()") < code.rindex("export_sources()")
    assert POLICY["request_stop_seconds"] == 104 * 60
    assert POLICY["last_admission_seconds"] + 600 + 300 == 6240
    assert build_observed_notebook(ROOT) == (ROOT / NOTEBOOK).read_bytes()


@pytest.mark.parametrize(
    "url",
    [
        "https://www.kaggle.com/code/owner/name",
        "https://www.kaggle.com/code/owner/name?scriptVersionId=1",
        ("https://www.kaggle.com/code/owner/other?scriptVersionId=358123456"),
        "https://example.com/code/owner/name?scriptVersionId=358123456",
    ],
)
def test_version_number_never_substitutes_for_opaque_id(url):
    with pytest.raises(ValueError):
        VersionIdentity("owner/name", 1, 358123456, url)


def test_browser_observed_version_url_binds_exact_identity():
    value = VersionIdentity(
        "owner/name",
        1,
        358123456,
        ("https://www.kaggle.com/code/owner/name?scriptVersionId=358123456"),
    )
    assert value.version_number != value.script_version_id
    assert (
        decide(sdk_status="COMPLETE", browser_status="ERROR")
        == "RECONCILE_EXACT_VERSION_STATUS"
    )


def launch_fixture():
    # Controller data fixture only; never passed to Kaggle or a model.
    import time

    return {
        "policy": POLICY.copy(),
        "approved": True,
        "approval_id": "local-unit-fixture",
        "single_use_id": "00000000-0000-4000-8000-000000000001",
        "ref": "diegofescobar/mostaza-b180-" + "0" * 32,
        "code_commit": "0" * 40,
        "t0_epoch": time.time(),
        "quota_observed_epoch": time.time() - 1,
        "remaining_quota_seconds": 28800,
        "reserved_quota_seconds": 0,
        "active_events": 0,
        "prelaunch_latest_versions_terminal": True,
        "prelaunch_quota_stable": True,
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("single_use_id", "../escape"),
        ("ref", "owner/old-notebook"),
        ("code_commit", "uncommitted"),
        ("quota_observed_epoch", 0),
        ("prelaunch_latest_versions_terminal", False),
        ("prelaunch_quota_stable", False),
        ("approved", False),
        ("reserved_quota_seconds", None),
        ("active_events", None),
    ],
)
def test_bound_receipt_fails_closed_without_new_scope_and_fresh_preflight(field, value):
    receipt = launch_fixture()
    receipt[field] = value
    with pytest.raises(RuntimeError):
        validate_launch_receipt(receipt)


def test_binding_valid_fixture_does_not_run_any_notebook_code(tmp_path):
    receipt = launch_fixture()
    validate_launch_receipt(receipt)
    notebook = json.loads(build_observed_notebook(ROOT, receipt))
    assert (
        notebook["metadata"]["mostaza"]["observed_preparation"]["authorization"]
        == "local-unit-fixture"
    )
    assert all(
        not c.get("outputs") and c.get("execution_count") is None
        for c in notebook["cells"]
    )
    assert not notebook["metadata"]["kaggle"]["isGpuEnabled"]
    with pytest.raises(ValueError, match="Unknown or missing"):
        validate_launch_receipt(
            {**receipt, "unexpected_secret": "must-not-be-embedded"}
        )


def test_unconfirmed_stop_and_unrestored_control_escalate_with_bounded_wait():
    assert (
        decide(6300, sdk_status="CANCEL_REQUESTED")
        == "ESCALATE_UNCONFIRMED_TERMINATION"
    )
    assert (
        decide(version_cancel_available=False, control_unavailable_seconds=60)
        == "ESCALATE_STOP_CONTROL"
    )
    assert (
        decide(expected_script_version_id=0, observed_script_version_id=0)
        == "IDENTIFY_EXACT_VERSION_OR_ESCALATE"
    )
