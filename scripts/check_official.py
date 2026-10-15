"""Read-only official prerequisites, compiler, ZIP and package-build checks."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import yaml

from mostaza.packaging import (
    EXPERIMENTS,
    VARIANTS,
    IncludeLoader,
    PackagingError,
    build_submission,
    configuration_files,
    load_manifest,
)
from mostaza.resources import ResourceError, require_resources, sha256


def phase2_resource_review(root: Path) -> dict[str, Any]:
    """Recompute input receipts separately from Planner current-source review."""
    index = json.loads((root / "resources/manifest.json").read_text())
    entries = index["resources"]
    resources = require_resources(root, [entry["id"] for entry in entries])
    pinned_wheel = "9ad876581f3acde8ec3c369858f0834e2b9f41a3cffce3ca42f09cb090aea9d3"
    if (
        sha256(resources["swegemma"]) != pinned_wheel
        or resources["swegemma"].stat().st_size != 119670
    ):
        raise PackagingError(
            "Current primary wheel identity differs from Planner review"
        )
    modules = ["swegemma/config.py", "swegemma/budget.py"]
    with zipfile.ZipFile(resources["swegemma"]) as wheel:
        # Bind native tool source modules alongside budget/config source.
        names = [
            name
            for name in wheel.namelist()
            if name in modules or name.startswith("swegemma/tools/")
        ]
        source_hashes = {
            name: hashlib.sha256(wheel.read(name)).hexdigest() for name in sorted(names)
        }
    return {
        "schema_version": 1,
        "kind": "official_primary_resource_review",
        "review_basis": (
            "Planner official API research recorded in approved plan, 2026-10-14 UTC"
        ),
        "plan": "docs/specs/plans/active/mostaza-phase2-budget-retrieval.md",
        "current_primary_sources": {
            "starter": {
                "url": "https://www.kaggle.com/api/v1/kernels/pull/ryanholbrook/getting-started-gemma-4-developer-agent",
                "version": 3,
                "model_revision": 2,
                "response_sha256": (
                    "238d1d45d9a98652d954310cd5b48d68baca54006174e28eb5104ca0af359aa6"
                ),
                "response_note": (
                    "Planner observed response; volatile metadata differs from "
                    "retained phase-1 response below"
                ),
            },
            "wheelhouse": {
                "url": "https://www.kaggle.com/api/v1/datasets/list?search=gemma-4-developer-agent-wheelhouse",
                "version": 31,
                "updated": "2026-10-12T19:51:31.09Z",
                "swegemma_bytes": 119670,
                "swegemma_sha256": sha256(resources["swegemma"]),
            },
        },
        "retained_inputs": [
            {
                "id": entry["id"],
                "path": entry["path"],
                "sha256": sha256(resources[entry["id"]]),
                "bytes": resources[entry["id"]].stat().st_size,
                "version": entry.get("version"),
                "source_url": entry["url"],
            }
            for entry in entries
        ],
        "native_source_sha256": source_hashes,
        "capabilities": {
            "eval_config": [
                "timeout_seconds",
                "max_time_minutes",
                "max_tool_calls",
                "max_turns",
                "verification_timeout_seconds",
            ],
            "verification_seconds": 300,
            "neighbors_bound": 10,
            "similarity_k": 5,
            "default_graph_hops": 1,
            "similarity_backend": (
                "Native symbol embeddings; unmatched query may fall back lexically"
            ),
        },
        "scope": (
            "Experimental local API review; no competition submission-limit change "
            "or GPU authorization"
        ),
    }


def phase2_compiler_receipts(root: Path, compiler: Path) -> dict[str, Any]:
    """Compile and reproduce all variants using inert bindings and temporary ZIPs."""
    phase2_resource_review(
        root
    )  # Fail closed before validation if any pin is unavailable.
    # Check actual rendered pair conditions before accepting compiler receipts.
    for left, right in (
        ("E0-B180", "E1-B180"),
        ("E0-B300", "E1-B300"),
        ("E1-B180", "E1-R180"),
    ):
        first_files = configuration_files(root, left)
        second_files = configuration_files(root, right)
        agents = [
            yaml.load(files["agent.yaml"], Loader=IncludeLoader)
            for files in (first_files, second_files)
        ]
        for agent in agents:
            agent.pop("instruction")
        if (
            agents[0] != agents[1]
            or first_files["eval_config.yaml"] != second_files["eval_config.yaml"]
        ):
            raise PackagingError("Rendered pair conditions differ")
    receipts = []
    with tempfile.TemporaryDirectory(prefix="mostaza-phase2-compiler-") as temporary:
        for config in VARIANTS:
            manifest = load_manifest(root, config)
            first = Path(temporary) / f"{config}-first.zip"
            second = Path(temporary) / f"{config}-second.zip"
            digest = build_submission(root, config, first, compiler)
            if (
                build_submission(root, config, second, compiler) != digest
                or first.read_bytes() != second.read_bytes()
            ):
                raise PackagingError("Variant archive reproduction differs")
            with zipfile.ZipFile(first) as archive:
                members = {
                    name: hashlib.sha256(archive.read(name)).hexdigest()
                    for name in archive.namelist()
                }
            receipts.append(
                {
                    "configuration_id": config,
                    "arm": manifest["arm"],
                    "manifest_sha256": sha256(
                        root / "experiments" / config / "manifest.json"
                    ),
                    "archive_sha256": digest,
                    "members_sha256": members,
                    "budget": manifest["budgets"],
                    "directory_schema_compiler": "PASS",
                    "eval_config_native_mapping": "PASS",
                    "reproducible_archive": True,
                    "real_gemma_execution": "NOT_RUN",
                    "reason": "Compiler-only inert bindings; GPU not authorized",
                }
            )
    return {
        "schema_version": 1,
        "kind": "official_compiler_only",
        "compiler_versions": {
            "adk-submission": "0.2.13",
            "google-adk": "1.36.1",
            "swegemma": "0.2.11",
        },
        "configurations": receipts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.add_argument(
        "--experiments", choices=list(EXPERIMENTS), nargs="+", required=True
    )
    parser.add_argument("--compiler-python", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    compiler = args.compiler_python or root / ".tools/official/bin/python"
    try:
        require_resources(
            root,
            [
                "notebook",
                "swegemma",
                "adk_submission",
                "adk_eval_core",
                "harness_readme",
                "starter_agent",
                "tasks",
            ],
        )
        with tempfile.TemporaryDirectory(prefix="mostaza-official-check-") as temporary:
            for experiment in args.experiments:
                first = Path(temporary) / f"{experiment}-1.zip"
                second = Path(temporary) / f"{experiment}-2.zip"
                first_hash = build_submission(root, experiment, first, compiler)
                second_hash = build_submission(root, experiment, second, compiler)
                if (
                    first_hash != second_hash
                    or first.read_bytes() != second.read_bytes()
                ):
                    raise PackagingError("Archive reproduction differs")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "build",
                    "--no-isolation",
                    "--outdir",
                    temporary,
                    str(root),
                ],
                check=True,
                timeout=180,
            )
    except (
        ResourceError,
        PackagingError,
        OSError,
        subprocess.SubprocessError,
    ) as error:
        parser.exit(1, f"Official validation prerequisite failed: {error}\n")
    print(
        "Official compiler-only validation and reproducible archives passed. "
        "Real Kaggle evidence is separate."
    )


if __name__ == "__main__":
    main()
