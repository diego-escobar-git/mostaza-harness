"""Local verification must exercise snapshot sources instead of host packages."""

import asyncio
import sys
from types import SimpleNamespace

import pytest

from mostaza.evaluation.local_imports import (
    snapshot_agent_imports,
    snapshot_test_command,
    snapshot_verification_imports,
)

COMMAND = (
    "cd /workspace && PYTHONSAFEPATH=1 PYTHONNOUSERSITE=1 python3 -s -m pytest "
    "tests/test_utils.py --junitxml=/tmp/report.xml -p no:anyio -o timeout=0 -q"
)


def test_verification_path_preserves_all_test_options() -> None:
    corrected = snapshot_test_command(COMMAND)
    assert corrected == COMMAND.replace(
        "&& ", "&& PYTHONPATH=/workspace/src:/workspace ", 1
    )
    assert snapshot_test_command("python3 -c 'print(1)'") == "python3 -c 'print(1)'"


def test_only_subprocess_verification_is_changed_and_restored(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, dict[str, int]]] = []

    async def execute(
        manager: object, sandbox_id: str, command: str, **kwargs: int
    ) -> int:
        calls.append((command, kwargs))
        return 7

    module = SimpleNamespace(sandbox_exec=execute)
    monkeypatch.setitem(sys.modules, "swegemma.harness.verification", module)
    local = type("SubprocessManager", (), {})()
    docker = type("ContainerManager", (), {})()
    with pytest.raises(RuntimeError), snapshot_verification_imports():
        assert asyncio.run(module.sandbox_exec(local, "id", COMMAND, timeout=300)) == 7
        asyncio.run(module.sandbox_exec(docker, "id", COMMAND, timeout=300))
        raise RuntimeError("restore even after failure")
    assert module.sandbox_exec is execute
    assert calls == [
        (snapshot_test_command(COMMAND), {"timeout": 300}),
        (COMMAND, {"timeout": 300}),
    ]


def test_agent_commands_keep_shell_body_and_call_original_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def execute(ctx: object, command: str) -> str:
        calls.append(command)
        return '{"status": "ok"}'

    module = SimpleNamespace(run_command=execute)
    monkeypatch.setitem(sys.modules, "swegemma.tools.execution", module)
    local = SimpleNamespace(docker=type("SubprocessManager", (), {})())
    docker = SimpleNamespace(docker=type("ContainerManager", (), {})())
    command = "cd /workspace && python3 check.py | cat\npython3 other.py"
    with pytest.raises(RuntimeError), snapshot_agent_imports():
        assert module.run_command(local, command) == '{"status": "ok"}'
        module.run_command(docker, command)
        raise RuntimeError("restore after failure")
    assert module.run_command is execute
    assert calls == [
        "export PYTHONPATH=/workspace/src:/workspace\n" + command,
        command,
    ]
