"""Bounded, passive public-source observations without pytest-item access."""

import ast
import hashlib
import json
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest

from mostaza.evaluation import pytest_origin_receipt as observer


def loaded(monkeypatch, tmp_path, name="pcv_public"):
    path = tmp_path / (name + ".py")
    source = b"def evaluate():\n    return 'public'\n"
    path.write_bytes(source)
    module = ModuleType(name)
    module.__file__ = str(path)
    exec(compile(source, str(path), "exec"), module.__dict__)
    monkeypatch.setitem(sys.modules, name, module)
    target = {
        "module": name,
        "symbol": "evaluate",
        "expected_file": str(path),
        "public_files": [
            {"path": str(path), "sha256": hashlib.sha256(source).hexdigest()}
        ],
    }
    return module, path, target


def test_observation_matches_loaded_code_and_does_not_mutate_product(
    monkeypatch, tmp_path
):
    module, path, target = loaded(monkeypatch, tmp_path)
    before = dict(module.__dict__)
    environment, search = dict(os.environ), list(sys.path)
    record = observer._observe(target)
    assert record["status"] == "OBSERVED"
    assert record["resolved_file"] == str(path)
    assert record["workspace_binding_matches"] is True
    assert record["function_identity"] == id(module.evaluate)
    assert len(record["function_code_sha256"]) == 64
    assert len(record["function_source_sha256"]) == 64
    assert module.__dict__ == before
    assert dict(os.environ) == environment and sys.path == search


def test_unloaded_module_remains_unknown_without_import(monkeypatch, tmp_path):
    _, _, target = loaded(monkeypatch, tmp_path)
    monkeypatch.delitem(sys.modules, target["module"])
    record = observer._observe(target)
    assert record["status"] == "UNAVAILABLE"
    assert record["workspace_binding_matches"] is None
    assert target["module"] not in sys.modules


def test_module_dynamic_getter_is_not_invoked(monkeypatch, tmp_path):
    module, _, target = loaded(monkeypatch, tmp_path)

    def forbidden(name):
        raise AssertionError("Dynamic attribute access is forbidden")

    module.__getattr__ = forbidden
    target["symbol"] = "absent"
    assert observer._observe(target)["function_code_sha256"] is None


def test_changed_disk_source_withholds_function_attribution(monkeypatch, tmp_path):
    _, path, target = loaded(monkeypatch, tmp_path)
    path.write_text("def evaluate():\n    return 'changed'\n")
    record = observer._observe(target)
    assert record["workspace_binding_matches"] is False
    assert record["function_code_sha256"] is None
    assert record["function_hash_reason"] == "Module source differs from reviewed bytes"


def test_fixture_replacement_is_not_serialized(monkeypatch, tmp_path):
    module, _, target = loaded(monkeypatch, tmp_path)
    fixture = tmp_path / "conftest.py"
    replacement = {}
    exec(
        compile(
            "def replacement():\n    return 'PRIVATE_EXPECTATION'\n",
            str(fixture),
            "exec",
        ),
        replacement,
    )
    module.evaluate = replacement["replacement"]
    record = observer._observe(target)
    assert record["workspace_binding_matches"] is True
    assert record["function_code_sha256"] is None
    assert record["function_identity"] is None
    assert "PRIVATE_EXPECTATION" not in json.dumps(record)


def test_reexport_does_not_misattribute_source_segment(monkeypatch, tmp_path):
    first, _, target = loaded(monkeypatch, tmp_path)
    second, second_path, second_target = loaded(monkeypatch, tmp_path, "pcv_other")
    first.evaluate = second.evaluate
    target["public_files"].extend(second_target["public_files"])
    record = observer._observe(target)
    assert record["function_code_sha256"] is not None
    assert record["function_source_sha256"] is None
    assert (
        record["function_hash_reason"] == "Function is defined in another reviewed file"
    )
    assert second.evaluate.__code__.co_filename == str(second_path)


@pytest.mark.parametrize(
    "name",
    [
        "tests/public.py",
        "test/public.py",
        "test_product.py",
        "conftest.py",
        "product_test.py",
    ],
)
def test_public_source_boundary_excludes_test_material(tmp_path, name):
    with pytest.raises(ValueError, match="Test material"):
        observer._public_file(str(tmp_path / name))


@pytest.mark.parametrize(
    "case",
    [
        "workspace_output",
        "test_module",
        "unreviewed_expected",
        "bad_pin",
        "relative_output",
    ],
)
def test_configuration_fails_closed(monkeypatch, tmp_path, case):
    _, source, target = loaded(monkeypatch, tmp_path)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.chdir(workspace)
    monkeypatch.setattr(observer, "__file__", str(tmp_path / "observer.py"))
    output = tmp_path / "receipt.jsonl"
    if case == "workspace_output":
        output = workspace / "receipt.jsonl"
    elif case == "test_module":
        target["module"] = "tests.secret"
    elif case == "unreviewed_expected":
        target["expected_file"] = str(source.with_name("other.py"))
    elif case == "bad_pin":
        target["public_files"][0]["sha256"] = "missing"
    elif case == "relative_output":
        output = Path("receipt.jsonl")
    config = {"schema_version": 1, "output_file": str(output), "targets": [target]}
    (tmp_path / observer.CONFIG_NAME).write_text(json.dumps(config))
    with pytest.raises(ValueError):
        observer._configuration()


def test_hook_records_public_process_without_test_arguments(monkeypatch, tmp_path):
    _, _, target = loaded(monkeypatch, tmp_path)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    monkeypatch.chdir(workspace)
    monkeypatch.setattr(observer, "__file__", str(tmp_path / "observer.py"))
    Path(observer.__file__).write_text("# CPU observer fixture\n")
    receipt = tmp_path / "receipt.jsonl"
    config = {"schema_version": 1, "output_file": str(receipt), "targets": [target]}
    (tmp_path / observer.CONFIG_NAME).write_text(json.dumps(config))
    observer.pytest_runtest_call()
    record = json.loads(receipt.read_text())
    assert record["process_id"] == os.getpid()
    assert record["targets"][0]["workspace_binding_matches"] is True
    assert record["coverage"] == "actual_pytest_call_hook_cpu_diagnostic"


def test_logging_failure_does_not_escape_hook(monkeypatch):
    def unavailable():
        raise OSError("Cannot log diagnostics")

    monkeypatch.setattr(observer, "_configuration", unavailable)
    assert observer.pytest_runtest_call() is None


def test_no_item_outcome_import_or_autoload_hooks():
    tree = ast.parse(Path(observer.__file__).read_text())
    hooks = [
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name.startswith("pytest_")
    ]
    assert len(hooks) == 1
    assert hooks[0].name == "pytest_runtest_call"
    assert not hooks[0].args.args
    assert not any(
        isinstance(n, ast.Import) and any(a.name.startswith("pcv_") for a in n.names)
        for n in ast.walk(tree)
    )
