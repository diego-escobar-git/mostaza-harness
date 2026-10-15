"""Build a fresh blocked notebook; keep every historical candidate byte-identical."""

from __future__ import annotations

import ast
import base64
import json
import subprocess
from pathlib import Path
from typing import Any

from mostaza.evaluation.contracts import canonical_json, sha256

NOTEBOOK = "notebooks/mostaza-notebook-import-cpu.ipynb"
EVIDENCE = "docs/implementation/evidence/mostaza-notebook-import-cpu"
PARENT = "notebooks/mostaza-context-verification.ipynb"
PARENT_SHA = "2fe6aafade2e0c11cf195a648462596651c59e9c5e2c92e750d750807df3f85f"
MODULE = "src/mostaza/evaluation/notebook_import.py"
POLICY = "layout-policy.json"


def payload_of(notebook: dict[str, Any]) -> dict[str, bytes]:
    tree = ast.parse("".join(notebook["cells"][2]["source"]))
    encoded = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(t, ast.Name) and t.id == "EMBEDDED_PAYLOAD" for t in node.targets
        )
    )
    return {name: base64.b64decode(data) for name, data in encoded.items()}


def parent_payload(root: Path) -> dict[str, bytes]:
    data = (root / PARENT).read_bytes()
    if sha256(data) != PARENT_SHA:
        raise ValueError("Frozen parent notebook changed")
    return payload_of(json.loads(data))


def layout_policy(root: Path) -> dict[str, Any]:
    payload = parent_payload(root)
    selection = json.loads(payload["selected-input-pins.json"])
    prerequisites = json.loads((root / EVIDENCE / "prerequisites.json").read_text())
    prefix = ".tools/official/lib/python3.13/site-packages/swegemma/"
    return {
        "profile": "requests-layout-v1",
        "package": "requests",
        "cohort": json.loads(payload["experiments/cohort.json"])["tasks"],
        "snapshots": {
            p["instance_id"]: p for p in selection if p["kind"] == "snapshot"
        },
        "native_sources": {
            p["path"].removeprefix(prefix): p["sha256"]
            for p in prerequisites["external_pins"]
            if p["path"].startswith(prefix)
        },
    }


def replace_once(source: str, before: str, after: str) -> str:
    if source.count(before) != 1:
        raise ValueError("Frozen notebook anchor changed: " + before[:90])
    return source.replace(before, after, 1)


def build_notebook(root: Path) -> bytes:
    notebook = json.loads((root / PARENT).read_bytes())
    payload = parent_payload(root)
    payload[MODULE] = (root / MODULE).read_bytes()
    payload[POLICY] = canonical_json(layout_policy(root))
    cell = notebook["cells"][2]
    code = "".join(cell["source"])
    tree = ast.parse(code)
    lines = code.splitlines(keepends=True)
    replacements = {
        "EMBEDDED_PAYLOAD": {
            name: base64.b64encode(data).decode()
            for name, data in sorted(payload.items())
        },
        "EMBEDDED_HASHES": {
            name: sha256(data) for name, data in sorted(payload.items())
        },
    }
    for node in reversed(tree.body):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in replacements
        ):
            name = node.targets[0].id
            literal = [name + " = {"]
            for key, value in replacements[name].items():
                literal.append("    " + repr(key) + ": (")
                literal.extend(
                    "        " + repr(value[i : i + 68])
                    for i in range(0, len(value), 68)
                )
                literal.append("    ),")
            lines[node.lineno - 1 : node.end_lineno] = ["\n".join([*literal, "}", ""])]
    cell["source"] = "".join(lines).splitlines(keepends=True)
    preflight = "".join(notebook["cells"][3]["source"])
    preflight = replace_once(
        preflight,
        "from mostaza.evaluation.runner import file_digest, snapshot_digest",
        "from mostaza.evaluation.notebook_import import (\n"
        "    execution_envelope, prepare_view, validate_execution_bindings,\n"
        ")\n"
        "from mostaza.evaluation.runner import file_digest, snapshot_digest",
    )
    preflight = replace_once(
        preflight,
        'STARTUP_OBSERVER.stage("preflight.complete")',
        "LAYOUT_POLICY = json.loads((EMBEDDED_ROOT / "
        '"layout-policy.json").read_text())\n'
        'LAYOUT_VIEW = prepare_view(DATA_DIR / "snapshots", '
        'STARTUP_OBSERVER.root / "layout-inputs", LAYOUT_POLICY)\n'
        'STARTUP_OBSERVER.stage("preflight.complete")',
    )
    notebook["cells"][3]["source"] = preflight.splitlines(keepends=True)
    code = "".join(notebook["cells"][6]["source"])
    code = replace_once(
        code,
        "from mostaza.evaluation.runner import describe_runtime, validate_bindings",
        "from mostaza.evaluation.runner import describe_runtime",
    )
    code = replace_once(
        code,
        'snapshots_dir=DATA_DIR / "snapshots",',
        'snapshots_dir=Path(LAYOUT_VIEW["root"]),',
    )
    code = replace_once(
        code,
        "        validate_bindings(\n            config,\n            manifest,",
        "        envelope = execution_envelope(manifest, LAYOUT_VIEW, LAYOUT_POLICY)\n"
        "        validate_execution_bindings(\n        "
        "    config,\n            envelope,\n"
        "            policy=LAYOUT_POLICY,",
    )
    code = replace_once(
        code,
        'with (RUN_ROOT / configuration / "manifest.json").open("xb") as stream:\n'
        "            stream.write(canonical_json(manifest))",
        'with (RUN_ROOT / configuration / "layout-mani'
        'fest.json").open("xb") as stream:\n'
        "            stream.write(canonical_json(envelope))",
    )
    code = replace_once(
        code,
        "                task = evaluator._hydrate_task_from_secret(",
        "                validate_execution_bindings(\n"
        "                    config, envelope, policy=LAYOUT_POLICY, server=server,\n"
        '                    archive_path=EMBEDDED_ROOT / "archives" / '
        '(configuration + ".zip"), wheelhouse_dir=WHEELHOUSE,\n'
        "                )\n"
        "                task = evaluator._hydrate_task_from_secret(",
    )
    code = replace_once(
        code,
        '                    "schema_version": 1,\n',
        '                    "schema_version": 1,\n'
        '                    "layout_envelope_sha256":'
        " sha256(canonical_json(envelope)),\n",
    )
    # Preserve the old import for the parent manifest checks; it is not called on
    # the derived view. Native evaluator and verifier are never replaced.
    notebook["cells"][6]["source"] = code.splitlines(keepends=True)
    notebook["cells"][0]["source"] = [
        "# N-IMPORT-CPU-01: Requests layout integration\n\n"
        "CPU-prepared candidate; native macOS verification and Python3.12 layout "
        "coverage are separate. No GPU authorization or private-scorer parity.\n"
    ]
    notebook["metadata"]["mostaza"]["notebook_import"] = {
        "candidate": "N-IMPORT-CPU-01",
        "profile": "requests-layout-v1",
        "parent_sha256": PARENT_SHA,
        "generator_sha256": sha256(Path(__file__).read_bytes()),
        "payload_sha256": replacements["EMBEDDED_HASHES"],
        "experiment_ids": ["E0-C8K-L1", "E1-C8K-L1"],
        "ready_for_gpu": False,
        "gpu_authorization": None,
        "real_evaluations": "NOT_RUN",
        "linux_runtime_portability": "NOT_TESTED",
        "private_scorer_parity": None,
    }
    notebook["metadata"]["kaggle"] = {"isGpuEnabled": False, "isInternetEnabled": False}
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            cell["execution_count"], cell["outputs"] = None, []
            ast.parse("".join(cell["source"]), feature_version=(3, 12))
    formatted = subprocess.run(
        [str(root / ".venv/bin/ruff"), "format", "--stdin-filename", NOTEBOOK, "-"],
        input=json.dumps(notebook).encode(),
        check=True,
        capture_output=True,
        timeout=30,
    ).stdout
    return canonical_json(json.loads(formatted))


def experiment_manifest(root: Path, arm: str) -> dict[str, Any]:
    if arm not in ("E0", "E1"):
        raise ValueError("Unknown comparison arm")
    parent = arm + "-C8K"
    payload = parent_payload(root)
    return {
        "schema": "mostaza.notebook-layout-experiment/v1",
        "experiment_id": parent + "-L1",
        "parent_configuration": parent,
        "parent_manifest_sha256": sha256(
            (root / f"experiments/{parent}/manifest.json").read_bytes()
        ),
        "unchanged_submission_archive_sha256": sha256(
            payload["archives/" + parent + ".zip"]
        ),
        "layout_policy_sha256": sha256(canonical_json(layout_policy(root))),
        "layout_profile": "requests-layout-v1",
        "ready_for_gpu": False,
        "real_evaluations": "NOT_RUN",
    }
