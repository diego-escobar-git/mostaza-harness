"""Adversarial contract tests for owned CPU receipts and bounded archives."""

import io
import tarfile

import pytest

from mostaza.evaluation.verify_task_cpu import (
    COVERAGE,
    assess,
    binding,
    expected_function,
    validate_archive,
)


def receipt(tmp_path):
    target = tmp_path / "swegemma_sandbox_owned/workspace/diag_product.py"
    expected = {
        "id": "V02",
        "python": "3.13.15",
        "pytest": "9.1.1",
        "module": "diag_product",
        "relative_file": "diag_product.py",
        "file_sha256": "source",
        "function_fingerprint": "code",
    }
    observed = {
        "coverage": COVERAGE,
        "case_id": "V02",
        "pid": 123,
        "ppid": 122,
        "python": "3.13.15",
        "pytest": "9.1.1",
        "executable": str(target.parent.parent / "venv/bin/python3"),
        "sys_path": [str(target.parent)],
        "cwd": str(target.parent),
        "module_path": str(target),
        "module_sha256": "source",
        "function_filename": str(target),
        "function_module": "diag_product",
        "function_fingerprint": "code",
        "fingerprint_algorithm": "cpu-code-json-v1",
    }
    return observed, expected


def test_loaded_code_must_match_even_when_file_matches(tmp_path):
    observed, expected = receipt(tmp_path)
    assert binding(observed, expected, tmp_path)
    observed["function_fingerprint"] = "different_loaded_code"
    assert not binding(observed, expected, tmp_path)


@pytest.mark.parametrize(
    "field,value",
    [("coverage", "sibling_probe"), ("pid", None), ("cwd", "/unrelated/workspace")],
)
def test_reject_wrong_scope_or_missing_process(tmp_path, field, value):
    observed, expected = receipt(tmp_path)
    observed[field] = value
    with pytest.raises(ValueError):
        binding(observed, expected, tmp_path)


def test_code_fingerprint_sensitive_to_behavior():
    assert expected_function("def f():\n    return 1\n", "f") != expected_function(
        "def f():\n    return 2\n", "f"
    )


@pytest.mark.parametrize(
    "name,target", [("../escape", None), ("/absolute", None), ("link", "../outside")]
)
def test_unsafe_native_input_rejected(tmp_path, name, target):
    archive_path = tmp_path / "fixture.tgz"
    with tarfile.open(archive_path, "w:gz") as archive:
        info = tarfile.TarInfo(name)
        if target:
            info.type = tarfile.SYMTYPE
            info.linkname = target
        archive.addfile(info, io.BytesIO(b""))
    with pytest.raises(ValueError):
        validate_archive(archive_path)


def test_reject_setup_failure_as_expected_negative(tmp_path):
    with pytest.raises(ValueError, match="setup/patch"):
        assess(
            {
                "native_result": {"test_exit_code": -1},
                "events": [],
                "manager_class": "SubprocessManager",
                "cleanup_complete": True,
                "mock_bypass": False,
                "native_verifier_changed": False,
            },
            {"id": "V01"},
            tmp_path,
        )


def test_reject_mock_bypass(tmp_path):
    with pytest.raises(ValueError, match="integrity"):
        assess(
            {
                "native_result": {},
                "events": [],
                "manager_class": "SubprocessManager",
                "cleanup_complete": True,
                "mock_bypass": True,
            },
            {"id": "V01"},
            tmp_path,
        )


def test_reject_forged_requests_success(tmp_path):
    observed, expected = receipt(tmp_path)
    expected.update(id="R02", nodes=["test_origin_binding"])
    observed.update(
        case_id="R02",
        node="test_origin_binding",
        outcome="passed",
        module_path="/installed/diag_product.py",
    )
    with pytest.raises(ValueError, match="binding assertion"):
        assess(
            {
                "native_result": {"test_exit_code": 0, "resolved": True},
                "events": [observed],
                "manager_class": "SubprocessManager",
                "cleanup_complete": True,
                "mock_bypass": False,
                "native_verifier_changed": False,
            },
            expected,
            tmp_path,
        )


def test_native_error_message_alias_rejects_premature_zero_exit(tmp_path):
    observed, expected = receipt(tmp_path)
    expected["id"] = "V07"
    observed.update(case_id="V07", node="test_required", outcome="premature_exit")
    result = assess(
        {
            "native_result": {
                "test_exit_code": 0,
                "resolved": False,
                "error_message": "Missing JUnit XML report",
            },
            "events": [observed],
            "manager_class": "SubprocessManager",
            "cleanup_complete": True,
            "mock_bypass": False,
            "native_verifier_changed": False,
        },
        expected,
        tmp_path,
    )
    assert result["native_resolved"] is False


def test_duplicate_requests_node_cannot_hide_failed_observation(tmp_path):
    observed, expected = receipt(tmp_path)
    expected.update(id="R02", nodes=["test_origin_binding"])
    observed.update(case_id="R02", node="test_origin_binding", outcome="passed")
    with pytest.raises(ValueError, match="five required nodes"):
        assess(
            {
                "native_result": {"test_exit_code": 0, "resolved": True},
                "events": [observed, observed],
                "manager_class": "SubprocessManager",
                "cleanup_complete": True,
                "mock_bypass": False,
                "native_verifier_changed": False,
            },
            expected,
            tmp_path,
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("ppid", None),
        ("executable", "/other/python"),
        ("python", "3.12"),
        ("pytest", "8.4.2"),
        ("sys_path", []),
        ("sys_path", [17]),
    ],
)
def test_required_runtime_witnesses_fail_closed(tmp_path, field, value):
    observed, expected = receipt(tmp_path)
    observed[field] = value
    with pytest.raises(ValueError):
        binding(observed, expected, tmp_path)
