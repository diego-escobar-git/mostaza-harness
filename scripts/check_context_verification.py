"""Read-only exact CPU gate for context, source binding and experimental isolation."""

from __future__ import annotations

import argparse
import ast
import base64
import io
import json
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import yaml

from mostaza.evaluation.context_candidate import (
    EVIDENCE,
    GUARD,
    NOTEBOOK,
    build_notebook,
    readiness,
)
from mostaza.evaluation.context_variants import (
    CONFIGURATIONS,
    Q1,
    configuration_files,
    digest,
    expected_manifest,
)
from mostaza.packaging import (
    IncludeLoader,
    archive_bytes,
    compile_directory,
)
from mostaza.packaging import (
    configuration_files as historical_files,
)

BASE = "129e76d58d82a8af40d02cefd39218ae70f08f9c"
HISTORICAL_ROOTS = (
    "submission",
    "experiments",
    "notebooks/mostaza-phase2-budget-retrieval.ipynb",
    "notebooks/mostaza-phase2-observed.ipynb",
    "notebooks/mostaza-phase2-startup-corrected.ipynb",
    "docs/implementation/evidence/mostaza-phase1-foundation",
    "docs/implementation/evidence/mostaza-phase2-budget-retrieval",
    "docs/implementation/evidence/mostaza-phase2-observed-run",
    "docs/implementation/evidence/mostaza-phase2-observed-startup",
    "docs/implementation/evidence/mostaza-phase2-startup-correction",
    "docs/implementation/evidence/mostaza-phase2-startup-run",
)
FORBIDDEN = (
    b"requests_7205",
    b"fastapi_15589",
    b"rich_3061",
    b"netrc",
    b"test_empty_default_credentials",
    b"postrun-diagnosis",
    b"test_patch",
    b"reference.patch",
)


def check_history(root: Path) -> int:
    names = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", BASE, "--", *HISTORICAL_ROOTS],
        cwd=root,
        capture_output=True,
        check=True,
        text=True,
    ).stdout.splitlines()
    for name in names:
        data = subprocess.run(
            ["git", "show", f"{BASE}:{name}"], cwd=root, capture_output=True, check=True
        ).stdout
        if (root / name).read_bytes() != data:
            raise ValueError("Historical artifact changed: " + name)
    return len(names)


def check_closure(files: dict[str, bytes]) -> None:
    for data in files.values():
        if any(marker in data for marker in FORBIDDEN):
            raise ValueError("Host diagnosis or task-specific material in archive")
    agent = yaml.load(files["agent.yaml"], Loader=IncludeLoader)
    if set(files) != {"agent.yaml", "eval_config.yaml", agent["instruction"].path}:
        raise ValueError("Unexpected submission dependency closure")


def check_pairs(root: Path) -> None:
    for left, right in (
        ("E0-C8K", "E1-C8K"),
        ("E0-C8K-Q1", "E1-C8K-Q1"),
        ("E1-C8K-Q1", "E1-C8K-Q1-R1"),
    ):
        left_files, right_files = (
            configuration_files(root, left),
            configuration_files(root, right),
        )
        agents = [
            yaml.load(f["agent.yaml"], Loader=IncludeLoader)
            for f in (left_files, right_files)
        ]
        for agent in agents:
            agent.pop("instruction")
        if (
            agents[0] != agents[1]
            or left_files["eval_config.yaml"] != right_files["eval_config.yaml"]
        ):
            raise ValueError("Matched pair changed non-instruction conditions")
        conditions = [
            expected_manifest(root, c)["shared_conditions"] for c in (left, right)
        ]
        if conditions[0] != conditions[1]:
            raise ValueError("Matched runtime/repair/budget conditions differ")
    for config in CONFIGURATIONS[:2]:
        original = historical_files(root, config[:2] + "-B180")
        current = configuration_files(root, config)
        baseline = yaml.load(original["agent.yaml"], Loader=IncludeLoader)
        actual = yaml.load(current["agent.yaml"], Loader=IncludeLoader)
        baseline["generate_content_config"]["max_output_tokens"] = 8192
        if baseline != actual or {
            k: v for k, v in original.items() if k != "agent.yaml"
        } != {k: v for k, v in current.items() if k != "agent.yaml"}:
            raise ValueError("C8K changes more than the output cap")
    for arm in ("E0", "E1"):
        base, quality = [
            configuration_files(root, arm + suffix) for suffix in ("-C8K", "-C8K-Q1")
        ]
        prompts = [
            next(data for name, data in f.items() if name.startswith("prompts/"))
            for f in (base, quality)
        ]
        if prompts[1] != prompts[0] + Q1.encode():
            raise ValueError("Common Q1 delta differs")
    recovery = [configuration_files(root, c) for c in ("E1-C8K-Q1", "E1-C8K-Q1-R1")]
    parts = [
        next(data for name, data in f.items() if name.startswith("prompts/")).split(
            b"### 2. Implement the Solution Directly", 1
        )
        for f in recovery
    ]
    if (
        parts[0][1] != parts[1][1]
        or parts[0][0].split(b"### 1.")[0] != parts[1][0].split(b"### 1.")[0]
    ):
        raise ValueError("R1 changes non-exploration bytes")


def check(root: Path) -> dict[str, Any]:
    count = check_history(root)
    check_pairs(root)
    receipts = []
    with tempfile.TemporaryDirectory(prefix="mostaza-context-compiler-") as temporary:
        for config in CONFIGURATIONS:
            files = configuration_files(root, config)
            check_closure(files)
            directory = Path(temporary) / config
            directory.mkdir()
            for name, data in files.items():
                target = directory / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            compile_directory(directory, root / ".tools/official/bin/python")
            first, second = (
                Path(temporary) / (config + "-a.zip"),
                Path(temporary) / (config + "-b.zip"),
            )
            a, b = archive_bytes(files, first), archive_bytes(files, second)
            if a != b or first.read_bytes() != second.read_bytes():
                raise ValueError("Archive nondeterminism")
            receipts.append(
                {
                    "configuration_id": config,
                    "archive_sha256": a,
                    "manifest_sha256": digest(
                        (root / f"experiments/{config}/manifest.json").read_bytes()
                    ),
                    "official_compiler": "PASS",
                }
            )
    if (root / NOTEBOOK).read_bytes() != build_notebook(root):
        raise ValueError("Fresh candidate provenance mismatch")
    notebook = json.loads((root / NOTEBOOK).read_text())
    if notebook["metadata"]["kaggle"] != {
        "isGpuEnabled": False,
        "isInternetEnabled": False,
    }:
        raise ValueError("Candidate enables GPU/network")
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code" and (
            cell["execution_count"] is not None or cell["outputs"]
        ):
            raise ValueError("Candidate contains executed outputs")
    try:
        exec(compile(GUARD, "fresh_candidate_guard", "exec"), {})
    except RuntimeError:
        pass
    else:
        raise ValueError("Candidate guard did not reject execution")
    tree = ast.parse("".join(notebook["cells"][2]["source"]))
    payload = next(
        ast.literal_eval(n.value)
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(
            isinstance(t, ast.Name) and t.id == "EMBEDDED_PAYLOAD" for t in n.targets
        )
    )
    expected_names = {
        "src/mostaza/__init__.py",
        "src/mostaza/resources.py",
        "src/mostaza/packaging.py",
        "src/mostaza/evaluation/__init__.py",
        "src/mostaza/evaluation/contracts.py",
        "src/mostaza/evaluation/tasks.py",
        "src/mostaza/evaluation/runner.py",
        "resources/manifest.json",
        "experiments/cohort.json",
        "selected-input-pins.json",
        "quota-proposal.json",
        "archives/E0-C8K.zip",
        "archives/E1-C8K.zip",
    }
    if set(payload) != expected_names:
        raise ValueError("Notebook payload escaped the positive allowlist")
    for config in CONFIGURATIONS[:2]:
        with zipfile.ZipFile(
            io.BytesIO(base64.b64decode(payload[f"archives/{config}.zip"]))
        ) as archive:
            actual = {name: archive.read(name) for name in archive.namelist()}
        if actual != configuration_files(root, config):
            raise ValueError("Notebook archive differs from compiled closure")
    actual_readiness = json.loads((root / EVIDENCE / "readiness.json").read_text())
    if (
        actual_readiness != readiness(root)
        or actual_readiness["ready_for_gpu"] is not False
    ):
        raise ValueError("Blocked readiness changed or falsely enabled execution")
    native = subprocess.run(
        [
            str(root / ".tools/official/bin/python"),
            str(root / "scripts/context_cpu_fixtures.py"),
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        timeout=120,
    )
    fixtures = json.loads(native.stdout)
    if fixtures["status"] != "PASS_CPU_FIXTURES":
        raise ValueError("Native CPU fixtures failed")
    return {
        "status": "PASS_CPU_PREPARATION_WITH_BLOCKED_GPU_READINESS",
        "historical_files_unchanged": count,
        "compiler_receipts": receipts,
        "fixtures": fixtures,
        "gpu_ready": False,
        "native_verifier_changed": False,
        "new_gpu_evaluations": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(check(Path(__file__).resolve().parents[1]), sort_keys=True))


if __name__ == "__main__":
    main()
