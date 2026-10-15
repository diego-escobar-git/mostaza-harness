"""budget-retrieval-calibration:AC-3/4/5: fixtures never represent real runs."""

import copy
import json

import pytest

from mostaza.evaluation.contracts import canonical_json
from mostaza.research.trace_diagnostics import classify_command, diagnose_trace


def event(index, tool="run_command", arguments=None, response=None, elapsed=1.0):
    return {
        "step_id": index,
        "source": "agent",
        "tool_calls": [
            {
                "tool_call_id": f"call-{index}",
                "function_name": tool,
                "arguments": arguments or {},
                "extra": {"elapsed_s": elapsed, "usage": {"total_tokens": 9999}},
            }
        ],
        "observation": {
            "content": json.dumps(
                response if response is not None else {"status": "ok"}
            ),
            "extra": {"tool_name": tool, "elapsed_s": elapsed + 0.25},
        },
        "metrics": {"prompt_tokens": 5, "completion_tokens": 7, "total_tokens": 12},
        "extra": {"elapsed_s": elapsed},
    }


def diagnose(tmp_path, steps, raw=None):
    trace = tmp_path / "trace_fixture.json"
    result = tmp_path / "official-result.json"
    trace.write_bytes(
        canonical_json(
            {
                "schema_version": "ATIF-v1.7",
                "steps": steps,
                "final_metrics": {"total_tokens": 99999},
            }
        )
    )
    result.write_bytes(
        canonical_json(
            {
                "task_id": "fixture",
                "trace_path": "/kaggle/traces/trace_fixture.json",
                "tool_calls": 1,
                "agent_patch": "",
                "test_exit_code": -1,
                "resolved": False,
            }
            | (raw or {})
        )
    )
    return diagnose_trace(trace, result, tmp_path)


def test_native_usage_once_and_separate_counters_and_intervals(tmp_path):
    steps = [
        event(1, arguments={"command": 'grep -n "symbol" file.py'}),
        event(2, "get_status", elapsed=5),
        event(
            3,
            "read_file",
            response={"status": "error", "error_type": "BudgetExceeded"},
            elapsed=8,
        ),
    ]
    row = diagnose(
        tmp_path,
        steps,
        {"tool_calls": 1, "error_message": "Agent exceeded session timeout (1.0 min)"},
    )
    metrics = row["metrics"]
    assert metrics["tokens"]["value"] == 36
    assert metrics["recorded_attempts"]["value"] == 3
    assert metrics["lexical_command_attempts"]["value"] == 1
    assert metrics["exempt_attempts"]["value"] == 1
    assert metrics["rejected_attempts"]["value"] == 1
    assert metrics["official_charged_calls"]["value"] == 1
    assert row["timeout"]["value"].startswith("Agent exceeded")
    assert row["adjacent_agent_intervals"][0]["value"] == 4
    assert row["calls"][0]["response_interval"]["value"] == 0.25
    assert metrics["pure_model_seconds"]["value"] is None
    assert metrics["localization_seconds"]["reason"]
    assert metrics["recorded_attempts"]["coverage"]["complete_execution"] is False
    assert row["calls"][0]["source"].endswith("#/steps/0/tool_calls/0")
    assert "@sha256:" in row["calls"][0]["source"]


@pytest.mark.parametrize(
    "command, expected",
    [
        ("rg symbol src", "lexical"),
        ('grep -n "foo bar" file', "lexical"),
        ("grep foo file | head", "unknown"),
        ("grep foo; cat bar", "unknown"),
        ("python3 script.py", "unknown"),
        ("sh -c 'grep foo'", "unknown"),
        ("", "unknown"),
        (None, "unknown"),
        ("grep 'unterminated", "unknown"),
        ("rg $(cat key)", "unknown"),
    ],
)
def test_command_classification_is_observed_and_conservative(command, expected):
    assert classify_command(command) == expected


@pytest.mark.parametrize("backend", [None, "vector", "lexical_fallback"])
def test_similarity_attempt_does_not_prove_vector_backend(tmp_path, backend):
    response = {
        "status": "ok",
        "results": [{"similarity": 0.9, "node_name": "module.Symbol"}],
        "is_truncated": True,
    }
    if backend:
        response["backend"] = backend
    row = diagnose(tmp_path, [event(1, "search_similar_code", response=response)])
    assert row["metrics"]["similarity_attempts"]["value"] == 1
    assert row["calls"][0]["similarity_backend"] == backend
    assert row["calls"][0]["response_truncated"] is True
    if backend is None:
        assert row["calls"][0]["backend_reason"]


@pytest.mark.parametrize(
    "field,value",
    [
        ("metrics", None),
        ("metrics", {}),
        ("metrics", {"total_tokens": True}),
        ("metrics", {"total_tokens": -1}),
        ("metrics", {"total_tokens": 12, "prompt_tokens": 5, "completion_tokens": 10}),
        ("metrics", {"prompt_tokens": 5}),
    ],
)
def test_missing_malformed_inconsistent_usage_never_zero(tmp_path, field, value):
    step = event(1)
    step[field] = value
    row = diagnose(tmp_path, [step, event(2)])
    assert row["metrics"]["tokens"]["value"] is None
    assert row["metrics"]["tokens"]["reason"]
    assert row["coverage"]["usage_steps"] == 1


@pytest.mark.parametrize(
    "mutation",
    [
        lambda s: s.pop("tool_calls"),
        lambda s: s.update(tool_calls=None),
        lambda s: s["tool_calls"][0].pop("function_name"),
        lambda s: s["tool_calls"][0].pop("tool_call_id"),
    ],
)
def test_incomplete_attempt_telemetry_never_zero(tmp_path, mutation):
    step = event(1)
    mutation(step)
    row = diagnose(tmp_path, [step])
    assert row["metrics"]["recorded_attempts"]["value"] is None
    assert row["metrics"]["similarity_attempts"]["value"] is None
    assert row["coverage"]["issues"]


def test_duplicate_step_or_call_ids_fail_closed_without_double_count(tmp_path):
    first, second = event(1), event(2)
    second["tool_calls"][0]["tool_call_id"] = "call-1"
    row = diagnose(tmp_path, [first, second])
    assert row["metrics"]["tokens"]["value"] is None
    assert row["metrics"]["recorded_attempts"]["value"] is None
    row = diagnose(tmp_path, [first, copy.deepcopy(first)])
    assert row["metrics"]["tokens"]["value"] is None
    assert len(row["calls"]) == 1


@pytest.mark.parametrize("steps", [None, [], [None], [{}]])
def test_empty_or_malformed_steps_are_unavailable(tmp_path, steps):
    row = diagnose(tmp_path, steps, {"tool_calls": None})
    assert row["metrics"]["recorded_attempts"]["value"] is None
    assert row["metrics"]["official_charged_calls"]["value"] is None
    assert row["metrics"]["tokens"]["value"] is None


@pytest.mark.parametrize(
    "mutation",
    [
        lambda s: s.pop("observation"),
        lambda s: s["observation"].update(content="malformed JSON"),
        lambda s: s["observation"]["extra"].update(tool_name="other"),
        lambda s: s["observation"]["extra"].pop("elapsed_s"),
        lambda s: s["observation"]["extra"].update(elapsed_s=0),
    ],
)
def test_missing_mismatched_or_reversed_response_timing(tmp_path, mutation):
    step = event(1)
    mutation(step)
    row = diagnose(tmp_path, [step])
    # Malformed content still has observable matching timestamps, but no status.
    if step.get("observation", {}).get("content") != "malformed JSON":
        assert row["calls"][0]["response_interval"]["value"] is None
    if (
        not step.get("observation")
        or step["observation"].get("content") == "malformed JSON"
        or step["observation"]["extra"].get("tool_name") == "other"
    ):
        assert row["metrics"]["rejected_attempts"]["value"] is None


def test_parallel_calls_require_explicit_response_identity(tmp_path):
    step = event(1)
    step["tool_calls"].append(event(2)["tool_calls"][0])
    row = diagnose(tmp_path, [step])
    assert all(c["response_interval"]["value"] is None for c in row["calls"])
    step["observation"]["extra"]["tool_call_id"] = "call-1"
    row = diagnose(tmp_path, [step])
    assert row["calls"][0]["response_interval"]["value"] == 0.25
    assert row["calls"][1]["response_interval"]["value"] is None


def test_graph_nodes_and_read_ranges_only_when_observed(tmp_path):
    args = {"filepath": "source.py", "start_line": 10, "end_line": 20}
    steps = [
        event(1, "read_file", args),
        event(2, "read_file", args),
        event(
            3,
            "get_code_neighbors",
            response={
                "status": "ok",
                "neighbors": ["m.A", "m.B"],
                "is_truncated": True,
            },
        ),
        event(4, "read_file", {"filepath": "source.py", 'start_line"': 10}),
    ]
    row = diagnose(tmp_path, steps)
    assert row["metrics"]["repeated_explicit_read_ranges"]["value"] == 1
    assert row["calls"][2]["returned_graph_nodes"] == ["m.A", "m.B"]
    assert row["calls"][2]["response_truncated"] is True
    assert row["calls"][3]["explicit_read_range"] is None
    assert row["metrics"]["full_unique_files"]["value"] is None


def test_patch_and_verification_remain_independent_and_host_only(tmp_path):
    patch = (
        "diff --git a/repro.py b/repro.py\nnew file mode 100644\n"
        "+try:\n+    assert False\n+except AssertionError:\n"
        "+    print('Test failed')\n"
    )
    row = diagnose(
        tmp_path,
        [
            event(
                1,
                response={
                    "status": "ok",
                    "exit_code": 0,
                    "stdout": "Test failed: Expected None",
                },
            )
        ],
        {
            "agent_patch": patch,
            "_mostaza": {"effective_agent_patch": patch},
            "resolved": False,
            "test_exit_code": 1,
            "test_output": (
                "PRIVATE HIDDEN CONTENT\n1 failed, 205 passed, 13 skipped in 0.33s"
            ),
        },
    )
    assert row["generated_patch"]["present"] is True
    assert row["effective_patch"]["changed_files"] == ["repro.py"]
    assert row["verification"]["summary"] == {"failed": 1, "passed": 205, "skipped": 13}
    assert row["verification"]["resolved"] is False
    assert row["verification"]["host_only"] is True
    assert row["requests_postrun_finding"]["zero_exit_with_failure_events"]
    assert b"PRIVATE HIDDEN" not in canonical_json(row)
    assert b"assert False" not in canonical_json(row)


def test_missing_patch_and_verification_are_unknown(tmp_path):
    row = diagnose(
        tmp_path,
        [event(1)],
        {"agent_patch": None, "resolved": None, "test_exit_code": None},
    )
    assert row["generated_patch"]["present"] is None
    assert row["effective_patch"]["present"] is None
    assert row["verification"]["resolved"] is None
    assert row["verification"]["summary"] is None
    assert row["effective_patch"]["reason"]


def test_diagnostic_sources_reject_escape_symlinks_and_identity_mismatch(tmp_path):
    diagnose(tmp_path, [event(1)])
    trace, result = tmp_path / "trace_fixture.json", tmp_path / "official-result.json"
    with pytest.raises(ValueError, match="escapes"):
        diagnose_trace(trace, result, tmp_path / "nested")
    link = tmp_path / "trace_link.json"
    link.symlink_to(trace)
    with pytest.raises(ValueError, match="symlink"):
        diagnose_trace(link, result, tmp_path)
    raw = json.loads(result.read_text())
    raw["task_id"] = "other"
    result.write_bytes(canonical_json(raw))
    with pytest.raises(ValueError, match="identity"):
        diagnose_trace(trace, result, tmp_path)


@pytest.mark.parametrize(
    "field,value", [("status", []), ("error_type", {}), ("backend", ["vector"])]
)
def test_malformed_response_fields_do_not_crash_or_fabricate_backend(
    tmp_path, field, value
):
    response = {"status": "ok", field: value}
    row = diagnose(tmp_path, [event(1, "search_similar_code", response=response)])
    assert row["calls"][0]["similarity_backend"] is None
    if field == "status":
        assert row["metrics"]["rejected_attempts"]["value"] is None


def test_graph_metric_requires_complete_nontruncated_returned_entries(tmp_path):
    response = {"status": "ok", "nodes": ["m.A", "m.B"], "is_truncated": False}
    row = diagnose(tmp_path, [event(1, "get_code_subgraph", response=response)])
    assert row["metrics"]["returned_graph_nodes"]["value"] == 2
    assert row["metrics"]["returned_graph_nodes"]["denominator"] == 1
    response["is_truncated"] = True
    row = diagnose(tmp_path, [event(1, "get_code_subgraph", response=response)])
    assert row["metrics"]["returned_graph_nodes"]["value"] is None
    assert row["metrics"]["returned_graph_nodes"]["reason"]


def test_partial_timestamp_coverage_never_yields_model_time(tmp_path):
    first, second = event(1), event(2, elapsed=5)
    second["extra"].pop("elapsed_s")
    row = diagnose(tmp_path, [first, second])
    assert row["adjacent_agent_intervals"][0]["value"] is None
    assert row["adjacent_agent_intervals"][0]["reason"]
    assert row["metrics"]["pure_model_seconds"]["value"] is None


def test_renamed_or_unparseable_product_patch_is_not_reproduction_only(tmp_path):
    row = diagnose(
        tmp_path,
        [event(1)],
        {
            "_mostaza": {
                "effective_agent_patch": (
                    "diff --git a/src/requests/utils.py b/repro.py\n"
                )
            }
        },
    )
    assert row["effective_patch"]["changed_files"] == [
        "repro.py",
        "src/requests/utils.py",
    ]
    row = diagnose(
        tmp_path,
        [event(1)],
        {
            "_mostaza": {
                "effective_agent_patch": (
                    "diff --git a/repro.py b/repro.py\ndiff --git unknown-file\n"
                )
            }
        },
    )
    assert row["effective_patch"]["changed_files"] is None
    assert row["effective_patch"]["reason"]


@pytest.mark.parametrize(
    "response",
    [
        {"status": "error"},
        {"status": "error", "error_type": []},
        {"status": "ok", "error_type": "BudgetExceeded"},
    ],
)
def test_incomplete_or_inconsistent_rejection_fields_are_unknown(tmp_path, response):
    row = diagnose(tmp_path, [event(1, response=response)])
    assert row["calls"][0]["rejected"] is None
    assert row["metrics"]["rejected_attempts"]["value"] is None
    assert row["metrics"]["rejected_attempts"]["reason"]


def test_error_backend_label_does_not_establish_vector_execution(tmp_path):
    row = diagnose(
        tmp_path,
        [
            event(
                1,
                "search_similar_code",
                response={
                    "status": "error",
                    "error_type": "SimilaritySearchError",
                    "backend": "vector",
                },
            )
        ],
    )
    assert row["calls"][0]["similarity_backend"] is None
    assert row["calls"][0]["backend_reason"]
    assert row["metrics"]["similarity_attempts"]["value"] == 1
    assert row["metrics"]["rejected_attempts"]["value"] == 0


@pytest.mark.parametrize(
    "mutation",
    [
        lambda s: s.pop("observation"),
        lambda s: s.update(observation=None),
        lambda s: s["observation"].update(content="malformed JSON"),
        lambda s: s["observation"].update(content=json.dumps({})),
        lambda s: s["observation"].update(content=json.dumps({"status": []})),
        lambda s: s["observation"]["extra"].update(tool_name="other"),
        lambda s: s["observation"]["extra"].update(tool_call_id="other"),
        lambda s: s["observation"].update(content=json.dumps({"status": "error"})),
        lambda s: s["observation"].update(
            content=json.dumps({"status": "ok", "error_type": "BudgetExceeded"})
        ),
    ],
)
def test_successful_repeated_reads_require_matched_response_status(tmp_path, mutation):
    """budget-retrieval-calibration:AC-4; AUD-001: no missingness-to-zero."""
    args = {"filepath": "a.py", "start_line": 1, "end_line": 5}
    steps = [event(1, "read_file", args), event(2, "read_file", args)]
    for step in steps:
        mutation(step)
    row = diagnose(tmp_path, steps)
    metric = row["metrics"]["repeated_explicit_read_ranges"]
    assert metric["value"] is None
    assert metric["numerator"] is None
    assert metric["denominator"] is None
    assert metric["availability"] == "unavailable"
    assert metric["reason"]
    assert metric["coverage"]["explicit_range_attempts"] == 2
    assert metric["coverage"]["known_response_attempts"] == 0
    assert row["metrics"]["recorded_attempts"]["value"] == 2


def test_ambiguous_parallel_read_responses_leave_success_membership_unknown(tmp_path):
    """budget-retrieval-calibration:AC-4; AUD-001: never reuse one observation."""
    args = {"filepath": "a.py", "start_line": 1, "end_line": 5}
    step = event(1, "read_file", args)
    step["tool_calls"].append(event(2, "read_file", args)["tool_calls"][0])
    row = diagnose(tmp_path, [step])
    assert row["metrics"]["repeated_explicit_read_ranges"]["value"] is None
    step["observation"]["extra"]["tool_call_id"] = "call-1"
    row = diagnose(tmp_path, [step])
    metric = row["metrics"]["repeated_explicit_read_ranges"]
    assert metric["value"] is None
    assert metric["coverage"]["known_response_attempts"] == 1


@pytest.mark.parametrize(
    "failed_indices,expected,denominator",
    [([], 2, 3), ([1], 1, 2), ([0, 1], 0, 1), ([0, 1, 2], 0, 0)],
)
def test_fully_observed_read_successes_and_failures_have_faithful_counts(
    tmp_path, failed_indices, expected, denominator
):
    """budget-retrieval-calibration:AC-4; AUD-001: known failures stay excluded."""
    args = {"filepath": "a.py", "start_line": 1, "end_line": 5}
    steps = [
        event(
            i + 1,
            "read_file",
            args,
            response={"status": "error", "error_type": "BudgetExceeded"}
            if i in failed_indices
            else {"status": "ok"},
        )
        for i in range(3)
    ]
    metric = diagnose(tmp_path, steps)["metrics"]["repeated_explicit_read_ranges"]
    assert metric["value"] == expected
    assert metric["denominator"] == denominator
    assert metric["availability"] == "measured"
    assert metric["reason"] is None
    assert metric["coverage"]["known_response_attempts"] == 3


def test_partial_read_response_coverage_does_not_publish_known_subset_as_total(
    tmp_path,
):
    """budget-retrieval-calibration:AC-4; AUD-001: unknown third result matters."""
    args = {"filepath": "a.py", "start_line": 1, "end_line": 5}
    steps = [event(i, "read_file", args) for i in (1, 2, 3)]
    steps[-1].pop("observation")
    metric = diagnose(tmp_path, steps)["metrics"]["repeated_explicit_read_ranges"]
    assert metric["value"] is None and metric["denominator"] is None
    assert metric["coverage"]["known_response_attempts"] == 2
    assert metric["coverage"]["explicit_range_attempts"] == 3
