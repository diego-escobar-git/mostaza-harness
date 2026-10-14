"""Host archive/path boundary tests; fixture declarations are synthetic, not E0."""

import json
import zipfile
from pathlib import Path

import pytest

from mostaza.packaging import (
    MODEL,
    PackagingError,
    archive_bytes,
    build_submission,
    collect_submission,
)
from mostaza.resources import ResourceError, require_resources, resource_path, sha256


@pytest.fixture
def submission(tmp_path: Path) -> Path:
    root = tmp_path / "submission"
    (root / "prompts").mkdir(parents=True)
    (root / "agent.yaml").write_text(
        f"name: synthetic_contract_fixture\nmodel: {MODEL}\n"
        "instruction: !include prompts/baseline.md\ntools: [get_status]\n"
    )
    (root / "prompts/baseline.md").write_text(
        "Synthetic compiler fixture; never run inference."
    )
    (root / "prompts/hybrid.md").write_text("Synthetic alternative fixture.")
    (root / "eval_config.yaml").write_text("evaluation: {max_tool_calls: 100}\n")
    return root


def test_ac5_deterministic_selected_dependency_closure(
    submission: Path, tmp_path: Path
) -> None:
    files = collect_submission(submission, "prompts/hybrid.md")
    assert set(files) == {"agent.yaml", "eval_config.yaml", "prompts/hybrid.md"}
    first, second = tmp_path / "first.zip", tmp_path / "second.zip"
    assert archive_bytes(files, first) == archive_bytes(files, second)
    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        assert archive.namelist() == sorted(files)
        assert all(
            info.date_time == (1980, 1, 1, 0, 0, 0) for info in archive.infolist()
        )
    assert b"hybrid.md" in files["agent.yaml"]
    assert b"baseline.md" not in files["agent.yaml"]


@pytest.mark.parametrize(
    "reference",
    [
        "../outside.md",
        "/etc/passwd",
        "prompts/../baseline.md",
        "C:/x",
        "prompts\\x",
        "prompts//x",
        "./prompts/x",
    ],
)
def test_ac5_rejects_path_traversal(submission: Path, reference: str) -> None:
    with pytest.raises(PackagingError):
        collect_submission(submission, reference)


def test_ac5_transitive_yaml_include(submission: Path) -> None:
    (submission / "prompts/outer.yaml").write_text("message: !include inner.md\n")
    (submission / "prompts/inner.md").write_text("Nested fixture")
    files = collect_submission(submission, "prompts/outer.yaml")
    assert "prompts/inner.md" in files


def test_ac5_rejects_include_cycle_and_missing(submission: Path) -> None:
    (submission / "prompts/cycle.yaml").write_text("message: !include cycle.yaml\n")
    with pytest.raises(PackagingError, match="cycle"):
        collect_submission(submission, "prompts/cycle.yaml")
    with pytest.raises(PackagingError, match="Missing"):
        collect_submission(submission, "prompts/absent.md")


@pytest.mark.parametrize(
    "name",
    [
        "secret.key",
        "tasks.jsonl",
        "test_patch.txt",
        "helper.py",
        ".env",
        "reference.patch",
        "prompts/test_patch.txt",
    ],
)
def test_ac5_rejects_forbidden_files(submission: Path, name: str) -> None:
    (submission / name).write_text("Do not package")
    with pytest.raises(PackagingError, match="Forbidden"):
        collect_submission(submission)


def test_ac5_rejects_symlink_even_unselected(submission: Path, tmp_path: Path) -> None:
    foreign = tmp_path / "foreign.md"
    foreign.write_text("Foreign")
    (submission / "prompts/unselected.md").symlink_to(foreign)
    with pytest.raises(PackagingError, match="Symlink"):
        collect_submission(submission)


@pytest.mark.parametrize(
    "change",
    [
        "model: forbidden",
        "tools: [unknown]",
        "adapter: sample",
        "sub_agents: []",
        "skills: []",
        "before_model_callbacks: []",
    ],
)
def test_ac5_rejects_unknown_model_tools_or_executable_features(
    submission: Path, change: str
) -> None:
    text = (submission / "agent.yaml").read_text()
    if change.startswith("model:"):
        text = text.replace(f"model: {MODEL}", change)
    elif change.startswith("tools:"):
        text = text.replace("tools: [get_status]", change)
    else:
        text += change + "\n"
    (submission / "agent.yaml").write_text(text)
    with pytest.raises(PackagingError):
        collect_submission(submission)


def test_ac5_archive_never_overwrites_user_file(
    submission: Path, tmp_path: Path
) -> None:
    output = tmp_path / "submission.zip"
    output.write_bytes(b"user-owned")
    with pytest.raises(PackagingError, match="overwrite"):
        archive_bytes(collect_submission(submission), output)
    assert output.read_bytes() == b"user-owned"


def test_ac3_missing_and_mutated_resources_fail_closed(tmp_path: Path) -> None:
    asset = tmp_path / "resources/official/file.md"
    asset.parent.mkdir(parents=True)
    asset.write_text("official fixture")
    manifest = {
        "schema_version": 1,
        "resources": [
            {
                "id": "readme",
                "path": "resources/official/file.md",
                "status": "verified",
                "sha256": sha256(asset),
            }
        ],
    }
    (tmp_path / "resources/manifest.json").write_text(json.dumps(manifest))
    assert require_resources(tmp_path, ["readme"])["readme"] == asset
    asset.write_text("Changed")
    with pytest.raises(ResourceError, match="hash mismatch"):
        require_resources(tmp_path, ["readme"])
    with pytest.raises(ResourceError, match="pending"):
        require_resources(tmp_path, ["unknown"])
    with pytest.raises(ResourceError):
        resource_path(tmp_path, "resources/official/../../foreign")


def test_ac5_explicit_arm_and_authentic_prerequisites(tmp_path: Path) -> None:
    with pytest.raises(PackagingError, match="Explicit"):
        build_submission(tmp_path, "auto", tmp_path / "out.zip", Path("python"))


@pytest.mark.parametrize("failure", ["oversize", "hash", "redirect"])
def test_ac3_fetch_is_bounded_atomic_and_hash_checked(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    import hashlib
    import io

    from mostaza import resources

    data = b"Authentic synthetic network fixture"
    entry = {
        "id": "wheel",
        "path": "resources/official/test.whl",
        "status": "verified",
        "sha256": hashlib.sha256(data).hexdigest(),
        "download_url": "https://www.kaggle.com/api/test",
        "max_bytes": 1 if failure == "oversize" else 1000,
    }
    directory = tmp_path / "resources"
    directory.mkdir()
    (directory / "manifest.json").write_text(
        json.dumps({"schema_version": 1, "resources": [entry]})
    )

    class Response(io.BytesIO):
        url = (
            "https://attacker.invalid/file"
            if failure == "redirect"
            else "https://storage.googleapis.com/pinned-file"
        )

    monkeypatch.setattr(
        resources,
        "urlopen",
        lambda *args, **kwargs: Response(b"Changed" if failure == "hash" else data),
    )
    with pytest.raises(ResourceError):
        resources.fetch_resource(tmp_path, "wheel")
    assert list((directory / "official").iterdir()) == []


def test_ac3_fetch_success_and_existing_conflict(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import hashlib
    import io

    from mostaza import resources

    data = b"Synthetic asset, no official provenance claim"
    directory = tmp_path / "resources"
    directory.mkdir()
    entry = {
        "id": "wheel",
        "path": "resources/official/test.whl",
        "status": "verified",
        "sha256": hashlib.sha256(data).hexdigest(),
        "download_url": "https://www.kaggle.com/api/test",
    }
    (directory / "manifest.json").write_text(
        json.dumps({"schema_version": 1, "resources": [entry]})
    )

    class Response(io.BytesIO):
        url = "https://storage.googleapis.com/pinned-file"

    monkeypatch.setattr(resources, "urlopen", lambda *args, **kwargs: Response(data))
    path = resources.fetch_resource(tmp_path, "wheel")
    assert path.read_bytes() == data
    assert resources.fetch_resource(tmp_path, "wheel") == path
    path.write_bytes(b"user modification")
    with pytest.raises(ResourceError, match="overwrite"):
        resources.fetch_resource(tmp_path, "wheel")
    assert path.read_bytes() == b"user modification"


def test_ac5_oversized_archive_and_missing_root(tmp_path: Path) -> None:
    from mostaza.packaging import MAX_BYTES

    with pytest.raises(PackagingError, match="Missing root"):
        archive_bytes({"prompts/only.md": b"No root"}, tmp_path / "no-root.zip")
    with pytest.raises(PackagingError, match="oversized"):
        archive_bytes({"agent.yaml": b"x" * (MAX_BYTES + 1)}, tmp_path / "large.zip")


def test_ac1_derivation_hash_must_match_actual_starter(tmp_path: Path) -> None:
    directory = tmp_path / "resources/official"
    directory.mkdir(parents=True)
    entries = []
    for resource_id in ["harness_readme", "starter_agent", "tasks"]:
        path = directory / (resource_id + ".txt")
        path.write_text("Synthetic resource fixture only")
        entries.append(
            {
                "id": resource_id,
                "path": path.relative_to(tmp_path).as_posix(),
                "status": "verified",
                "sha256": sha256(path),
            }
        )
    (tmp_path / "resources/manifest.json").write_text(
        json.dumps({"schema_version": 1, "resources": entries})
    )
    experiment = tmp_path / "experiments/E0-baseline"
    experiment.mkdir(parents=True)
    (experiment / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "status": "ready",
                "ready_for_evaluation": True,
                "experiment_id": "E0",
                "baseline_source_sha256": "0" * 64,
            }
        )
    )
    with pytest.raises(PackagingError, match="provenance"):
        build_submission(tmp_path, "E0", tmp_path / "submission.zip", Path("python"))


def test_ac5_selected_file_swap_cannot_escape_root(
    submission: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from mostaza import packaging

    foreign = tmp_path / "private.md"
    foreign.write_text("Must never enter archive")
    inspect = packaging._check_tree

    def swap_after_inspection(root: Path) -> None:
        inspect(root)
        selected = root / "prompts/baseline.md"
        selected.unlink()
        selected.symlink_to(foreign)

    monkeypatch.setattr(packaging, "_check_tree", swap_after_inspection)
    with pytest.raises(PackagingError, match="unsafe"):
        collect_submission(submission)


def test_ac5_fifo_swap_rejected_without_blocking(
    submission: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import os

    from mostaza import packaging

    inspect = packaging._check_tree

    def swap_after_inspection(root: Path) -> None:
        inspect(root)
        selected = root / "prompts/baseline.md"
        selected.unlink()
        os.mkfifo(selected)

    monkeypatch.setattr(packaging, "_check_tree", swap_after_inspection)
    with pytest.raises(PackagingError, match="Non-regular"):
        collect_submission(submission)


@pytest.mark.parametrize(
    "status, readiness",
    [
        ("draft_pending_baseline", False),
        ("draft_pending_baseline", True),
        ("ready", False),
        ("ready", 1),
        (None, True),
    ],
)
def test_ac5_pending_arm_is_rejected_after_resources_available(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    status: str | None,
    readiness: object,
) -> None:
    from mostaza import packaging

    source = tmp_path / "starter.yaml"
    source.write_text("Synthetic source only")
    monkeypatch.setattr(
        packaging, "require_resources", lambda root, ids: {"starter_agent": source}
    )
    experiment = tmp_path / "experiments/E1-hybrid-retrieval"
    experiment.mkdir(parents=True)
    (experiment / "manifest.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "status": status,
                "ready_for_evaluation": readiness,
                "experiment_id": "E1",
                "baseline_source_sha256": sha256(source),
                "prompt": "prompts/hybrid-retrieval.md",
            }
        )
    )
    with pytest.raises(PackagingError, match="pending or not ready"):
        build_submission(tmp_path, "E1", tmp_path / "submission.zip", Path("python"))
    assert not (tmp_path / "submission.zip").exists()
