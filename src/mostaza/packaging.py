"""Deterministic declarative MVP archive boundary (agent-retrieval:AC-5)."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import tempfile
import zipfile
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from mostaza.resources import ResourceError, require_resources, sha256

MODEL = "gemma-4-31b-it-qat-w4a16-ct"
# swegemma 0.2.11, swegemma/tools/__init__.py:create_tools.
TOOLS = frozenset(
    {
        "run_command",
        "read_file",
        "write_file",
        "edit_file",
        "submit_patch",
        "get_status",
        "get_code_neighbors",
        "search_similar_code",
        "get_code_subgraph",
    }
)
EXPERIMENTS = {"E0": "E0-baseline", "E1": "E1-hybrid-retrieval"}
MAX_BYTES = 5 * 1024 * 1024  # Host MVP bound; below the official 3 GiB limit.
MAX_FILES = 100


class PackagingError(ValueError):
    """The submission violates the declarative MVP boundary."""


@dataclass(frozen=True)
class Include:
    path: str


class IncludeLoader(yaml.SafeLoader):
    pass


class IncludeDumper(yaml.SafeDumper):
    pass


def _include(loader: IncludeLoader, node: yaml.ScalarNode) -> Include:
    return Include(loader.construct_scalar(node))


def _represent(dumper: IncludeDumper, value: Include) -> yaml.ScalarNode:
    return dumper.represent_scalar("!include", value.path)


IncludeLoader.add_constructor("!include", _include)
IncludeDumper.add_representer(Include, _represent)


def _relative(value: str) -> str:
    parts = value.split("/")
    if (
        not value
        or any(p in {"", ".", ".."} for p in parts)
        or "\\" in value
        or ":" in value
        or "\0" in value
    ):
        raise PackagingError(f"Unsafe submission path: {value!r}")
    return str(PurePosixPath(value))


def _allowed(value: str) -> bool:
    if PurePosixPath(value).stem in {
        "test_patch",
        "patch",
        "reference",
        "solution",
        "tasks",
    }:
        return False
    return value in {"agent.yaml", "eval_config.yaml"} or (
        value.startswith("prompts/")
        and PurePosixPath(value).suffix in {".md", ".txt", ".yaml", ".yml"}
    )


def _check_tree(root: Path) -> None:
    if root.is_symlink() or not root.is_dir():
        raise PackagingError("Submission root must be a real directory")
    for directory, dirs, names in os.walk(root, followlinks=False):
        for name in [*dirs, *names]:
            path = Path(directory) / name
            relative = path.relative_to(root).as_posix()
            _relative(relative)
            if path.is_symlink():
                raise PackagingError(f"Symlink is forbidden: {relative}")
            if path.is_dir():
                if relative != "prompts" and not relative.startswith("prompts/"):
                    raise PackagingError(f"Forbidden directory: {relative}")
            elif not path.is_file() or not _allowed(relative):
                raise PackagingError(f"Forbidden submission file: {relative}")


def _read_input(root: Path, relative: str) -> bytes:
    """Open components without following symlinks after inspection."""
    parts = _relative(relative).split("/")
    directory: int | None = None
    file_descriptor: int | None = None
    try:
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        directory = os.open(root, flags)
        for part in parts[:-1]:
            child = os.open(part, flags, dir_fd=directory)
            os.close(directory)
            directory = child
        file_descriptor = os.open(
            parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
        )
        if not stat.S_ISREG(os.fstat(file_descriptor).st_mode):
            raise PackagingError(f"Non-regular submission input: {relative}")
        with os.fdopen(file_descriptor, "rb") as stream:
            file_descriptor = None
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise PackagingError("Submission exceeds MVP byte limit")
        return data
    except OSError as error:
        raise PackagingError(
            f"Missing or unsafe submission input: {relative}"
        ) from error
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
        if directory is not None:
            os.close(directory)


def _validate_agent(agent: Any) -> dict[str, Any]:
    if not isinstance(agent, dict):
        raise PackagingError("Agent config must be a mapping")
    allowed = {
        "agent_class",
        "name",
        "description",
        "model",
        "instruction",
        "output_key",
        "include_contents",
        "generate_content_config",
        "tools",
    }
    if set(agent) - allowed:
        raise PackagingError("MVP config contains unsupported fields or delegation")
    if (
        agent.get("agent_class", "LlmAgent") != "LlmAgent"
        or agent.get("model") != MODEL
    ):
        raise PackagingError("MVP requires one LlmAgent and the pinned 31B model")
    if not isinstance(agent.get("name"), str) or not agent["name"]:
        raise PackagingError("Agent name is missing")
    if not isinstance(agent.get("instruction"), (str, Include)):
        raise PackagingError("Instruction must be text or !include")
    tools = agent.get("tools", [])
    if (
        not isinstance(tools, list)
        or any(not isinstance(t, str) or t not in TOOLS for t in tools)
        or len(tools) != len(set(tools))
    ):
        raise PackagingError("Unknown, duplicate or non-native tool")
    return agent


def collect_submission(root: Path, prompt: str | None = None) -> dict[str, bytes]:
    """Collect root config, optional eval settings and transitive !include closure.

    This checks the host boundary only. Official schema/compiler validation is separate.
    """
    _check_tree(root)
    agent = _validate_agent(
        yaml.load(_read_input(root, "agent.yaml"), Loader=IncludeLoader)
    )
    if prompt is not None:
        selected = _relative(prompt)
        if not selected.startswith("prompts/") or not _allowed(selected):
            raise PackagingError("Selected prompt must be an allowed prompt file")
        agent["instruction"] = Include(selected)
    files: dict[str, bytes] = {}
    active: set[str] = set()

    containers: set[int] = set()
    completed_containers: set[tuple[int, str]] = set()

    def references(value: Any, parent: str) -> None:
        if isinstance(value, Include):
            relative = _relative(value.path)
            resolved = (PurePosixPath(parent).parent / relative).as_posix()
            visit(resolved)
        elif isinstance(value, (dict, list)):
            if (id(value), parent) in completed_containers:
                return
            if id(value) in containers or len(containers) >= 50:
                raise PackagingError("YAML containers are cyclic or too deep")
            containers.add(id(value))
            if isinstance(value, dict):
                children: Iterable[tuple[Any, Any]] = value.items()
            else:
                children = [(str(i), child) for i, child in enumerate(value)]
            for key, child in children:
                if not isinstance(key, str):
                    raise PackagingError("YAML mapping keys must be strings")
                references(child, parent)
            containers.remove(id(value))
            completed_containers.add((id(value), parent))

    def visit(relative: str) -> None:
        relative = _relative(relative)
        if not _allowed(relative):
            raise PackagingError(f"Forbidden include: {relative}")
        if relative in active:
            raise PackagingError(f"Include cycle: {relative}")
        if relative in files:
            return
        if len(files) >= MAX_FILES:
            raise PackagingError("Submission exceeds MVP file count")
        path = root / relative
        data = _read_input(root, relative)
        if sum(map(len, files.values())) + len(data) > MAX_BYTES:
            raise PackagingError("Submission exceeds MVP byte limit")
        active.add(relative)
        files[relative] = data
        if path.suffix in {".yaml", ".yml"}:
            references(yaml.load(data, Loader=IncludeLoader), relative)
        active.remove(relative)

    # Root bytes are normalized after selecting precisely one experiment's instruction.
    root_data = yaml.dump(agent, Dumper=IncludeDumper, sort_keys=True).encode()
    files["agent.yaml"] = root_data
    active.add("agent.yaml")
    references(agent, "agent.yaml")
    active.remove("agent.yaml")
    if (root / "eval_config.yaml").exists():
        visit("eval_config.yaml")
    return dict(sorted(files.items()))


def archive_bytes(files: dict[str, bytes], output: Path) -> str:
    """Write reproducible ZIP bytes with fixed metadata and no replacement races."""
    if (
        "agent.yaml" not in files
        or len(files) > MAX_FILES
        or sum(map(len, files.values())) > MAX_BYTES
    ):
        raise PackagingError("Missing root config or oversized archive")
    if output.is_symlink() or output.exists():
        raise PackagingError("Archive output already exists; refusing to overwrite")
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, delete=False) as stream:
            temporary = Path(stream.name)
            with zipfile.ZipFile(
                stream, "w", compression=zipfile.ZIP_STORED
            ) as archive:
                for name, data in sorted(files.items()):
                    if not _allowed(_relative(name)):
                        raise PackagingError("Forbidden archive member")
                    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                    info.create_system = 3
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, data)
        digest = hashlib.sha256(temporary.read_bytes()).hexdigest()
        os.link(temporary, output)
        return digest
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def compile_directory(directory: Path, compiler_python: Path) -> None:
    """Execute the real ADK compiler with inert registry bindings."""
    # macOS temporary roots may be spelled /var, a symlink to /private/var.
    # Pass the resolved directory; the official no-symlink checks stay unchanged.
    directory = directory.resolve(strict=True)
    code = r"""
import importlib.metadata as m
import sys
from pathlib import Path
from adk_submission import ModelRegistry, compile_submission, validate_directory
from adk_submission.schema import SandboxedAgentConfig
from adk_submission.yaml_loader import load_yaml
from swegemma.config import build_submission_limits
assert m.version('adk-submission') == '0.2.13'
assert m.version('google-adk') == '1.36.1'
assert m.version('swegemma') == '0.2.11'
root = Path(sys.argv[1])
limits, constraints = build_submission_limits()
validate_directory(root, limits=limits)
raw = load_yaml(root / 'agent.yaml', root_dir=root, limits=limits)
SandboxedAgentConfig.model_validate(raw)
models = ModelRegistry()
models.register('gemma-4-31b-it-qat-w4a16-ct', 'inert-compiler-only-model')
def inert_tool(**kwargs):
    raise RuntimeError('Compiler-only binding must never execute')
names = ['run_command', 'read_file', 'write_file', 'edit_file', 'submit_patch',
         'get_status', 'get_code_neighbors', 'search_similar_code', 'get_code_subgraph']
tools = {name: inert_tool for name in names}
agent = compile_submission(root, tools, models, limits=limits,
                           generation_constraints=constraints)
assert agent.name == raw['name']
print('official directory/schema/compiler passed; no inference performed')
"""
    result = subprocess.run(
        [str(compiler_python), "-c", code, str(directory)],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    if result.returncode:
        raise PackagingError(f"Official compiler failed: {result.stderr.strip()}")


def build_submission(
    root: Path, experiment: str, output: Path, compiler_python: Path
) -> str:
    if experiment not in EXPERIMENTS:
        raise PackagingError("Explicit experiment must be E0 or E1")
    sources = require_resources(root, ["harness_readme", "starter_agent", "tasks"])
    manifest = json.loads(
        (root / "experiments" / EXPERIMENTS[experiment] / "manifest.json").read_text()
    )
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema_version") != 1
        or manifest.get("status") != "ready"
        or manifest.get("ready_for_evaluation") is not True
    ):
        raise PackagingError(
            "Experiment manifest is pending or not ready for packaging"
        )
    if manifest.get("experiment_id") != experiment or manifest.get(
        "baseline_source_sha256"
    ) != sha256(sources["starter_agent"]):
        raise PackagingError("Experiment lacks official baseline derivation provenance")
    files = collect_submission(root / "submission", manifest["prompt"])
    if output.resolve().is_relative_to((root / "submission").resolve()):
        raise PackagingError("Archive output must be outside submission inputs")
    with tempfile.TemporaryDirectory(prefix="mostaza-compile-") as temporary:
        directory = Path(temporary)
        for name, data in files.items():
            target = directory / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        compile_directory(directory, compiler_python)
    return archive_bytes(files, output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", required=True, choices=list(EXPERIMENTS))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--compiler-python", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    compiler = args.compiler_python or root / ".tools/official/bin/python"
    try:
        digest = build_submission(
            root, args.experiment, args.output.resolve(), compiler
        )
    except (PackagingError, ResourceError, OSError, KeyError, yaml.YAMLError) as error:
        parser.exit(1, f"Packaging prerequisite failed: {error}\n")
    print(
        json.dumps(
            {
                "experiment": args.experiment,
                "archive": str(args.output.resolve()),
                "sha256": digest,
                "validation_kind": "official_compiler_only",
            }
        )
    )


if __name__ == "__main__":
    main()
