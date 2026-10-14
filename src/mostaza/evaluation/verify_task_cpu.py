"""Validation for owned CPU diagnostics; never a substitute for the native verifier."""

from __future__ import annotations

import hashlib
import json
import posixpath
import tarfile
import types
from pathlib import Path
from typing import Any

COVERAGE = "actual_pytest_owned_diagnostic_test_cpu"
LIMIT_BYTES = 1024**3
CASES = tuple(f"V0{i}" for i in range(1, 9)) + ("R00", "R01", "R02")

# Embedded verbatim in our test_patch, never installed as a pytest plugin.
FINGERPRINT_SOURCE = """def code_fingerprint(code):
    def constant(value):
        if isinstance(value, type(code)):
            return payload(value)
        if isinstance(value, tuple):
            return [constant(item) for item in value]
        return repr(value)
    def payload(value):
        return {"bytecode": value.co_code.hex(),
                "constants": [constant(item) for item in value.co_consts],
                "names": value.co_names, "varnames": value.co_varnames,
                "argcount": value.co_argcount, "posonly": value.co_posonlyargcount,
                "kwonly": value.co_kwonlyargcount, "flags": value.co_flags,
                "firstlineno": value.co_firstlineno,
                "freevars": value.co_freevars, "cellvars": value.co_cellvars}
    data = json.dumps(payload(code), sort_keys=True).encode()
    return hashlib.sha256(data).hexdigest()
"""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_function(source: str, name: str) -> str:
    namespace: dict[str, Any] = {"hashlib": hashlib, "json": json}
    exec(FINGERPRINT_SOURCE, namespace)
    module = compile(source, "<cpu-product>", "exec", dont_inherit=True)
    matches = [
        c
        for c in module.co_consts
        if isinstance(c, types.CodeType) and c.co_name == name
    ]
    if len(matches) != 1:
        raise ValueError("Expected exactly one top-level product function")
    return str(namespace["code_fingerprint"](matches[0]))


def validate_archive(path: Path) -> None:
    """Check the unchanged native input before native extraction, including links."""
    with tarfile.open(path) as archive:
        members = archive.getmembers()
        if len(members) > 10000 or sum(m.size for m in members) > 128 * 1024**2:
            raise ValueError("Archive exceeds CPU input bound")
        for member in members:
            name = member.name
            normalized = posixpath.normpath(name)
            if (
                name.startswith("/")
                or normalized == ".."
                or normalized.startswith("../")
            ):
                raise ValueError("Archive path escapes owned root")
            if not (
                member.isfile() or member.isdir() or member.issym() or member.islnk()
            ):
                raise ValueError("Unsupported archive member type")
            if member.issym() or member.islnk():
                target = member.linkname
                base = posixpath.dirname(normalized) if member.issym() else ""
                resolved = posixpath.normpath(posixpath.join(base, target))
                if (
                    target.startswith("/")
                    or resolved == ".."
                    or resolved.startswith("../")
                ):
                    raise ValueError("Archive link escapes owned root")
                # Reject traversal via a link used as a parent by another member.
                if any(
                    posixpath.normpath(m.name).startswith(normalized + "/")
                    for m in members
                ):
                    raise ValueError("Archive member descends through a link")


def validate_pins(root: Path, manifest: dict[str, Any]) -> None:
    for item in manifest["files"]:
        path = root / item["path"]
        if not path.is_file() or digest(path) != item["sha256"]:
            raise ValueError(f"Missing/changed immutable input: {item['path']}")
    for item in manifest["retained_agent_patches"]:
        path = root / item["path"]
        if digest(path) != item["result_sha256"]:
            raise ValueError("Historical result changed")
        patch = json.loads(path.read_text())["agent_patch"].encode()
        if hashlib.sha256(patch).hexdigest() != item["agent_patch_sha256"]:
            raise ValueError("Historical agent patch changed")


def binding(receipt: dict[str, Any], expected: dict[str, Any], case_root: Path) -> bool:
    if receipt.get("coverage") != COVERAGE or receipt.get("case_id") != expected["id"]:
        raise ValueError("Wrong witness scope/coverage")
    if type(receipt.get("pid")) is not int or receipt["pid"] <= 0:
        raise ValueError("Missing actual test-process PID")
    if type(receipt.get("ppid")) is not int or receipt["ppid"] <= 0:
        raise ValueError("Missing pytest parent PID")
    for key in ("cwd", "executable", "python", "pytest"):
        if not isinstance(receipt.get(key), str) or not receipt[key]:
            raise ValueError(f"Missing process witness: {key}")
    paths = receipt.get("sys_path")
    if (
        not isinstance(paths, list)
        or not paths
        or not all(isinstance(path, str) and bool(path) for path in paths)
    ):
        raise ValueError("Missing ordered import-path witness")
    if (
        receipt["python"] != expected["python"]
        or receipt["pytest"] != expected["pytest"]
    ):
        raise ValueError("Wrong diagnostic interpreter/pytest version")
    cwd = Path(receipt["cwd"])
    if not cwd.is_absolute() or cwd != cwd.resolve():
        raise ValueError("Noncanonical workspace witness")
    executable = Path(receipt["executable"])
    if executable.parent != cwd.parent / "venv/bin" or not executable.name.startswith(
        "python"
    ):
        raise ValueError("Interpreter is outside native sandbox venv")
    if not cwd.is_relative_to(case_root) or cwd.name != "workspace":
        raise ValueError("Witness outside owned sandbox")
    target = cwd / expected["relative_file"]
    return bool(
        receipt["module_path"] == str(target)
        and receipt["module_sha256"] == expected["file_sha256"]
        and receipt["function_filename"] == str(target)
        and receipt["function_module"] == expected["module"]
        and receipt["function_fingerprint"] == expected["function_fingerprint"]
        and receipt["fingerprint_algorithm"] == "cpu-code-json-v1"
    )


def assess(
    row: dict[str, Any], expected: dict[str, Any], case_root: Path
) -> dict[str, Any]:
    case = expected["id"]
    result = row["native_result"]
    events = row["events"]
    if row["manager_class"] != "SubprocessManager" or not row["cleanup_complete"]:
        raise ValueError("Wrong backend or incomplete cleanup")
    if row["mock_bypass"] or row["native_verifier_changed"]:
        raise ValueError("Native-path integrity failure")
    if result["test_exit_code"] == -1:
        raise ValueError("Native setup/patch failure is not a valid control")
    matches = None
    if case not in ("V05", "V06"):
        if not events:
            raise ValueError("Missing actual pytest witness")
        bindings = [binding(e, expected, case_root) for e in events]
        if len({e["pid"] for e in events}) != 1:
            raise ValueError("Mixed pytest processes")
        matches = all(bindings)
    if case.startswith("R"):
        if len(events) != len(expected["nodes"]) or {e["node"] for e in events} != set(
            expected["nodes"]
        ):
            raise ValueError("Requests did not reach all five required nodes")
        if any(
            e["outcome"] not in ("passed", "assertion_failed", "exception")
            for e in events
        ):
            raise ValueError("Incomplete Requests observation")
        origin = next(e for e in events if e["node"] == "test_origin_binding")
        if (origin["outcome"] == "passed") != matches:
            raise ValueError("Forged/inconsistent binding assertion")
        if result["resolved"] and (
            not matches or any(e["outcome"] != "passed" for e in events)
        ):
            raise ValueError("False Requests success")
    else:
        positive = case == "V02"
        if result["resolved"] is not positive:
            raise ValueError(f"Unexpected native control result: {case}")
        if case in ("V01", "V02", "V03", "V08"):
            outcome = "passed" if positive else "assertion_failed"
            if (
                matches is not True
                or len(events) != 1
                or events[0]["outcome"] != outcome
            ):
                raise ValueError("Control failed for an unrelated cause")
        if case == "V04" and (
            matches is not False or events[0]["outcome"] != "assertion_failed"
        ):
            raise ValueError("Shadow control did not reject competing module")
        if case == "V05" and (
            result["test_exit_code"] != 0 or "skipped" not in result["test_output"]
        ):
            raise ValueError("Skip control missing intended evidence")
        if case == "V06" and (
            result["test_exit_code"] != 5 or "no tests ran" not in result["test_output"]
        ):
            raise ValueError("No-collection control missing intended evidence")
        if case == "V07" and (
            result["test_exit_code"] != 0
            or "JUnit" not in (result["error_message"] or "")
            or events[0]["outcome"] != "premature_exit"
        ):
            raise ValueError("Missing-JUnit control not demonstrated")
    return {
        "id": case,
        "workspace_binding": matches,
        "native_resolved": result["resolved"],
        "test_exit_code": result["test_exit_code"],
        "node_outcomes": {e["node"]: e["outcome"] for e in events},
        "coverage": COVERAGE if events else None,
        "coverage_reason": None if events else "Intentional skip/no-collection control",
        "native_error_message": result.get("error_message"),
        "native_duration_seconds": row.get("duration_seconds"),
        "process_witnesses": [
            {
                key: event[key]
                for key in (
                    "pid",
                    "ppid",
                    "executable",
                    "python",
                    "pytest",
                    "cwd",
                    "sys_path",
                    "module_path",
                    "module_sha256",
                    "function_filename",
                    "function_module",
                    "function_fingerprint",
                    "fingerprint_algorithm",
                )
            }
            for event in events[:1]
        ],
    }
