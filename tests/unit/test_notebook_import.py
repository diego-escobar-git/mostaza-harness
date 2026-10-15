"""Host provenance and safety; no native verification calls."""

from __future__ import annotations

import copy
import dataclasses
import json
import subprocess
import tarfile
from pathlib import Path
from typing import Any

import pytest

from mostaza.evaluation import notebook_import as layout
from mostaza.evaluation.notebook_import_candidate import (
    NOTEBOOK,
    build_notebook,
    experiment_manifest,
    layout_policy,
    payload_of,
)

ROOT = Path(__file__).resolve().parents[2]


def source_archive(
    tmp_path: Path, *, conflict: bool = False, certificate_alias: bool = False
) -> Path:
    source = tmp_path / "source"
    source.mkdir()
    package = source / "src/cpu_import_product"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("value = 1\n")
    if conflict:
        (source / "cpu_import_product").mkdir()
        (source / "cpu_import_product/conflict").write_text("occupied")
    if certificate_alias:
        target = source / "tests/certs/expired/ca"
        target.mkdir(parents=True)
        link = source / "tests/certs/mtls/client/ca"
        link.parent.mkdir(parents=True)
        link.symlink_to("../../expired/ca/")
    layout.git(source, "init", "-q")
    layout.git(source, "add", ".")
    layout.git(
        source,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=cpu@invalid",
        "commit",
        "-qm",
        "Owned fixture",
    )
    archive = tmp_path / "source.tgz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(source, arcname=".")
    return archive


def test_layout_proof_changes_only_allowlisted_symlink(tmp_path: Path) -> None:
    archive = source_archive(tmp_path)
    proof = layout.layout_proof(archive, "cpu_import_product", tmp_path)
    assert proof["source_tree"] != proof["derived_prebootstrap_tree"]
    assert proof["mode"] == "120000"
    assert proof["target"] == "src/cpu_import_product"
    assert not list(tmp_path.glob("layout-proof-*"))


def test_layout_conflict_fails_and_cleans(tmp_path: Path) -> None:
    archive = source_archive(tmp_path, conflict=True)
    with pytest.raises(ValueError, match="Alias conflict"):
        layout.layout_proof(archive, "cpu_import_product", tmp_path)
    assert not list(tmp_path.glob("layout-proof-*"))


def test_layout_rejects_escape_member(tmp_path: Path) -> None:
    archive = tmp_path / "evil.tgz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.addfile(tarfile.TarInfo("../escape"))
    with pytest.raises(ValueError, match="Unsafe archive member"):
        layout.layout_proof(archive, "cpu_import_product", tmp_path)
    assert not (tmp_path.parent / "escape").exists()


def test_layout_rejects_link_traversal(tmp_path: Path) -> None:
    archive = tmp_path / "evil.tgz"
    with tarfile.open(archive, "w:gz") as tar:
        link = tarfile.TarInfo("link")
        link.type, link.linkname = tarfile.SYMTYPE, "inside"
        tar.addfile(link)
        tar.addfile(tarfile.TarInfo("link/child"))
    with pytest.raises(ValueError, match="traverses a link"):
        layout.layout_proof(archive, "cpu_import_product", tmp_path)


@pytest.mark.parametrize("package", ("../requests", "/requests", "other", "requests\n"))
def test_delta_is_not_arbitrary_package(package: str) -> None:
    with pytest.raises(ValueError):
        layout.delta_bytes(package)


def test_fixture_policy_cannot_select_real_tasks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    policy = layout_policy(ROOT)
    monkeypatch.setattr(layout, "native_sources", lambda: policy["native_sources"])
    with pytest.raises(ValueError, match="Fixture policy"):
        layout.policy_tasks(policy, fixture=True)


def test_production_policy_rejects_generic(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = layout_policy(ROOT)
    monkeypatch.setattr(layout, "native_sources", lambda: policy["native_sources"])
    policy["cohort"] = [
        {"instance_id": "cpu_owned_layout", "repo": "mostaza/owned_src_layout"}
    ]
    policy["package"] = "cpu_import_product"
    with pytest.raises(ValueError, match="Production cohort"):
        layout.policy_tasks(policy)


def test_source_drift_rejects_before_prepare(monkeypatch: pytest.MonkeyPatch) -> None:
    policy = layout_policy(ROOT)
    monkeypatch.setattr(layout, "native_sources", lambda: {})
    with pytest.raises(ValueError, match="Official source drift"):
        layout.policy_tasks(policy)


@dataclasses.dataclass
class Config:
    snapshots_dir: Path
    model: str = "expected"
    budget: int = 180
    tasks: tuple[str, ...] = ("requests_7205",)
    closure: str = "expected-archive"


def binding_fixture(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[dict[str, Any], dict[str, Any]]:
    policy = layout_policy(ROOT)
    parent = {"experiment_id": "E0-C8K", "cohort": policy["cohort"]}
    view = {"root": "/derived", "source_root": "/original", "fixture": False}
    envelope = layout.execution_envelope(parent, view, policy)
    monkeypatch.setattr(layout, "validate_view", lambda *args: None)

    def old_validator(config: Config, manifest: dict[str, Any], **kwargs: Any) -> None:
        assert config.snapshots_dir == Path("/original")
        assert manifest == parent
        assert kwargs["server"] == "contract-only"
        if config.model != "expected" or config.budget != 180:
            raise ValueError("Actual model/budget changed")
        if config.tasks != ("requests_7205",) or config.closure != "expected-archive":
            raise ValueError("Actual task/closure changed")

    monkeypatch.setattr(layout, "validate_bindings", old_validator)
    return policy, envelope


def bind(config: Config, policy: dict[str, Any], envelope: dict[str, Any]) -> None:
    layout.validate_execution_bindings(
        config,
        envelope,
        policy=policy,
        server="contract-only",
        archive_path=Path("/archive"),
        wheelhouse_dir=Path("/wheels"),
    )


def test_parent_is_derived_from_actual_config(monkeypatch: pytest.MonkeyPatch) -> None:
    policy, envelope = binding_fixture(monkeypatch)
    bind(Config(Path("/derived")), policy, envelope)


@pytest.mark.parametrize(
    "field,value",
    [
        ("model", "other"),
        ("budget", 999),
        ("tasks", ("other",)),
        ("closure", "other"),
    ],
)
def test_actual_settings_cannot_hide_in_parent(
    monkeypatch: pytest.MonkeyPatch, field: str, value: Any
) -> None:
    policy, envelope = binding_fixture(monkeypatch)
    config = dataclasses.replace(Config(Path("/derived")), **{field: value})
    with pytest.raises(ValueError, match="Actual"):
        bind(config, policy, envelope)


def test_parent_path_is_not_actual_input(monkeypatch: pytest.MonkeyPatch) -> None:
    policy, envelope = binding_fixture(monkeypatch)
    with pytest.raises(ValueError, match="Actual view"):
        bind(Config(Path("/original")), policy, envelope)


@pytest.mark.parametrize("change", ("schema", "identity", "policy", "cohort", "extra"))
def test_rejects_forged_envelopes(monkeypatch: pytest.MonkeyPatch, change: str) -> None:
    policy, envelope = binding_fixture(monkeypatch)
    envelope = copy.deepcopy(envelope)
    if change == "schema":
        envelope["schema"] = "legacy"
    elif change == "identity":
        envelope["experiment_id"] = "E1-C8K-L1"
    elif change == "policy":
        envelope["policy_sha256"] = "0" * 64
    elif change == "cohort":
        envelope["parent_binding"]["cohort"] = []
    else:
        envelope["snapshot_sha256"] = "parent-claimed-as-actual"
    with pytest.raises(ValueError):
        bind(Config(Path("/derived")), policy, envelope)


def test_notebook_preserves_agent_closures_and_guard() -> None:
    notebook = json.loads(build_notebook(ROOT))
    parent = json.loads(
        (ROOT / "notebooks/mostaza-context-verification.ipynb").read_bytes()
    )
    assert notebook["cells"][1] == parent["cells"][1]
    old, new = payload_of(parent), payload_of(notebook)
    for name, content in old.items():
        assert new[name] == content
    assert set(new) - set(old) == {
        "layout-policy.json",
        "src/mostaza/evaluation/notebook_import.py",
    }
    assert notebook["metadata"]["mostaza"]["notebook_import"]["ready_for_gpu"] is False
    assert notebook["metadata"]["kaggle"]["isGpuEnabled"] is False
    assert NOTEBOOK != "notebooks/mostaza-context-verification.ipynb"


def test_new_pair_preserves_each_parent_closure() -> None:
    manifests = [experiment_manifest(ROOT, arm) for arm in ("E0", "E1")]
    assert manifests[0]["layout_policy_sha256"] == manifests[1]["layout_policy_sha256"]
    for arm, manifest in zip(("E0", "E1"), manifests, strict=True):
        assert manifest["experiment_id"] == arm + "-C8K-L1"
        assert manifest["parent_configuration"] == arm + "-C8K"


def test_git_failure_is_not_treated_as_layout_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    archive = source_archive(tmp_path)

    def fail(*args: Any, **kwargs: Any) -> str:
        raise subprocess.CalledProcessError(1, ["git"])

    monkeypatch.setattr(layout, "git", fail)
    with pytest.raises(subprocess.CalledProcessError):
        layout.layout_proof(archive, "cpu_import_product", tmp_path)


def small_view(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Use native resolver SOURCE only, not a native sandbox or verifier."""
    import ast
    import re
    import types

    source = (
        ROOT / ".tools/official/lib/python3.13/site-packages/swegemma/deduplication.py"
    )
    parsed = ast.parse(source.read_text())
    names = {
        "clean_repo_name",
        "get_base_snapshot_filename",
        "resolve_task_snapshot_paths",
    }
    selected = [
        n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name in names
    ]
    namespace: dict[str, Any] = {"Path": Path, "re": re}
    exec(
        compile(ast.Module(body=selected, type_ignores=[]), str(source), "exec"),
        namespace,
    )
    dedup = types.SimpleNamespace(**{name: namespace[name] for name in names})
    monkeypatch.setattr(
        layout, "importlib", types.SimpleNamespace(import_module=lambda name: dedup)
    )
    policy = layout_policy(ROOT)
    monkeypatch.setattr(layout, "native_sources", lambda: policy["native_sources"])
    original, derived = tmp_path / "original", tmp_path / "derived"
    original.mkdir()
    derived.mkdir()
    paths = layout.expected_paths(policy)
    for index, task in enumerate(policy["cohort"]):
        data = f"owned archive stand-in {index}".encode()
        path = original / (task["instance_id"] + ".tgz")
        path.write_bytes(data)
        pin = policy["snapshots"][task["instance_id"]]
        pin["sha256"], pin["bytes"] = layout.sha256(data), len(data)
        target = derived / paths[task["instance_id"]]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    patch = derived / "patches/requests_7205.patch"
    patch.parent.mkdir()
    patch.write_bytes(layout.delta_bytes("requests"))
    proof = {
        "source_tree": "a" * 40,
        "derived_prebootstrap_tree": "b" * 40,
        "alias": "requests",
        "target": "src/requests",
        "mode": "120000",
        "patch_sha256": layout.sha256(layout.delta_bytes("requests")),
    }
    monkeypatch.setattr(layout, "policy_proof", lambda *args: proof)
    view = {
        "root": str(derived),
        "source_root": str(original),
        "fixture": False,
        "policy_sha256": layout.sha256(layout.canonical_json(policy)),
        "layout": proof,
        "native_sources": policy["native_sources"],
        "tasks": {
            t["instance_id"]: layout.components(derived, t) for t in policy["cohort"]
        },
    }
    return policy, view


def test_three_task_native_resolver_source_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    policy, view = small_view(tmp_path, monkeypatch)
    layout.validate_view(view, policy)
    assert [len(view["tasks"][t["instance_id"]]) for t in policy["cohort"]] == [3, 1, 1]


@pytest.mark.parametrize(
    "tamper",
    [
        "fallback",
        "extra_patch",
        "bad_delta",
        "bad_base",
        "bad_original",
        "resolver_override",
        "parent_as_actual",
        "symlink",
    ],
)
def test_view_rejects_effective_input_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, tamper: str
) -> None:
    policy, view = small_view(tmp_path, monkeypatch)
    derived = Path(view["root"])
    if tamper == "fallback":
        target = derived / "fallbacks/requests_7205.tgz"
        target.parent.mkdir()
        target.write_bytes(b"wrong")
    elif tamper == "extra_patch":
        (derived / "patches/fastapi_15589.patch").write_bytes(b"extra")
    elif tamper == "bad_delta":
        (derived / "patches/requests_7205.patch").write_bytes(b"other")
    elif tamper == "bad_base":
        (derived / layout.expected_paths(policy)["requests_7205"]).write_bytes(
            b"changed"
        )
    elif tamper == "bad_original":
        (Path(view["source_root"]) / "requests_7205.tgz").write_bytes(b"changed")
    elif tamper == "resolver_override":
        old = layout.components
        monkeypatch.setattr(
            layout,
            "components",
            lambda root, task: [
                {**record, "role": "overridden"} for record in old(root, task)
            ],
        )
    elif tamper == "parent_as_actual":
        view["tasks"]["requests_7205"] = [
            {
                "role": "effective",
                "path": "requests_7205.tgz",
                "bytes": 0,
                "sha256": policy["cohort"][0]["snapshot_sha256"],
            }
        ]
    else:
        (derived / "outside").symlink_to(
            tmp_path / "original", target_is_directory=True
        )
    with pytest.raises(ValueError):
        layout.validate_view(view, policy)


def setup_event(tmp_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    from mostaza.evaluation.notebook_import_cpu import SETUP_COVERAGE

    cwd = tmp_path.resolve() / "sandboxes/a/workspace"
    product = "src/cpu_import_product/__init__.py"
    expected = {
        "pair": "L01",
        "package": "cpu_import_product",
        "module": "cpu_import_product",
        "relative_file": product,
        "allowed_product_paths": [product, product.removeprefix("src/")],
        "parent_sha256": "a" * 64,
        "file_sha256": "a" * 64,
        "function_fingerprint": "b" * 64,
        "python": "3.13.15",
        "pytest": "9.1.1",
    }
    raw = str(cwd / "cpu_import_product/__init__.py")
    canonical = str(cwd / product)
    event = {
        "coverage": SETUP_COVERAGE,
        "pair": "L01",
        "node": "setup",
        "pid": 123,
        "ppid": 122,
        "cwd": str(cwd),
        "executable": str(cwd.parent / "venv/bin/python3"),
        "sys_path": ["", str(cwd), "/stdlib"],
        "python": "3.13.15",
        "pytest": "9.1.1",
        "alias_target": "src/cpu_import_product",
        "parent_raw": raw,
        "parent_canonical": canonical,
        "parent_sha256": "a" * 64,
        "module_raw": raw,
        "module_canonical": canonical,
        "module_sha256": "a" * 64,
        "function_raw": raw,
        "function_canonical": canonical,
        "function_module": "cpu_import_product",
        "function_fingerprint": "b" * 64,
        "fingerprint_algorithm": "cpu-code-json-v1",
    }
    return event, expected


def test_setup_c_path_interpretation_preserves_raw_witness(tmp_path: Path) -> None:
    from mostaza.evaluation.notebook_import_cpu import setup_binding

    event, expected = setup_event(tmp_path)
    original = copy.deepcopy(event)
    result, effective = setup_binding(event, expected, tmp_path.resolve())
    assert result is True
    assert effective[0] == event["cwd"]
    assert event == original
    assert event["sys_path"][0] == ""


@pytest.mark.parametrize("paths", (None, [], ["/cwd"], ["", ""], ["", 123]))
def test_setup_path_interpretation_rejects_malformed_witness(
    tmp_path: Path, paths: Any
) -> None:
    from mostaza.evaluation.notebook_import_cpu import setup_binding

    event, expected = setup_event(tmp_path)
    event["sys_path"] = paths
    with pytest.raises(ValueError, match="Malformed setup"):
        setup_binding(event, expected, tmp_path.resolve())


def test_setup_interpretation_keeps_source_checks_strict(tmp_path: Path) -> None:
    from mostaza.evaluation.notebook_import_cpu import setup_binding

    event, expected = setup_event(tmp_path)
    event["module_sha256"] = "0" * 64
    assert setup_binding(event, expected, tmp_path.resolve())[0] is False


def test_setup_scope_cannot_claim_pytest(tmp_path: Path) -> None:
    from mostaza.evaluation.notebook_import_cpu import setup_binding

    event, expected = setup_event(tmp_path)
    event["coverage"] = "actual_pytest_owned_import_layout_cpu"
    with pytest.raises(ValueError, match="Malformed setup"):
        setup_binding(event, expected, tmp_path.resolve())


def test_host_proof_preserves_tracked_certificate_symlink_bytes(tmp_path: Path) -> None:
    archive = source_archive(tmp_path, certificate_alias=True)
    proof = layout.layout_proof(archive, "cpu_import_product", tmp_path)
    assert proof["source_tree"] == layout.git(
        tmp_path / "source", "rev-parse", "HEAD^{tree}"
    )
    assert proof["derived_prebootstrap_tree"] != proof["source_tree"]
    assert not list(tmp_path.glob("layout-proof-*"))


def test_source_filter_preserves_only_trailing_symlink_separator(
    tmp_path: Path,
) -> None:
    member = tarfile.TarInfo("tests/certs/mtls/client/ca")
    member.type, member.linkname = tarfile.SYMTYPE, "../../expired/ca/"
    filtered = layout.source_data_filter(member, str(tmp_path))
    assert filtered.linkname == member.linkname
    assert filtered.uid is None and filtered.mode is None
    assert member.uid == 0


@pytest.mark.parametrize(
    "linkname", ("inside/../target/", "./target/", "inside//target/")
)
def test_source_filter_rejects_other_link_normalization(
    tmp_path: Path, linkname: str
) -> None:
    member = tarfile.TarInfo("link")
    member.type, member.linkname = tarfile.SYMTYPE, linkname
    with pytest.raises(ValueError, match="Unexpected archive link normalization"):
        layout.source_data_filter(member, str(tmp_path))


@pytest.mark.parametrize("linkname", ("/outside", "../outside/"))
def test_source_filter_keeps_standard_escape_rejection(
    tmp_path: Path, linkname: str
) -> None:
    member = tarfile.TarInfo("link")
    member.type, member.linkname = tarfile.SYMTYPE, linkname
    with pytest.raises(tarfile.FilterError):
        layout.source_data_filter(member, str(tmp_path))


def test_source_filter_does_not_restore_hard_link_spelling(tmp_path: Path) -> None:
    member = tarfile.TarInfo("link")
    member.type, member.linkname = tarfile.LNKTYPE, "target/"
    with pytest.raises(ValueError, match="Unexpected archive link normalization"):
        layout.source_data_filter(member, str(tmp_path))
