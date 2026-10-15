"""Validate only P-CV-01 CPU compatibility/parity and frozen model payloads."""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import io
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Any

from mostaza.evaluation.context_candidate import NOTEBOOK
from mostaza.evaluation.context_variants import CONFIGURATIONS, configuration_files
from mostaza.evaluation.runner import WHEEL_PINS

BASE = "eb04b1ccf6be629c7490d42b9e8de8cd28784bdc"
PLUGIN = "src/mostaza/evaluation/pytest_origin_receipt.py"
PYTEST_SHA = "872f880de3fc3a5bdc88a11b39c9710c3497a547cfa9320bc3c5e62fbf272e79"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compatibility(root: Path) -> dict[str, Any]:
    wheel = root / "resources/official/swegemma-0.2.11-py3-none-any.whl"
    if digest(wheel.read_bytes()) != WHEEL_PINS[wheel.name]:
        raise ValueError("Reviewed official harness wheel changed")
    installed = root / ".tools/official/lib/python3.13/site-packages"
    sources = {}
    with zipfile.ZipFile(wheel) as archive:
        for name in ("swegemma/config.py", "swegemma/harness/verification.py"):
            original = archive.read(name)
            if (installed / name).read_bytes() != original:
                raise ValueError("Installed native source differs from reviewed wheel")
            sources[name] = digest(original)
        config = ast.parse(archive.read("swegemma/config.py").decode())
        native = next(
            n
            for n in config.body
            if isinstance(n, ast.ClassDef) and n.name == "EvalConfig"
        )
        fields = sorted(
            n.target.id
            for n in native.body
            if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)
        )
        verification = archive.read("swegemma/harness/verification.py").decode()
        if "python3 -s -m pytest {test_files_str}" not in verification:
            raise ValueError("Reviewed verification invocation changed")
    pytest_wheel = root / "resources/official/pytest-8.4.2-py3-none-any.whl"
    if digest(pytest_wheel.read_bytes()) != PYTEST_SHA:
        raise ValueError("CPU compatibility wheel missing/changed")
    with zipfile.ZipFile(pytest_wheel) as archive:
        sources["pytest8.4.2/_pytest/hookspec.py"] = digest(
            archive.read("_pytest/hookspec.py")
        )
    sources["pytest9.1.1/_pytest/hookspec.py"] = digest(
        (installed / "_pytest/hookspec.py").read_bytes()
    )
    return {
        "pytest_public_api": (
            "Explicit -p loading and tryfirst pytest_runtest_call with argument pruning"
        ),
        "pinned_harness": "swegemma0.2.11",
        "native_source_sha256": sources,
        "inspected_eval_config_fields": fields,
        "harness_config_support_for_plugin": (
            "No plugin activation parameter in inspected "
            "EvalConfig; native verifier constructs fixed "
            "command"
        ),
        "organizer_permission_or_scorer_parity": None,
        "organizer_permission_missing_reason": (
            "Official setup unavailable (prior403); no real "
            "verifier change or organizer acceptance tested"
        ),
        "official_sources": [
            "https://docs.pytest.org/en/8.4.x/how-to/plugins.html",
            (
                "https://docs.pytest.org/en/8.4.x/reference/refer"
                "ence.html#pytest.hookspec.pytest_runtest_call"
            ),
            "https://docs.pytest.org/en/stable/how-to/writing_plugins.html",
            "https://www.kaggle.com/datasets/metric/gemma-4-developer-agent-wheelhouse",
        ],
        "pytest842_wheel": {
            "path": str(pytest_wheel.relative_to(root)),
            "sha256": PYTEST_SHA,
            "url": (
                "https://files.pythonhosted.org/packages/a8/a4/20"
                "da314d277121d6534b3a980b29035dcd51e6744bd79075a6"
                "ce8fa4eb8d/pytest-8.4.2-py3-none-any.whl"
            ),
            "metadata": "https://pypi.org/pypi/pytest/8.4.2/json",
        },
    }


def isolation(root: Path) -> dict[str, Any]:
    paths = subprocess.run(
        [
            "git",
            "ls-tree",
            "-r",
            "--name-only",
            BASE,
            "--",
            "submission",
            "experiments",
            "notebooks",
            "pyproject.toml",
            "uv.lock",
            "src/mostaza/evaluation/verification_origin.py",
            "src/mostaza/evaluation/context_candidate.py",
            "docs/implementation/evidence",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    for name in paths:
        before = subprocess.run(
            ["git", "show", f"{BASE}:{name}"], cwd=root, capture_output=True, check=True
        ).stdout
        if (root / name).read_bytes() != before:
            raise ValueError("Historical/protected input changed: " + name)
    for config in CONFIGURATIONS:
        files = configuration_files(root, config)
        if any(
            b"mostaza_origin_receipt" in data or b"P-CV-01" in data
            for data in files.values()
        ):
            raise ValueError("Diagnostic plugin leaked into agent closure")
    notebook = json.loads((root / NOTEBOOK).read_text())
    tree = ast.parse("".join(notebook["cells"][2]["source"]))
    payload = next(
        ast.literal_eval(n.value)
        for n in tree.body
        if isinstance(n, ast.Assign)
        and any(
            isinstance(t, ast.Name) and t.id == "EMBEDDED_PAYLOAD" for t in n.targets
        )
    )
    for name, value in payload.items():
        data = base64.b64decode(value)
        if b"mostaza_origin_receipt" in data or b"P-CV-01" in data:
            raise ValueError("Diagnostic data in notebook payload")
        if name.startswith("archives/"):
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                if any(
                    b"mostaza_origin_receipt" in archive.read(n)
                    or b"P-CV-01" in archive.read(n)
                    for n in archive.namelist()
                ):
                    raise ValueError("Diagnostic data in embedded agent archive")
    readiness = json.loads(
        (
            root
            / "docs/implementation/evidence/mostaza-context-verification/readiness.json"
        ).read_text()
    )
    if readiness["ready_for_gpu"] is not False:
        raise ValueError("CPU diagnostic must not unlock real readiness")
    ast.parse((root / PLUGIN).read_text(), feature_version=(3, 12))
    return {
        "historical_files_unchanged": len(paths),
        "agent_closures_checked": len(CONFIGURATIONS),
        "notebook_payload_contains_plugin": False,
        "real_gpu_readiness_changed": False,
        "plugin_auto_registration": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.add_argument("--raw-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source_review = compatibility(root)
    boundary = isolation(root)
    command = [
        str(root / ".tools/official/bin/python"),
        str(root / "scripts/pcv01_cpu_fixtures.py"),
    ]
    if args.raw_dir:
        command += ["--raw-dir", str(args.raw_dir)]
    completed = subprocess.run(
        command, cwd=root, capture_output=True, text=True, timeout=180, check=True
    )
    native = json.loads(completed.stdout)
    if native["status"] != "PASS_PCV01_CPU" or len(native["runs"]) != 14:
        raise ValueError("Native P-CV-01 control matrix failed")
    print(
        json.dumps(
            {
                "status": "PASS_PCV01_CPU_ONLY",
                "compatibility": source_review,
                "isolation": boundary,
                "cpu_controls": native,
                "real_kaggle_compatibility_confirmed": False,
                "real_kaggle_verifier_changed": False,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
