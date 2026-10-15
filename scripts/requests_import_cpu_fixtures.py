"""Direct native CPU layout cases; own diagnostics, no verifier/environment edits."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib
import importlib.metadata
import json
import platform
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mostaza.evaluation.requests_import_cpu import (
    COVERAGE,
    check_layout,
    git,
    immutable_inputs,
    layout_patch,
    validate_delta,
)
from mostaza.evaluation.verify_task_cpu import (
    FINGERPRINT_SOURCE,
    digest,
    expected_function,
    validate_archive,
)

TEST_FILE = "test_mostaza_import_diagnostic.py"
FAULTY = "def evaluate():\n    return 0\n"


def test_source(expected: dict[str, Any], output: Path) -> str:
    legacy = importlib.import_module("verify_task_cpu_fixtures")
    header = f"""import os, sys, json, hashlib, importlib, platform
from pathlib import Path
import pytest
EXPECTED = {expected!r}
OUTPUT = Path({str(output)!r})
{FINGERPRINT_SOURCE}
def observe(node, action):
    parent = importlib.import_module(EXPECTED["package"])
    module = importlib.import_module(EXPECTED["module"])
    function = getattr(module, EXPECTED["function"])
    cwd = Path.cwd()
    alias = cwd / EXPECTED["package"]
    parent_raw = str(parent.__file__)
    module_raw = str(module.__file__)
    record = {{"coverage": {COVERAGE!r}, "pair": EXPECTED["pair"], "node": node,
              "pid": os.getpid(), "ppid": os.getppid(), "executable": sys.executable,
              "python": platform.python_version(), "pytest": pytest.__version__,
              "cwd": str(cwd), "sys_path": list(sys.path),
              "parent_raw": parent_raw,
              "parent_canonical": str(Path(parent_raw).resolve()),
              "parent_sha256":
                  hashlib.sha256(Path(parent_raw).read_bytes()).hexdigest(),
              "module_raw": module_raw,
              "module_canonical": str(Path(module_raw).resolve()),
              "module_sha256":
                  hashlib.sha256(Path(module_raw).read_bytes()).hexdigest(),
              "function_raw": function.__code__.co_filename,
              "function_canonical": str(Path(function.__code__.co_filename).resolve()),
              "function_module": function.__module__,
              "function_fingerprint": code_fingerprint(function.__code__),
              "fingerprint_algorithm": "cpu-code-json-v1",
              "alias_target": os.readlink(alias) if alias.is_symlink() else None,
              "public_version": getattr(parent, "__version__", None)}}
    record["public_version_reason"] = (None if record["public_version"] is not None
                                       else "Public package exposes no version")
    target_parent = cwd / "src" / EXPECTED["package"] / "__init__.py"
    matches = (record["parent_canonical"] == str(target_parent)
               and record["parent_sha256"] == EXPECTED["parent_sha256"]
               and record["module_canonical"] == str(cwd / EXPECTED["relative_file"])
               and record["module_sha256"] == EXPECTED["file_sha256"]
               and record["function_canonical"] == str(cwd / EXPECTED["relative_file"])
               and record["function_module"] == EXPECTED["module"]
               and record["function_fingerprint"] == EXPECTED["function_fingerprint"]
               and record["alias_target"] == "src/" + EXPECTED["package"])
    try:
        action(function, matches)
        record["outcome"] = "passed"
    except AssertionError:
        record["outcome"] = "assertion_failed"
        raise
    except BaseException as error:
        record["outcome"] = "exception"
        record["exception_type"] = type(error).__name__
        raise
    finally:
        records = json.loads(OUTPUT.read_text()) if OUTPUT.exists() else []
        records.append(record)
        temporary = OUTPUT.with_suffix(".tmp")
        temporary.write_text(json.dumps(records, sort_keys=True))
        temporary.replace(OUTPUT)
"""
    if expected["package"] == "requests":
        old = legacy.diagnostic_source("R00", output, expected)
        # Preserve the independently authored five assertion bodies verbatim.
        body = old[old.index("\ndef test_origin_binding():") :]
    else:
        body = """
def test_required():
    def check(function, matches):
        assert matches, "intended workspace package not imported"
        assert function() == 1
    observe("test_required", check)
"""
    return header + str(body)


def run_case(root: Path, case_dir: Path, case: str) -> None:
    manifest = immutable_inputs(root)
    legacy = importlib.import_module("verify_task_cpu_fixtures")
    case_dir.mkdir()
    scratch = case_dir / "fixture"
    scratch.mkdir()
    pair = case.split("-")[0]
    receipt = case_dir.parent / (pair + "-current.json")
    if receipt.exists() or receipt.with_suffix(".tmp").exists():
        raise ValueError("Stale pair receipt exists")
    agent_patch = ""
    if case.startswith("R"):
        package, module, function = "requests", "requests.utils", "get_netrc_auth"
        product = "src/requests/utils.py"
        snapshot = root / "resources/official/snapshots/requests_7205.tgz"
        validate_archive(snapshot)
        with tarfile.open(snapshot) as archive:
            archive.extractall(scratch, filter="data")
        source_tree = git(scratch, "rev-parse", "HEAD^{tree}")
        if source_tree != "683d44befe0d3519469011c35e46f332eebbc010":
            raise ValueError("Original Requests tree changed")
        repo, base_commit = "psf/requests", "1b40fdd004bfc8ba5301bcf8a6908264e9b6b877"
        if pair != "R00":
            item = manifest["retained_agent_patches"][int(pair[-1]) - 1]
            agent_patch = json.loads((root / item["path"]).read_text())["agent_patch"]
        nodes = [
            "test_origin_binding",
            "test_empty_machine",
            "test_empty_default",
            "test_missing",
            "test_valid",
        ]
    else:
        package, module, function = (
            "cpu_import_product",
            "cpu_import_product",
            "evaluate",
        )
        product = "src/cpu_import_product/__init__.py"
        (scratch / product).parent.mkdir(parents=True)
        (scratch / product).write_text(FAULTY)
        git(scratch, "init", "-q")
        git(scratch, "add", ".")
        git(
            scratch,
            "-c",
            "user.name=CPU Fixture",
            "-c",
            "user.email=cpu@invalid",
            "commit",
            "-qm",
            "Owned src package",
        )
        base_commit = git(scratch, "rev-parse", "HEAD")
        source_tree = git(scratch, "rev-parse", "HEAD^{tree}")
        repo = "mostaza/owned_src_layout"
        snapshot = case_dir / "fixture.tgz"
        with tarfile.open(snapshot, "w:gz") as archive:
            archive.add(scratch, arcname=".")
        if case in ("L02", "L03"):
            value = 1 if case == "L02" else 2
            agent_patch = legacy.patch(
                FAULTY, f"def evaluate():\n    return {value}\n", product
            )
        nodes = ["test_required"]
    validate_archive(snapshot)
    check_layout(scratch, package)
    delta = layout_patch(package)
    validate_delta(delta, package)
    delta_path = case_dir / "layout.patch"
    delta_path.write_text(delta)
    use_layout = not case.endswith("-U")
    layout = None
    if use_layout:
        subprocess.run(
            ["git", "-C", str(scratch), "apply", str(delta_path)],
            capture_output=True,
            check=True,
            timeout=30,
        )
        git(scratch, "add", "--", package)
        if git(scratch, "diff", "--cached", "--name-only") != package:
            raise ValueError("Layout delta touched extra paths")
        if git(scratch, "ls-files", "--stage", "--", package).split()[0] != "120000":
            raise ValueError("Layout alias is not a Git symlink")
        layout = {
            "alias": package,
            "target": "src/" + package,
            "mode": "120000",
            "patch_sha256": digest(delta_path),
            "source_tree": source_tree,
            "derived_prebootstrap_tree": git(scratch, "write-tree"),
        }
    if agent_patch:
        subprocess.run(
            ["git", "-C", str(scratch), "apply", "-"],
            input=agent_patch,
            text=True,
            capture_output=True,
            check=True,
            timeout=30,
        )
    source = (scratch / product).read_text()
    expected = {
        "pair": pair,
        "package": package,
        "module": module,
        "function": function,
        "relative_file": product,
        "allowed_product_paths": [product, product.removeprefix("src/")],
        "file_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "parent_sha256": digest(scratch / "src" / package / "__init__.py"),
        "function_fingerprint": expected_function(source, function),
        "nodes": nodes,
        "python": platform.python_version(),
        "pytest": importlib.metadata.version("pytest"),
    }
    test_patch = legacy.patch("", test_source(expected, receipt), TEST_FILE)
    (case_dir / "test.patch").write_text(test_patch)
    native = importlib.import_module("swegemma.harness.verification")
    native_sha = digest(Path(str(native.__file__)))
    manager = importlib.import_module("swegemma.sandbox.subprocess").SubprocessManager(
        timeout_seconds=30, base_dir=case_dir / "sandboxes"
    )
    empty = case_dir / "empty-wheels"
    empty.mkdir()
    config = importlib.import_module("swegemma.config").EvalConfig(
        tasks_path=case_dir / "owned-tasks.json",
        snapshots_dir=case_dir,
        results_dir=case_dir / "native",
        submission_dir=case_dir,
        models=importlib.import_module("adk_submission").ModelRegistry(),
        sandbox="subprocess",
        wheels_dir=empty,
        timeout_seconds=30,
        verification_timeout_seconds=30,
        concurrency=1,
    )
    task = importlib.import_module("swegemma.models.task").Task(
        instance_id="import_cpu_" + case,
        repo=repo,
        base_commit=base_commit,
        problem_statement="Owned CPU layout diagnostic",
        patch="",
        test_patch=test_patch,
        FAIL_TO_PASS=tuple(TEST_FILE + "::" + n for n in nodes),
    )
    started = time.perf_counter()
    (case_dir / "native-started.json").write_text(
        json.dumps(
            {
                "id": case,
                "task_id": task.instance_id,
                "native_verifier_sha256": native_sha,
                "boundary": "Immediately before direct verify_task dispatch",
            }
        )
        + "\n"
    )
    result = asyncio.run(
        native.verify_task(
            manager,
            config,
            task,
            snapshot,
            patch_path=delta_path if use_layout else None,
            fast_path=True,
            agent_patch=agent_patch,
            start_time=started,
        )
    )
    events = json.loads(receipt.read_text()) if receipt.exists() else []
    if receipt.exists():
        receipt.replace(case_dir / "events.json")
    row = {
        "id": case,
        "expected": expected,
        "events": events,
        "native_result": result.model_dump(mode="json"),
        "manager_class": type(manager).__name__,
        "mock_bypass": repo.startswith("test/mock_repo") and base_commit == "123456",
        "cleanup_complete": not manager.sandboxes
        and not list((case_dir / "sandboxes").glob("swegemma_sandbox_*")),
        "native_verifier_changed": digest(Path(str(native.__file__))) != native_sha,
        "agent_patch_sha256": hashlib.sha256(agent_patch.encode()).hexdigest(),
        "test_patch_sha256": hashlib.sha256(test_patch.encode()).hexdigest(),
        "layout": layout,
        "conditions": {
            "snapshot_sha256": digest(snapshot),
            "verifier_sha256": native_sha,
            "native_versions": manifest["native_environment_versions"],
            "timeout_seconds": 30,
            "verification_timeout_seconds": 30,
            "concurrency": 1,
            "backend": "subprocess",
        },
        "duration_seconds": time.perf_counter() - started,
        "raw_junit": None,
        "raw_junit_reason": "Native JUnit consumed internally and removed at cleanup",
    }
    (case_dir / "result.json").write_text(
        json.dumps(row, indent=2, sort_keys=True) + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run_case(Path(__file__).resolve().parents[1], args.output.resolve(), args.case)


if __name__ == "__main__":
    main()
