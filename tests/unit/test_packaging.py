"""Host archive/path boundary tests; fixture declarations are synthetic, not E0."""

import json
import zipfile
from pathlib import Path

import pytest

from mostaza.packaging import (
    ACTIVE_TOOLS,
    MODEL,
    SEARCH_SKILL,
    SKILL_FILES,
    TOOLS,
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


@pytest.mark.parametrize(
    "config", ["E0-B180", "E1-B180", "E0-B300", "E1-B300", "E1-R180"]
)
def test_phase2_ac1_immutable_sources_and_budget_closure(config: str) -> None:
    import yaml

    from mostaza.packaging import (
        BUDGETS,
        HISTORICAL_SUBMISSION,
        configuration_files,
        load_manifest,
    )

    root = Path(__file__).resolve().parents[2]
    paths = [
        root / directory / name
        for directory in ("submission", HISTORICAL_SUBMISSION)
        for name in ("agent.yaml", "eval_config.yaml")
    ]
    before = [path.read_bytes() for path in paths]
    m = load_manifest(root, config)
    files = configuration_files(root, config)
    assert yaml.safe_load(files["eval_config.yaml"]) == {
        "evaluation": BUDGETS[m["budget_family"]]
    }
    assert (
        files[m["prompt"]] == (root / HISTORICAL_SUBMISSION / m["prompt"]).read_bytes()
    )
    assert [path.read_bytes() for path in paths] == before
    assert set(files) == {"agent.yaml", "eval_config.yaml", m["prompt"]}


@pytest.mark.parametrize(
    "field,value",
    [
        ("budgets", {}),
        ("model", "other"),
        ("prompt_sha256", "0" * 64),
        ("arm", "E0"),
        ("calibration_eligible", False),
    ],
)
def test_phase2_ac2_rejects_manifest_drift(
    tmp_path: Path, field: str, value: object
) -> None:
    import shutil

    from mostaza.packaging import load_manifest

    root = Path(__file__).resolve().parents[2]
    for directory in ("experiments", "submission", "resources"):
        shutil.copytree(root / directory, tmp_path / directory)
    path = tmp_path / "experiments/E1-B180/manifest.json"
    data = json.loads(path.read_text())
    data[field] = value
    path.write_text(json.dumps(data))
    with pytest.raises(PackagingError):
        load_manifest(tmp_path, "E1-B180")


@pytest.fixture
def skill_submission(submission: Path) -> Path:
    """search-code:AC-7 uses the sole runtime source, never a second implementation."""
    import yaml

    from mostaza.packaging import IncludeDumper, IncludeLoader

    config = submission / "agent.yaml"
    agent = yaml.load(config.read_bytes(), Loader=IncludeLoader)
    agent["tools"] = sorted(ACTIVE_TOOLS)
    agent["skills"] = [SEARCH_SKILL]
    config.write_text(yaml.dump(agent, Dumper=IncludeDumper))
    (submission / "eval_config.yaml").write_text(
        "evaluation: {timeout_seconds: 60, max_time_minutes: 5, "
        "max_tool_calls: 20, max_turns: 50}\n"
    )
    skill = submission / SEARCH_SKILL
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: search-code\ndescription: Deterministic source retrieval.\n---\n"
        "Run scripts/search_code.py with an explicit workspace root.\n"
    )
    source = Path(__file__).resolve().parents[2] / "submission" / SEARCH_SKILL
    (skill / "scripts/search_code.py").write_bytes(
        (source / "scripts/search_code.py").read_bytes()
    )
    return submission


def test_search_code_ac7_exact_skill_closure_zip_and_notebook_bytes(
    skill_submission: Path, tmp_path: Path
) -> None:
    import base64
    import io
    import re

    from mostaza.development import write_kaggle_notebook

    files = collect_submission(skill_submission)
    assert set(files) == {
        "agent.yaml",
        "eval_config.yaml",
        "prompts/baseline.md",
        *SKILL_FILES,
    }
    for name in SKILL_FILES:
        assert files[name] == (skill_submission / name).read_bytes()
    first, second = tmp_path / "first.zip", tmp_path / "second.zip"
    assert archive_bytes(files, first) == archive_bytes(files, second)
    assert first.read_bytes() == second.read_bytes()
    notebook = json.loads(write_kaggle_notebook(first).read_text())
    code = "".join(notebook["cells"][1]["source"])
    payload = re.search(r"base64.b64decode\('([A-Za-z0-9+/=]+)'\)", code)
    assert payload is not None
    delivery = base64.b64decode(payload[1], validate=True)
    assert delivery == first.read_bytes()
    with zipfile.ZipFile(io.BytesIO(delivery)) as archive:
        assert archive.namelist() == sorted(files)
        assert {name: archive.read(name) for name in archive.namelist()} == files
        assert all(info.external_attr >> 16 == 0o100644 for info in archive.infolist())


@pytest.mark.parametrize(
    "declaration",
    [
        "[]",
        "null",
        "skills/search-code",
        "[skills/unknown]",
        "[skills/search-code, skills/search-code]",
        "[skills/search-code, skills/unknown]",
        "[../skills/search-code]",
        "[/skills/search-code]",
        "[skills/search-code/../search-code]",
        "[skills/search-code/]",
        "[skills//search-code]",
        "[{path: skills/search-code}]",
        "!include prompts/skill.yaml",
    ],
)
def test_search_code_ac7_rejects_invalid_skill_declarations(
    submission: Path, declaration: str
) -> None:
    with (submission / "agent.yaml").open("a") as stream:
        stream.write(f"skills: {declaration}\n")
    with pytest.raises(PackagingError, match="single search-code"):
        collect_submission(submission)


@pytest.mark.parametrize(
    "tools",
    [
        ["get_status"],
        sorted(TOOLS),
        [*sorted(ACTIVE_TOOLS), "run_command"],
        [*sorted(ACTIVE_TOOLS), "unknown"],
    ],
)
def test_search_code_ac7_requires_six_unique_native_tools(
    skill_submission: Path, tools: list[str]
) -> None:
    import yaml

    from mostaza.packaging import IncludeDumper, IncludeLoader

    config = skill_submission / "agent.yaml"
    agent = yaml.load(config.read_bytes(), Loader=IncludeLoader)
    agent["tools"] = tools
    config.write_text(yaml.dump(agent, Dumper=IncludeDumper))
    with pytest.raises(PackagingError, match="native tool"):
        collect_submission(skill_submission)


@pytest.mark.parametrize(
    "name",
    [
        "skills/search-code/scripts/extra.py",
        "skills/search-code/scripts/search_code.pyc",
        "skills/search-code/search_code.py",
        "skills/search-code/references/input.md",
        "skills/search-code/resources/graph.json",
        "skills/search-code/scripts/.env",
        "skills/search-code/scripts/__pycache__/cache.pyc",
        "skills/another/SKILL.md",
        "skills/SKILL.md",
    ],
)
def test_search_code_ac7_rejects_extra_code_and_resources(
    skill_submission: Path, name: str
) -> None:
    path = skill_submission / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("Never deliver")
    with pytest.raises(PackagingError, match="Forbidden"):
        collect_submission(skill_submission)


@pytest.mark.parametrize("missing", sorted(SKILL_FILES))
def test_search_code_ac7_declared_skill_requires_both_files(
    skill_submission: Path, missing: str
) -> None:
    (skill_submission / missing).unlink()
    with pytest.raises(PackagingError, match="Missing or unsafe"):
        collect_submission(skill_submission)


def test_search_code_ac7_rejects_undeclared_skill(skill_submission: Path) -> None:
    config = skill_submission / "agent.yaml"
    config.write_text(config.read_text().replace("skills:\n- skills/search-code\n", ""))
    with pytest.raises(PackagingError, match="Undeclared"):
        collect_submission(skill_submission)


@pytest.mark.parametrize(
    "name",
    [
        "skills",
        "skills/search-code",
        "skills/search-code/scripts",
        *sorted(SKILL_FILES),
    ],
)
def test_search_code_ac7_rejects_symlink_in_each_skill_component(
    skill_submission: Path, tmp_path: Path, name: str
) -> None:
    path = skill_submission / name
    foreign = tmp_path / "foreign"
    path.rename(foreign)
    path.symlink_to(foreign, target_is_directory=foreign.is_dir())
    with pytest.raises(PackagingError, match="Symlink"):
        collect_submission(skill_submission)


def test_search_code_ac7_skill_swap_after_inspection_cannot_escape(
    skill_submission: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from mostaza import packaging

    inspect = packaging._check_tree
    foreign = tmp_path / "private.py"
    foreign.write_text("Private source")

    def swap(root: Path) -> None:
        inspect(root)
        script = root / SEARCH_SKILL / "scripts/search_code.py"
        script.unlink()
        script.symlink_to(foreign)

    monkeypatch.setattr(packaging, "_check_tree", swap)
    with pytest.raises(PackagingError, match="unsafe"):
        collect_submission(skill_submission)


@pytest.mark.parametrize("name", sorted(SKILL_FILES))
def test_search_code_ac7_skill_cannot_be_selected_as_an_include(
    skill_submission: Path, name: str
) -> None:
    config = skill_submission / "agent.yaml"
    config.write_text(config.read_text().replace("prompts/baseline.md", name))
    with pytest.raises(PackagingError, match="Forbidden include"):
        collect_submission(skill_submission)


@pytest.mark.parametrize("limit", ["bytes", "files"])
def test_search_code_ac7_skill_closure_retains_size_and_count_limits(
    skill_submission: Path, monkeypatch: pytest.MonkeyPatch, limit: str
) -> None:
    from mostaza import packaging

    if limit == "bytes":
        monkeypatch.setattr(packaging, "MAX_BYTES", 1000)
    else:
        monkeypatch.setattr(packaging, "MAX_FILES", 4)
    with pytest.raises(PackagingError, match="limit|count"):
        collect_submission(skill_submission)


@pytest.mark.parametrize("change", ["missing", "undeclared", "extra"])
def test_search_code_ac7_archive_checks_skill_declaration_and_members(
    skill_submission: Path, tmp_path: Path, change: str
) -> None:
    files = collect_submission(skill_submission)
    if change == "missing":
        del files[f"{SEARCH_SKILL}/SKILL.md"]
    elif change == "undeclared":
        files["agent.yaml"] = files["agent.yaml"].replace(
            b"skills:\n- skills/search-code\n", b""
        )
    else:
        files[f"{SEARCH_SKILL}/scripts/injected.py"] = b"Injected code"
    with pytest.raises(PackagingError, match="skill files|Forbidden archive"):
        archive_bytes(files, tmp_path / "rejected.zip")
    assert not (tmp_path / "rejected.zip").exists()


def test_search_code_ac7_real_official_compiler_accepts_allowed_skill(
    skill_submission: Path, tmp_path: Path
) -> None:
    from mostaza.packaging import compile_directory

    directory = tmp_path / "compiled"
    for name, data in collect_submission(skill_submission).items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    compiler = Path(__file__).resolve().parents[2] / ".tools/official/bin/python"
    compile_directory(directory, compiler)


@pytest.mark.parametrize(
    "experiment, expected_sha256",
    [
        ("E0", "aa40c075b2bf77c62cca80b9a9b1ec8fd5f28131295c9bf03926fce241464fe4"),
        ("E1", "be8ebd8e660c75b6a7e467b6590e0ff4f093077055e7aeee0db6fa6a0ddd375e"),
    ],
)
def test_search_code_ac7_frozen_historical_archive_bytes_and_native_registry(
    tmp_path: Path, experiment: str, expected_sha256: str
) -> None:
    # agent-retrieval:AC-5: hashes verified using original packaging.py from
    # initial HEAD 1969aa509b6a161a159c79454e95100f6fba8b54.
    import yaml

    from mostaza.packaging import IncludeLoader, configuration_files

    root = Path(__file__).resolve().parents[2]
    files = configuration_files(root, experiment)
    prompt = "baseline.md" if experiment == "E0" else "hybrid-retrieval.md"
    assert set(files) == {"agent.yaml", "eval_config.yaml", f"prompts/{prompt}"}
    assert (
        files[f"prompts/{prompt}"]
        == (root / "experiments/historical-submission/prompts" / prompt).read_bytes()
    )
    assert set(yaml.load(files["agent.yaml"], Loader=IncludeLoader)["tools"]) == TOOLS
    assert len(TOOLS) == 9
    assert archive_bytes(files, tmp_path / f"{experiment}.zip") == expected_sha256
