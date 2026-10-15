"""Read-only sandbox import observations; sibling probes never prove scorer imports."""

from __future__ import annotations

import json
import re
import shlex
from pathlib import PurePosixPath
from typing import Any, Protocol


class SandboxExecutor(Protocol):
    def exec(
        self, sandbox_id: str, command: str, *, timeout: int | None = None
    ) -> Any: ...


PROBE = r"""import hashlib, importlib, inspect, json, sys
from pathlib import Path
module_name, relative, expected_hash, symbol = sys.argv[1:]
workspace = Path.cwd().resolve()
expected = (workspace / relative).resolve()
record = {'coverage': 'sibling_probe_not_actual_test_process',
          'interpreter': sys.executable, 'working_directory': str(workspace),
          'effective_import_path': sys.path, 'module': module_name,
          'expected_file': str(expected), 'expected_sha256': expected_hash,
          'function_source_sha256': None}
try:
    module = importlib.import_module(module_name)
    actual = Path(module.__file__).resolve()
    record.update(resolved_file=str(actual),
                  file_sha256=hashlib.sha256(actual.read_bytes()).hexdigest())
    if symbol:
        target = module
        for part in symbol.split('.'):
            target = getattr(target, part)
        function_source = inspect.getsource(target).encode()
        record['function_source_sha256'] = hashlib.sha256(function_source).hexdigest()
    record['workspace_binding_matches'] = (
        actual == expected and expected.is_relative_to(workspace)
        and record['file_sha256'] == expected_hash
    )
    record['status'] = 'OBSERVED'
except Exception as error:
    record.update(status='UNAVAILABLE', resolved_file=None, file_sha256=None,
                  workspace_binding_matches=None, reason=type(error).__name__)
print(json.dumps(record, sort_keys=True))
"""


def observe_origin(
    executor: SandboxExecutor,
    sandbox_id: str,
    *,
    module: str,
    expected_relative_file: str,
    expected_sha256: str,
    phase: str,
    symbol: str = "",
) -> dict[str, Any]:
    """Use the existing public exec boundary, without changing env, setup or pytest."""
    relative = PurePosixPath(expected_relative_file)
    dotted = r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*"
    if (
        not re.fullmatch(dotted, module)
        or symbol
        and not re.fullmatch(dotted, symbol)
        or relative.is_absolute()
        or ".." in relative.parts
        or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256)
        or phase not in {"agent", "verification"}
    ):
        raise ValueError("Unsafe or incomplete binding request")
    command = (
        "cd /workspace && python3 -s -c "
        + shlex.quote(PROBE)
        + " "
        + " ".join(
            shlex.quote(v) for v in (module, str(relative), expected_sha256, symbol)
        )
    )
    result = executor.exec(sandbox_id, command, timeout=30)
    if result.exit_code != 0:
        return {
            "status": "UNAVAILABLE",
            "phase": phase,
            "workspace_binding_matches": None,
            "coverage": "sibling_probe_not_actual_test_process",
            "reason": "Probe process failed",
        }
    try:
        record = json.loads(result.stdout)
        if not isinstance(record, dict):
            raise ValueError("Not a record")
    except (ValueError, TypeError):
        return {
            "status": "UNAVAILABLE",
            "phase": phase,
            "workspace_binding_matches": None,
            "coverage": "sibling_probe_not_actual_test_process",
            "reason": "Probe output is not an isolated JSON record",
        }
    record["phase"] = phase
    return record


def binding_readiness(
    records: list[dict[str, Any]], *, editable_install_exit_code: int | None
) -> dict[str, Any]:
    blockers = [
        "Exact-test-process observation is unsupported by the sibling probe adapter"
    ]
    if type(editable_install_exit_code) is not int or editable_install_exit_code != 0:
        blockers.append("Editable installation success is unknown or failed")
    for phase in ("agent", "verification"):
        matches = [r for r in records if r.get("phase") == phase]
        if not matches or any(
            r.get("workspace_binding_matches") is not True
            or r.get("status") != "OBSERVED"
            for r in matches
        ):
            blockers.append(f"{phase}: imported source is unbound or mismatched")
        if not matches or any(
            r.get("coverage") != "actual_test_process" for r in matches
        ):
            blockers.append(f"{phase}: exact executing-process receipt unavailable")
    return {
        "ready_for_real_evaluation": not blockers,
        "blockers": blockers,
        "historical_verifier_origin": None,
        "native_verifier_changed": False,
    }
