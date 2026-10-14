"""Owned fixture construction and direct native verify_task invocation, CPU only."""

from __future__ import annotations

import argparse
import asyncio
import difflib
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
from mostaza.evaluation.verify_task_cpu import (
    COVERAGE,
    FINGERPRINT_SOURCE,
    digest,
    expected_function,
    validate_archive,
)

TEST_FILE = "test_mostaza_cpu_diagnostic.py"
FAULTY = "def evaluate():\n    return 0\n"
CORRECT = "def evaluate():\n    return 1\n"


def patch(old: str, new: str, path: str) -> str:
    return "".join(
        difflib.unified_diff(
            old.splitlines(True),
            new.splitlines(True),
            fromfile="a/" + path if old else "/dev/null",
            tofile="b/" + path,
        )
    )


def diagnostic_source(case: str, output: Path, expected: dict[str, Any]) -> str:
    header = f"""import os, sys, json, hashlib, importlib, platform
from pathlib import Path
import pytest
CASE = {case!r}
OUTPUT = Path({str(output)!r})
EXPECTED = {expected!r}
{FINGERPRINT_SOURCE}
def observe(node, action):
    module = importlib.import_module(EXPECTED["module"])
    function = getattr(module, EXPECTED["function"])
    file = Path(module.__file__).resolve()
    target = Path.cwd() / EXPECTED["relative_file"]
    record = {{"coverage": {COVERAGE!r}, "case_id": CASE, "node": node,
              "pid": os.getpid(), "ppid": os.getppid(), "executable": sys.executable,
              "python": platform.python_version(), "pytest": pytest.__version__,
              "cwd": str(Path.cwd()), "sys_path": list(sys.path),
              "module_path": str(file),
              "module_sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
              "function_filename": function.__code__.co_filename,
              "function_module": function.__module__,
              "function_fingerprint": code_fingerprint(function.__code__),
              "fingerprint_algorithm": "cpu-code-json-v1"}}
    matches = (str(file) == str(target)
               and record["module_sha256"] == EXPECTED["file_sha256"]
               and record["function_filename"] == str(target)
               and record["function_module"] == EXPECTED["module"]
               and record["function_fingerprint"] == EXPECTED["function_fingerprint"])
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
        temporary = OUTPUT.with_suffix(".tmp")
        records = json.loads(OUTPUT.read_text()) if OUTPUT.exists() else []
        records.append(record)
        temporary.write_text(json.dumps(records, sort_keys=True))
        temporary.replace(OUTPUT)
"""
    if case == "V05":
        return (
            header
            + '\n@pytest.mark.skip(reason="owned required skip control")\n'
            + "def test_required():\n    assert False\n"
        )
    if case == "V06":
        return header  # Actual pytest collection, no test function.
    if case == "V07":
        return (
            header
            + """
def test_required():
    observe("test_required", lambda function, matches: None)
    records = json.loads(OUTPUT.read_text())
    records[-1]["outcome"] = "premature_exit"
    temporary = OUTPUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(records))
    temporary.replace(OUTPUT)
    os._exit(0)
"""
        )
    if case.startswith("V"):
        return (
            header
            + """
def test_required():
    def check(function, matches):
        assert matches, "intended workspace product not imported"
        assert function() == 1
    observe("test_required", check)
"""
        )
    cases = {
        "test_empty_machine": ("machine diag.invalid\n", None),
        "test_empty_default": (
            "machine other.invalid login user password pass\ndefault\n",
            None,
        ),
        "test_missing": ("machine other.invalid login user password pass\n", None),
        "test_valid": (
            "machine diag.invalid login user password pass\n",
            ("user", "pass"),
        ),
    }
    body = """
def test_origin_binding():
    def check(function, matches):
        assert matches, "intended Requests workspace product not imported"
    observe("test_origin_binding", check)
"""
    for name, (contents, value) in cases.items():
        body += f"""
def {name}(tmp_path):
    netrc = tmp_path / "owned_netrc"
    netrc.write_text({contents!r})
    previous = os.environ.get("NETRC")
    os.environ["NETRC"] = str(netrc)
    try:
        def check(function, matches):
            assert function("https://diag.invalid/") == {value!r}
        observe({name!r}, check)
    finally:
        if previous is None:
            os.environ.pop("NETRC", None)
        else:
            os.environ["NETRC"] = previous
"""
    return header + body


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.strip()


def run_case(root: Path, case_dir: Path, case: str) -> dict[str, Any]:
    case_dir.mkdir(parents=True, exist_ok=True)
    fixture = case_dir / "fixture"
    fixture.mkdir()
    agent_patch = ""
    product = "diag_product.py"
    module, function = "diag_product", "evaluate"
    source = FAULTY
    manifest = json.loads(
        (
            root
            / "docs/implementation/evidence/mostaza-verify-task-cpu/prerequisites.json"
        ).read_text()
    )
    if case.startswith("R"):
        snapshot = root / "resources/official/snapshots/requests_7205.tgz"
        validate_archive(snapshot)
        # Owned scratch copy only for tree identity and expected fingerprints.
        with tarfile.open(snapshot) as archive:
            archive.extractall(fixture, filter="data")
        if (
            git(fixture, "rev-parse", "HEAD^{tree}")
            != "683d44befe0d3519469011c35e46f332eebbc010"
        ):
            raise ValueError("Requests base tree changed")
        base_commit = "1b40fdd004bfc8ba5301bcf8a6908264e9b6b877"
        repo = "psf/requests"
        product, module, function = (
            "src/requests/utils.py",
            "requests.utils",
            "get_netrc_auth",
        )
        if case != "R00":
            item = manifest["retained_agent_patches"][int(case[-1]) - 1]
            agent_patch = json.loads((root / item["path"]).read_text())["agent_patch"]
            subprocess.run(
                ["git", "-C", str(fixture), "apply", "-"],
                input=agent_patch,
                text=True,
                check=True,
                capture_output=True,
                timeout=30,
            )
        source = (fixture / product).read_text()
    else:
        if case == "V04":
            product = "src/diag_product.py"
            (fixture / "src").mkdir()
            (fixture / "diag_product.py").write_text(CORRECT)
        (fixture / product).write_text(FAULTY)
        git(fixture, "init", "-q")
        git(fixture, "add", ".")
        git(
            fixture,
            "-c",
            "user.name=CPU Fixture",
            "-c",
            "user.email=cpu@invalid",
            "commit",
            "-qm",
            "Owned CPU baseline",
        )
        base_commit = git(fixture, "rev-parse", "HEAD")
        repo = "mostaza/owned_cpu_fixture"
        snapshot = case_dir / "fixture.tgz"
        with tarfile.open(snapshot, "w:gz") as archive:
            archive.add(fixture, arcname=".")
        if case in ("V02", "V04"):
            source = CORRECT
            agent_patch = patch(FAULTY, source, product)
        elif case == "V03":
            source = "def evaluate():\n    return 2\n"
            agent_patch = patch(FAULTY, source, product)
        elif case == "V08":
            agent_patch = patch(
                "", "def test_required():\n    assert True\n", TEST_FILE
            )
    validate_archive(snapshot)
    nodes = (
        ["test_required"]
        if case.startswith("V")
        else [
            "test_origin_binding",
            "test_empty_machine",
            "test_empty_default",
            "test_missing",
            "test_valid",
        ]
    )
    expected = {
        "id": case,
        "python": platform.python_version(),
        "pytest": importlib.metadata.version("pytest"),
        "module": module,
        "function": function,
        "relative_file": product,
        "file_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "function_fingerprint": expected_function(source, function),
        "nodes": nodes,
    }
    test_source = diagnostic_source(case, case_dir / "events.json", expected)
    (case_dir / "diagnostic-test.py").write_text(test_source)
    (case_dir / "expected.json").write_text(json.dumps(expected, indent=2) + "\n")
    manager_type = importlib.import_module(
        "swegemma.sandbox.subprocess"
    ).SubprocessManager
    manager = manager_type(timeout_seconds=30, base_dir=case_dir / "sandboxes")
    config_type = importlib.import_module("swegemma.config").EvalConfig
    registry = importlib.import_module("adk_submission").ModelRegistry()
    empty = case_dir / "empty-wheels"
    empty.mkdir()
    config = config_type(
        tasks_path=case_dir / "owned-tasks.json",
        snapshots_dir=case_dir,
        results_dir=case_dir / "native",
        submission_dir=case_dir,
        models=registry,
        sandbox="subprocess",
        wheels_dir=empty,
        timeout_seconds=30,
        verification_timeout_seconds=30,
        concurrency=1,
    )
    task = importlib.import_module("swegemma.models.task").Task(
        instance_id="cpu_" + case,
        repo=repo,
        base_commit=base_commit,
        problem_statement="Owned CPU verification diagnostic, not an agent input",
        patch="",
        test_patch=patch("", test_source, TEST_FILE),
        FAIL_TO_PASS=tuple(TEST_FILE + "::" + node for node in nodes),
    )
    verifier = importlib.import_module("swegemma.harness.verification")
    native_sha = digest(Path(str(verifier.__file__)))
    started = time.perf_counter()
    result = asyncio.run(
        verifier.verify_task(
            manager,
            config,
            task,
            snapshot,
            fast_path=True,
            agent_patch=agent_patch,
            start_time=started,
        )
    )
    leftovers = list((case_dir / "sandboxes").glob("swegemma_sandbox_*"))
    events_path = case_dir / "events.json"
    row = {
        "id": case,
        "native_result": result.model_dump(mode="json"),
        "events": json.loads(events_path.read_text()) if events_path.exists() else [],
        "manager_class": type(manager).__name__,
        "mock_bypass": repo.startswith("test/mock_repo") and base_commit == "123456",
        "native_verifier_changed": digest(Path(str(verifier.__file__))) != native_sha,
        "native_verifier_sha256": native_sha,
        "cleanup_complete": not manager.sandboxes and not leftovers,
        "duration_seconds": time.perf_counter() - started,
        "agent_patch_sha256": hashlib.sha256(agent_patch.encode()).hexdigest(),
        "test_patch_sha256": hashlib.sha256(task.test_patch.encode()).hexdigest(),
        "raw_junit": None,
        "raw_junit_reason": (
            "Native verifier consumes JUnit and removes sandbox in finally; "
            "XML is not returned"
        ),
    }
    (case_dir / "result.json").write_text(
        json.dumps(row, indent=2, sort_keys=True) + "\n"
    )
    return row


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run_case(Path(__file__).resolve().parents[1], args.output.resolve(), args.case)


if __name__ == "__main__":
    main()
