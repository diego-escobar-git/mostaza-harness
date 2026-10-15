"""Read-only historical evidence fixtures; never grant execution allowance."""

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HISTORICAL_HEAD = "1b86b19f7654212c1d9f95eeca84d0e2a05db16b"
CLOSED_PLAN = "docs/specs/plans/closed/mostaza-phase2-budget-retrieval.md"


def read_git(root, *args):
    return subprocess.check_output(
        ["git", "--no-optional-locks", *args], cwd=root, timeout=10
    )


@pytest.fixture(scope="session")
def historical_phase2_root():
    configured = os.environ.get("MOSTAZA_HISTORICAL_PHASE2_ROOT")
    if not configured:
        pytest.fail("Set MOSTAZA_HISTORICAL_PHASE2_ROOT to the retained evidence root")
    root = Path(configured)
    assert root.is_absolute() and root.is_dir() and root.resolve() == root
    assert root != ROOT
    assert read_git(root, "rev-parse", "--show-toplevel").decode().strip() == str(root)
    assert read_git(root, "rev-parse", "HEAD").decode().strip() == HISTORICAL_HEAD
    manifests = []
    for name in ("notebook-import", "requests-import", "verify-task"):
        path = (
            "docs/implementation/evidence/mostaza-" + name + "-cpu/prerequisites.json"
        )
        data = (ROOT / path).read_bytes()
        assert data == read_git(ROOT, "show", HISTORICAL_HEAD + ":" + path)
        manifest = json.loads(data)
        assert manifest["project_path"] == str(root)
        read_git(root, "merge-base", "--is-ancestor", manifest["head"], "HEAD")
        manifests.append(manifest)
    status = read_git(root, "status", "--porcelain=v1", "--untracked-files=all")
    assert status.decode().splitlines() == [" M " + CLOSED_PLAN]
    pin = next(
        item
        for item in manifests[0]["frozen_existing_files"]
        if item["path"] == CLOSED_PLAN
    )
    assert pin["sha256"] == (
        "5457a535f1e8457789d73ef38f0346c04ded2d18424a172e12d7b3ed6e66a8d5"
    )
    assert (
        hashlib.sha256((root / CLOSED_PLAN).read_bytes()).hexdigest() == pin["sha256"]
    )
    return root
