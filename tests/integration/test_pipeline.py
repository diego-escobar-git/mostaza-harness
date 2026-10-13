"""Synthetic end-to-end import/report and fail-closed official evidence checks."""

import asyncio
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from mostaza.evaluation.contracts import canonical_json
from mostaza.evaluation.import_results import import_run, load_run
from mostaza.research.metrics import compare
from mostaza.research.report import markdown, write_report


def fixture_helpers():
    # Explicit import of unit fixture builders, independent of pytest collection order.
    path = Path(__file__).parents[1] / "unit" / "test_results.py"
    spec = importlib.util.spec_from_file_location("result_fixture_helpers", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_fixture_pipeline_is_deterministic_and_not_real(tmp_path):
    fixture = fixture_helpers()
    paths = []
    for arm in ("E0", "E1"):
        manifest = fixture.make_manifest(arm)
        record = fixture.measured(
            fixture.failed_record(manifest), "tool_calls", 7 if arm == "E0" else 4
        )
        paths.append(import_run(manifest, [record], tmp_path / "records"))
    output, narrative = tmp_path / "comparison.json", tmp_path / "report.md"
    write_report(*paths, output, narrative)
    expected = compare(load_run(paths[0]), load_run(paths[1]))
    assert output.read_bytes() == canonical_json(expected)
    assert narrative.read_text() == markdown(expected)
    first = output.read_bytes(), narrative.read_bytes()
    write_report(*paths, output, narrative)
    assert first == (output.read_bytes(), narrative.read_bytes())
    assert json.loads(output.read_text())["run_kind"] == "synthetic_test"
    assert expected["metrics"]["tool_calls"]["measured_mean_delta"] == -3


def test_import_and_report_clis(tmp_path):
    fixture = fixture_helpers()
    paths = []
    for arm in ("E0", "E1"):
        manifest = fixture.make_manifest(arm)
        raw_manifest, raw_records = tmp_path / f"{arm}.json", tmp_path / f"{arm}.jsonl"
        raw_manifest.write_bytes(canonical_json(manifest))
        raw_records.write_bytes(canonical_json(fixture.make_record(manifest)))
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "mostaza.evaluation.import_results",
                str(raw_manifest),
                str(raw_records),
                "--output",
                str(tmp_path / "store"),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        paths.append(result.stdout.strip())
    subprocess.run(
        [
            sys.executable,
            "-m",
            "mostaza.research.report",
            *paths,
            "--json",
            str(tmp_path / "report.json"),
            "--markdown",
            str(tmp_path / "report.md"),
        ],
        check=True,
    )
    assert "synthetic_test" in (tmp_path / "report.md").read_text()


def test_missing_official_evidence_fails_without_writes(tmp_path):
    project = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [
            sys.executable,
            str(project / "scripts/check_evidence.py"),
            "--require-real-paired",
            "--cohort",
            str(tmp_path / "cohort.json"),
            "--evidence-dir",
            str(tmp_path / "evidence"),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "verification failed" in result.stderr
    assert not (tmp_path / "evidence").exists()


def test_official_adapter_does_not_execute_synthetic_runs():
    from mostaza.evaluation.runner import evaluate_official

    fixture = fixture_helpers()
    with pytest.raises(ValueError, match="real run kind"):
        asyncio.run(evaluate_official(None, fixture.make_manifest()))


def test_synthetic_evidence_cannot_satisfy_real_gate(tmp_path):
    fixture = fixture_helpers()
    tasks = [
        fixture.make_manifest()["cohort"][0]
        | {
            "instance_id": "fixture-" + str(index),
            "repo": repo,
        }
        for index, repo in enumerate(
            ("psf/requests", "fastapi/fastapi", "encode/httpx")
        )
    ]
    cohort = {
        "schema_version": 1,
        "frozen_at": "2026-10-12T00:00:00Z",
        "selection_basis": "pre-outcome",
        "tasks": tasks,
    }
    cohort_path = tmp_path / "cohort.json"
    cohort_path.write_bytes(canonical_json(cohort))
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "resource-review.json").write_text(
        json.dumps(
            {
                "status": "VERIFIED",
                "official_resources_reviewed": True,
            }
        )
    )
    manifests = {
        arm: fixture.make_manifest(arm) | {"cohort": tasks} for arm in ("E0", "E1")
    }
    (evidence / "official-validation.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "manifests": manifests,
            }
        )
    )
    (evidence / "paired-results.jsonl").write_text("")
    project = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        [
            sys.executable,
            str(project / "scripts/check_evidence.py"),
            "--require-real-paired",
            "--cohort",
            str(cohort_path),
            "--evidence-dir",
            str(evidence),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "Synthetic evidence" in result.stderr


def test_native_official_protocol_without_model_execution(tmp_path):
    """Exercise installed organizer classes; this is synthetic source integration."""
    project = Path(__file__).resolve().parents[2]
    official_python = project / ".tools/official/bin/python"
    if not official_python.exists() or not (project / "submission/agent.yaml").exists():
        pytest.skip("Pinned official source environment not installed")
    code = r"""
import json, sys
from pathlib import Path
from types import SimpleNamespace
from swegemma.config import EvalConfig, build_submission_limits
from swegemma.models import TaskResult
from adk_eval_core.tracing import SessionTrace
from adk_submission import ModelRegistry, VllmConfig, VllmServer
from mostaza.evaluation.contracts import MODEL, canonical_json, sha256
from mostaza.evaluation.runner import (
    describe_runtime,
    snapshot_digest,
    validate_bindings,
    file_digest,
    WHEEL_PINS,
)
from mostaza.evaluation.import_results import normalize_official_result
from mostaza.packaging import collect_submission, archive_bytes

project, root = map(Path, sys.argv[1:])
sys.path.insert(0, str(project / "tests/unit"))
from test_results import make_manifest

submission = root / "submission"
submission.mkdir()
for name, data in collect_submission(
    project / "submission", "prompts/baseline.md"
).items():
    path = submission / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
archive = root / "submission.zip"
archive_bytes(collect_submission(submission), archive)
data_root = project / "resources/official"
snapshots = data_root / "snapshots"
tasks = data_root / "tasks.jsonl"
cohort = json.loads((project / "experiments/cohort.json").read_text())
selected = cohort["tasks"][0]
review = json.loads(
    (
        project
        / "docs/implementation/evidence/mostaza-phase1-foundation/resource-review.json"
    ).read_text()
)
receipts = {
    entry["instance_id"]: entry
    for entry in review["selected_resources"]
    if entry["kind"] == "snapshot"
}
vllm = VllmConfig(
    model="/kaggle/input/models/google/gemma-4/other/" + MODEL + "/2",
    tensor_parallel_size=4,
    enable_lora=False,
)
server = VllmServer(vllm)
registry = ModelRegistry()
registry.register(
    MODEL,
    SimpleNamespace(
        model="openai/" + vllm.model, _additional_args={"api_base": server.base_url}
    ),
)
limits, constraints = build_submission_limits()
config = EvalConfig(
    tasks_path=tasks,
    snapshots_dir=snapshots,
    results_dir=root / "results",
    submission_dir=submission,
    models=registry,
    sandbox="subprocess",
    limits=limits,
    generation_constraints=constraints,
    max_time_minutes=1,
    max_tool_calls=10,
    max_turns=50,
)
manifest = make_manifest()
manifest["run_kind"] = "real_kaggle"
manifest.update(describe_runtime(config, vllm))
manifest["archive_sha256"] = file_digest(archive)
manifest["resources"]["harness"]["sha256"] = WHEEL_PINS[
    "swegemma-0.2.11-py3-none-any.whl"
]
wheelhouse = project / "resources/official"
manifest["resources"]["wheelhouse"]["sha256"] = sha256(
    canonical_json(
        [
            {"name": p.name, "sha256": file_digest(p)}
            for p in sorted(wheelhouse.glob("*.whl"))
        ]
    )
)
manifest["resources"]["dataset"]["sha256"] = file_digest(tasks)
manifest["cohort"] = [selected]
manifest["environment"]["snapshot_validation"] = receipts
assert selected["snapshot_sha256"] == snapshot_digest(
    snapshots, selected["instance_id"], selected["repo"], data_root
)
validate_bindings(
    config, manifest, server=server, archive_path=archive, wheelhouse_dir=wheelhouse
)
manifest["budgets"]["evaluation"]["tool_calls"] += 1
try:
    validate_bindings(
        config, manifest, server=server, archive_path=archive, wheelhouse_dir=wheelhouse
    )
except ValueError as error:
    assert "budgets" in str(error)
else:
    raise AssertionError("Mismatched actual budgets accepted")
manifest["budgets"]["evaluation"]["tool_calls"] -= 1
manifest = make_manifest()
trace = SessionTrace()
trace.start()
trace.record_custom("text", "Synthetic class protocol fixture")
traces = root / "traces"
traces.mkdir()
trace.save(traces / "trace_fixture-1.json")
patch = "diff --git a/source.py b/source.py\n"
result = TaskResult(
    instance_id="fixture-1",
    repo="fixture/repo",
    resolved=True,
    agent_patch=patch,
    test_exit_code=0,
    test_output="STDOUT:\n1 passed\nSTDERR:\n",
    duration_seconds=1.0,
    trace_json_path=str(traces / "trace_fixture-1.json"),
)
raw = result.model_dump(mode="json", exclude={"trace"})
raw["_mostaza"] = {
    "schema_version": 1,
    "effective_agent_patch": patch,
    "original_patch_sha256": sha256(patch.encode()),
}
path = root / "official-result-0001.json"
path.write_bytes(canonical_json(raw))
normalized = normalize_official_result(path, manifest, root)
assert normalized["status"] == "PASS" and normalized["run_kind"] == "synthetic_test"
assert normalized["metrics"]["tokens"]["value"] is None
server.stop()
print("Native official source protocol validated; no model or sandbox execution")
"""
    result = subprocess.run(
        [str(official_python), "-c", code, str(project), str(tmp_path)],
        env={**__import__("os").environ, "PYTHONPATH": str(project / "src")},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "no model or sandbox execution" in result.stdout


def native_evidence_fixture(tmp_path):
    """Copy authentic retained inputs; refresh test-only path/host-hash metadata."""
    import hashlib
    import shutil

    project = Path(__file__).resolve().parents[2]
    source_evidence = project / "docs/implementation/evidence/mostaza-phase1-foundation"
    original = json.loads((source_evidence / "official-validation.json").read_text())
    acquisition = original["acquisition"]
    packet = project / Path(acquisition["retained_source_root"]).parent.parent
    originals = {}
    for key in ("source_zip", "source_notebook"):
        pin = acquisition[key]
        path = (
            project / pin["path"]
            if "path" in pin
            else Path.home() / "Downloads" / pin["download_name"]
        )
        if not path.is_file():
            pytest.skip("Authentic native download fixture is not retained")
        originals[key] = path
    clone = tmp_path / "project"
    packet_relative = packet.relative_to(project)
    copied_packet = clone / packet_relative
    shutil.copytree(packet, copied_packet)
    for key, name in (
        ("source_zip", "original-results.zip"),
        ("source_notebook", "executed-notebook.ipynb"),
    ):
        destination = copied_packet / name
        if not destination.exists():
            shutil.copyfile(originals[key], destination)
        acquisition[key]["path"] = str(destination.relative_to(clone))
    inputs = list(copied_packet.glob("mostaza-reviewed-input-*"))
    assert len(inputs) == 1
    acquisition["executed_input_root"] = str(inputs[0].relative_to(clone))
    evidence = clone / "docs/implementation/evidence/mostaza-phase1-foundation"
    shutil.copytree(source_evidence, evidence)
    cohort = clone / "experiments/cohort.json"
    cohort.parent.mkdir()
    shutil.copyfile(project / "experiments/cohort.json", cohort)
    for name in original["host_postprocessing"]["sources"]:
        destination = clone / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(project / name, destination)
        original["host_postprocessing"]["sources"][name] = hashlib.sha256(
            destination.read_bytes()
        ).hexdigest()
    (evidence / "official-validation.json").write_bytes(canonical_json(original))
    review = json.loads((evidence / "resource-review.json").read_text())
    review["host_postprocessing_sources"] = original["host_postprocessing"]["sources"]
    (evidence / "resource-review.json").write_bytes(canonical_json(review))
    path = project / "scripts/check_evidence.py"
    spec = importlib.util.spec_from_file_location("native_evidence_checker", path)
    assert spec is not None and spec.loader is not None
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    return clone, cohort, evidence, checker


def test_authentic_native_source_gate_passes(tmp_path):
    project, cohort, evidence, checker = native_evidence_fixture(tmp_path)
    report = checker.check_real(cohort, evidence, project_root=project)
    assert report["outcomes"]["E0"]["FAIL"] == 1
    assert report["outcomes"]["E1"]["ERROR"] == 2
    assert report["metrics"]["tokens"]["measured_pairs"] == 3


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_root",
        "native_bytes",
        "inventory",
        "declared_manifest",
        "archive_provenance",
        "executed_notebook",
        "host_provenance",
        "source_analysis",
        "path_escape",
        "symlink",
    ],
)
def test_native_gate_rejects_missing_changed_or_mismatched_sources(tmp_path, mutation):
    project, cohort, evidence, checker = native_evidence_fixture(tmp_path)
    receipt_path = evidence / "official-validation.json"
    receipt = json.loads(receipt_path.read_text())
    native = project / receipt["acquisition"]["retained_source_root"]
    if mutation == "missing_root":
        receipt["acquisition"]["retained_source_root"] = (
            "results/nonexistent/private-run-evidence/missing"
        )
    elif mutation == "native_bytes":
        path = native / "E0/results/official-result-0001.json"
        path.chmod(0o644)
        path.write_bytes(path.read_bytes() + b" ")
    elif mutation == "inventory":
        path = native / "source-inventory.json"
        path.chmod(0o644)
        data = json.loads(path.read_text())
        data["files"][0]["sha256"] = "0" * 64
        path.write_bytes(canonical_json(data))
    elif mutation == "declared_manifest":
        receipt["manifests"]["E0"]["config_sha256"] = "0" * 64
    elif mutation == "archive_provenance":
        receipt["compiler"]["E0"]["archive_sha256"] = "0" * 64
    elif mutation == "executed_notebook":
        receipt["acquisition"]["source_notebook"]["sha256"] = "0" * 64
    elif mutation == "host_provenance":
        receipt["host_postprocessing"]["executed_normalizer_sha256"] = "0" * 64
    elif mutation == "source_analysis":
        review_path = evidence / "resource-review.json"
        review = json.loads(review_path.read_text())
        review["source_analysis"]["tools"][0]["charged"] += 1
        review_path.write_bytes(canonical_json(review))
    elif mutation == "path_escape":
        receipt["acquisition"]["source_zip"]["path"] = "results/../outside.zip"
    elif mutation == "symlink":
        path = native / "E0/results/official-result-0001.json"
        target = project / "outside-result.json"
        target.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(target)
    receipt_path.write_bytes(canonical_json(receipt))
    with pytest.raises((ValueError, KeyError)):
        checker.check_real(cohort, evidence, project_root=project)


def test_forged_metric_with_regenerated_summaries_and_original_trace_hash_fails(
    tmp_path,
):
    project, cohort, evidence, checker = native_evidence_fixture(tmp_path)
    receipt = json.loads((evidence / "official-validation.json").read_text())
    records_path = evidence / "paired-results.jsonl"
    records = [json.loads(line) for line in records_path.read_text().splitlines()]
    forged = next(
        row
        for row in records
        if row["arm"] == "E0" and row["instance_id"] == "requests_7205"
    )
    original_trace = forged["artifacts"]["trace"]["sha256"]
    forged["metrics"]["tokens"]["value"] = 1038522
    records_path.write_bytes(b"".join(canonical_json(row) for row in records))
    review = json.loads((evidence / "resource-review.json").read_text())
    arms = {
        arm: (receipt["manifests"][arm], [r for r in records if r["arm"] == arm])
        for arm in ("E0", "E1")
    }
    report = compare(arms["E0"], arms["E1"], source_analysis=review["source_analysis"])
    (evidence / "comparison.json").write_bytes(canonical_json(report))
    (evidence / "report.md").write_text(markdown(report))
    assert forged["artifacts"]["trace"]["sha256"] == original_trace
    with pytest.raises(ValueError, match="measurements.*native"):
        checker.check_real(cohort, evidence, project_root=project)
