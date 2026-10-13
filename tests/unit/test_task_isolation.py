"""evaluation:AC-2: reference fields never enter serialized inputs or exported files."""

import io
import json
import subprocess
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from mostaza.evaluation.tasks import agent_task, export_base_snapshot, load_agent_tasks


def metadata():
    return {
        "instance_id": "synthetic-only",
        "repo": "fixture/repo",
        "base_commit": "a" * 40,
        "problem_statement": "Fix the visible issue",
        "patch": "SECRET_REFERENCE",
        "test_patch": "SECRET_TEST",
        "hints_text": "SECRET_HINT",
        "FAIL_TO_PASS": ["SECRET_NODE"],
    }


def test_allowlist_serialization_and_logs(tmp_path, caplog):
    data = metadata()
    task = agent_task(data)
    encoded = task.to_json()
    assert set(json.loads(encoded)) == {
        "instance_id",
        "repo",
        "base_commit",
        "problem_statement",
    }
    assert "SECRET" not in encoded + repr(task) + caplog.text
    path = tmp_path / "private.jsonl"
    path.write_text(json.dumps(data) + "\n")
    assert load_agent_tasks(path) == [task]
    data["base_commit"] = "SECRET_INVALID"
    with pytest.raises(ValueError) as error:
        agent_task(data)
    assert "SECRET" not in str(error.value)


def test_duplicate_and_invalid_metadata(tmp_path):
    path = tmp_path / "tasks.jsonl"
    path.write_text((json.dumps(metadata()) + "\n") * 2)
    with pytest.raises(ValueError, match="Duplicate"):
        load_agent_tasks(path)
    path.write_text('"SECRET_REFERENCE"')
    with pytest.raises(ValueError) as error:
        load_agent_tasks(path)
    assert "SECRET" not in str(error.value)


def test_base_commit_export_has_no_future_history_or_untracked_references(tmp_path):
    # The test owns this temporary Git fixture; product code never mutates Git.
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
        ).stdout.strip()

    git("init")
    git("config", "user.email", "fixture@example.invalid")
    git("config", "user.name", "Fixture")
    (repo / "code.py").write_text("before = True\n")
    git("add", "code.py")
    git("commit", "-m", "base")
    base = git("rev-parse", "HEAD")
    (repo / "code.py").write_text("SECRET_FUTURE_FIX\n")
    git("commit", "-am", "SECRET_REFERENCE_COMMIT_MESSAGE")
    (repo / "private-test.patch").write_text("SECRET_TEST")
    data = metadata() | {"base_commit": base}
    output = tmp_path / "sandbox"
    export_base_snapshot(repo, agent_task(data), output)
    assert [p.name for p in output.iterdir()] == ["code.py"]
    assert (output / "code.py").read_text() == "before = True\n"
    assert not (output / ".git").exists()
    assert "SECRET" not in str(list(output.rglob("*")))


@pytest.mark.parametrize(
    "name,kind",
    [
        ("../private", "file"),
        (".git/config", "file"),
        ("link", "link"),
        ("/absolute", "file"),
    ],
)
def test_snapshot_rejects_unsafe_packaging(tmp_path, monkeypatch, name, kind):
    data = io.BytesIO()
    with tarfile.open(fileobj=data, mode="w") as archive:
        member = tarfile.TarInfo(name)
        if kind == "link":
            member.type = tarfile.SYMTYPE
            member.linkname = "../private/reference.patch"
        archive.addfile(member)
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout=data.getvalue()),
    )
    output = tmp_path / "sandbox"
    with pytest.raises(ValueError, match="Unsafe"):
        export_base_snapshot(Path("/unused"), agent_task(metadata()), output)
    assert not output.exists()


def test_official_history_rejects_forward_refs_and_unreachable_commit_objects(tmp_path):
    from mostaza.evaluation.contracts import sha256
    from mostaza.evaluation.tasks import validate_snapshot_history

    repo = tmp_path / "history"
    repo.mkdir()

    def git(*args):
        return subprocess.run(
            ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
        ).stdout.strip()

    git("init")
    git("config", "user.email", "fixture@example.invalid")
    git("config", "user.name", "Fixture")
    (repo / "source.py").write_text("before\n")
    git("add", "source.py")
    git("commit", "-m", "synthetic base")
    base = git("rev-parse", "HEAD")
    tree = git("rev-parse", "HEAD^{tree}")
    original_branch = git("symbolic-ref", "HEAD")
    (repo / "source.py").write_text("SECRET_FUTURE_REFERENCE\n")
    git("commit", "-am", "synthetic future")
    git("update-ref", "refs/heads/exported-base", base)
    git("symbolic-ref", "HEAD", "refs/heads/exported-base")
    selected = metadata() | {"base_commit": base}
    archive = tmp_path / "snapshot.tgz"

    def receipt():
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(repo / ".git", arcname=".git")
        return {
            "kind": "snapshot",
            "instance_id": selected["instance_id"],
            "sha256": sha256(archive.read_bytes()),
            "validation": {
                "original_base_commit": base,
                "head": base,
                "base_tree_identity_matches": True,
                "original_base_tree_sha": tree,
                "snapshot_head_tree_sha": tree,
                "reachable_forward_commits": 0,
                "forward_or_unrelated_commit_objects": 0,
                "commit_objects": 2,
                "original_tree_source": f"https://api.github.com/repos/fixture/repo/git/commits/{base}",
            },
        }

    with pytest.raises(ValueError, match="Forward or unrelated Git refs"):
        validate_snapshot_history(archive, selected, receipt())
    git("update-ref", "-d", original_branch)
    with pytest.raises(ValueError, match="commit-object inventory"):
        validate_snapshot_history(archive, selected, receipt())
