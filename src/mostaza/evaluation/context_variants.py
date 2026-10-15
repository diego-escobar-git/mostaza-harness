"""Approved context/workflow variants without changing historical packaging inputs."""

from __future__ import annotations

import copy
import difflib
import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from mostaza.packaging import (
    Include,
    IncludeDumper,
    IncludeLoader,
    PackagingError,
    load_manifest,
)
from mostaza.packaging import (
    configuration_files as historical_files,
)

CONFIGURATIONS = ("E0-C8K", "E1-C8K", "E0-C8K-Q1", "E1-C8K-Q1", "E1-C8K-Q1-R1")
PAIR = CONFIGURATIONS[:2]
Q1 = """
## Shared Workflow Quality Q1
- Locate the symbol before reading a bounded range. Use the exact read_file keys
  filepath, start_line and end_line; prefer at most 50 relevant lines per read.
  Check the returned start_line, end_line and is_truncated before drawing conclusions.
  After one unsuccessful duplicate read, use a bounded shell read with an authorized
  command rather than repeating the same request. Reuse already observed code.
- Before verification, confirm the imported module resolves to the edited workspace
  source. For a src layout, establish the source binding within the workspace and
  report it; do not mistake an installed copy for the changed implementation.
- Use targeted assertions whose failures exit nonzero. Establish a meaningful
  negative control on the unchanged behavior and a positive control that should
  remain valid. Printing observations or a successful shell exit alone is insufficient.
- Inspect the final source diff and remove temporary reproduction artifacts before
  submit_patch. Reserve time for implementation and targeted verification. Do not
  alter protected tests, dependencies, grader settings or unrelated files.
"""
DECISION = """
9. When choosing how to resolve a lexical dead end or an unresolved relationship,
   emit a short `Retrieval decision: ...` statement naming the question and useful
   native query, or why retrieval is unnecessary or unavailable. This is an
   observable navigation decision, not a requirement to call a tool. Never invent
   a result or call graph/vector tools just to satisfy a metric.

"""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def prompt(root: Path, configuration: str) -> bytes:
    if configuration not in CONFIGURATIONS:
        raise PackagingError("Unknown context configuration")
    arm = configuration[:2]
    base = load_manifest(root, arm + "-B180")
    text = (root / "submission" / str(base["prompt"])).read_text()
    if configuration.endswith("-R1"):
        recovery = (root / "submission/prompts/hybrid-recovery.md").read_text()
        before, rest = recovery.split("### 2. Implement the Solution Directly", 1)
        text = (
            before.rstrip()
            + "\n"
            + DECISION
            + "### 2. Implement the Solution Directly"
            + rest
        )
    if "-Q1" in configuration:
        text += Q1
    return text.encode()


def expected_manifest(root: Path, configuration: str) -> dict[str, Any]:
    if configuration not in CONFIGURATIONS:
        raise PackagingError("Unknown context configuration")
    base_id = configuration[:2] + "-B180"
    base = load_manifest(root, base_id)
    generation = {**base["generation_parameters"], "max_output_tokens": 8192}
    quality = "-Q1" in configuration
    recovery = configuration.endswith("-R1")
    selected = f"prompts/{configuration.lower()}.md" if quality else base["prompt"]
    shared = copy.deepcopy(base["shared_conditions"])
    shared["generation_parameters"] = generation
    shared["serving_profile"] = "serial-memory-v3"
    shared["workflow_quality"] = "Q1" if quality else None
    shared["repair_policy"] = (
        "Q1 targeted assertions; no repair loop" if quality else base["repair_policy"]
    )
    shared["cohort_sha256"] = digest((root / "experiments/cohort.json").read_bytes())
    original = (root / "submission" / base["prompt"]).read_bytes()
    text = prompt(root, configuration)
    return {
        "schema_version": 1,
        "configuration_id": configuration,
        "arm": configuration[:2],
        "base_configuration_id": base_id,
        "status": "ready_for_compiler",
        "ready_for_packaging": True,
        "ready_for_evaluation": False,
        "real_evaluation": "NOT_RUN",
        "model": base["model"],
        "generation_parameters": generation,
        "budgets": base["budgets"],
        "tools": base["tools"],
        "prompt": selected,
        "prompt_sha256": digest(text),
        "shared_conditions": shared,
        "shared_conditions_sha256": digest(_json(shared)),
        "base_manifest_sha256": digest(
            (root / f"experiments/{base_id}/manifest.json").read_bytes()
        ),
        "treatment": "exploration_recovery_R1"
        if recovery
        else "common_workflow_Q1"
        if quality
        else "output_cap_only",
        "compared_configuration_id": "E1-C8K-Q1"
        if recovery
        else configuration[:2] + "-C8K"
        if quality
        else base_id,
        "prompt_diff": "".join(
            difflib.unified_diff(
                original.decode().splitlines(True),
                text.decode().splitlines(True),
                fromfile=base["prompt"],
                tofile=selected,
            )
        ),
        "limitations": [
            (
                "Compiler readiness is not runtime verification binding"
                " or GPU authorization"
            ),
            "Output headroom is not a guarantee of future context fit",
            "Native compaction and cache remain disabled",
        ],
    }


def configuration_files(root: Path, configuration: str) -> dict[str, bytes]:
    expected = expected_manifest(root, configuration)
    path = root / f"experiments/{configuration}/manifest.json"
    if json.loads(path.read_text()) != expected:
        raise PackagingError("Context manifest drift")
    files = historical_files(root, expected["base_configuration_id"])
    agent = yaml.load(files["agent.yaml"], Loader=IncludeLoader)
    old = agent["instruction"].path
    del files[old]
    agent["generate_content_config"] = expected["generation_parameters"]
    agent["instruction"] = Include(expected["prompt"])
    files[expected["prompt"]] = prompt(root, configuration)
    files["agent.yaml"] = yaml.dump(
        agent, Dumper=IncludeDumper, sort_keys=True
    ).encode()
    return dict(sorted(files.items()))


def prepare_manifests(root: Path) -> None:
    for configuration in CONFIGURATIONS:
        path = root / f"experiments/{configuration}/manifest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = _json(expected_manifest(root, configuration))
        if path.exists() and path.read_bytes() != data:
            raise PackagingError("Refusing to replace an existing different manifest")
        if not path.exists():
            path.write_bytes(data)
