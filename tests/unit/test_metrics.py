"""evaluation:AC-5: paired differences reject mismatches and preserve missingness."""

import copy

import pytest
from test_results import failed_record, make_manifest, make_record, measured

from mostaza.research.metrics import compare
from mostaza.research.report import markdown


def pair():
    m0, m1 = make_manifest("E0"), make_manifest("E1")
    return (m0, [failed_record(m0)]), (m1, [failed_record(m1)])


def test_differences_include_failures_and_do_not_impute_missing_zero():
    a, b = pair()
    measured(a[1][0], "read_operations", 7)
    measured(b[1][0], "read_operations", 3)
    report = compare(a, b)
    assert report["metrics"]["read_operations"]["measured_mean_delta"] == -4
    assert report["metrics"]["tokens"]["measured_mean_delta"] is None
    assert report["metrics"]["tokens"]["measured_pairs"] == 0
    assert report["outcomes"]["E0"]["FAIL"] == 1
    assert report["outcomes"]["E0"]["cohort_denominator"] == 1
    assert "synthetic_test" in markdown(report)
    assert "superiority" in markdown(report)


@pytest.mark.parametrize(
    "field,value",
    [
        ("inference", {"temperature": 0.5}),
        ("budgets", {"max_tool_calls": 200}),
        ("environment", {"platform": "different"}),
        ("working_tree_sha256", "0" * 64),
        (
            "resources",
            {
                k: {"version": "other", "sha256": "0" * 64, "source": "fixture"}
                for k in ("dataset", "harness", "wheelhouse")
            },
        ),
        ("run_kind", "real_kaggle"),
    ],
)
def test_unmatched_non_treatment_conditions(field, value):
    a, b = pair()
    b[0][field] = value
    if field == "run_kind":
        b[1][0][field] = value
        b[1][0]["artifacts"] = {
            k: {"sha256": "0" * 64, "source": "fixture"} for k in ("trace", "result")
        }
    with pytest.raises(ValueError, match="Unmatched"):
        compare(a, b)


def test_missing_pair_and_duplicate_are_rejected():
    a, b = pair()
    with pytest.raises(ValueError):
        compare(a, (b[0], []))
    with pytest.raises(ValueError):
        compare(a, (b[0], b[1] * 2))


def test_estimation_separate_from_measurement():
    a, b = pair()
    measured(a[1][0], "localization_seconds", 5.0, "estimated")
    measured(b[1][0], "localization_seconds", 2.0, "estimated")
    report = compare(a, b)
    metric = report["metrics"]["localization_seconds"]
    assert metric["estimated_mean_delta"] == -3
    assert metric["measured_mean_delta"] is None
    b[1][0]["metrics"]["localization_seconds"]["availability"] = "measured"
    report = compare(a, b)
    assert report["metrics"]["localization_seconds"]["estimated_pairs"] == 0
    assert report["metrics"]["localization_seconds"]["excluded"]


def test_ground_truth_definitions_are_paired_and_post_run():
    a, b = pair()
    ground = {
        "mapping": {"sha256": "5" * 64, "source": "post-run:reference-files"},
        "definitions": {
            "recall_at_k": "K=5; mapped relevant symbols found / all relevant symbols"
        },
    }
    for run in (a, b):
        measured(run[1][0], "recall_at_k", 0.5)
        run[1][0]["ground_truth"] = copy.deepcopy(ground)
    assert compare(a, b)["metrics"]["recall_at_k"]["measured_pairs"] == 1
    b[1][0]["ground_truth"]["definitions"]["recall_at_k"] = "K=10"
    with pytest.raises(ValueError, match="ground truth"):
        compare(a, b)


def test_not_run_stays_in_denominator():
    a, b = pair()
    b[1][0] = make_record(b[0])
    report = compare(a, b)
    assert report["cohort_denominator"] == 1
    assert report["outcomes"]["E1"]["NOT_RUN"] == 1
    assert report["outcome_pairs"][0]["resolved_delta"] is None


def test_report_preserves_per_task_failure_and_verified_patch_details():
    a, b = pair()
    a[1][0]["reason"] = "Agent exceeded session timeout (1.0 min)"
    report = compare(a, b)
    details = report["outcome_pairs"][0]["details"]["E0"]
    assert details["patch_present"] and details["patch_valid"] is True
    assert details["tests"]["outcome"] == "FAIL"
    assert details["resolved"] is False
    assert "session timeout" in markdown(report)
    assert "Next research steps" in markdown(report)


def test_source_linked_tool_attempts_are_not_capped_to_charged_budget():
    a, b = pair()
    rows = []
    for arm, run, attempts, charged, counts in (
        (
            "E0",
            a,
            12,
            10,
            {"get_status": 1, "run_command": 10, "search_similar_code": 1},
        ),
        ("E1", b, 8, 7, {"get_status": 1, "read_file": 7}),
    ):
        record = measured(run[1][0], "tool_calls", attempts)
        record["artifacts"] = {
            name: {"sha256": "5" * 64, "source": "fixture:" + name}
            for name in ("trace", "result")
        }
        rows.append(
            {
                "arm": arm,
                "instance_id": record["instance_id"],
                "attempts": attempts,
                "charged": charged,
                "counts": counts,
                "trace_sha256": "5" * 64,
                "result_sha256": "5" * 64,
                "source": "fixture:trace",
            }
        )
    analysis = {
        "schema_version": 1,
        "definition": "Synthetic source protocol only",
        "tools": rows,
    }
    report = compare(a, b, source_analysis=analysis)
    assert report["metrics"]["tool_calls"]["measured_mean_delta"] == -4
    assert "| E0 | 12 | 10 | 1 | 0 |" in markdown(report)
    assert "E1 made no recorded vector or graph tool call" in markdown(report)
    bad = copy.deepcopy(analysis)
    bad["tools"][0]["trace_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="provenance"):
        compare(a, b, source_analysis=bad)
    bad = copy.deepcopy(analysis)
    bad["tools"][0]["counts"]["run_command"] += 1
    with pytest.raises(ValueError, match="attempts"):
        compare(a, b, source_analysis=bad)
