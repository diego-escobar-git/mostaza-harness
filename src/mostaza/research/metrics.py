"""Matched E1-minus-E0 calculations; unavailable and estimated values stay distinct."""

from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any

from mostaza.evaluation.contracts import (
    METRIC_UNITS,
    canonical_json,
    require,
    sha256,
    validate_run,
)

MATCHED_FIELDS = (
    "experiment_id",
    "run_kind",
    "code_commit",
    "working_tree_sha256",
    "model",
    "resources",
    "cohort",
    "inference",
    "budgets",
    "environment",
)


def compare(
    e0: tuple[dict[str, Any], list[dict[str, Any]]],
    e1: tuple[dict[str, Any], list[dict[str, Any]]],
    *,
    source_analysis: dict[str, Any] | None = None,
) -> dict[str, Any]:
    m0, r0 = e0
    m1, r1 = e1
    validate_run(m0, r0)
    validate_run(m1, r1)
    require(m0["arm"] == "E0" and m1["arm"] == "E1", "Expected ordered E0/E1 arms")
    require(m0["run_id"] != m1["run_id"], "Arms require distinct run IDs")
    for field in MATCHED_FIELDS:
        require(m0[field] == m1[field], f"Unmatched non-treatment condition: {field}")
    baseline = {r["instance_id"]: r for r in r0}
    hybrid = {r["instance_id"]: r for r in r1}
    paired: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}
    for name, unit in METRIC_UNITS.items():
        counts: dict[str, list[float]] = {"measured": [], "estimated": []}
        excluded: list[dict[str, str]] = []
        for instance_id in sorted(baseline):
            a = baseline[instance_id]["metrics"][name]
            b = hybrid[instance_id]["metrics"][name]
            if (
                a["availability"] == b["availability"]
                and a["availability"] != "unavailable"
            ):
                # Relevance requires the same mapping and operational definition.
                if name in ("recall_at_k", "relevant_context_ratio"):
                    require(
                        baseline[instance_id]["ground_truth"]
                        == hybrid[instance_id]["ground_truth"],
                        "Unmatched post-run ground truth",
                    )
                delta = b["value"] - a["value"]
                counts[a["availability"]].append(delta)
                paired.append(
                    {
                        "instance_id": instance_id,
                        "metric": name,
                        "unit": unit,
                        "availability": a["availability"],
                        "E0": a["value"],
                        "E1": b["value"],
                        "delta": delta,
                        "sources": {"E0": a["source"], "E1": b["source"]},
                    }
                )
            else:
                excluded.append(
                    {
                        "instance_id": instance_id,
                        "reason": "Missing or noncomparable measurement",
                        "E0": a["reason"] or a["availability"],
                        "E1": b["reason"] or b["availability"],
                    }
                )
        summary[name] = {
            "unit": unit,
            "cohort_denominator": len(baseline),
            "measured_pairs": len(counts["measured"]),
            "estimated_pairs": len(counts["estimated"]),
            "measured_mean_delta": mean(counts["measured"])
            if counts["measured"]
            else None,
            "estimated_mean_delta": mean(counts["estimated"])
            if counts["estimated"]
            else None,
            "excluded": excluded,
        }
    outcomes: dict[str, Any] = {}
    for arm, rows in (("E0", r0), ("E1", r1)):
        count = Counter(r["status"] for r in rows)
        outcomes[arm] = {s: count[s] for s in ("PASS", "FAIL", "ERROR", "NOT_RUN")}
        outcomes[arm]["cohort_denominator"] = len(rows)
        outcomes[arm]["resolved"] = sum(r["resolved"] is True for r in rows)
        outcomes[arm]["resolution_unknown"] = sum(r["resolved"] is None for r in rows)
        outcomes[arm]["patch_present"] = sum(r["patch"]["present"] for r in rows)
        outcomes[arm]["patch_valid"] = sum(r["patch"]["valid"] is True for r in rows)
        outcomes[arm]["patch_validity_unknown"] = sum(
            r["patch"]["valid"] is None for r in rows
        )
        outcomes[arm]["tests_passed"] = sum(
            r["tests"]["outcome"] == "PASS" for r in rows
        )
        outcomes[arm]["tests_not_run"] = sum(
            r["tests"]["outcome"] == "NOT_RUN" for r in rows
        )
    transitions = [
        {
            "instance_id": key,
            "E0": baseline[key]["status"],
            "E1": hybrid[key]["status"],
            "resolved_delta": int(hybrid[key]["resolved"])
            - int(baseline[key]["resolved"])
            if baseline[key]["resolved"] is not None
            and hybrid[key]["resolved"] is not None
            else None,
        }
        for key in sorted(baseline)
    ]
    if source_analysis is not None:
        require(
            source_analysis.get("schema_version") == 1
            and isinstance(source_analysis.get("tools"), list),
            "Invalid source analysis",
        )
        seen = set()
        for row in source_analysis["tools"]:
            key = (row["arm"], row["instance_id"])
            require(
                key not in seen
                and row["arm"] in ("E0", "E1")
                and row["instance_id"] in baseline,
                "Duplicate or unknown source analysis task",
            )
            seen.add(key)
            record = (
                baseline[row["instance_id"]]
                if row["arm"] == "E0"
                else hybrid[row["instance_id"]]
            )
            require(
                row["trace_sha256"] == record["artifacts"]["trace"]["sha256"]
                and row["result_sha256"] == record["artifacts"]["result"]["sha256"],
                "Source analysis provenance mismatch",
            )
            native_counts = row["counts"]
            require(
                isinstance(native_counts, dict)
                and all(
                    isinstance(name, str) and type(value) is int and value >= 0
                    for name, value in native_counts.items()
                ),
                "Invalid native tool breakdown",
            )
            require(
                sum(native_counts.values())
                == row["attempts"]
                == record["metrics"]["tool_calls"]["value"],
                "Source analysis attempts mismatch",
            )
            require(
                row["charged"] is None
                or type(row["charged"]) is int
                and 0 <= row["charged"] <= row["attempts"],
                "Invalid charged tool count",
            )
        require(
            seen == {(arm, key) for arm in ("E0", "E1") for key in baseline},
            "Source analysis requires complete pairing",
        )
    for item in transitions:
        item["details"] = {}
        for arm, records in (("E0", baseline), ("E1", hybrid)):
            record = records[item["instance_id"]]
            item["details"][arm] = {
                "reason": record["reason"],
                "patch_present": record["patch"]["present"],
                "patch_valid": record["patch"]["valid"],
                "tests": record["tests"],
                "resolved": record["resolved"],
            }
    return {
        "schema_version": 1,
        "experiment_id": m0["experiment_id"],
        "run_kind": m0["run_kind"],
        "cohort_denominator": len(baseline),
        "direction": "E1 minus E0",
        "metrics": summary,
        "pairs": paired,
        "outcomes": outcomes,
        "outcome_pairs": transitions,
        "source_analysis": source_analysis,
        "provenance": {
            "E0": {
                "run_id": m0["run_id"],
                "source_run_id": m0["source_run_id"],
                "manifest_sha256": sha256(canonical_json(m0)),
                "records_sha256": sha256(
                    canonical_json(sorted(r0, key=lambda r: r["instance_id"]))
                ),
            },
            "E1": {
                "run_id": m1["run_id"],
                "source_run_id": m1["source_run_id"],
                "manifest_sha256": sha256(canonical_json(m1)),
                "records_sha256": sha256(
                    canonical_json(sorted(r1, key=lambda r: r["instance_id"]))
                ),
            },
        },
        "limitations": sorted(
            set(
                m0["limitations"]
                + m1["limitations"]
                + [
                    "Small exploratory cohort; descriptive differences "
                    "do not establish significance or superiority.",
                    "Missing measurements are excluded per metric, "
                    "never imputed as zero.",
                ]
            )
        ),
    }
