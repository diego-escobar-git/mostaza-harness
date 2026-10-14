"""evaluation:AC-3: explicit states, source measurements and immutable publication."""

import copy
from concurrent.futures import ThreadPoolExecutor

import pytest

from mostaza.evaluation.contracts import MODEL, unavailable_metrics, validate_run
from mostaza.evaluation.import_results import import_run, load_run


def make_manifest(arm="E0"):
    return {
        "schema_version": 1,
        "experiment_id": "synthetic-only",
        "run_id": "fixture-" + arm,
        "arm": arm,
        "run_kind": "synthetic_test",
        "timestamp": "2026-10-13T00:00:00Z",
        "code_commit": "a" * 40,
        "working_tree_sha256": "b" * 64,
        "config_sha256": "c" * 64,
        "archive_sha256": "d" * 64,
        "model": MODEL,
        "resources": {
            k: {"version": "fixture", "sha256": "e" * 64, "source": "fixture"}
            for k in ("harness", "wheelhouse", "dataset")
        },
        "cohort": [
            {
                "instance_id": "fixture-1",
                "repo": "fixture/repo",
                "base_commit": "f" * 40,
                "snapshot_sha256": "1" * 64,
                "rationale": "Synthetic contract test",
            }
        ],
        "inference": {"temperature": 0},
        "budgets": {"max_tool_calls": 100},
        "environment": {"platform": "unit-test"},
        "limitations": ["Synthetic only"],
        "source_run_id": "fixture:" + arm,
    }


def make_record(manifest):
    return {
        "schema_version": 1,
        **{k: manifest[k] for k in ("experiment_id", "run_id", "arm", "run_kind")},
        "instance_id": "fixture-1",
        "status": "NOT_RUN",
        "reason": "Fixture not executed",
        "patch": {
            "present": False,
            "valid": None,
            "sha256": None,
            "validity_source": None,
            "reason": "Not generated",
        },
        "tests": {
            "outcome": "NOT_RUN",
            "exit_code": None,
            "source": None,
            "reason": "Not run",
        },
        "resolved": None,
        "metrics": unavailable_metrics("Not measured"),
        "artifacts": {},
        "ground_truth": None,
    }


def failed_record(manifest):
    record = make_record(manifest)
    record.update(status="FAIL", reason=None, resolved=False)
    record["patch"].update(
        present=True,
        sha256="2" * 64,
        valid=True,
        validity_source="fixture:git-apply",
        reason=None,
    )
    record["tests"].update(
        outcome="FAIL", exit_code=1, source="fixture:test-output", reason=None
    )
    return record


def measured(record, name, value, availability="measured"):
    record["metrics"][name].update(
        value=value, availability=availability, source="fixture:trace", reason=None
    )
    return record


def test_immutable_publication_and_concurrent_idempotence(tmp_path):
    manifest = make_manifest()
    record = make_record(manifest)
    with ThreadPoolExecutor(max_workers=4) as pool:
        paths = list(
            pool.map(lambda _: import_run(manifest, [record], tmp_path), range(8))
        )
    assert len(set(paths)) == 1
    assert load_run(paths[0]) == (manifest, [record])
    assert len(list(tmp_path.iterdir())) == 3
    records_path = next(tmp_path.glob("*.jsonl"))
    records_path.chmod(0o644)
    records_path.write_text("{}\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        load_run(paths[0])


def test_every_task_requires_record_and_no_duplicate():
    m = make_manifest()
    with pytest.raises(ValueError, match="Every cohort"):
        validate_run(m, [])
    r = make_record(m)
    with pytest.raises(ValueError, match="Duplicate"):
        validate_run(m, [r, r])


@pytest.mark.parametrize("status", ["PASS", "FAIL", "ERROR", "NOT_RUN"])
def test_outcomes_are_explicit(status):
    m = make_manifest()
    r = failed_record(m) if status in ("PASS", "FAIL") else make_record(m)
    r["status"] = status
    if status == "PASS":
        r["resolved"] = True
        r["tests"].update(outcome="PASS", exit_code=0)
    if status == "ERROR":
        r["reason"] = "Infrastructure failure"
    validate_run(m, [r])


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r["metrics"]["tokens"].update(value=0),
        lambda r: r["metrics"]["tokens"].update(reason=None),
        lambda r: r["metrics"].pop("tokens"),
        lambda r: r["patch"].update(valid=True),
        lambda r: r.update(status="PASS"),
    ],
)
def test_missing_or_fabricated_measurements_are_rejected(mutation):
    m = make_manifest()
    r = make_record(m)
    mutation(r)
    with pytest.raises(ValueError):
        validate_run(m, [r])


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1, True, 1.5])
def test_invalid_discrete_metrics(value):
    m = make_manifest()
    r = measured(failed_record(m), "tokens", value)
    with pytest.raises(ValueError):
        validate_run(m, [r])


def test_real_label_requires_source_artifacts():
    m = make_manifest() | {"run_kind": "real_kaggle"}
    r = failed_record(m)
    with pytest.raises(ValueError, match="trace/result"):
        validate_run(m, [r])


def test_timestamp_and_reference_mapping_requirements():
    m = make_manifest()
    r = measured(failed_record(m), "recall_at_k", 0.5)
    with pytest.raises(ValueError, match="post-run"):
        validate_run(m, [r])
    bad = copy.deepcopy(m)
    bad["timestamp"] = "2026-10-13T00:00:00"
    with pytest.raises(ValueError, match="UTC"):
        validate_run(bad, [make_record(bad)])


def test_same_run_identity_cannot_be_rebound(tmp_path):
    manifest = make_manifest()
    path = import_run(manifest, [make_record(manifest)], tmp_path)
    changed = copy.deepcopy(manifest)
    changed["limitations"].append("Changed evidence")
    with pytest.raises(ValueError, match="identity"):
        import_run(changed, [make_record(changed)], tmp_path)
    assert load_run(path) == (manifest, [make_record(manifest)])


def write_official_fixture(tmp_path, manifest, **changes):
    """Synthetic raw schema fixture; never a real Gemma execution."""
    import json

    from mostaza.evaluation.contracts import sha256

    trace = {
        "schema_version": "ATIF-v1.7",
        "steps": [
            {
                "source": "agent",
                "message": "Synthetic model response",
                "tool_calls": [
                    {
                        "function_name": "read_file",
                        "extra": {"usage": {"total_tokens": 12}},
                    }
                ],
                "metrics": {
                    "prompt_tokens": 5,
                    "completion_tokens": 7,
                    "total_tokens": 12,
                },
            },
        ],
        "final_metrics": {"total_tokens": 12},
    }
    traces = tmp_path / "traces"
    traces.mkdir(exist_ok=True)
    (traces / "trace_fixture-1.json").write_text(json.dumps(trace))
    patch = "diff --git a/source.py b/source.py\n"
    raw = {
        "task_id": "fixture-1",
        "repo": "fixture/repo",
        "resolved": True,
        "agent_patch": patch,
        "test_exit_code": 0,
        "test_output": "STDOUT:\n1 passed\nSTDERR:\n",
        "error_message": None,
        "duration_seconds": 1.5,
        "total_tokens": 0,
        "trace_path": "/kaggle/working/original/traces/trace_fixture-1.json",
        "_mostaza": {
            "schema_version": 1,
            "effective_agent_patch": patch,
            "original_patch_sha256": sha256(patch.encode()),
        },
    }
    raw.update(changes)
    path = tmp_path / "official-result-0001.json"
    path.write_text(json.dumps(raw))
    return path, traces / "trace_fixture-1.json"


def test_native_schema_normalization_uses_trace_usage_not_result_defaults(tmp_path):
    from mostaza.evaluation.import_results import (
        normalize_official_result,
        official_execution_receipt,
    )

    m = make_manifest()
    path, trace_path = write_official_fixture(tmp_path, m)
    record = normalize_official_result(path, m, tmp_path)
    assert record["status"] == "PASS" and record["run_kind"] == "synthetic_test"
    assert (
        record["metrics"]["tokens"]["value"] == 12
    )  # Step metrics counted once, not again per call.
    assert record["metrics"]["tool_calls"]["value"] == 1
    assert record["metrics"]["localization_seconds"]["value"] is None
    assert official_execution_receipt(m, [record])["model_inference_observed"] is True
    import json

    trace = json.loads(trace_path.read_text())
    trace["steps"][0].pop("metrics")
    trace_path.write_text(json.dumps(trace))
    record = normalize_official_result(path, m, tmp_path)
    assert record["metrics"]["tokens"]["value"] is None
    assert record["metrics"]["tokens"]["reason"]


@pytest.mark.parametrize(
    "changes,status,test_outcome,valid",
    [
        (
            {
                "resolved": False,
                "test_exit_code": 1,
                "error_message": "Agent exceeded session timeout (1.0 min)",
            },
            "FAIL",
            "FAIL",
            True,
        ),
        (
            {
                "resolved": False,
                "test_exit_code": 1,
                "test_output": "Patch failed",
                "error_message": "Failed to apply agent patch: malformed",
            },
            "FAIL",
            "NOT_RUN",
            False,
        ),
        (
            {
                "resolved": False,
                "test_exit_code": -1,
                "test_output": "",
                "error_message": "Evaluation error: infrastructure",
            },
            "ERROR",
            "NOT_RUN",
            None,
        ),
        (
            {
                "resolved": False,
                "test_exit_code": 0,
                "error_message": "Missing JUnit XML report",
            },
            "ERROR",
            "ERROR",
            True,
        ),
    ],
)
def test_official_error_and_verification_distinctions(
    tmp_path, changes, status, test_outcome, valid
):
    from mostaza.evaluation.import_results import normalize_official_result

    m = make_manifest()
    path, _ = write_official_fixture(tmp_path, m, **changes)
    record = normalize_official_result(path, m, tmp_path)
    assert record["status"] == status
    assert record["tests"]["outcome"] == test_outcome
    assert record["patch"]["valid"] is valid
    if changes.get("error_message"):
        assert record["reason"] == changes["error_message"]
    if status == "ERROR":
        assert record["resolved"] is None


def test_official_trace_identity_and_source_boundary_fail_closed(tmp_path):
    from mostaza.evaluation.import_results import normalize_official_result

    m = make_manifest()
    path, trace = write_official_fixture(tmp_path, m)
    trace.unlink()
    with pytest.raises(ValueError, match="missing"):
        normalize_official_result(path, m, tmp_path)
    path, _ = write_official_fixture(
        tmp_path, m, trace_path="/outside/trace_OTHER.json"
    )
    with pytest.raises(ValueError, match="identity"):
        normalize_official_result(path, m, tmp_path)
    with pytest.raises(ValueError, match="escapes"):
        normalize_official_result(path, m, tmp_path / "other")


def test_downloaded_notebook_payload_is_never_executed(tmp_path):
    import json

    from mostaza.evaluation.import_results import _notebook_payload

    marker = tmp_path / "must-not-exist"
    notebook = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "EMBEDDED_PAYLOAD = __import__('pathlib').Path("
                    + repr(str(marker))
                    + ").touch()\n"
                ],
            }
        ],
        "metadata": {},
    }
    path = tmp_path / "untrusted.ipynb"
    path.write_text(json.dumps(notebook))
    with pytest.raises(ValueError):
        _notebook_payload(path)
    assert not marker.exists()
