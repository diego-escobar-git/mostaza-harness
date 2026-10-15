"""CPU contract checks and immutable evidence for notebook integration."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
from typing import Any

from mostaza.evaluation.contracts import canonical_json
from mostaza.evaluation.notebook_import_candidate import (
    EVIDENCE,
    MODULE,
    NOTEBOOK,
    POLICY,
    build_notebook,
    experiment_manifest,
    layout_policy,
    parent_payload,
    payload_of,
)
from mostaza.evaluation.requests_import_cpu import COVERAGE as PYTEST_COVERAGE
from mostaza.evaluation.requests_import_cpu import assess, bound
from mostaza.evaluation.verify_task_cpu import digest

CASES = ("L01", "L02", "L03", "R00", "R01", "R02")
SETUP_STEPS = (
    "setup_container_wheels",
    "extract_snapshot",
    "setup_git_exclude",
    "install_editable_package",
    "install_test_dependencies",
    "setup_workspace_test_config",
    "setup_baseline_commit",
)


def immutable_inputs(root: Path) -> dict[str, Any]:
    evidence = root / EVIDENCE
    manifest: dict[str, Any] = json.loads((evidence / "prerequisites.json").read_text())
    approval = json.loads((evidence / "approval.json").read_text())
    if (
        approval["plan_sha256"] != digest(evidence / "plan-for-approval.md")
        or manifest["plan_sha256"] != approval["plan_sha256"]
    ):
        raise ValueError("Approved N-IMPORT plan changed")
    for item in manifest["frozen_existing_files"] + manifest["external_pins"]:
        if digest(root / item["path"]) != item["sha256"]:
            raise ValueError("Immutable file changed: " + item["path"])
    prefix = manifest["runbook_prefix"]
    if (
        hashlib.sha256(
            (root / prefix["path"]).read_bytes()[: prefix["bytes"]]
        ).hexdigest()
        != prefix["sha256"]
    ):
        raise ValueError("Historical runbook changed")
    return manifest


def candidate_contract(root: Path) -> dict[str, Any]:
    immutable_inputs(root)
    path = root / NOTEBOOK
    if path.read_bytes() != build_notebook(root):
        raise ValueError("Candidate is not reproducible")
    notebook = json.loads(path.read_bytes())
    if notebook["metadata"]["kaggle"] != {
        "isGpuEnabled": False,
        "isInternetEnabled": False,
    }:
        raise ValueError("Candidate enables execution resources")
    parent = json.loads(
        (root / "notebooks/mostaza-context-verification.ipynb").read_bytes()
    )
    if notebook["cells"][1] != parent["cells"][1]:
        raise ValueError("Fail-closed guard changed")
    # Execute only the unconditional CPU guard fragment, no bootstrap/IO.
    from mostaza.evaluation.context_candidate import GUARD

    try:
        exec(compile(GUARD, "cpu_only_guard", "exec"), {})
    except RuntimeError:
        pass
    else:
        raise ValueError("CPU-only guard did not reject")
    payload = payload_of(notebook)
    original = parent_payload(root)
    if set(payload) != set(original) | {MODULE, POLICY}:
        raise ValueError("Payload escaped positive allowlist")
    if any(payload[name] != data for name, data in original.items()):
        raise ValueError("Parent closure or host source changed")
    if payload[MODULE] != (root / MODULE).read_bytes():
        raise ValueError("Host adapter mismatch")
    if payload[POLICY] != canonical_json(layout_policy(root)):
        raise ValueError("Policy mismatch")
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            if cell["outputs"] or cell["execution_count"] is not None:
                raise ValueError("Candidate has executed output")
            ast.parse("".join(cell["source"]), feature_version=(3, 12))
    for name, data in payload.items():
        if name.endswith(".py"):
            ast.parse(data.decode(), feature_version=(3, 12))
    preflight = "".join(notebook["cells"][3]["source"])
    if (
        'STARTUP_OBSERVER.root / "layout-inputs"' not in preflight
        or 'RUN_ROOT / "layout-inputs"' in preflight
    ):
        raise ValueError("Preflight uses a not-yet-defined run root")
    execution = "".join(notebook["cells"][6]["source"])
    required = [
        'snapshots_dir=Path(LAYOUT_VIEW["root"])',
        "envelope = execution_envelope(manifest, LAYOUT_VIEW, LAYOUT_POLICY)",
        "evaluator = Evaluator(config)",
        "evaluator._hydrate_task_from_secret(",
        "evaluator.evaluate_task(",
        '"layout-manifest.json"',
        '"layout_envelope_sha256": sha256(canonical_json(envelope))',
    ]
    if any(item not in execution for item in required):
        raise ValueError("Notebook wiring changed")
    if execution.count("validate_execution_bindings(") != 2:
        raise ValueError("Missing construct/dispatch provenance check")
    for arm in ("E0", "E1"):
        name = f"experiments/{arm}-C8K-L1/manifest.json"
        if json.loads((root / name).read_bytes()) != experiment_manifest(root, arm):
            raise ValueError("New host experiment manifest mismatch")
    return {
        "status": "PASS_BLOCKED_NOTEBOOK_CONTRACT",
        "payload_count": len(payload),
        "gpu_readiness": False,
        "native_agent_loop_executed": False,
    }


SETUP_COVERAGE = "actual_native_setup_import_cpu"


def setup_binding(
    event: dict[str, Any], expected: dict[str, Any], case_home: Path
) -> tuple[bool, list[str]]:
    """Interpret a -c witness; never change the process or its retained receipt."""
    paths = event.get("sys_path")
    if (
        event.get("coverage") != SETUP_COVERAGE
        or not isinstance(paths, list)
        or not paths
        or paths[0] != ""
        or any(not isinstance(path, str) or not path for path in paths[1:])
    ):
        raise ValueError("Malformed setup -c path witness")
    effective = [event["cwd"], *paths[1:]]
    # Reuse the unchanged pytest binding predicate on an explicit interpretation
    # view. The raw receipt, including its distinct scope and "", is preserved.
    interpreted = {**event, "coverage": PYTEST_COVERAGE, "sys_path": effective}
    return bound(interpreted, expected, case_home), effective


def assess_case(row: dict[str, Any], case_home: Path) -> dict[str, Any]:
    result = assess(row, case_home)
    events = row["setup_events"]
    expected = row["setup_expected"]
    setup_ok, effective_paths = (
        setup_binding(events[0], expected, case_home)
        if len(events) == 1
        else (False, [])
    )
    if (
        len(events) != 1
        or events[0]["node"] != "setup"
        or events[0]["outcome"] != "passed"
        or not setup_ok
        or tuple(row["setup_steps"]) != SETUP_STEPS
        or not row["setup_baseline_alias"].startswith("120000 ")
        or row["setup_working_diff"].strip()
    ):
        raise ValueError("Agent setup reconstruction witness failed")
    if events[0]["pid"] == row["events"][0]["pid"]:
        raise ValueError("Setup/verification reused a stale process witness")
    host = Path(row["relocated_host"])
    launch = Path(row["launch_cwd"])
    if (
        not host.is_relative_to(case_home)
        or " " not in str(host)
        or "ñ" not in str(host)
        or host == launch
        or "ñ" not in str(launch)
        or not Path(row["host_module_file"]).is_relative_to(host)
        or Path(row["events"][0]["cwd"]).is_relative_to(host)
    ):
        raise ValueError("Relocation/host/native path coverage mismatch")
    # Paths/fingerprints were observed before native cleanup removed the alias.
    if not row["view"]["layout"]["derived_prebootstrap_tree"]:
        raise ValueError("No derived layout tree")
    return {
        **result,
        "id": "N-" + row["id"],
        "setup_binding": True,
        "setup_witness": events[0],
        "setup_effective_sys_path": effective_paths,
        "setup_path_interpretation": (
            "Only the first empty -c entry denotes witnessed cwd; "
            "raw witness and process unchanged"
        ),
        "setup_steps": row["setup_steps"],
        "actual_inputs": row["view"],
        "relocated_host": str(host),
        "launch_cwd": str(launch),
        "host_module_file": row["host_module_file"],
        "coverage_limit": (
            "Host payload/cwd include spaces and Unicode; native sandbox paths "
            "are ASCII. No native agent loop or Linux runtime executed."
        ),
    }
