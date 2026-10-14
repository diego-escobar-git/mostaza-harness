"""Import-layout validators reject unsafe deltas and misleading witnesses."""

from copy import deepcopy
from pathlib import Path

import pytest

from mostaza.evaluation.requests_import_cpu import (
    CASES,
    assess,
    bound,
    check_layout,
    git,
    layout_patch,
    validate_delta,
    validate_pairs,
)


def witness(tmp_path):
    cwd = tmp_path / "sandboxes/swegemma_sandbox_owned/workspace"
    expected = {
        "pair": "R02",
        "package": "requests",
        "module": "requests.utils",
        "function": "get_netrc_auth",
        "relative_file": "src/requests/utils.py",
        "allowed_product_paths": ["src/requests/utils.py", "requests/utils.py"],
        "parent_sha256": "parent",
        "file_sha256": "file",
        "function_fingerprint": "code",
        "nodes": ["test_origin_binding"],
        "python": "3.13.15",
        "pytest": "9.1.1",
    }
    event = {
        "coverage": "actual_pytest_owned_import_layout_cpu",
        "pair": "R02",
        "node": "test_origin_binding",
        "pid": 100,
        "ppid": 99,
        "cwd": str(cwd),
        "executable": str(cwd.parent / "venv/bin/python3"),
        "python": "3.13.15",
        "pytest": "9.1.1",
        "sys_path": [str(cwd)],
        "alias_target": "src/requests",
        "parent_raw": str(cwd / "requests/__init__.py"),
        "parent_canonical": str(cwd / "src/requests/__init__.py"),
        "parent_sha256": "parent",
        "module_raw": str(cwd / "requests/utils.py"),
        "module_canonical": str(cwd / "src/requests/utils.py"),
        "module_sha256": "file",
        "function_raw": str(cwd / "requests/utils.py"),
        "function_canonical": str(cwd / "src/requests/utils.py"),
        "function_module": "requests.utils",
        "function_fingerprint": "code",
        "fingerprint_algorithm": "cpu-code-json-v1",
        "outcome": "passed",
    }
    return event, expected


def test_declared_alias_can_bind_without_equal_raw_spelling(tmp_path):
    event, expected = witness(tmp_path)
    assert event["function_raw"] != event["function_canonical"]
    assert bound(event, expected, tmp_path)


@pytest.mark.parametrize(
    "field,value",
    [
        ("module_raw", "/installed/utils.py"),
        ("function_raw", "/installed/utils.py"),
        ("function_fingerprint", "wrong_loaded_code"),
        ("parent_sha256", "wrong_parent"),
        ("module_canonical", "/outside/utils.py"),
    ],
)
def test_matching_resolved_claim_alone_does_not_prove_binding(tmp_path, field, value):
    event, expected = witness(tmp_path)
    event[field] = value
    assert not bound(event, expected, tmp_path)


@pytest.mark.parametrize(
    "field,value",
    [
        ("pid", None),
        ("ppid", 0),
        ("sys_path", []),
        ("python", "3.12"),
        ("alias_target", "../../outside"),
    ],
)
def test_invalid_runtime_or_alias_rejected(tmp_path, field, value):
    event, expected = witness(tmp_path)
    event[field] = value
    with pytest.raises(ValueError):
        bound(event, expected, tmp_path)


def own_repo(path):
    target = path / "src/cpu_import_product/__init__.py"
    target.parent.mkdir(parents=True)
    target.write_text("VALUE = 1\n")
    git(path, "init", "-q")
    git(path, "add", ".")
    git(
        path,
        "-c",
        "user.name=CPU Test",
        "-c",
        "user.email=cpu@invalid",
        "commit",
        "-qm",
        "owned",
    )
    return target


def test_git_accepts_only_new_local_link_without_product_change(tmp_path):
    import subprocess

    target = own_repo(tmp_path)
    original = target.read_bytes()
    check_layout(tmp_path, "cpu_import_product")
    delta = layout_patch("cpu_import_product")
    validate_delta(delta, "cpu_import_product")
    subprocess.run(
        ["git", "-C", str(tmp_path), "apply", "-"],
        input=delta,
        text=True,
        check=True,
        capture_output=True,
    )
    assert (tmp_path / "cpu_import_product").readlink() == Path(
        "src/cpu_import_product"
    )
    assert target.read_bytes() == original
    with pytest.raises(ValueError, match="already exists"):
        check_layout(tmp_path, "cpu_import_product")


@pytest.mark.parametrize(
    "replace",
    [
        lambda p: p.replace("120000", "100644"),
        lambda p: p.replace("src/requests", "../outside"),
        lambda p: p + "extra path\n",
    ],
)
def test_delta_cannot_smuggle_other_changes(replace):
    with pytest.raises(ValueError):
        validate_delta(replace(layout_patch("requests")), "requests")


def test_ignored_alias_is_not_silently_added(tmp_path):
    own_repo(tmp_path)
    (tmp_path / ".gitignore").write_text("cpu_import_product\n")
    with pytest.raises(ValueError, match="ignored"):
        check_layout(tmp_path, "cpu_import_product")


def test_requests_duplicate_witness_not_credited(tmp_path):
    event, expected = witness(tmp_path)
    row = {
        "id": "R02-B",
        "expected": expected,
        "events": [event, event],
        "native_result": {"task_id": "import_cpu_R02-B", "test_exit_code": 0},
        "cleanup_complete": True,
        "manager_class": "SubprocessManager",
        "mock_bypass": False,
        "native_verifier_changed": False,
    }
    with pytest.raises(ValueError, match="duplicate"):
        assess(row, tmp_path)


@pytest.mark.parametrize(
    "change",
    ["test_patch_sha256", "agent_patch_sha256", "conditions", "expected", "pid"],
)
def test_pairs_reject_nonlayout_change_or_stale_process(change):
    rows = [
        {
            "id": case,
            "test_patch_sha256": "tests",
            "agent_patch_sha256": "patch",
            "expected": {},
            "conditions": {},
            "events": [{"pid": i + 1}],
        }
        for i, case in enumerate(CASES)
    ]
    validate_pairs(rows)
    bad = deepcopy(rows)
    if change == "pid":
        bad[4]["events"][0]["pid"] = bad[3]["events"][0]["pid"]
    else:
        bad[4][change] = "different"
    with pytest.raises(ValueError):
        validate_pairs(bad)
