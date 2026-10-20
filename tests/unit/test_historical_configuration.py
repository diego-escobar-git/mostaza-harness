"""Historical closures stay frozen while the active submission evolves."""

import shutil
from pathlib import Path

import pytest
import yaml

from mostaza import packaging
from mostaza.evaluation import context_variants

ROOT = Path(__file__).resolve().parents[2]
CONFIGURATIONS = ("E0", "E1", *packaging.VARIANTS, *context_variants.CONFIGURATIONS)


def closure(root: Path, configuration: str) -> dict[str, bytes]:
    builder = (
        context_variants.configuration_files
        if configuration in context_variants.CONFIGURATIONS
        else packaging.configuration_files
    )
    return builder(root, configuration)


@pytest.fixture
def isolated_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    shutil.copytree(ROOT / "experiments", tmp_path / "experiments")
    # Resource/manifest provenance is checked against the authentic repository;
    # the disposable root supplies the source closures under test.
    original = packaging.load_manifest

    def manifest(root: Path, configuration: str) -> dict:
        return original(ROOT, configuration)

    monkeypatch.setattr(packaging, "load_manifest", manifest)
    monkeypatch.setattr(context_variants, "load_manifest", manifest)
    return tmp_path


@pytest.mark.parametrize("configuration", CONFIGURATIONS)
def test_active_submission_drift_does_not_change_history(
    isolated_root: Path, configuration: str
) -> None:
    expected = closure(isolated_root, configuration)
    current = isolated_root / "submission"
    current.mkdir()
    (current / "agent.yaml").write_text("invalid: active configuration\n")
    (current / "eval_config.yaml").write_text("evaluation: {max_time_minutes: 99}\n")
    (current / "prompts").mkdir()
    (current / "prompts/baseline.md").write_text("A different active prompt")
    assert closure(isolated_root, configuration) == expected


@pytest.mark.parametrize("configuration", ("E0", "E0-B180"))
@pytest.mark.parametrize("target", ("agent", "evaluation", "prompt"))
def test_historical_drift_still_fails_closed(
    isolated_root: Path, configuration: str, target: str
) -> None:
    directory = isolated_root / packaging.HISTORICAL_SUBMISSION
    if target == "agent":
        path = directory / "agent.yaml"
        path.write_text(path.read_text().replace("16384", "8192"))
    elif target == "evaluation":
        path = directory / "eval_config.yaml"
        path.write_text(
            path.read_text().replace("max_time_minutes: 1", "max_time_minutes: 5")
        )
    else:
        (directory / "prompts/baseline.md").write_text("Changed historical prompt")
    with pytest.raises(packaging.PackagingError):
        closure(isolated_root, configuration)


def test_current_packaging_keeps_its_own_configuration() -> None:
    files = packaging.collect_submission(ROOT / "submission")
    agent = yaml.load(files["agent.yaml"], Loader=packaging.IncludeLoader)
    evaluation = yaml.safe_load(files["eval_config.yaml"])["evaluation"]
    assert agent["generate_content_config"]["max_output_tokens"] == 16384
    assert "thinking_budget" not in agent["generate_content_config"]["thinking_config"]
    assert evaluation["max_time_minutes"] == 5
    assert evaluation["max_tool_calls"] == 20
