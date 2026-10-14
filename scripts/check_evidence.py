"""Fail closed unless the declared real paired evidence is complete and reproducible."""

from __future__ import annotations

import argparse
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

from mostaza.evaluation.contracts import MODEL, canonical_json, nonempty, require
from mostaza.evaluation.import_results import verify_native_evidence
from mostaza.research.metrics import compare
from mostaza.research.report import markdown


def check_real(
    cohort_path: Path, evidence: Path, project_root: Path | None = None
) -> dict[str, Any]:
    cohort = json.loads(cohort_path.read_text())
    require(
        isinstance(cohort, dict)
        and set(cohort) == {"schema_version", "frozen_at", "selection_basis", "tasks"},
        "Invalid frozen cohort",
    )
    require(
        cohort["schema_version"] == 1 and cohort["selection_basis"] == "pre-outcome",
        "Cohort must be selected before outcomes",
    )
    tasks = cohort["tasks"]
    require(len(tasks) == 3, "Real benchmark requires exactly three tasks")
    repos = {task["repo"].casefold() for task in tasks}
    require(
        "psf/requests" in repos
        and "fastapi/fastapi" in repos
        and bool(repos & {"textualize/rich", "encode/httpx"}),
        "Required project cohort missing",
    )
    review = json.loads((evidence / "resource-review.json").read_text())
    require(
        review.get("status") == "VERIFIED"
        and review.get("official_resources_reviewed") is True,
        "Verified official resource review required",
    )
    receipt = json.loads((evidence / "official-validation.json").read_text())
    require(receipt.get("schema_version") == 1, "Unsupported validation receipt")
    manifests = receipt["manifests"]
    records = [
        json.loads(line)
        for line in (evidence / "paired-results.jsonl").read_text().splitlines()
    ]
    arms: dict[str, tuple[dict[str, Any], list[dict[str, Any]]]] = {}
    for arm in ("E0", "E1"):
        manifest = manifests[arm]
        require(
            manifest["run_kind"] == "real_kaggle",
            "Synthetic evidence is not real evaluation",
        )
        require(
            manifest["cohort"] == tasks, "Evidence cohort differs from frozen selection"
        )
        require(
            datetime.fromisoformat(cohort["frozen_at"].replace("Z", "+00:00"))
            < datetime.fromisoformat(manifest["timestamp"].replace("Z", "+00:00")),
            "Cohort was not frozen before execution",
        )
        environment = manifest["environment"]
        require(
            environment.get("platform") == "kaggle"
            and environment.get("gpu_count") == 4
            and environment.get("gpu_model") == "NVIDIA L4",
            "Official Kaggle L4x4 required",
        )
        require(
            manifest["source_run_id"].startswith("https://www.kaggle.com/code/"),
            "Durable Kaggle source run identifier required",
        )
        compiler = receipt["compiler"][arm]
        require(
            compiler.get("status") == "PASS"
            and compiler.get("archive_sha256") == manifest["archive_sha256"]
            and bool(compiler.get("source")),
            "Official compiler receipt must match the archive",
        )
        execution = receipt["execution"][arm]
        require(
            execution.get("model") == MODEL
            and execution.get("model_inference_observed") is True
            and execution.get("source_run_id") == manifest["source_run_id"]
            and nonempty(execution.get("source")),
            "Actual required-model inference needs a sourced execution receipt",
        )
        arm_records = [r for r in records if r["arm"] == arm]
        require(
            all(r["status"] != "NOT_RUN" for r in arm_records),
            "Paired execution incomplete",
        )
        arms[arm] = (manifest, arm_records)
    require(len(records) == 6, "Expected exactly six paired task records")
    project_root = project_root or Path(__file__).resolve().parents[1]
    native_manifests, native_records, native_analysis = verify_native_evidence(
        project_root,
        cohort,
        receipt,
    )
    native_rows = [record for arm in ("E0", "E1") for record in native_records[arm]]

    def record_key(record: dict[str, Any]) -> tuple[str, str]:
        return record["arm"], record["instance_id"]

    require(
        sorted(records, key=record_key) == sorted(native_rows, key=record_key),
        "Declared measurements differ from retained native derivation",
    )
    require(
        review.get("source_analysis") == native_analysis,
        "Declared tool analysis differs from retained native derivation",
    )
    require(
        review.get("host_postprocessing_sources")
        == receipt["host_postprocessing"]["sources"],
        "Review and receipt postprocessing provenance differ",
    )
    actual_review = review["actual_execution_review"]
    acquisition = receipt["acquisition"]
    require(
        actual_review["run_id"] == acquisition["run_id"]
        and actual_review["run_url"] == acquisition["run_url"]
        and actual_review["source_inventory_sha256"]
        == acquisition["source_inventory"]["sha256"],
        "Resource review actual-run provenance mismatch",
    )
    report = compare(
        (native_manifests["E0"], native_records["E0"]),
        (native_manifests["E1"], native_records["E1"]),
        source_analysis=native_analysis,
    )
    require(
        (evidence / "comparison.json").read_bytes() == canonical_json(report),
        "Comparison differs from raw paired records",
    )
    require(
        (evidence / "report.md").read_text() == markdown(report),
        "Report differs from recomputed paired records",
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-real-paired", action="store_true", required=True)
    parser.add_argument("--cohort", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        check_real(args.cohort, args.evidence_dir)
    except (
        OSError,
        ValueError,
        KeyError,
        TypeError,
        AttributeError,
        zipfile.BadZipFile,
    ) as error:
        print(f"Real paired evidence verification failed: {error}", file=sys.stderr)
        raise SystemExit(1) from None
    print("Verified real paired evidence and deterministic report")


if __name__ == "__main__":
    main()
