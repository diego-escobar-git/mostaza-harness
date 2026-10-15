"""P-CV-01 opt-in pytest observer; install ONLY in disposable CPU diagnostic sandboxes.

Copy this file as mostaza_origin_receipt.py beside a host-only JSON configuration.
No entry point/autoload registration. No product imports, test-item access or outcome
hooks. Missing/logging-failed receipts are unavailable evidence, never a zero count.
"""

from __future__ import annotations

import ast
import hashlib
import json
import marshal
import os
import re
import stat
import sys
import time
from pathlib import Path
from types import FunctionType, ModuleType
from typing import Any

import pytest

CONFIG_NAME = "mostaza_origin_receipt_config.json"
MAX_SOURCE_BYTES = 2 * 1024 * 1024


def _public_file(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise ValueError("Only reviewed absolute public-source paths are accepted")
    resolved = path.resolve()
    for candidate in (path, resolved):
        if (
            "tests" in candidate.parts
            or "test" in candidate.parts
            or candidate.name.startswith(("test_", "conftest"))
            or candidate.name.endswith("_test.py")
        ):
            raise ValueError("Test material is outside the observer contract")
    return resolved


def _configuration() -> dict[str, Any]:
    path = Path(__file__).with_name(CONFIG_NAME)
    if path.is_symlink() or path.stat().st_size > 65536:
        raise ValueError("Unreviewed configuration")
    config = json.loads(path.read_text())
    if (
        not isinstance(config, dict)
        or set(config) != {"schema_version", "output_file", "targets"}
        or config["schema_version"] != 1
    ):
        raise ValueError("Unsupported observer configuration")
    output = Path(config["output_file"])
    if (
        not output.is_absolute()
        or output.is_symlink()
        or output.resolve().is_relative_to(Path.cwd().resolve())
    ):
        raise ValueError(
            "Receipts must stay in a host-only directory outside workspace"
        )
    if not isinstance(config["targets"], list) or not 1 <= len(config["targets"]) <= 20:
        raise ValueError("Bounded reviewed targets required")
    for target in config["targets"]:
        if not isinstance(target, dict) or set(target) != {
            "module",
            "symbol",
            "expected_file",
            "public_files",
        }:
            raise ValueError("Unsupported target")
        module = target["module"]
        if (
            not isinstance(module, str)
            or not re.fullmatch(r"[A-Za-z]\w*(?:\.[A-Za-z]\w*)*", module)
            or any(
                part in {"pytest", "conftest", "tests", "test"}
                or part.startswith("test_")
                for part in module.split(".")
            )
        ):
            raise ValueError("Only named public product modules are permitted")
        symbol = target["symbol"]
        if symbol is not None and (
            not isinstance(symbol, str) or not re.fullmatch(r"[A-Za-z]\w*", symbol)
        ):
            raise ValueError("Only public module-level functions are supported")
        files = target["public_files"]
        if not isinstance(files, list) or not 1 <= len(files) <= 5:
            raise ValueError("Reviewed source files required")
        reviewed = {}
        for file in files:
            if (
                not isinstance(file, dict)
                or set(file) != {"path", "sha256"}
                or not re.fullmatch(r"[0-9a-f]{64}", file["sha256"])
            ):
                raise ValueError("Public source pin missing")
            reviewed[str(_public_file(file["path"]))] = file["sha256"]
        expected = _public_file(target["expected_file"])
        if str(expected) not in reviewed:
            raise ValueError("Expected source is not reviewed")
    return config


def _function_receipt(
    target: Any, source: bytes, allowed: set[str], source_file: str
) -> dict[str, Any]:
    missing: dict[str, Any] = {
        "function_code_sha256": None,
        "function_source_sha256": None,
        "function_identity": None,
        "function_hash_reason": "No supported public Python function is loaded",
    }
    if not isinstance(target, FunctionType):
        return missing
    code = target.__code__
    if str(Path(code.co_filename).resolve()) not in allowed:
        missing["function_hash_reason"] = (
            "Function code is outside reviewed public source"
        )
        return missing
    value: dict[str, Any] = {
        "function_code_sha256": hashlib.sha256(marshal.dumps(code)).hexdigest(),
        "function_source_sha256": None,
        "function_identity": id(target),
        "function_hash_reason": "Source segment unavailable",
    }
    if str(Path(code.co_filename).resolve()) != source_file:
        value["function_hash_reason"] = "Function is defined in another reviewed file"
        return value
    # Parse pinned public bytes, never a test/fixture or loader callback.
    tree = ast.parse(source.decode("utf-8"))
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = min([node.lineno, *(d.lineno for d in node.decorator_list)])
            if start == code.co_firstlineno and node.name == code.co_name:
                segment = ast.get_source_segment(source.decode("utf-8"), node)
                if segment is not None:
                    value["function_source_sha256"] = hashlib.sha256(
                        segment.encode()
                    ).hexdigest()
                    value["function_hash_reason"] = None
                break
    return value


def _observe(target: dict[str, Any]) -> dict[str, Any]:
    record: dict[str, Any] = {
        "module": target["module"],
        "symbol": target["symbol"],
        "status": "UNAVAILABLE",
        "reason": "Public module not already loaded",
        "resolved_file": None,
        "file_sha256": None,
        "expected_file": str(_public_file(target["expected_file"])),
        "workspace_binding_matches": None,
        "function_code_sha256": None,
        "function_source_sha256": None,
        "function_identity": None,
        "function_hash_reason": "Public module not already loaded",
    }
    module = sys.modules.get(target["module"])
    if not isinstance(module, ModuleType):
        return record
    namespace = ModuleType.__getattribute__(module, "__dict__")
    filename = namespace.get("__file__")
    if not isinstance(filename, str):
        record["reason"] = "No module file available"
        return record
    path = Path(filename).resolve()
    pins = {str(_public_file(f["path"])): f["sha256"] for f in target["public_files"]}
    if str(path) not in pins or path.stat().st_size > MAX_SOURCE_BYTES:
        record["reason"] = (
            "Loaded module file is outside bounded reviewed public source"
        )
        return record
    with path.open("rb") as stream:
        source = stream.read(MAX_SOURCE_BYTES + 1)
    if len(source) > MAX_SOURCE_BYTES:
        record["reason"] = "Public source exceeds the bounded read limit"
        return record
    observed = hashlib.sha256(source).hexdigest()
    record.update(
        status="OBSERVED",
        reason=None,
        resolved_file=str(path),
        file_sha256=observed,
        workspace_binding_matches=path == _public_file(target["expected_file"])
        and observed == pins[str(path)],
    )
    if observed != pins[str(path)]:
        record["function_hash_reason"] = "Module source differs from reviewed bytes"
    elif target["symbol"] is None:
        record["function_hash_reason"] = "No function requested"
    else:
        record.update(
            _function_receipt(
                namespace.get(target["symbol"]), source, set(pins), str(path)
            )
        )
    return record


def _append(path: Path, record: dict[str, Any]) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NONBLOCK
    flags |= getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > 10 * 1024 * 1024:
            raise ValueError("Receipt destination is not a bounded regular file")
        with os.fdopen(descriptor, "a", closefd=False) as stream:
            stream.write(json.dumps(record, sort_keys=True) + "\n")
    finally:
        os.close(descriptor)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call() -> None:
    """Observe the call phase without accepting/reading the pytest test item."""
    try:
        config = _configuration()
        record = {
            "schema_version": 1,
            "protocol": "P-CV-01",
            "coverage": "actual_pytest_call_hook_cpu_diagnostic",
            "phase": "pytest_runtest_call_tryfirst",
            "process_id": os.getpid(),
            "timestamp_epoch": time.time(),
            "interpreter": sys.executable,
            "python_version": sys.version.split()[0],
            "pytest_version": pytest.__version__,
            "working_directory": str(Path.cwd()),
            "effective_import_path": list(sys.path),
            "plugin_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "targets": [_observe(t) for t in config["targets"]],
        }
        _append(Path(config["output_file"]), record)
    except Exception:
        # Diagnostics must never turn an unrelated pass/fail/error into another outcome.
        # The host validator reports a missing receipt as unavailable evidence.
        return
