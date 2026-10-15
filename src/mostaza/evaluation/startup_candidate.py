"""Prepare a new startup profile without changing the previously executed candidate."""

from __future__ import annotations

import ast
import hashlib
import json
import math
import re
import subprocess
import time
import uuid
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from mostaza.evaluation import browser_supervision as previous
from mostaza.evaluation.startup_configuration import ENVIRONMENT, EXTRA_ARGS, PROFILE_ID

NOTEBOOK = "notebooks/mostaza-phase2-startup-corrected.ipynb"
PREVIOUS_SHA256 = "a50664fae097d1c79d2b3b724cb3524e0ad85cbde53cae175e0d2cfdc7494d95"
POLICY = {**previous.POLICY, "id": "B180-startup-v3", "serving_profile": PROFILE_ID}


def validate_receipt(receipt: dict[str, Any]) -> None:
    # Keep the previous exact field schema; run the new guard itself without IO.
    normalized = {**receipt, "policy": previous.POLICY}
    previous.validate_launch_receipt(normalized)
    guard = previous.GUARD.replace("__POLICY__", repr(POLICY))
    tree = ast.parse(guard)
    function = next(
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "require_launch_ready"
    )
    namespace: dict[str, Any] = {
        "BROWSER_AUTHORIZATION": receipt,
        "observation_math": math,
        "observation_re": re,
        "observation_uuid": uuid,
        "observation_time": SimpleNamespace(time=time.time),
    }
    exec(
        compile(ast.Module(body=[function], type_ignores=[]), "v3_guard", "exec"),
        namespace,
    )
    namespace["require_launch_ready"]()


def build_notebook(root: Path, receipt: dict[str, Any] | None = None) -> bytes:
    original = (root / previous.NOTEBOOK).read_bytes()
    if hashlib.sha256(original).hexdigest() != PREVIOUS_SHA256:
        raise ValueError("Previously executed unbound candidate changed")
    if previous.build_observed_notebook(root) != original:
        raise ValueError("Previous candidate provenance changed")
    notebook = json.loads(original)
    guard = "".join(notebook["cells"][1]["source"])
    # Ruff formatted the old policy; identify its literal through AST coordinates.
    tree = ast.parse(guard)
    function = next(
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "require_launch_ready"
    )
    comparison = function.body[1]
    assert isinstance(comparison, ast.If) and isinstance(comparison.test, ast.BoolOp)
    policy_compare = comparison.test.values[1]
    assert isinstance(policy_compare, ast.Compare)
    literal = ast.get_source_segment(guard, policy_compare.comparators[0])
    if literal is None or ast.literal_eval(literal) != previous.POLICY:
        raise ValueError("Policy anchor changed")
    guard = previous._replace_once(guard, literal, repr(POLICY))
    guard = guard.replace(
        "New observed-v2 quota authorization", "New startup-v3 quota authorization"
    )
    if receipt is not None:
        validate_receipt(receipt)
        guard = previous._replace_once(
            guard,
            "BROWSER_AUTHORIZATION = None",
            "BROWSER_AUTHORIZATION = " + repr(receipt),
        )
    source = (root / "src/mostaza/evaluation/startup_configuration.py").read_text()
    guard += (
        '\nSTARTUP_CONFIGURATION = {"__name__": "startup_configuration"}\n'
        + "exec(compile("
        + previous._source_literal(source)
        + ', "startup_configuration.py", "exec"), STARTUP_CONFIGURATION)\n'
        + 'STARTUP_CONFIGURATION["apply_environment"]()\n'
        + (
            'STARTUP_OBSERVER.event("startup.environment.configured", '
            'profile_id="serial-memory-v3", '
            'environment=STARTUP_CONFIGURATION["ENVIRONMENT"])\n'
        )
    )
    notebook["cells"][1]["source"] = guard.splitlines(keepends=True)
    code = "".join(notebook["cells"][-1]["source"])
    code = previous._replace_once(
        code, "extra_args=[],", "extra_args=" + repr(EXTRA_ARGS) + ","
    )
    code = previous._replace_once(
        code,
        '    OBSERVATION_NAMESPACE["start_observed_server"](server, STARTUP_OBSERVER)',
        '    STARTUP_CONFIGURATION["observe_server_environment"]'
        "(server, STARTUP_OBSERVER)\n"
        '    OBSERVATION_NAMESPACE["start_observed_server"](server, STARTUP_OBSERVER)\n'
        '    STARTUP_CONFIGURATION["memory_observation"]'
        '(STARTUP_OBSERVER, "model_ready")',
    )
    code = previous._replace_once(
        code,
        '            "embedded_input_hashes": EMBEDDED_HASHES,',
        '            "embedded_input_hashes": EMBEDDED_HASHES,\n'
        '            "serving_profile": "serial-memory-v3",\n'
        '            "startup_configuration_sha256": file_digest(\n'
        '                RUN_ROOT / "startup-configuration.json"),',
    )
    notebook["cells"][-1]["source"] = code.splitlines(keepends=True)
    notebook["cells"][0]["source"] = [
        "# Mostaza B180 startup-v3 preparation\n\n"
        "New quota approval required. GPU and internet disabled; "
        "no evaluations executed.\n"
        "Common serving profile serial-memory-v3: restored environment, "
        "max-num-seqs=1.\n"
    ]
    notebook["metadata"]["mostaza"]["observed_preparation"]["policy"] = POLICY
    notebook["metadata"]["mostaza"]["observed_preparation"]["authorization"] = (
        None if receipt is None else receipt["approval_id"]
    )
    notebook["metadata"]["mostaza"]["startup_correction"] = {
        "profile_id": PROFILE_ID,
        "environment": ENVIRONMENT,
        "extra_args": EXTRA_ARGS,
        "previous_notebook_sha256": PREVIOUS_SHA256,
        "configuration_source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "gpu_execution_validated": False,
    }
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            ast.parse("".join(cell["source"]), feature_version=(3, 12))
    formatted = subprocess.run(
        [str(root / ".venv/bin/ruff"), "format", "--stdin-filename", NOTEBOOK, "-"],
        input=json.dumps(notebook).encode(),
        check=True,
        capture_output=True,
        timeout=30,
    ).stdout
    return (
        json.dumps(json.loads(formatted), sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()
