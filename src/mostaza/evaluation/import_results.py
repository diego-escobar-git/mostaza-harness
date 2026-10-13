"""Import normalized records without overwriting previously published evidence."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from mostaza.evaluation.contracts import canonical_json, require, sha256, validate_run


def publish(root: Path, data: bytes, suffix: str) -> Path:
    """Atomically publish content once, including concurrent writers."""
    root.mkdir(parents=True, exist_ok=True)
    destination = root / (sha256(data) + suffix)
    fd, temp = tempfile.mkstemp(prefix=".import-", dir=root)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, 0o444)
        try:
            os.link(temp, destination)
        except FileExistsError:
            require(
                not destination.is_symlink() and destination.read_bytes() == data,
                "Existing immutable artifact differs",
            )
    finally:
        Path(temp).unlink(missing_ok=True)
    return destination


def import_run(
    manifest: dict[str, Any], records: list[dict[str, Any]], root: Path
) -> Path:
    """Publish one manifest and one JSONL; hashes permit drift detection on reload."""
    validate_run(manifest, records)
    ordered = sorted(records, key=lambda item: item["instance_id"])
    records_path = publish(root, b"".join(canonical_json(r) for r in ordered), ".jsonl")
    bundle = {
        "manifest": manifest,
        "records_sha256": records_path.stem,
        "records_file": records_path.name,
    }
    path = publish(root, canonical_json(bundle), ".json")
    identity = sha256(
        canonical_json(
            {
                "experiment_id": manifest["experiment_id"],
                "run_id": manifest["run_id"],
            }
        )
    )
    binding = root / (identity + ".run")
    try:
        os.link(path, binding)
    except FileExistsError:
        require(
            not binding.is_symlink() and binding.read_bytes() == path.read_bytes(),
            "Run identity already bound to different immutable evidence",
        )
    return path


def load_run(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    require(not path.is_symlink(), "Run manifest must not be a symlink")
    raw = path.read_bytes()
    require(path.name == sha256(raw) + ".json", "Immutable manifest hash mismatch")
    bundle = json.loads(raw)
    require(
        isinstance(bundle, dict)
        and set(bundle) == {"manifest", "records_sha256", "records_file"},
        "Invalid run bundle",
    )
    name = bundle["records_file"]
    require(
        isinstance(name, str)
        and name == bundle["records_sha256"] + ".jsonl"
        and Path(name).name == name,
        "Invalid records reference",
    )
    records_path = path.parent / name
    require(not records_path.is_symlink(), "Task records must not be a symlink")
    data = records_path.read_bytes()
    require(
        sha256(data) == bundle["records_sha256"], "Immutable task records hash mismatch"
    )
    records = [json.loads(line) for line in data.splitlines()]
    manifest = bundle["manifest"]
    require(
        isinstance(manifest, dict) and all(isinstance(r, dict) for r in records),
        "Invalid run record objects",
    )
    validate_run(manifest, records)
    return manifest, records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("records", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    records = [
        json.loads(line)
        for line in args.records.read_text().splitlines()
        if line.strip()
    ]
    print(import_run(manifest, records, args.output).resolve())


def _source_file(path: Path, root: Path) -> Path:
    require(
        not path.is_symlink() and path.is_file(), "Source artifact missing or symlinked"
    )
    resolved = path.resolve()
    require(
        resolved.is_relative_to(root.resolve()), "Source artifact escapes evidence root"
    )
    return resolved


def _trace_measurements(
    data: dict[str, Any],
) -> tuple[dict[str, int], int | None, bool]:
    """Read pinned ATIF-v1.7/legacy trace counts, without double-counting tool usage.

    ATIF step metrics already aggregate its tool-call extra.usage; only step
    metrics are summed. The default final_metrics.total_tokens zero proves no
    measurement. This mirrors the pinned SessionTrace.summarize token definition.
    """
    from collections import Counter

    if data.get("schema_version") == "ATIF-v1.7":
        steps = data.get("steps")
        require(isinstance(steps, list), "Invalid official ATIF steps")
        assert isinstance(steps, list)
        calls = [
            call["function_name"]
            for step in steps
            for call in step.get("tool_calls", [])
        ]
        usage = [step["metrics"] for step in steps if step.get("metrics")]
        observed = any(
            step.get("source") == "agent"
            and (bool(step.get("message")) or bool(step.get("tool_calls")))
            for step in steps
        )
    elif data.get("trace_version") == "1.0":
        entries = data.get("entries")
        require(isinstance(entries, list), "Invalid official legacy trace entries")
        assert isinstance(entries, list)
        calls = [entry["tool"] for entry in entries if entry.get("type") == "tool_call"]
        usage = [entry["usage"] for entry in entries if entry.get("usage")]
        observed = any(
            entry.get("type") in ("thinking", "text", "final", "tool_call")
            for entry in entries
        )
    else:
        raise ValueError("Unsupported official trace schema")
    total = 0
    token_usage_seen = False
    for metric in usage:
        require(isinstance(metric, dict), "Invalid recorded trace usage")
        present = {
            name: metric[name]
            for name in ("prompt_tokens", "completion_tokens", "total_tokens")
            if name in metric and metric[name] is not None
        }
        require(
            all(type(value) is int and value >= 0 for value in present.values()),
            "Invalid recorded token counts",
        )
        if present:
            token_usage_seen = True
            total += max(
                present.get("total_tokens", 0),
                present.get("prompt_tokens", 0) + present.get("completion_tokens", 0),
            )
    return dict(Counter(calls)), total if token_usage_seen else None, observed


def normalize_official_result(
    result_path: Path, manifest: dict[str, Any], evidence_root: Path
) -> dict[str, Any]:
    """Normalize a pinned official raw result and its actual trace, never defaults.

    Only organizer verification outputs establish patch validity. Reference tests,
    raw traces, issue text and generated patch text stay outside compact records.
    Rebased downloaded bundles locate traces alongside their raw result file.
    """
    from mostaza.evaluation.contracts import (
        unavailable_metrics,
        validate_manifest,
        validate_record,
    )

    validate_manifest(manifest)
    result_path = _source_file(result_path, evidence_root)
    raw_bytes = result_path.read_bytes()
    raw = json.loads(raw_bytes)
    require(isinstance(raw, dict), "Official result must be an object")
    instance_id = raw.get("task_id")
    selected = next(
        (task for task in manifest["cohort"] if task["instance_id"] == instance_id),
        None,
    )
    require(
        selected is not None and raw.get("repo") == selected["repo"],
        "Official task identity mismatch",
    )
    require(
        isinstance(instance_id, str)
        and "/" not in instance_id
        and ".." not in instance_id,
        "Unsafe official trace identity",
    )
    expected_name = f"trace_{instance_id}.json"
    trace_reference = raw.get("trace_path")
    require(
        isinstance(trace_reference, str)
        and Path(trace_reference).name == expected_name
        and Path(trace_reference).parent.name == "traces",
        "Missing or mismatched official trace identity",
    )
    trace_path = _source_file(
        result_path.parent / "traces" / expected_name, evidence_root
    )
    trace_bytes = trace_path.read_bytes()
    breakdown, tokens, inference_observed = _trace_measurements(json.loads(trace_bytes))
    source_prefix: str = manifest["source_run_id"] + "#output/"

    def source(path: Path) -> str:
        return source_prefix + str(path.relative_to(evidence_root.resolve()))

    result_source, trace_source = source(result_path), source(trace_path)
    extension = raw.get("_mostaza")
    require(
        isinstance(extension, dict) and extension.get("schema_version") == 1,
        "Pinned runner effective-patch provenance missing",
    )
    original = raw.get("agent_patch")
    patch = extension.get("effective_agent_patch")
    require(
        isinstance(original, str)
        and isinstance(patch, str)
        and sha256(original.encode()) == extension.get("original_patch_sha256"),
        "Generated patch provenance mismatch",
    )
    resolved, exit_code = raw.get("resolved"), raw.get("test_exit_code")
    require(
        type(resolved) is bool and type(exit_code) is int,
        "Official verification fields missing",
    )
    error = raw.get("error_message")
    require(error is None or isinstance(error, str), "Invalid official error")
    output = raw.get("test_output")
    require(isinstance(output, str), "Official verification output missing")
    pytest_ran = output.startswith("STDOUT:\n") and "\nSTDERR:\n" in output
    apply_failed = bool(error and error.startswith("Failed to apply agent patch:"))
    tests_outcome = (
        "PASS"
        if resolved
        else "FAIL"
        if pytest_ran and exit_code > 0
        else "ERROR"
        if pytest_ran
        else "NOT_RUN"
    )
    status = (
        "PASS"
        if resolved
        else "FAIL"
        if tests_outcome == "FAIL" or apply_failed
        else "ERROR"
    )
    require(
        not resolved or (pytest_ran and exit_code == 0 and bool(patch.strip())),
        "Official resolution lacks verified patch/test evidence",
    )
    present = bool(patch.strip())
    validity = (
        False if apply_failed and present else True if present and pytest_ran else None
    )
    metrics = unavailable_metrics("Not measured by the pinned result/trace contract")

    def measure(name: str, value: int | float, origin: str) -> None:
        metrics[name].update(
            value=value, source=origin, availability="measured", reason=None
        )

    duration = raw.get("duration_seconds")
    if type(duration) in (int, float):
        measure("total_seconds", duration, result_source + ":duration_seconds")
    # Trace tool counts are observed events; result.tool_calls may be a default.
    measure("tool_calls", sum(breakdown.values()), trace_source + ":tool_calls")
    metrics["read_operations"]["reason"] = (
        "Native read_file events omit shell reads; full read coverage unavailable"
    )
    metrics["search_operations"]["reason"] = (
        "Native similarity events omit lexical shell searches; "
        "full search coverage unavailable"
    )
    if tokens is not None:
        measure("tokens", tokens, trace_source + ":recorded_usage")
    artifacts = {
        "result": {"sha256": sha256(raw_bytes), "source": result_source},
        "trace": {"sha256": sha256(trace_bytes), "source": trace_source},
    }
    if original.strip():
        artifacts["original_patch"] = {
            "sha256": sha256(original.encode()),
            "source": result_source + ":agent_patch",
        }
    if inference_observed:
        artifacts["inference"] = {
            "sha256": sha256(trace_bytes),
            "source": trace_source + ":agent_response",
        }
    record = {
        "schema_version": 1,
        **{
            field: manifest[field]
            for field in ("experiment_id", "run_id", "arm", "run_kind")
        },
        "instance_id": instance_id,
        "status": status,
        "reason": error or "Official verification did not produce a test outcome"
        if status == "ERROR"
        else error,
        "resolved": None if status == "ERROR" else resolved,
        "patch": {
            "present": present,
            "sha256": sha256(patch.encode()) if present else None,
            "valid": validity,
            "validity_source": result_source + ":official_effective_patch_application"
            if validity is not None
            else None,
            "reason": None
            if validity is not None
            else "Effective patch applicability not established",
        },
        "tests": {
            "outcome": tests_outcome,
            "exit_code": exit_code if pytest_ran else None,
            "source": result_source + ":official_verification" if pytest_ran else None,
            "reason": None
            if tests_outcome in ("PASS", "FAIL")
            else error or "Verification not run",
        },
        "metrics": metrics,
        "artifacts": artifacts,
        "ground_truth": None,
    }
    validate_record(record, manifest)
    return record


def official_execution_receipt(
    manifest: dict[str, Any], records: list[dict[str, Any]]
) -> dict[str, Any]:
    """Identify recorded model responses independently of server readiness."""
    validate_run(manifest, records)
    evidence = next(
        (
            record["artifacts"]["inference"]
            for record in records
            if "inference" in record["artifacts"]
        ),
        None,
    )
    return {
        "model": manifest["model"],
        "source_run_id": manifest["source_run_id"],
        "model_inference_observed": evidence is not None,
        "source": evidence["source"] if evidence else None,
    }


def official_source_analysis(
    manifests: dict[str, dict[str, Any]],
    records_by_arm: dict[str, list[dict[str, Any]]],
    evidence_root: Path,
) -> dict[str, Any]:
    """Derive diagnostic native attempts/charged counts from immutable source files."""
    rows = []
    for arm in ("E0", "E1"):
        validate_run(manifests[arm], records_by_arm[arm])
        normalized = {r["instance_id"]: r for r in records_by_arm[arm]}
        seen: set[str] = set()
        for path in sorted(
            (evidence_root / arm / "results").glob("official-result-*.json")
        ):
            path = _source_file(path, evidence_root)
            raw_bytes = path.read_bytes()
            raw = json.loads(raw_bytes)
            instance_id = raw["task_id"]
            require(
                instance_id in normalized and instance_id not in seen,
                "Source analysis task identity mismatch",
            )
            seen.add(instance_id)
            trace_path = _source_file(
                path.parent / "traces" / Path(raw["trace_path"]).name, evidence_root
            )
            trace_bytes = trace_path.read_bytes()
            counts, _, _ = _trace_measurements(json.loads(trace_bytes))
            record = normalized[instance_id]
            require(
                sha256(raw_bytes) == record["artifacts"]["result"]["sha256"]
                and sha256(trace_bytes) == record["artifacts"]["trace"]["sha256"],
                "Source analysis differs from normalized provenance",
            )
            charged = raw.get("tool_calls")
            require(
                charged is None or type(charged) is int and charged >= 0,
                "Invalid native charged tool count",
            )
            rows.append(
                {
                    "arm": arm,
                    "instance_id": instance_id,
                    "counts": dict(sorted(counts.items())),
                    "attempts": sum(counts.values()),
                    "charged": charged,
                    "trace_sha256": sha256(trace_bytes),
                    "result_sha256": sha256(raw_bytes),
                    "source": record["artifacts"]["trace"]["source"],
                }
            )
        require(seen == set(normalized), "Source analysis needs every task")
    return {
        "schema_version": 1,
        "definition": "Native trace attempts include exempt and denied invocations; "
        "reported charged calls come from official result.tool_calls. "
        "get_status/submit_patch are exempt; check_budget rejects before "
        "incrementing, while accepted calls that later fail are charged. "
        "Source: swegemma0.2.11 context.py:check_budget "
        "and tools/base.py:budget_gated.",
        "tools": rows,
    }


HOST_SOURCE_PATHS = (
    "scripts/check_evidence.py",
    "src/mostaza/evaluation/import_results.py",
    "src/mostaza/research/metrics.py",
    "src/mostaza/research/report.py",
)


def retained_path(root: Path, relative: Any, *, directory: bool = False) -> Path:
    """Resolve a retained input inside its declared root without following links."""
    require(
        isinstance(relative, str)
        and bool(relative)
        and not Path(relative).is_absolute()
        and "\\" not in relative
        and ":" not in relative
        and all(part not in ("", ".", "..") for part in relative.split("/")),
        "Unsafe retained source path",
    )
    path = root.resolve()
    for part in relative.split("/"):
        path = path / part
        require(not path.is_symlink(), "Retained source symlink forbidden")
    require(
        path.resolve().is_relative_to(root.resolve()), "Retained source escapes root"
    )
    require(
        path.is_dir() if directory else path.is_file(), "Retained native source missing"
    )
    return path


def _file_pin(path: Path, pin: dict[str, Any]) -> None:
    require(
        sha256(path.read_bytes()) == pin.get("sha256"), "Retained source hash mismatch"
    )
    if "bytes" in pin:
        require(path.stat().st_size == pin["bytes"], "Retained source size mismatch")


def _notebook_payload(
    path: Path,
) -> tuple[dict[str, bytes], dict[str, str], dict[str, Any]]:
    """Read literal payload data only; never execute downloaded notebook cells."""
    import ast
    import base64

    notebook = json.loads(path.read_text())
    values: dict[str, Any] = {}
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        for node in ast.parse("".join(cell["source"])).body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in (
                        "EMBEDDED_PAYLOAD",
                        "EMBEDDED_HASHES",
                    ):
                        require(
                            target.id not in values,
                            "Duplicate executed notebook payload",
                        )
                        values[target.id] = ast.literal_eval(node.value)
    encoded, hashes = values["EMBEDDED_PAYLOAD"], values["EMBEDDED_HASHES"]
    require(
        isinstance(encoded, dict)
        and isinstance(hashes, dict)
        and set(encoded) == set(hashes)
        and len(encoded) == 16,
        "Executed notebook payload identity mismatch",
    )
    payload = {}
    for name, value in encoded.items():
        require(
            isinstance(name, str) and isinstance(value, str), "Invalid notebook payload"
        )
        data = base64.b64decode(value, validate=True)
        require(sha256(data) == hashes[name], "Executed notebook payload hash mismatch")
        payload[name] = data
    metadata = notebook["metadata"]["mostaza"]
    require(metadata["embedded_hashes"] == hashes, "Notebook metadata/payload mismatch")
    require(
        not any(
            output.get("output_type") == "error"
            for cell in notebook["cells"]
            for output in cell.get("outputs", [])
        ),
        "Executed notebook contains errors",
    )
    return payload, hashes, metadata


def verify_native_evidence(
    project_root: Path,
    cohort: dict[str, Any],
    receipt: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]], dict[str, Any]]:
    """Bind compact results to the immutable downloaded native packet and notebook.

    Acquisition records remain the external provenance boundary; this verifies
    their exact retained bytes and derivations, rather than trusting summary claims.
    Neither current HEAD nor current host sources identify the code executed in Kaggle.
    """
    import io
    import zipfile

    import yaml

    from mostaza.evaluation.contracts import MODEL, validate_manifest
    from mostaza.packaging import IncludeLoader

    acquisition = receipt["acquisition"]
    relative = acquisition["retained_source_root"]
    require(
        isinstance(relative, str) and relative.startswith("results/"),
        "Native sources must be retained below results",
    )
    native = retained_path(project_root, relative, directory=True)
    packet = native.parent.parent
    require(
        native.parent.name == "private-run-evidence"
        and packet.is_relative_to(project_root.resolve() / "results"),
        "Invalid retained native bundle location",
    )
    inputs_relative = acquisition["executed_input_root"]
    require(
        isinstance(inputs_relative, str) and inputs_relative.startswith("results/"),
        "Executed inputs must be retained below results",
    )
    inputs = retained_path(project_root, inputs_relative, directory=True)
    require(
        inputs.parent == packet and inputs.name.startswith("mostaza-reviewed-input-"),
        "Executed input bundle differs from native packet",
    )
    source_paths = {}
    for key in ("source_zip", "source_notebook"):
        pin = acquisition[key]
        require(
            isinstance(pin.get("path"), str) and pin["path"].startswith("results/"),
            "Original download needs a retained project-relative path",
        )
        path = retained_path(project_root, pin["path"])
        require(path.parent == packet, "Original download differs from retained packet")
        _file_pin(path, pin)
        source_paths[key] = path
    with zipfile.ZipFile(source_paths["source_zip"]) as archive:
        members = archive.infolist()
        require(
            len(members) <= 1000
            and sum(member.file_size for member in members) <= 100 * 1024 * 1024,
            "Native packet exceeds read-only verification bounds",
        )
        seen = set()
        for member in members:
            require(
                member.filename not in seen
                and not member.is_dir()
                and (member.external_attr >> 16) & 0o170000 != 0o120000,
                "Duplicate or unsafe native packet member",
            )
            seen.add(member.filename)
            path = retained_path(packet, member.filename)
            require(
                sha256(path.read_bytes()) == sha256(archive.read(member)),
                "Retained native packet bytes differ from original download",
            )
    inventory_pin = acquisition["source_inventory"]
    inventory_path = retained_path(project_root, inventory_pin["path"])
    require(
        inventory_path == native / "source-inventory.json",
        "Native inventory root mismatch",
    )
    _file_pin(inventory_path, inventory_pin)
    inventory = json.loads(inventory_path.read_text())
    require(
        len(inventory["files"]) == inventory_pin["verified_entries"],
        "Native inventory count mismatch",
    )
    seen = set()
    for entry in inventory["files"]:
        require(entry["path"] not in seen, "Duplicate native inventory entry")
        seen.add(entry["path"])
        _file_pin(retained_path(native, entry["path"]), entry)
    payload, hashes, notebook_metadata = _notebook_payload(
        source_paths["source_notebook"]
    )
    for name, data in payload.items():
        require(
            retained_path(inputs, name).read_bytes() == data,
            "Retained executed input differs from notebook",
        )
    require(
        json.loads(payload["cohort.json"]) == cohort,
        "Executed cohort differs from frozen cohort",
    )
    execution_metadata = json.loads(payload["execution-metadata.json"])
    require(
        notebook_metadata["embedded_source_commit"] == execution_metadata["code_commit"]
        and notebook_metadata["embedded_working_tree_sha256"]
        == execution_metadata["working_tree_sha256"],
        "Executed notebook code overlay metadata mismatch",
    )
    url = acquisition["notebook_url"]
    require(
        isinstance(url, str)
        and url.startswith("https://www.kaggle.com/code/")
        and acquisition["run_url"] == url + "/edit/run/" + acquisition["run_id"]
        and type(acquisition["notebook_version"]) is int
        and acquisition["notebook_version"] >= 1
        and acquisition["platform"] == "kaggle"
        and acquisition["observed_notebook_completion"] == "successful",
        "Invalid actual Kaggle run provenance",
    )
    require(inventory["source_run_id"] == url, "Native inventory source run mismatch")
    original_receipt = json.loads(
        retained_path(native, "compact-evidence/official-validation.json").read_text()
    )
    manifests: dict[str, dict[str, Any]] = {}
    records: dict[str, list[dict[str, Any]]] = {}
    agents = {}
    for arm in ("E0", "E1"):
        manifest = json.loads(retained_path(native, arm + "/manifest.json").read_text())
        validate_manifest(manifest)
        require(
            manifest == receipt["manifests"][arm] == original_receipt["manifests"][arm],
            "Declared manifest differs from native execution",
        )
        require(
            manifest["source_run_id"] == url
            and manifest["run_kind"] == "real_kaggle"
            and manifest["cohort"] == cohort["tasks"],
            "Native execution/cohort identity mismatch",
        )
        environment = manifest["environment"]
        require(
            environment["embedded_input_hashes"] == hashes
            and manifest["code_commit"] == execution_metadata["code_commit"]
            and manifest["working_tree_sha256"]
            == execution_metadata["working_tree_sha256"]
            and environment["platform"] == "kaggle"
            and environment["gpu_count"] == 4
            and environment["gpu_model"] == "NVIDIA L4",
            "Native runtime/code source mismatch",
        )
        for package, expected in (
            ("swegemma", "0.2.11"),
            ("adk-submission", "0.2.13"),
            ("adk-eval-core", "0.1.0"),
            ("google-adk", "1.36.1"),
        ):
            require(
                environment["packages"][package] == expected,
                "Native pinned runtime mismatch",
            )
        model_path = "/kaggle/input/models/google/gemma-4/other/" + MODEL + "/2"
        server = manifest["inference"]["server"]
        require(
            manifest["model"] == MODEL
            and server["model"] == model_path
            and server["host"] == "127.0.0.1"
            and server["tensor_parallel_size"] == 4
            and server["enable_lora"] is False,
            "Native model/server binding mismatch",
        )
        archive_bytes = payload["archives/" + arm + ".zip"]
        require(
            sha256(archive_bytes) == manifest["archive_sha256"],
            "Executed archive identity mismatch",
        )
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            names = archive.namelist()
            require(len(names) == len(set(names)), "Duplicate executed archive member")
            files = {name: archive.read(name) for name in names}
        require(
            sha256(canonical_json({name: sha256(data) for name, data in files.items()}))
            == manifest["config_sha256"],
            "Executed archive/config digest mismatch",
        )
        agent = yaml.load(files["agent.yaml"], Loader=IncludeLoader)
        require(
            agent["model"] == MODEL
            and agent.get("agent_class", "LlmAgent") == "LlmAgent"
            and agent.get("generate_content_config")
            == manifest["inference"]["agent_generate_content_config"],
            "Executed agent/model/inference configuration mismatch",
        )
        agents[arm] = agent
        paths = sorted((native / arm / "results").glob("official-result-*.json"))
        require(
            len(paths) == len(cohort["tasks"]), "Native paired result count mismatch"
        )
        normalized = [
            normalize_official_result(path, manifest, native) for path in paths
        ]
        validate_run(manifest, normalized)
        for path, record in zip(paths, normalized, strict=True):
            raw = json.loads(path.read_text())
            trace_relative = arm + "/results/traces/" + Path(raw["trace_path"]).name
            trace = json.loads(retained_path(native, trace_relative).read_text())
            require(
                trace.get("schema_version") == "ATIF-v1.7",
                "Actual source trace schema mismatch",
            )
            model_names = {
                step["model_name"] for step in trace["steps"] if step.get("model_name")
            }
            require(
                model_names == {model_path} and "inference" in record["artifacts"],
                "Native trace does not establish required-model inference",
            )
        require(
            receipt["compiler"][arm] == original_receipt["compiler"][arm]
            and receipt["execution"][arm]
            == original_receipt["execution"][arm]
            == official_execution_receipt(manifest, normalized),
            "Declared official receipts differ from native evidence",
        )
        manifests[arm], records[arm] = manifest, normalized
    require(
        {key: value for key, value in agents["E0"].items() if key != "instruction"}
        == {key: value for key, value in agents["E1"].items() if key != "instruction"},
        "Executed non-treatment agent configuration differs",
    )
    log = retained_path(native, "vllm-server.log").read_text()
    require(
        "'model': '" + model_path + "'" in log
        and "'tensor_parallel_size': 4" in log
        and 'POST /v1/chat/completions HTTP/1.1" 200 OK' in log,
        "Native server log does not establish actual model serving",
    )
    postprocessing = receipt["host_postprocessing"]
    require(
        postprocessing["executed_normalizer_sha256"]
        == hashes["src/mostaza/evaluation/import_results.py"],
        "Executed normalizer provenance mismatch",
    )
    require(
        set(postprocessing["sources"]) == set(HOST_SOURCE_PATHS),
        "Host postprocessing source set mismatch",
    )
    for name, expected in postprocessing["sources"].items():
        require(
            sha256(retained_path(project_root, name).read_bytes()) == expected,
            "Host postprocessing source changed; regenerate metadata",
        )
    return manifests, records, official_source_analysis(manifests, records, native)


if __name__ == "__main__":
    main()
