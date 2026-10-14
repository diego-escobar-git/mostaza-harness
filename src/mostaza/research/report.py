"""Recompute deterministic JSON/Markdown reports from immutable raw run records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from mostaza.evaluation.contracts import canonical_json
from mostaza.evaluation.import_results import load_run
from mostaza.research.metrics import compare


def markdown(report: dict[str, Any]) -> str:
    def cell(value: Any) -> str:
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = [
        f"# Paired experiment: {cell(report['experiment_id'])}",
        "",
        f"Run kind: **{cell(report['run_kind'])}**. "
        f"Cohort: {report['cohort_denominator']}.",
        "Differences are E1 minus E0; "
        "the direction of improvement depends on the metric.",
        "",
        "| Metric | Unit | Measured pairs | Measured mean delta | "
        "Estimated pairs | Estimated mean delta |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for name, metric in report["metrics"].items():
        a = metric["measured_mean_delta"]
        b = metric["estimated_mean_delta"]
        lines.append(
            f"| {name} | {metric['unit']} | {metric['measured_pairs']} | "
            f"{'unavailable' if a is None else a} | {metric['estimated_pairs']} | "
            f"{'unavailable' if b is None else b} |"
        )
    lines += [
        "",
        "| Arm | PASS | FAIL | ERROR | NOT_RUN | Cohort denominator |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for arm, counts in report["outcomes"].items():
        lines.append(
            f"| {arm} | {counts['PASS']} | {counts['FAIL']} | {counts['ERROR']} | "
            f"{counts['NOT_RUN']} | {counts['cohort_denominator']} |"
        )
    lines += [
        "",
        "## Per-task outcomes",
        "",
        "| Instance | Arm | Status | Patch present | Patch valid | "
        "Tests | Resolved | Reason |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for pair in report["outcome_pairs"]:
        for arm in ("E0", "E1"):
            detail = pair["details"][arm]
            valid = (
                "unknown"
                if detail["patch_valid"] is None
                else str(detail["patch_valid"])
            )
            resolved = (
                "unknown" if detail["resolved"] is None else str(detail["resolved"])
            )
            reason = detail["reason"] or detail["tests"]["reason"] or "none"
            lines.append(
                f"| {cell(pair['instance_id'])} | {arm} | {pair[arm]} | "
                f"{detail['patch_present']} | {valid} | {detail['tests']['outcome']} | "
                f"{resolved} | {cell(reason)} |"
            )
    analysis = report.get("source_analysis")
    if analysis is not None:
        lines += [
            "",
            "## Native tool engagement",
            "",
            cell(analysis["definition"]),
            "",
            "| Arm | Recorded attempts | Reported charged calls | "
            "Vector calls | Graph calls |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
        totals = {}
        for arm in ("E0", "E1"):
            rows = [row for row in analysis["tools"] if row["arm"] == arm]
            attempts = sum(row["attempts"] for row in rows)
            charged = (
                sum(row["charged"] for row in rows)
                if all(row["charged"] is not None for row in rows)
                else "unavailable"
            )
            vector = sum(row["counts"].get("search_similar_code", 0) for row in rows)
            graph = sum(
                row["counts"].get(name, 0)
                for row in rows
                for name in ("get_code_neighbors", "get_code_subgraph")
            )
            totals[arm] = vector + graph
            lines.append(f"| {arm} | {attempts} | {charged} | {vector} | {graph} |")
        if totals["E1"] == 0:
            lines += [
                "",
                "E1 made no recorded vector or graph tool call. Under the observed "
                "time limits, these runs do not test the efficacy "
                "of vector/graph retrieval.",
            ]
    lines += [
        "",
        "## Next research steps",
        "",
        "- Inspect the failed verification and incomplete patch-generation traces.",
        "- Assess whether the fixed budgets permit implementation and verification "
        "before another experiment.",
        "- Instrument missing localization/context metrics "
        "before interpreting retrieval efficiency.",
    ]
    lines += ["", "## Provenance", ""]
    for arm, pin in report["provenance"].items():
        lines.append(
            f"- {arm}: {cell(pin['run_id'])}; source {cell(pin['source_run_id'])}; "
            f"manifest SHA-256 `{pin['manifest_sha256']}`; "
            f"records SHA-256 `{pin['records_sha256']}`."
        )
    lines += ["", "## Unavailable or noncomparable measurements", ""]
    for name, metric in report["metrics"].items():
        for missing in metric["excluded"]:
            lines.append(
                f"- {name}, {cell(missing['instance_id'])}: "
                f"E0: {cell(missing['E0'])}; E1: {cell(missing['E1'])}."
            )
    lines += ["", "## Limitations", ""]
    lines.extend(f"- {cell(value)}" for value in report["limitations"])
    return "\n".join(lines) + "\n"


def write_report(
    e0: Path,
    e1: Path,
    json_path: Path,
    markdown_path: Path,
    resource_review: Path | None = None,
) -> None:
    analysis = None
    if resource_review is not None:
        analysis = json.loads(resource_review.read_text())["source_analysis"]
    report = compare(load_run(e0), load_run(e1), source_analysis=analysis)
    json_path.write_bytes(canonical_json(report))
    markdown_path.write_text(markdown(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("e0", type=Path)
    parser.add_argument("e1", type=Path)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--markdown", type=Path, required=True)
    parser.add_argument("--resource-review", type=Path)
    args = parser.parse_args()
    write_report(args.e0, args.e1, args.json, args.markdown, args.resource_review)


if __name__ == "__main__":
    main()
