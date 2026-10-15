"Recompute sourced outcomes locally; never contacts Kaggle or executes a model."

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from mostaza.evaluation.contracts import canonical_json
from mostaza.evaluation.import_results import import_run, normalize_official_result
from mostaza.research.metrics import compare
from mostaza.research.report import markdown
from mostaza.research.trace_diagnostics import diagnose_trace

ROOT = Path(__file__).resolve().parents[4]
BUNDLE = ROOT / ("results/kaggle-phase2-startup-v3-ea1534a86873409b870b3b04d04e347f")
OUTPUT = BUNDLE / "downloaded-output"
NATIVE = OUTPUT / ("private-phase2-evidence/ea1534a8-6873-409b-870b-3b04d04e347f")
EVIDENCE = Path(__file__).resolve().parent
PAIR_ID = "B180-startup-v3"
VERSION_URL = "https://www.kaggle.com/code/diegofescobar/" + (
    "mostaza-b180-ea1534a86873409b870b3b04d04e347f?scriptVersionId=358394257"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recompute(check: bool) -> None:
    def emit(name: str, value: Any) -> None:
        data = canonical_json(value)
        if check:
            assert (EVIDENCE / name).read_bytes() == data, name
        else:
            (EVIDENCE / name).write_bytes(data)

    inventory = json.loads((BUNDLE / "download-inventory.json").read_text())
    for item in inventory:
        path = OUTPUT / item["path"]
        assert path.stat().st_size == item["bytes"]
        assert digest(path) == item["sha256"], item["path"]
    for item in json.loads((NATIVE / "source-inventory.json").read_text()):
        assert digest(NATIVE / item["path"]) == item["sha256"], item["path"]
    claim = json.loads((BUNDLE / "launch-claim.json").read_text())
    assert digest(BUNDLE / "launched.ipynb") == claim["notebook_sha256"]
    assert claim["approved_candidate_sha256"] == (
        "127ad5adec71cd25d8da80afbcb78cc8f1a899a9dcca2ba9a58af51900e4cf1b"
    )
    submitted = json.loads((BUNDLE / "launched.ipynb").read_text())
    executed = json.loads((BUNDLE / "executed-notebook.ipynb").read_text())
    for before, after in zip(submitted["cells"], executed["cells"], strict=True):
        assert "".join(before["source"]) == "".join(after["source"])
    assert [
        c["execution_count"] for c in executed["cells"] if c["cell_type"] == "code"
    ] == [1, 2, 3, 4, 5]
    snapshots = BUNDLE / "audited-source"
    prepared = json.loads(
        (
            ROOT
            / (
                "docs/implementation/evidence/mostaza-phase2-star"
                "tup-correction/manifest.json"
            )
        ).read_text()
    )
    for name, expected in prepared["files"].items():
        assert digest(snapshots / name) == expected
    arms = []
    all_records = []
    observations = []
    derivations = []
    for configuration in ("E0-B180", "E1-B180"):
        native_manifest_path = NATIVE / configuration / "manifest.json"
        manifest = json.loads(native_manifest_path.read_text())
        assert manifest["experiment_id"] == configuration
        # The comparator needs a shared experiment ID. Native manifests stay intact.
        manifest["experiment_id"] = PAIR_ID
        manifest["source_run_id"] = VERSION_URL
        manifest["limitations"] += [
            f"Host-derived pair ID {PAIR_ID}; native configuration ID {configuration}",
            ("Native unversioned source URL refined to observed exact saved version"),
            (
                "Recorded usage excludes unreported failed-reques"
                "t usage; not physical token billing"
            ),
        ]
        derivations.append(
            {
                "configuration_id": configuration,
                "native_manifest_path": native_manifest_path.relative_to(
                    ROOT
                ).as_posix(),
                "native_manifest_sha256": digest(native_manifest_path),
                "changed_fields": ["experiment_id", "source_run_id", "limitations"],
            }
        )
        records = []
        for result_path in sorted(
            (NATIVE / configuration / "results").glob("official-result-*.json")
        ):
            record = normalize_official_result(result_path, manifest, OUTPUT)
            records.append(record)
            raw = json.loads(result_path.read_text())
            task = raw["task_id"]
            trace_path = result_path.parent / "traces" / f"trace_{task}.json"
            trace = json.loads(trace_path.read_text())
            diagnosis = diagnose_trace(trace_path, result_path, ROOT)
            # In the native StepObject serializer, omitted tool_calls means empty.
            # Count only actually listed events; never infer whole-execution totals.
            counts: Counter[str] = Counter()
            for step in trace["steps"]:
                if "tool_calls" in step:
                    assert isinstance(step["tool_calls"], list)
                    counts.update(call["function_name"] for call in step["tool_calls"])
            attempts = sum(counts.values())
            assert attempts == record["metrics"]["tool_calls"]["value"]
            calls = diagnosis["calls"]
            assert len(calls) == attempts
            observations.append(
                {
                    "configuration_id": configuration,
                    "instance_id": task,
                    "native_status": raw["status"],
                    "normalized_status": record["status"],
                    "sources": diagnosis["sources"],
                    "recorded_attempts": attempts,
                    "official_charged_calls": raw["tool_calls"],
                    "tool_counts": dict(sorted(counts.items())),
                    "lexical_command_attempts": sum(
                        c["shell_classification"] == "lexical" for c in calls
                    ),
                    "similarity_attempts": counts["search_similar_code"],
                    "graph_attempts": counts["get_code_neighbors"]
                    + counts["get_code_subgraph"],
                    "backend_execution": None,
                    "backend_execution_reason": (
                        "No similarity invocation or backend receipt in t"
                        "hese recorded traces"
                    ),
                    "recorded_tokens": record["metrics"]["tokens"]["value"],
                    "native_default_total_tokens_ignored": raw["total_tokens"],
                    "native_llm_calls": raw["total_llm_calls"],
                    "duration_seconds": raw["duration_seconds"],
                    "timeout": diagnosis["timeout"],
                    "error_message": raw["error_message"],
                    "verification": diagnosis["verification"],
                    "effective_patch": diagnosis["effective_patch"],
                    "legacy_strict_diagnostic_coverage": diagnosis["coverage"],
                    "legacy_strict_metrics": {
                        k: diagnosis["metrics"][k]
                        for k in ("recorded_attempts", "tokens")
                    },
                    "unobservable_metrics": {
                        k: diagnosis["metrics"][k]
                        for k in (
                            "pure_model_seconds",
                            "tool_execution_seconds",
                            "localization_seconds",
                            "recall_at_k",
                            "relevant_context_ratio",
                            "repairs",
                        )
                    },
                }
            )
        assert len(records) == 3
        arms.append((manifest, records))
        all_records.extend(records)
        emit(configuration + "-derived-manifest.json", manifest)
        if not check:
            import_run(manifest, records, BUNDLE / "immutable-store")
    comparison = compare(arms[0], arms[1])
    emit("evaluation-records.json", all_records)
    emit("comparison.json", comparison)
    report_bytes = markdown(comparison).encode()
    if check:
        assert (EVIDENCE / "paired-report.md").read_bytes() == report_bytes
    else:
        (EVIDENCE / "paired-report.md").write_bytes(report_bytes)
    emit(
        "trace-observations.json",
        {
            "schema_version": 1,
            "metrics_contract": {
                "recorded_attempts": (
                    "count of explicitly listed native tool-call even"
                    "ts, including exempt attempts; not full executio"
                    "n coverage"
                ),
                "official_charged_calls": (
                    "count from native result; get_status/submit_patc"
                    "h exempt under pinned policy"
                ),
                "lexical_command_attempts": (
                    "count of simple rg/grep/git-grep commands recogn"
                    "ized by source classifier; lower-bound lexical c"
                    "overage"
                ),
                "similarity_and_graph_attempts": (
                    "count of named native tool events; backend execu"
                    "tion remains null absent a backend receipt"
                ),
                "recorded_tokens": (
                    "tokens, sum of observed step usage once; ignore "
                    "default result total_tokens0; failed-request/unr"
                    "eported usage unknown"
                ),
                "duration_seconds": (
                    "native task wall seconds including orchestration"
                    " and verification, not pure model time"
                ),
                "optional_tool_calls": (
                    "Pinned adk_eval_core StepObject omits empty tool"
                    "_calls; legacy strict diagnostic flags Requests "
                    "text/final steps conservatively; its nulls are r"
                    "etained separately"
                ),
            },
            "serializer_source_sha256": digest(
                BUNDLE / "official-source-review/atif.py"
            ),
            "derivations": derivations,
            "tasks": observations,
        },
    )
    print(
        json.dumps(
            {
                "status": "PASS_RECOMPUTED_LOCAL",
                "real_evaluations": 6,
                "download_files": len(inventory),
                "outcomes": comparison["outcomes"],
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    recompute(parser.parse_args().check)
