"""Pinned real compiler and authentic E0 provenance checks; no model inference."""

from pathlib import Path

import pytest

from mostaza.packaging import (
    MODEL,
    PackagingError,
    collect_submission,
    compile_directory,
)
from mostaza.resources import require_resources

ROOT = Path(__file__).resolve().parents[2]
COMPILER = ROOT / ".tools/official/bin/python"


def test_ac5_current_official_directory_schema_compiler(tmp_path: Path) -> None:
    require_resources(ROOT, ["swegemma", "adk_submission", "adk_eval_core"])
    (tmp_path / "agent.yaml").write_text(
        f"name: synthetic_contract_fixture\nmodel: {MODEL}\n"
        "instruction: Synthetic compiler fixture only.\ntools: [get_status]\n"
    )
    compile_directory(tmp_path, COMPILER)


def test_ac5_official_schema_rejects_code_config(tmp_path: Path) -> None:
    (tmp_path / "agent.yaml").write_text(
        f"name: synthetic_contract_fixture\nmodel: {MODEL}\n"
        "instruction: Test\ncode_executor: {name: arbitrary_python}\n"
    )
    with pytest.raises(PackagingError, match="Official compiler failed"):
        compile_directory(tmp_path, COMPILER)


def test_ac5_yaml_alias_cycle_rejected_locally(tmp_path: Path) -> None:
    (tmp_path / "agent.yaml").write_text(
        f"name: synthetic_contract_fixture\nmodel: {MODEL}\n"
        "instruction: Test\ngenerate_content_config: &cycle {nested: *cycle}\n"
    )
    with pytest.raises(PackagingError, match="cyclic"):
        collect_submission(tmp_path)


def test_ac4_pinned_native_tool_registry_and_workspace_boundary(tmp_path: Path) -> None:
    import json
    import subprocess

    from mostaza.packaging import TOOLS

    code = """
import json, sys
from pathlib import Path
from swegemma.context import SwegemmaContext
from swegemma.tools import create_tools
from swegemma.tools.workspace import _resolve_workspace_path
ctx = SwegemmaContext(max_tool_calls=5, max_time_minutes=1)
tools = create_tools(ctx)
status = tools['get_status']()
assert status['max_tool_calls'] == 5 and status['tool_calls_remaining'] == 5
assert status['patch_submitted'] is False
workspace = Path(sys.argv[1])
resolved = _resolve_workspace_path('code.py', workspace_root=workspace)
assert resolved == workspace / 'code.py'
for path in ['../foreign.py', '/etc/passwd']:
    try:
        _resolve_workspace_path(path, workspace_root=workspace)
    except ValueError:
        pass
    else:
        raise AssertionError('Native workspace boundary accepted traversal')
print(json.dumps(sorted(tools)))
"""
    result = subprocess.run(
        [str(COMPILER), "-c", code, str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    assert set(json.loads(result.stdout)) == TOOLS


def test_ac1_authentic_e0_derivation_preserves_official_conditions() -> None:
    import json

    import yaml

    from mostaza.packaging import Include, IncludeLoader
    from mostaza.resources import sha256

    resources = require_resources(
        ROOT,
        [
            "harness_readme",
            "starter_agent",
            "starter_eval",
            "starter_sampling",
            "starter_prompt",
            "tasks",
        ],
    )
    source = yaml.load(resources["starter_agent"].read_text(), Loader=IncludeLoader)
    derived = yaml.load(
        (ROOT / "submission/agent.yaml").read_text(), Loader=IncludeLoader
    )
    expected = dict(source)
    expected.pop("adapter")
    expected["tools"] = [tool for tool in source["tools"] if isinstance(tool, str)]
    expected["instruction"] = Include("prompts/baseline.md")
    expected["generate_content_config"] = yaml.safe_load(
        resources["starter_sampling"].read_text()
    )
    assert derived == expected
    assert len(derived["tools"]) == 9
    assert derived["model"] == MODEL
    assert (ROOT / "submission/eval_config.yaml").read_bytes() == resources[
        "starter_eval"
    ].read_bytes()
    manifest = json.loads((ROOT / "experiments/E0-baseline/manifest.json").read_text())
    assert manifest["baseline_source_sha256"] == sha256(resources["starter_agent"])
    assert manifest["source_prompt_sha256"] == sha256(resources["starter_prompt"])
    assert manifest["source_sampling_sha256"] == sha256(resources["starter_sampling"])
    assert manifest["source_eval_sha256"] == sha256(resources["starter_eval"])
    shared = manifest["derivation"]["changes"][-1]["added_text"].encode()
    assert (ROOT / "submission/prompts/baseline.md").read_bytes() == resources[
        "starter_prompt"
    ].read_bytes() + shared
    assert manifest["generation_parameters"] == expected["generate_content_config"]
    assert (
        manifest["budgets"]
        == yaml.safe_load(resources["starter_eval"].read_text())["evaluation"]
    )
    assert manifest["validation"]["real_gemma_execution"] == "NOT_RUN"


def test_ac5_authentic_e0_archive_compiles_and_reproduces(tmp_path: Path) -> None:
    import zipfile

    from mostaza.packaging import build_submission

    first, second = tmp_path / "E0-first.zip", tmp_path / "E0-second.zip"
    assert build_submission(ROOT, "E0", first, COMPILER) == build_submission(
        ROOT, "E0", second, COMPILER
    )
    assert first.read_bytes() == second.read_bytes()
    with zipfile.ZipFile(first) as archive:
        assert set(archive.namelist()) == {
            "agent.yaml",
            "eval_config.yaml",
            "prompts/baseline.md",
        }
        assert (
            archive.read("eval_config.yaml")
            == (ROOT / "submission/eval_config.yaml").read_bytes()
        )
        assert (
            archive.read("prompts/baseline.md")
            == (ROOT / "submission/prompts/baseline.md").read_bytes()
        )


def test_phase2_ac2_native_budget_and_all_variant_compilation(tmp_path: Path) -> None:
    import zipfile

    import yaml

    from mostaza.packaging import VARIANTS, build_submission, load_manifest

    for config in VARIANTS:
        first, second = tmp_path / f"{config}-1.zip", tmp_path / f"{config}-2.zip"
        assert build_submission(ROOT, config, first, COMPILER) == build_submission(
            ROOT, config, second, COMPILER
        )
        m = load_manifest(ROOT, config)
        with zipfile.ZipFile(first) as archive:
            assert yaml.safe_load(archive.read("eval_config.yaml")) == {
                "evaluation": m["budgets"]
            }
            assert (
                archive.read(m["prompt"])
                == (ROOT / "submission" / m["prompt"]).read_bytes()
            )
