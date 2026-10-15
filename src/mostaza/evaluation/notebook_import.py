"""Explicit host-only reconstruction inputs; the official evaluator stays unchanged."""

from __future__ import annotations

import dataclasses
import importlib
import os
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path
from typing import Any

from mostaza.evaluation.contracts import canonical_json, require, sha256
from mostaza.evaluation.runner import file_digest, validate_bindings
from mostaza.evaluation.tasks import validate_snapshot_history

SCHEMA = "mostaza.notebook-layout-evaluation/v1"
PROFILE = "requests-layout-v1"
TASK_IDS = ("requests_7205", "fastapi_15589", "rich_3061")
NATIVE_FILES = (
    "evaluate.py",
    "deduplication.py",
    "harness/agent_runner.py",
    "harness/verification.py",
    "harness/container_setup.py",
    "sandbox/subprocess.py",
    "config.py",
)


def native_sources() -> dict[str, str]:
    package = Path(str(importlib.import_module("swegemma").__file__)).parent
    return {name: file_digest(package / name) for name in NATIVE_FILES}


def delta_bytes(package: str) -> bytes:
    require(package in ("requests", "cpu_import_product"), "Unsupported layout package")
    return (
        f"diff --git a/{package} b/{package}\nnew file mode 120000\n"
        f"--- /dev/null\n+++ b/{package}\n@@ -0,0 +1 @@\n"
        f"+src/{package}\n\\ No newline at end of file\n"
    ).encode()


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.strip()


def source_data_filter(member: tarfile.TarInfo, destination: str) -> tarfile.TarInfo:
    """Keep tracked symlink spelling after all standard data-filter checks."""
    filtered = tarfile.data_filter(member, destination)
    require(filtered.name == member.name, "Archive filename normalization")
    if filtered.linkname != member.linkname:
        require(
            member.issym() and member.linkname.rstrip("/") == filtered.linkname,
            "Unexpected archive link normalization",
        )
        root = Path(destination).resolve()
        link_parent = root / Path(member.name).parent
        original = (link_parent / member.linkname).resolve()
        normalized = (link_parent / filtered.linkname).resolve()
        require(
            original == normalized and original.is_relative_to(root),
            "Archive link destination changed",
        )
        filtered = filtered.replace(linkname=member.linkname)
    return filtered


def layout_proof(snapshot: Path, package: str, parent: Path) -> dict[str, str]:
    """Independently measure only the allowlisted link before native bootstrap."""
    with tempfile.TemporaryDirectory(prefix="layout-proof-", dir=parent) as directory:
        tree = Path(directory)
        with tarfile.open(snapshot) as archive:
            members = archive.getmembers()
            require(len(members) <= 10000, "Layout archive member limit")
            require(
                sum(m.size for m in members) <= 128 * 1024**2, "Layout archive size"
            )
            for member in members:
                path = Path(member.name)
                require(
                    not path.is_absolute() and ".." not in path.parts,
                    "Unsafe archive member",
                )
                require(
                    member.isfile()
                    or member.isdir()
                    or member.issym()
                    or member.islnk(),
                    "Unsafe archive type",
                )
                if member.issym() or member.islnk():
                    target = Path(member.linkname)
                    base = path.parent if member.issym() else Path(".")
                    require(not target.is_absolute(), "Absolute archive link")
                    resolved = Path(os.path.normpath(base / target))
                    require(".." not in resolved.parts, "Escaping archive link")
                    require(
                        not any(
                            Path(m.name) != path and path in Path(m.name).parents
                            for m in members
                        ),
                        "Archive traverses a link",
                    )
            archive.extractall(tree, filter=source_data_filter)
        target = tree / "src" / package
        alias = tree / package
        require(not alias.exists() and not alias.is_symlink(), "Alias conflict")
        require(
            not (tree / "src").is_symlink()
            and not target.is_symlink()
            and (target / "__init__.py").is_file()
            and (target / "__init__.py").resolve().is_relative_to(target.resolve())
            and target.resolve().is_relative_to(tree),
            "Invalid in-workspace source package",
        )
        require(not git(tree, "ls-files", "--", package), "Alias already tracked")
        ignored = subprocess.run(
            ["git", "-C", str(tree), "check-ignore", "-q", "--", package],
            capture_output=True,
            timeout=30,
        )
        require(ignored.returncode == 1, "Alias ignored or Git check failed")
        original = git(tree, "rev-parse", "HEAD^{tree}")
        require(git(tree, "write-tree") == original, "Original index changed")
        require(not git(tree, "diff", "--name-only"), "Original worktree changed")
        subprocess.run(
            ["git", "-C", str(tree), "apply", "-"],
            input=delta_bytes(package),
            capture_output=True,
            check=True,
            timeout=30,
        )
        git(tree, "add", "--", package)
        require(
            git(tree, "diff", "--cached", "--name-only") == package,
            "Delta touches additional paths",
        )
        require(
            git(tree, "ls-files", "--stage", "--", package).split()[0] == "120000"
            and alias.is_symlink()
            and os.readlink(alias) == "src/" + package,
            "Unexpected alias mode/target",
        )
        return {
            "source_tree": original,
            "derived_prebootstrap_tree": git(tree, "write-tree"),
            "alias": package,
            "target": "src/" + package,
            "mode": "120000",
            "patch_sha256": sha256(delta_bytes(package)),
        }


def policy_tasks(
    policy: dict[str, Any], *, fixture: bool = False
) -> list[dict[str, Any]]:
    require(policy["profile"] == PROFILE, "Unknown layout profile")
    tasks: list[dict[str, Any]] = policy["cohort"]
    ids = tuple(t["instance_id"] for t in tasks)
    if fixture:
        require(
            ids == ("cpu_owned_layout",)
            and tasks[0]["repo"] == "mostaza/owned_src_layout"
            and policy["package"] == "cpu_import_product",
            "Fixture policy escaped owned fixture",
        )
    else:
        require(
            ids == TASK_IDS and policy["package"] == "requests", "Production cohort"
        )
        require(
            [t["repo"] for t in tasks]
            == ["psf/requests", "fastapi/fastapi", "Textualize/rich"],
            "Production repositories",
        )
    require(policy["native_sources"] == native_sources(), "Official source drift")
    return tasks


def expected_paths(policy: dict[str, Any], *, fixture: bool = False) -> dict[str, str]:
    tasks = policy_tasks(policy, fixture=fixture)
    dedup = importlib.import_module("swegemma.deduplication")
    result = {
        tasks[0]["instance_id"]: (
            "base_snapshots/" + dedup.get_base_snapshot_filename(tasks[0]["repo"])
        )
    }
    for task in tasks[1:]:
        result[task["instance_id"]] = task["instance_id"] + ".tgz"
    return result


def components(view: Path, task: dict[str, Any]) -> list[dict[str, Any]]:
    resolve = importlib.import_module(
        "swegemma.deduplication"
    ).resolve_task_snapshot_paths
    effective, base, delta = resolve(view, task["instance_id"], task["repo"])
    records = []
    for role, path in (("effective", effective), ("base", base), ("delta", delta)):
        if path is not None:
            path = Path(path)
            require(path.is_file() and not path.is_symlink(), "Nonregular input")
            records.append(
                {
                    "role": role,
                    "path": str(path.relative_to(view)),
                    "bytes": path.stat().st_size,
                    "sha256": file_digest(path),
                }
            )
    return records


def validate_view(
    view: dict[str, Any], policy: dict[str, Any], *, fixture: bool = False
) -> None:
    tasks = policy_tasks(policy, fixture=fixture)
    root = Path(view["root"])
    source = Path(view["source_root"])
    require(root.is_absolute() and root == root.resolve(), "Noncanonical view")
    require(source.is_absolute() and source == source.resolve(), "Noncanonical source")
    require(
        view["policy_sha256"] == sha256(canonical_json(policy)), "Wrong layout policy"
    )
    require(view["fixture"] is fixture, "Fixture/production distinction")
    paths = expected_paths(policy, fixture=fixture)
    delta_path = "patches/" + tasks[0]["instance_id"] + ".patch"
    allowed = set(paths.values()) | {delta_path}
    actual = set()
    for path in root.rglob("*"):
        require(not path.is_symlink(), "View contains a symlink")
        require(path.is_file() or path.is_dir(), "Special file in view")
        if path.is_file():
            actual.add(str(path.relative_to(root)))
    require(actual == allowed, "View contains missing/extra reconstruction inputs")
    require(
        (root / delta_path).read_bytes() == delta_bytes(policy["package"]),
        "Wrong delta",
    )
    require(view["native_sources"] == policy["native_sources"], "Wrong native receipt")
    require(
        set(view["tasks"]) == {t["instance_id"] for t in tasks}, "View task mismatch"
    )
    for index, task in enumerate(tasks):
        iid = task["instance_id"]
        selected = policy["snapshots"][iid]
        original = source / (iid + ".tgz")
        require(file_digest(original) == selected["sha256"], "Original archive drift")
        require(
            file_digest(root / paths[iid]) == selected["sha256"], "Derived base drift"
        )
        measured = components(root, task)
        expected = [
            {
                "role": "effective",
                "path": paths[iid],
                "bytes": selected["bytes"],
                "sha256": selected["sha256"],
            }
        ]
        if index == 0:
            expected += [
                {**expected[0], "role": "base"},
                {
                    "role": "delta",
                    "path": delta_path,
                    "bytes": len(delta_bytes(policy["package"])),
                    "sha256": sha256(delta_bytes(policy["package"])),
                },
            ]
        require(measured == expected, "Native resolver selected an unexpected tuple")
        require(view["tasks"][iid] == measured, "Actual input receipt differs")
    proof = view["layout"]
    require(
        set(proof)
        == {
            "source_tree",
            "derived_prebootstrap_tree",
            "alias",
            "target",
            "mode",
            "patch_sha256",
        }
        and proof["alias"] == policy["package"]
        and proof["target"] == "src/" + policy["package"]
        and proof["mode"] == "120000"
        and proof["patch_sha256"] == sha256(delta_bytes(policy["package"]))
        and proof["source_tree"] != proof["derived_prebootstrap_tree"],
        "Invalid layout proof",
    )
    require(
        proof == policy_proof(source, policy, root.parent), "Layout tree proof drift"
    )


def policy_proof(source: Path, policy: dict[str, Any], parent: Path) -> dict[str, str]:
    first = policy["cohort"][0]
    proof = layout_proof(
        source / (first["instance_id"] + ".tgz"), policy["package"], parent
    )
    expected = policy["snapshots"][first["instance_id"]]["validation"]
    require(
        proof["source_tree"] == expected["snapshot_head_tree_sha"], "Source tree drift"
    )
    return proof


def prepare_view(
    source: Path, destination: Path, policy: dict[str, Any], *, fixture: bool = False
) -> dict[str, Any]:
    """Use native resolver layout; no environment or verifier change."""
    tasks = policy_tasks(policy, fixture=fixture)
    require(source.is_absolute() and source == source.resolve(), "Noncanonical source")
    require(
        destination.is_absolute() and destination == destination.resolve(),
        "Noncanonical destination",
    )
    require(not destination.exists(), "Reconstruction view must be fresh")
    resolve = importlib.import_module(
        "swegemma.deduplication"
    ).resolve_task_snapshot_paths
    for task in tasks:
        original, base, delta = resolve(source, task["instance_id"], task["repo"])
        require(
            base is None
            and delta is None
            and original == source / (task["instance_id"] + ".tgz"),
            "Original must be the pinned standalone snapshot",
        )
        receipt = policy["snapshots"][task["instance_id"]]
        require(
            file_digest(original) == receipt["sha256"]
            and original.stat().st_size == receipt["bytes"],
            "Original pin mismatch",
        )
        if not fixture:
            validate_snapshot_history(original, task, receipt)
    proof = policy_proof(source, policy, destination.parent)
    destination.mkdir()
    for task in tasks:
        relative = expected_paths(policy, fixture=fixture)[task["instance_id"]]
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / (task["instance_id"] + ".tgz"), target)
        target.chmod(0o444)
    delta_path = destination / "patches" / (tasks[0]["instance_id"] + ".patch")
    delta_path.parent.mkdir()
    delta_path.write_bytes(delta_bytes(policy["package"]))
    delta_path.chmod(0o444)
    view = {
        "root": str(destination),
        "source_root": str(source),
        "policy_sha256": sha256(canonical_json(policy)),
        "fixture": fixture,
        "layout": proof,
        "tasks": {t["instance_id"]: components(destination, t) for t in tasks},
        "native_sources": native_sources(),
    }
    validate_view(view, policy, fixture=fixture)
    return view


def execution_envelope(
    parent: dict[str, Any], view: dict[str, Any], policy: dict[str, Any]
) -> dict[str, Any]:
    require(parent["experiment_id"] in ("E0-C8K", "E1-C8K"), "Unsupported parent")
    return {
        "schema": SCHEMA,
        "experiment_id": parent["experiment_id"] + "-L1",
        "parent_binding": parent,
        "actual_execution": view,
        "policy_sha256": sha256(canonical_json(policy)),
    }


def validate_execution_bindings(
    config: Any,
    envelope: dict[str, Any],
    *,
    policy: dict[str, Any],
    server: Any,
    archive_path: Path,
    wheelhouse_dir: Path,
) -> None:
    require(
        set(envelope)
        == {
            "schema",
            "experiment_id",
            "parent_binding",
            "actual_execution",
            "policy_sha256",
        }
        and envelope["schema"] == SCHEMA,
        "Unknown layout execution envelope",
    )
    parent, actual = envelope["parent_binding"], envelope["actual_execution"]
    require(
        envelope["experiment_id"] in ("E0-C8K-L1", "E1-C8K-L1")
        and envelope["experiment_id"] == parent["experiment_id"] + "-L1"
        and parent["cohort"] == policy["cohort"]
        and envelope["policy_sha256"] == sha256(canonical_json(policy)),
        "Envelope binding mismatch",
    )
    validate_view(actual, policy)
    require(
        Path(config.snapshots_dir) == Path(actual["root"]), "Actual view not configured"
    )
    # The parent is deliberately constructed from the actual config: no other
    # setting can be swapped to a convenient parent value during validation.
    parent_config = dataclasses.replace(
        config, snapshots_dir=Path(actual["source_root"])
    )
    for field in dataclasses.fields(config):
        if field.name != "snapshots_dir":
            require(
                getattr(parent_config, field.name) == getattr(config, field.name),
                "Actual/parent config difference",
            )
    validate_bindings(
        parent_config,
        parent,
        server=server,
        archive_path=archive_path,
        wheelhouse_dir=wheelhouse_dir,
    )
