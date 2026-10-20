"""Bind local subprocess commands to the snapshot's Python sources."""

from __future__ import annotations

import importlib
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any


def snapshot_test_command(command: str) -> str:
    """Prepend src-layout sources while retaining root-layout imports."""
    return command.replace(
        "PYTHONSAFEPATH=1 PYTHONNOUSERSITE=1 python3 -s -m pytest ",
        "PYTHONPATH=/workspace/src:/workspace "
        "PYTHONSAFEPATH=1 PYTHONNOUSERSITE=1 python3 -s -m pytest ",
        1,
    )


@contextmanager
def snapshot_agent_imports() -> Iterator[None]:
    """Give agent shell commands the same source priority as verification."""
    execution: Any = importlib.import_module("swegemma.tools.execution")
    original = execution.run_command

    def execute(ctx: Any, command: str) -> str:
        if type(ctx.docker).__name__ == "SubprocessManager":
            command = "export PYTHONPATH=/workspace/src:/workspace\n" + command
        return str(original(ctx, command))

    execution.run_command = execute
    try:
        yield
    finally:
        execution.run_command = original


@contextmanager
def snapshot_verification_imports() -> Iterator[None]:
    """Scope the import correction to local verification, restoring on exit."""
    verification: Any = importlib.import_module("swegemma.harness.verification")
    original = verification.sandbox_exec

    async def execute(
        manager: Any, sandbox_id: str, command: str, *args: Any, **kwargs: Any
    ) -> Any:
        if type(manager).__name__ == "SubprocessManager":
            command = snapshot_test_command(command)
        return await original(manager, sandbox_id, command, *args, **kwargs)

    verification.sandbox_exec = execute
    try:
        yield
    finally:
        verification.sandbox_exec = original
