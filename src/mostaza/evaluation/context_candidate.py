"""Fresh GPU-disabled candidate, built from the frozen startup notebook and closures."""

from __future__ import annotations

import ast
import base64
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from mostaza.evaluation import startup_candidate
from mostaza.evaluation.context_variants import (
    CONFIGURATIONS,
    PAIR,
    configuration_files,
    digest,
)
from mostaza.packaging import archive_bytes

NOTEBOOK = "notebooks/mostaza-context-verification.ipynb"
EVIDENCE = "docs/implementation/evidence/mostaza-context-verification"
GUARD = """CPU_PREPARATION_ONLY = True
VERIFICATION_ORIGIN_CONFIRMED = False
GPU_AUTHORIZATION = None
raise RuntimeError(
    "CPU preparation only: exact verifier binding and GPU approval are absent"
)
"""


def build_notebook(root: Path, selected: tuple[str, str] = PAIR) -> bytes:
    allowed = (PAIR, ("E0-C8K-Q1", "E1-C8K-Q1"), ("E1-C8K-Q1", "E1-C8K-Q1-R1"))
    if selected not in allowed:
        raise ValueError("Select one approved matched comparison, never a mixed pair")
    frozen = (root / startup_candidate.NOTEBOOK).read_bytes()
    if (
        digest(frozen)
        != "127ad5adec71cd25d8da80afbcb78cc8f1a899a9dcca2ba9a58af51900e4cf1b"
    ):
        raise ValueError("Historical startup notebook changed")
    notebook = json.loads(frozen)
    cell = notebook["cells"][2]
    code = "".join(cell["source"])
    tree = ast.parse(code)
    payload = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "EMBEDDED_PAYLOAD" for t in node.targets
        ):
            payload = {
                name: base64.b64decode(value)
                for name, value in ast.literal_eval(node.value).items()
            }
    if payload is None:
        raise ValueError("Frozen embedded input dictionary missing")
    payload = {k: v for k, v in payload.items() if not k.startswith("archives/")}
    quota = json.loads(payload["quota-proposal.json"])
    quota.update(
        batch="C8K-context-only" if selected == PAIR else "C8K-separate-treatment",
        configurations=list(selected),
    )
    payload["quota-proposal.json"] = (
        json.dumps(quota, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()
    with tempfile.TemporaryDirectory(prefix="mostaza-context-payload-") as directory:
        for configuration in selected:
            path = Path(directory) / (configuration + ".zip")
            archive_bytes(configuration_files(root, configuration), path)
            payload["archives/" + path.name] = path.read_bytes()
    replacements = {
        "EMBEDDED_PAYLOAD": {
            name: base64.b64encode(value).decode()
            for name, value in sorted(payload.items())
        },
        "EMBEDDED_HASHES": {
            name: digest(value) for name, value in sorted(payload.items())
        },
    }

    def mapping_literal(name: str, values: dict[str, str]) -> str:
        output = [name + " = {"]
        for key, value in values.items():
            output.append("    " + repr(key) + ": (")
            output.extend(
                "        " + repr(value[i : i + 68]) for i in range(0, len(value), 68)
            )
            output.append("    ),")
        return "\n".join([*output, "}", ""])

    # Replace data assignments at exact AST spans; keep bootstrap logic intact.
    lines = code.splitlines(keepends=True)
    for node in reversed(tree.body):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in replacements
        ):
            lines[node.lineno - 1 : node.end_lineno] = [
                mapping_literal(node.targets[0].id, replacements[node.targets[0].id])
            ]
    cell["source"] = "".join(lines).splitlines(keepends=True)
    guard_source = "".join(notebook["cells"][1]["source"])
    anchor = "BROWSER_AUTHORIZATION = None"
    if guard_source.count(anchor) != 1:
        raise ValueError("Historical authorization anchor changed")
    notebook["cells"][1]["source"] = guard_source.replace(
        anchor, GUARD + "\n" + anchor, 1
    ).splitlines(keepends=True)
    notebook["cells"][0]["source"] = [
        (
            "# Context / verification CPU preparation\n\nNew matched "
            "variants; verifier import provenance blocks real "
            "readiness. No GPU authorization.\n"
        )
    ]
    notebook["metadata"]["mostaza"]["context_verification"] = {
        "configurations": list(selected),
        "all_prepared_configurations": list(CONFIGURATIONS),
        "parent_candidate_sha256": digest(frozen),
        "generator_sha256": digest(Path(__file__).read_bytes()),
        "payload_sha256": replacements["EMBEDDED_HASHES"],
        "verification_origin_confirmed": False,
        "gpu_authorization": None,
        "real_evaluations": 0,
    }
    notebook["metadata"]["kaggle"] = {"isGpuEnabled": False, "isInternetEnabled": False}
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            cell["execution_count"], cell["outputs"] = None, []
            ast.parse("".join(cell["source"]), feature_version=(3, 12))
    formatted = subprocess.run(
        [str(root / ".venv/bin/ruff"), "format", "--stdin-filename", NOTEBOOK, "-"],
        input=json.dumps(notebook).encode(),
        capture_output=True,
        check=True,
        timeout=30,
    ).stdout
    return (
        json.dumps(json.loads(formatted), sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()


def readiness(root: Path) -> dict[str, Any]:
    notebook = build_notebook(root)
    return {
        "status": "PREPARED_BLOCKED_VERIFICATION_ORIGIN",
        "configurations": list(CONFIGURATIONS),
        "candidate_pair": list(PAIR),
        "candidate_sha256": digest(notebook),
        "manifest_sha256": {
            c: digest((root / f"experiments/{c}/manifest.json").read_bytes())
            for c in CONFIGURATIONS
        },
        "ready_for_gpu": False,
        "gpu_starts": 0,
        "real_evaluations": "NOT_RUN",
        "blockers": [
            "Exact Kaggle verifier-process import/source receipt is unavailable",
            (
                "Official setup script and its effective editable-"
                "install result were not retained locally"
            ),
            "Fresh GPU authorization, quota and exact session controls are absent",
        ],
        "protocol_change_proposed_not_applied": (
            "Obtain official setup provenance and an organizer-"
            "supported executing-process import receipt; changing "
            "verifier PYTHONPATH, plugins or grader requires a "
            "separate reviewed protocol decision"
        ),
        "context_limit": (
            "8192 output reservation increases nominal input "
            "headroom; no future-fit guarantee or automatic "
            "compaction"
        ),
        "physical_gpu_release_confirmed": None,
    }
