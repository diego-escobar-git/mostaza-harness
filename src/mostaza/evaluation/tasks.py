"""Separate agent-visible issue data from private post-generation references."""

from __future__ import annotations

import io
import json
import re
import subprocess
import tarfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Any


@dataclass(frozen=True)
class AgentTask:
    """The entire allowed issue context. Never serialize the source task object."""

    instance_id: str
    repo: str
    base_commit: str
    problem_statement: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, ensure_ascii=False)


def agent_task(metadata: dict[str, Any]) -> AgentTask:
    fields = ("instance_id", "repo", "base_commit", "problem_statement")
    if any(not isinstance(metadata.get(k), str) or not metadata[k] for k in fields):
        # Do not include rejected values: error messages may become agent logs.
        raise ValueError("Task requires nonempty allowlisted string fields")
    if not re.fullmatch(r"[0-9a-f]{40}", metadata["base_commit"]):
        raise ValueError("Task base_commit must be an exact Git commit")
    return AgentTask(**{key: metadata[key] for key in fields})


def load_agent_tasks(path: Path) -> list[AgentTask]:
    tasks: list[AgentTask] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            raise ValueError("Invalid task metadata JSON") from None
        if not isinstance(data, dict):
            raise ValueError("Task metadata must be an object")
        task = agent_task(data)
        if task.instance_id in seen:
            raise ValueError("Duplicate task ID")
        seen.add(task.instance_id)
        tasks.append(task)
    return tasks


def export_base_snapshot(repository: Path, task: AgentTask, destination: Path) -> None:
    """Export exactly base_commit, without refs, history, untracked files or links.

    The source repository and task JSONL must remain outside the agent sandbox.
    This host helper is not an implementation of Kaggle's sandbox pipeline.
    """
    if destination.exists() or destination.is_symlink():
        raise ValueError("Snapshot destination must not already exist")
    if not re.fullmatch(r"[0-9a-f]{40}", task.base_commit):
        raise ValueError("Task base_commit must be an exact Git commit")
    result = subprocess.run(
        ["git", "-C", str(repository.resolve()), "archive", task.base_commit],
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ValueError("Cannot export the selected base commit")
    with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
        members = archive.getmembers()
        for member in members:
            path = PurePosixPath(member.name)
            if (
                path.is_absolute()
                or ".." in path.parts
                or any(part.casefold() == ".git" for part in path.parts)
                or not (member.isfile() or member.isdir())
            ):
                raise ValueError("Unsafe snapshot member")
        destination.mkdir(parents=True)
        for member in members:
            target = destination.joinpath(*PurePosixPath(member.name).parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                stream = archive.extractfile(member)
                if stream is None:
                    raise ValueError("Invalid snapshot member")
                with stream, target.open("xb") as output:
                    output.write(stream.read())
                target.chmod(0o755 if member.mode & 0o111 else 0o644)


def validate_snapshot_history(
    archive_path: Path, selected: dict[str, Any], receipt: dict[str, Any]
) -> None:
    """Validate authenticated fast-export snapshot history against its tree receipt.

    Official fast-import may rewrite commit IDs. Original base identity is bound
    through the verified original tree and source hash, never timestamps or a
    requirement that the original commit object survive export.
    """
    import os
    import tempfile

    from mostaza.evaluation.contracts import require
    from mostaza.resources import sha256 as file_digest

    validation = receipt.get("validation", {})
    require(
        receipt.get("kind") == "snapshot"
        and receipt.get("instance_id") == selected["instance_id"]
        and file_digest(archive_path) == receipt.get("sha256"),
        "Snapshot receipt/hash mismatch",
    )
    require(
        validation.get("original_base_commit") == selected["base_commit"]
        and validation.get("base_tree_identity_matches") is True
        and validation.get("original_base_tree_sha")
        == validation.get("snapshot_head_tree_sha")
        and validation.get("original_tree_source")
        == f"https://api.github.com/repos/{selected['repo']}/git/commits/{selected['base_commit']}",
        "Original base/tree identity receipt missing",
    )
    require(
        validation.get("reachable_forward_commits") == 0
        and validation.get("forward_or_unrelated_commit_objects") == 0,
        "Snapshot receipt records unsafe history",
    )
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    environment.update(
        GIT_CONFIG_NOSYSTEM="1",
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_NO_REPLACE_OBJECTS="1",
    )
    with tempfile.TemporaryDirectory(prefix="mostaza-snapshot-history-") as temporary:
        git_dir = Path(temporary) / ".git"
        with tarfile.open(archive_path, "r:gz") as archive:
            for member in archive:
                path = PurePosixPath(member.name)
                require(
                    not path.is_absolute() and ".." not in path.parts,
                    "Unsafe snapshot archive member",
                )
                if path.parts and path.parts[0] == ".git":
                    require(
                        member.isdir() or member.isfile(),
                        "Git snapshot links are forbidden",
                    )
                    if member.isfile():
                        target = Path(temporary).joinpath(*path.parts)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        stream = archive.extractfile(member)
                        require(stream is not None, "Unreadable snapshot Git object")
                        assert stream is not None
                        with stream, target.open("xb") as output:
                            output.write(stream.read())
        require(git_dir.is_dir(), "Snapshot Git metadata missing")
        for relative in ("objects/info/alternates", "shallow", "info/grafts"):
            require(
                not (git_dir / relative).exists(),
                "External or incomplete Git history forbidden",
            )

        def git(*arguments: str) -> str:
            result = subprocess.run(
                [
                    "git",
                    "--git-dir",
                    str(git_dir),
                    "-c",
                    "core.hooksPath=" + os.devnull,
                    "-c",
                    "core.fsmonitor=false",
                    *arguments,
                ],
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            require(result.returncode == 0, "Cannot verify snapshot Git history")
            return result.stdout.strip()

        head = git("rev-parse", "HEAD")
        tree = git("rev-parse", "HEAD^{tree}")
        require(
            head == validation.get("head")
            and tree == validation.get("original_base_tree_sha"),
            "Exported HEAD/tree differs from verified original-base receipt",
        )
        ancestors = set(git("rev-list", "HEAD").splitlines())
        require(
            not git("rev-list", "--all", "--not", "HEAD"),
            "Forward or unrelated Git refs detected",
        )
        for ref in git("for-each-ref", "--format=%(refname)").splitlines():
            require(
                git("rev-parse", ref + "^{commit}") in ancestors,
                "Git reference is not an exported HEAD ancestor",
            )
        objects = git(
            "cat-file",
            "--batch-all-objects",
            "--batch-check=%(objecttype) %(objectname)",
        )
        commits = {
            line.split()[1]
            for line in objects.splitlines()
            if line.startswith("commit ")
        }
        require(
            commits <= ancestors and len(commits) == validation.get("commit_objects"),
            "Forward/unrelated or changed Git commit-object inventory",
        )
