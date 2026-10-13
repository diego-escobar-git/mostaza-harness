"""Strict versioned contracts for immutable, provenance-bearing research records."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timedelta
from typing import Any

MODEL = "gemma-4-31b-it-qat-w4a16-ct"
METRIC_UNITS = {
    "symbols_explored": "count",
    "files_explored": "count",
    "read_operations": "count",
    "search_operations": "count",
    "localization_seconds": "seconds",
    "tokens": "tokens",
    "code_characters": "characters",
    "graph_expansions": "count",
    "repeated_context_characters": "characters",
    "recall_at_k": "ratio",
    "relevant_context_ratio": "ratio",
    "tool_calls": "count",
    "total_seconds": "seconds",
    "repairs": "count",
}
GROUND_TRUTH_METRICS = {"recall_at_k", "relevant_context_ratio"}
MANIFEST_FIELDS = {
    "schema_version",
    "experiment_id",
    "run_id",
    "arm",
    "run_kind",
    "timestamp",
    "code_commit",
    "working_tree_sha256",
    "config_sha256",
    "archive_sha256",
    "model",
    "resources",
    "cohort",
    "inference",
    "budgets",
    "environment",
    "limitations",
    "source_run_id",
}
RECORD_FIELDS = {
    "schema_version",
    "experiment_id",
    "run_id",
    "arm",
    "run_kind",
    "instance_id",
    "status",
    "reason",
    "patch",
    "tests",
    "resolved",
    "metrics",
    "artifacts",
    "ground_truth",
}


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def artifact(value: Any) -> None:
    require(
        isinstance(value, dict) and set(value) == {"sha256", "source"},
        "Artifact must declare digest and source",
    )
    require(
        digest(value["sha256"]) and nonempty(value["source"]),
        "Invalid artifact provenance",
    )


def validate_manifest(manifest: dict[str, Any]) -> None:
    require(set(manifest) == MANIFEST_FIELDS, "Unknown or missing manifest fields")
    require(
        type(manifest["schema_version"]) is int and manifest["schema_version"] == 1,
        "Unsupported manifest schema",
    )
    for field in ("experiment_id", "run_id", "source_run_id"):
        require(nonempty(manifest[field]), f"Missing {field}")
    require(manifest["arm"] in ("E0", "E1"), "Unknown arm")
    require(
        manifest["run_kind"] in ("real_kaggle", "synthetic_test"), "Unknown run kind"
    )
    require(manifest["model"] == MODEL, "The required model must be pinned")
    require(
        isinstance(manifest["code_commit"], str)
        and re.fullmatch(r"[0-9a-f]{40}", manifest["code_commit"]) is not None,
        "An exact code commit is required",
    )
    for field in ("working_tree_sha256", "config_sha256", "archive_sha256"):
        require(digest(manifest[field]), f"Invalid {field}")
    try:
        stamp = datetime.fromisoformat(manifest["timestamp"].replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Invalid UTC timestamp") from None
    require(stamp.utcoffset() == timedelta(0), "Timestamp must be UTC")
    for field in ("inference", "budgets", "environment"):
        require(
            isinstance(manifest[field], dict) and bool(manifest[field]),
            f"Explicit {field} is required",
        )
    require(
        isinstance(manifest["limitations"], list)
        and all(nonempty(x) for x in manifest["limitations"]),
        "Invalid limitations",
    )
    resources = manifest["resources"]
    require(
        isinstance(resources, dict)
        and set(resources) == {"harness", "wheelhouse", "dataset"},
        "Required resource pins missing",
    )
    for resource in resources.values():
        require(
            isinstance(resource, dict)
            and set(resource) == {"version", "sha256", "source"},
            "Invalid resource pin",
        )
        require(nonempty(resource["version"]), "Resource version missing")
        artifact({"sha256": resource["sha256"], "source": resource["source"]})
    cohort = manifest["cohort"]
    require(
        isinstance(cohort, list) and bool(cohort),
        "A nonempty frozen cohort is required",
    )
    seen: set[str] = set()
    for task in cohort:
        require(
            isinstance(task, dict)
            and set(task)
            == {"instance_id", "repo", "base_commit", "snapshot_sha256", "rationale"},
            "Invalid frozen task",
        )
        for field in ("instance_id", "repo", "rationale"):
            require(nonempty(task[field]), "Frozen task context missing")
        require(task["instance_id"] not in seen, "Duplicate cohort task")
        seen.add(task["instance_id"])
        require(
            isinstance(task["base_commit"], str)
            and re.fullmatch(r"[0-9a-f]{40}", task["base_commit"]) is not None,
            "Frozen base commit required",
        )
        require(digest(task["snapshot_sha256"]), "Snapshot hash required")
    # Catch non-JSON values/NaN in arbitrary inference/environment mappings.
    canonical_json(manifest)


def unavailable_metrics(reason: str) -> dict[str, Any]:
    require(nonempty(reason), "Missing metric reason required")
    return {
        name: {
            "value": None,
            "unit": unit,
            "source": None,
            "availability": "unavailable",
            "reason": reason,
        }
        for name, unit in METRIC_UNITS.items()
    }


def validate_record(record: dict[str, Any], manifest: dict[str, Any]) -> None:
    require(set(record) == RECORD_FIELDS, "Unknown or missing task record fields")
    require(
        type(record["schema_version"]) is int and record["schema_version"] == 1,
        "Unsupported record schema",
    )
    for field in ("experiment_id", "run_id", "arm", "run_kind"):
        require(record[field] == manifest[field], f"Record {field} mismatch")
    require(
        record["instance_id"] in {t["instance_id"] for t in manifest["cohort"]},
        "Record outside frozen cohort",
    )
    status = record["status"]
    require(status in ("PASS", "FAIL", "ERROR", "NOT_RUN"), "Unknown task status")
    require(
        record["reason"] is None or nonempty(record["reason"]), "Invalid status reason"
    )
    if status in ("ERROR", "NOT_RUN"):
        require(nonempty(record["reason"]), "Error/not-run reason required")
    patch = record["patch"]
    require(
        isinstance(patch, dict)
        and set(patch) == {"present", "valid", "sha256", "validity_source", "reason"},
        "Invalid patch fields",
    )
    require(
        type(patch["present"]) is bool
        and (patch["valid"] is None or type(patch["valid"]) is bool),
        "Invalid patch state",
    )
    require(
        digest(patch["sha256"]) if patch["present"] else patch["sha256"] is None,
        "Patch presence/digest mismatch",
    )
    require(
        nonempty(patch["validity_source"])
        if patch["valid"] is not None
        else nonempty(patch["reason"]),
        "Patch validity evidence or reason required",
    )
    require(
        patch["present"] or patch["valid"] is not True, "Absent patch cannot be valid"
    )
    tests = record["tests"]
    require(
        isinstance(tests, dict)
        and set(tests) == {"outcome", "exit_code", "source", "reason"},
        "Invalid test fields",
    )
    require(
        tests["outcome"] in ("PASS", "FAIL", "ERROR", "NOT_RUN"), "Invalid test outcome"
    )
    require(
        tests["exit_code"] is None or type(tests["exit_code"]) is int,
        "Invalid test exit code",
    )
    require(
        nonempty(tests["source"])
        if tests["outcome"] in ("PASS", "FAIL")
        else nonempty(tests["reason"]),
        "Test evidence or reason required",
    )
    if tests["outcome"] == "PASS":
        require(tests["exit_code"] == 0, "Passing tests require exit zero")
    if tests["outcome"] == "FAIL":
        require(
            tests["exit_code"] is not None and tests["exit_code"] > 0,
            "Failed tests require a positive exit code",
        )
    require(
        record["resolved"] is None or type(record["resolved"]) is bool,
        "Invalid resolution state",
    )
    if status == "PASS":
        require(
            record["resolved"] is True
            and patch["present"]
            and patch["valid"] is True
            and tests["outcome"] == "PASS",
            "PASS requires verified resolution",
        )
    if status == "ERROR":
        require(record["resolved"] is not True, "ERROR cannot claim resolution")
    if status == "FAIL":
        require(record["resolved"] is False, "FAIL requires unresolved outcome")
    if status == "NOT_RUN":
        require(
            record["resolved"] is None
            and not patch["present"]
            and tests["outcome"] == "NOT_RUN",
            "NOT_RUN cannot contain an outcome",
        )
    artifacts = record["artifacts"]
    require(isinstance(artifacts, dict), "Artifacts must be an object")
    for value in artifacts.values():
        artifact(value)
    if record["run_kind"] == "real_kaggle" and status != "NOT_RUN":
        require(
            {"result", "trace"} <= set(artifacts),
            "Real execution requires trace/result hashes",
        )
    ground = record["ground_truth"]
    if ground is not None:
        require(
            isinstance(ground, dict) and set(ground) == {"mapping", "definitions"},
            "Invalid post-run ground truth",
        )
        artifact(ground["mapping"])
        require(isinstance(ground["definitions"], dict), "Metric definitions missing")
    metrics = record["metrics"]
    require(
        isinstance(metrics, dict) and set(metrics) == set(METRIC_UNITS),
        "Every metric must be present, using explicit missing values",
    )
    for name, metric in metrics.items():
        require(
            isinstance(metric, dict)
            and set(metric) == {"value", "unit", "source", "availability", "reason"},
            "Invalid metric fields",
        )
        require(metric["unit"] == METRIC_UNITS[name], "Metric unit mismatch")
        available = metric["availability"]
        require(
            available in ("measured", "estimated", "unavailable"),
            "Invalid availability",
        )
        if available == "unavailable":
            require(
                metric["value"] is None
                and metric["source"] is None
                and nonempty(metric["reason"]),
                "Missing metric requires null and reason",
            )
        else:
            value = metric["value"]
            require(
                type(value) in (int, float) and math.isfinite(value) and value >= 0,
                "Metric value must be finite and nonnegative",
            )
            require(
                nonempty(metric["source"]) and metric["reason"] is None,
                "Available metric requires source",
            )
            if metric["unit"] in ("count", "tokens", "characters"):
                require(type(value) is int, "Discrete metric requires an integer")
            if metric["unit"] == "ratio":
                require(value <= 1, "Ratio out of range")
            if name in GROUND_TRUTH_METRICS:
                require(
                    ground is not None and nonempty(ground["definitions"].get(name)),
                    "Relevance metrics require post-run mapping and definitions",
                )
        if status == "NOT_RUN":
            require(available == "unavailable", "NOT_RUN cannot have measurements")
    canonical_json(record)


def validate_run(manifest: dict[str, Any], records: list[dict[str, Any]]) -> None:
    validate_manifest(manifest)
    seen: set[str] = set()
    for record in records:
        validate_record(record, manifest)
        require(record["instance_id"] not in seen, "Duplicate task/arm record")
        seen.add(record["instance_id"])
    require(
        seen == {t["instance_id"] for t in manifest["cohort"]},
        "Every cohort task requires a record, including NOT_RUN",
    )
