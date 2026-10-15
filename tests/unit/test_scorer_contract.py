"""Source selection and unverified metadata must never become scorer attestations."""

import copy
import json
import shutil
from pathlib import Path

import pytest

from mostaza.evaluation.scorer_contract import (
    ATTESTATIONS,
    EVIDENCE,
    PUBLIC_ROOT,
    compatibility_status,
    public_sources,
    review_docker_recipe,
    review_native_setup,
    review_public_setup,
)

ROOT = Path(__file__).resolve().parents[2]


def test_native_subprocess_returns_before_any_install():
    source = (
        ROOT
        / (
            ".tools/official/lib/python3.13/site-"
            "packages/swegemma/harness/container_setup.py"
        )
    ).read_bytes()
    receipt = review_native_setup(source)
    assert set(receipt["subprocess_early_returns"]) == {
        "install_editable_package",
        "install_test_dependencies",
    }
    assert receipt["effective_selected_setup"] is None
    changed = source.replace(
        b"    if type(docker).__name__ in {'SubprocessManager', 'SubprocessSandbox'}:",
        (
            b"    logger.info('before guard')\n    if "
            b"type(docker).__name__ in "
            b"{'SubprocessManager', 'SubprocessSandbox'}:"
        ),
    )
    with pytest.raises(ValueError, match="return before"):
        review_native_setup(changed)


def test_public_setup_is_read_as_data_not_executed():
    source = (ROOT / PUBLIC_ROOT / "sandbox/setup.py").read_bytes()
    result = review_public_setup(
        source + b"\nraise RuntimeError('must never execute setup')\n"
    )
    assert result["fast_path_writes_workspace_paths_pth"] is True
    assert result["editable_install_result"] is None
    assert "not executed" in result["editable_install_result_reason"]


@pytest.mark.parametrize("name", ["Dockerfile.public", "Dockerfile.sandbox"])
def test_docker_tags_and_requirements_are_not_effective_versions(name):
    source = (ROOT / PUBLIC_ROOT / "docker" / name).read_bytes()
    result = review_docker_recipe(source)
    assert result["python_minor_declared"] == "3.13"
    assert result["pytest_version"] is None
    assert result["image_digest"] is None
    assert result["python_patch_version"] is None


@pytest.mark.parametrize(
    "metadata",
    [
        None,
        {},
        {
            "response_url": (
                "https://www.kaggle.com/competitions/gemma-4-"
                "developer-agent/discussion/1"
            ),
            "attestations": {"scorer_backend_attested": None},
        },
    ],
)
def test_absent_or_unverified_response_metadata_stays_unknown(metadata):
    result = compatibility_status(metadata)
    assert result["status"] == "PENDING_HOST_CONFIRMATION"
    for field in ATTESTATIONS:
        assert result[field] is None
        assert result["missing_reasons"][field]
    assert result["gpu_readiness"] is False


@pytest.mark.parametrize("value", [True, False, "docker"])
def test_unverified_claims_cannot_promote_or_deny_compatibility(value):
    with pytest.raises(ValueError, match="unverified"):
        compatibility_status({"attestations": {"scorer_backend_attested": value}})


def test_outreach_is_explicitly_not_authorized():
    with pytest.raises(ValueError, match="publication"):
        compatibility_status({"publication_authorized": True})
    with pytest.raises(ValueError, match="publication"):
        compatibility_status({"messages_sent": 1})


@pytest.fixture
def bounded_public_copy(tmp_path):
    shutil.copytree(ROOT / PUBLIC_ROOT, tmp_path / PUBLIC_ROOT)
    evidence = tmp_path / EVIDENCE
    evidence.mkdir(parents=True)
    shutil.copyfile(
        ROOT / EVIDENCE / "public-sources.json", evidence / "public-sources.json"
    )
    return tmp_path


def test_public_file_inventory_has_exact_source_provenance(bounded_public_copy):
    sources, manifest = public_sources(bounded_public_copy)
    assert set(sources) == {
        "sandbox/setup.py",
        "docker/Dockerfile.public",
        "docker/Dockerfile.sandbox",
    }
    assert sum(map(len, sources.values())) == 15644
    assert manifest["metric_bootstrap_wrapper"]["value"] is None


@pytest.mark.parametrize(
    "mutation",
    ["bytes", "pin", "location", "invented_version", "extra_file", "duplicate"],
)
def test_source_drift_and_inventory_expansion_fail_closed(
    bounded_public_copy, mutation
):
    path = bounded_public_copy / EVIDENCE / "public-sources.json"
    manifest = json.loads(path.read_text())
    row = manifest["sources"][0]
    if mutation == "bytes":
        source = bounded_public_copy / row["local_path"]
        source.write_bytes(source.read_bytes().replace(b"python", b"Python", 1))
    elif mutation == "pin":
        row["sha256"] = "0" * 64
    elif mutation == "location":
        row["local_path"] = "outside/setup.py"
    elif mutation == "invented_version":
        row["numeric_source_version"] = 1
    elif mutation == "extra_file":
        (bounded_public_copy / PUBLIC_ROOT / "unexpected.txt").write_text(
            "outside allowlist"
        )
    else:
        manifest["sources"][1] = copy.deepcopy(row)
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError):
        public_sources(bounded_public_copy)
