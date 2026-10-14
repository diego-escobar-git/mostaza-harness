"""CPU-only source-layout inputs and independently validated import witnesses."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import subprocess
from pathlib import Path
from typing import Any

from mostaza.evaluation.verify_task_cpu import digest, validate_pins

EVIDENCE = "docs/implementation/evidence/mostaza-requests-import-cpu"
CASES = ("L01", "L02", "L03") + tuple(
    f"R0{i}-{stage}" for i in range(3) for stage in ("U", "B")
)
COVERAGE = "actual_pytest_owned_import_layout_cpu"


def layout_patch(package: str) -> str:
    if package not in ("requests", "cpu_import_product"):
        raise ValueError("Unsupported CPU package alias")
    return (
        f"diff --git a/{package} b/{package}\nnew file mode 120000\n"
        f"--- /dev/null\n+++ b/{package}\n@@ -0,0 +1 @@\n"
        f"+src/{package}\n\\ No newline at end of file\n"
    )


def validate_delta(text: str, package: str) -> None:
    if text != layout_patch(package):
        raise ValueError("Layout delta is not the exact allowlisted symlink")


def git(path: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(path), *args],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    ).stdout.strip()


def check_layout(root: Path, package: str) -> None:
    layout_patch(package)
    alias = root / package
    target = root / "src" / package
    if alias.exists() or alias.is_symlink():
        raise ValueError("Root alias already exists")
    if (root / "src").is_symlink() or target.is_symlink():
        raise ValueError("Target is not a direct in-workspace package")
    if not target.is_dir() or not (target / "__init__.py").is_file():
        raise ValueError("Source package missing")
    if not target.resolve().is_relative_to(root.resolve()) or not (
        target / "__init__.py"
    ).resolve().is_relative_to(target.resolve()):
        raise ValueError("Source package escapes workspace")
    if git(root, "ls-files", "--", package):
        raise ValueError("Root alias is already tracked")
    result = subprocess.run(
        ["git", "-C", str(root), "check-ignore", "-q", "--", package],
        capture_output=True,
        timeout=30,
    )
    if result.returncode != 1:
        raise ValueError("Root alias is ignored or ignore check failed")


def immutable_inputs(root: Path) -> dict[str, Any]:
    manifest: dict[str, Any] = json.loads(
        (root / EVIDENCE / "prerequisites.json").read_text()
    )
    validate_pins(
        root,
        {
            "files": manifest["external_pins"],
            "retained_agent_patches": manifest["retained_agent_patches"],
        },
    )
    for item in manifest["frozen_vcpu01_files"]:
        if digest(root / item["path"]) != item["sha256"]:
            raise ValueError("Frozen V-CPU-01 file changed: " + item["path"])
    prefix = manifest["runbook_prefix"]
    if (
        hashlib.sha256(
            (root / prefix["path"]).read_bytes()[: prefix["bytes"]]
        ).hexdigest()
        != prefix["sha256"]
    ):
        raise ValueError("Historical runbook prefix changed")
    approval = json.loads((root / EVIDENCE / "approval.json").read_text())
    if approval["plan_sha256"] != digest(root / EVIDENCE / "plan-for-approval.md"):
        raise ValueError("Approved plan changed")
    return manifest


def runtime_versions(manifest: dict[str, Any]) -> None:
    for name, version in manifest["native_environment_versions"].items():
        if importlib.metadata.version(name) != version:
            raise ValueError("Native environment changed: " + name)


def bound(event: dict[str, Any], expected: dict[str, Any], case_dir: Path) -> bool:
    if event.get("coverage") != COVERAGE or event.get("pair") != expected["pair"]:
        raise ValueError("Wrong witness coverage/pair")
    for key in ("pid", "ppid"):
        if type(event.get(key)) is not int or event[key] <= 0:
            raise ValueError("Missing process identity")
    for key in ("cwd", "executable", "python", "pytest"):
        if not isinstance(event.get(key), str) or not event[key]:
            raise ValueError("Missing runtime witness")
    cwd = Path(event["cwd"])
    if (
        cwd != cwd.resolve()
        or not cwd.is_relative_to(case_dir)
        or cwd.name != "workspace"
    ):
        raise ValueError("Witness outside owned native workspace")
    exe = Path(event["executable"])
    if exe.parent != cwd.parent / "venv/bin" or not exe.name.startswith("python"):
        raise ValueError("Wrong interpreter location")
    if any(event[key] != expected[key] for key in ("python", "pytest")):
        raise ValueError("Wrong Python/pytest")
    paths = event.get("sys_path")
    if (
        not isinstance(paths, list)
        or not paths
        or not all(isinstance(p, str) and p for p in paths)
    ):
        raise ValueError("Missing ordered sys.path")
    package = expected["package"]
    alias = event.get("alias_target")
    if alias not in (None, "src/" + package):
        raise ValueError("Unapproved alias target")
    package_raw = {
        str(cwd / package / "__init__.py"),
        str(cwd / "src" / package / "__init__.py"),
    }
    product_raw = {str(cwd / p) for p in expected["allowed_product_paths"]}
    return bool(
        event["parent_raw"] in package_raw
        and event["parent_canonical"] == str(cwd / "src" / package / "__init__.py")
        and event["parent_sha256"] == expected["parent_sha256"]
        and event["module_raw"] in product_raw
        and event["module_canonical"] == str(cwd / expected["relative_file"])
        and event["module_sha256"] == expected["file_sha256"]
        and event["function_raw"] in product_raw
        and event["function_canonical"] == str(cwd / expected["relative_file"])
        and event["function_module"] == expected["module"]
        and event["function_fingerprint"] == expected["function_fingerprint"]
        and event["fingerprint_algorithm"] == "cpu-code-json-v1"
        and alias == "src/" + package
    )


def assess(row: dict[str, Any], case_dir: Path) -> dict[str, Any]:
    expected, events, result = row["expected"], row["events"], row["native_result"]
    case = row["id"]
    if result["task_id"] != "import_cpu_" + case:
        raise ValueError("Stage does not match native result")
    if (
        not row["cleanup_complete"]
        or row["manager_class"] != "SubprocessManager"
        or row["mock_bypass"]
        or row["native_verifier_changed"]
    ):
        raise ValueError("Native integrity/cleanup failure")
    if result["test_exit_code"] in (-1, 4, 5, 124):
        raise ValueError("Setup/collection/timeout failure")
    if len(events) != len(expected["nodes"]) or {e["node"] for e in events} != set(
        expected["nodes"]
    ):
        raise ValueError("Missing/duplicate required node observations")
    if len({e["pid"] for e in events}) != 1:
        raise ValueError("Mixed pytest processes")
    if any(
        e["outcome"] not in ("passed", "assertion_failed", "exception") for e in events
    ):
        raise ValueError("Incomplete test-body outcome")
    bindings = [bound(e, expected, case_dir) for e in events]
    binding = all(bindings)
    if len(set(bindings)) != 1:
        raise ValueError("Binding changed during owned tests")
    wanted = not case.endswith("-U")
    if binding is not wanted:
        raise ValueError("Layout remedy/control failed")
    if wanted and any(
        e["alias_target"] != "src/" + expected["package"] for e in events
    ):
        raise ValueError("Missing native-applied layout alias")
    if not wanted and any(e["alias_target"] is not None for e in events):
        raise ValueError("Unbound control unexpectedly has an alias")
    if case.startswith("L"):
        positive = case == "L02"
        if result["resolved"] is not positive or events[0]["outcome"] != (
            "passed" if positive else "assertion_failed"
        ):
            raise ValueError("Generic patch sensitivity control failed")
    else:
        origin = next(e for e in events if e["node"] == "test_origin_binding")
        if (origin["outcome"] == "passed") != wanted:
            raise ValueError("Origin assertion contradicts validated witness")
    all_passed = all(e["outcome"] == "passed" for e in events)
    if (
        result["resolved"] != all_passed
        or (result["test_exit_code"] == 0) != all_passed
    ):
        raise ValueError("Native and owned-test outcomes disagree")
    return {
        "id": case,
        "binding": binding,
        "native_resolved": result["resolved"],
        "test_exit_code": result["test_exit_code"],
        "error_message": result["error_message"],
        "node_outcomes": {e["node"]: e["outcome"] for e in events},
        "witness": events[0],
        "test_patch_sha256": row["test_patch_sha256"],
        "agent_patch_sha256": row["agent_patch_sha256"],
        "layout": row["layout"],
        "duration_seconds": row["duration_seconds"],
    }


def validate_pairs(rows: list[dict[str, Any]]) -> None:
    if [r["id"] for r in rows] != list(CASES):
        raise ValueError("Matrix incomplete or repeated")
    for index in range(3):
        unbound, bound_row = rows[3 + 2 * index : 5 + 2 * index]
        for key in (
            "test_patch_sha256",
            "agent_patch_sha256",
            "expected",
            "conditions",
        ):
            if unbound[key] != bound_row[key]:
                raise ValueError("Pair differs outside layout input: " + key)
        if unbound["events"][0]["pid"] == bound_row["events"][0]["pid"]:
            raise ValueError("Stale process receipt reused across stages")
