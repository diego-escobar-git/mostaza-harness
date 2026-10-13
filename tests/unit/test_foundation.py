"""Foundation contracts; fresh installation/build runs during setup review."""

import subprocess
import sys
import tomllib
from pathlib import Path

from packaging.specifiers import SpecifierSet

import mostaza

ROOT = Path(__file__).resolve().parents[2]


def test_foundation_ac1_python_and_locked_dependencies() -> None:
    """foundation:AC-1 — local tools use Python 3.13 and a complete lock."""
    assert sys.version_info[:2] == (3, 13)
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())
    lock = tomllib.loads((ROOT / "uv.lock").read_text())
    for requirement in [lock["requires-python"], project["project"]["requires-python"]]:
        allowed = SpecifierSet(requirement)
        assert "3.13.15" in allowed
        assert "3.12.9" not in allowed
        assert "3.14.0" not in allowed
    names = {package["name"] for package in lock["package"]}
    assert {"pytest", "ruff", "mypy", "build", "pyyaml"} <= names
    for package in lock["package"]:
        for wheel in package.get("wheels", []):
            assert wheel["hash"].startswith("sha256:")


def test_foundation_ac2_sensitive_assets_are_ignored() -> None:
    """foundation:AC-2 — generated and secret assets stay outside Git."""
    paths = [
        ".env",
        "kaggle.json",
        ".venv/lib/example.py",
        ".tools/uv/bin/uv",
        "resources/HARNESS_README.md",
        "datasets/tasks.json",
        "models/model.bin",
        "weights/model.safetensors",
        "submission.zip",
        "results/trace.jsonl",
    ]
    result = subprocess.run(
        ["git", "check-ignore", "--stdin"],
        cwd=ROOT,
        input="\n".join(paths) + "\n",
        text=True,
        capture_output=True,
        check=True,
    )
    assert set(result.stdout.splitlines()) == set(paths)
    public_paths = [
        "resources/manifest.json",
        "results/.gitkeep",
        "docs/specs/plans/active/example.md",
    ]
    public = subprocess.run(
        ["git", "check-ignore", "--stdin"],
        cwd=ROOT,
        input="\n".join(public_paths) + "\n",
        text=True,
        capture_output=True,
        check=False,
    )
    assert public.returncode == 1
    assert public.stdout == ""


def test_foundation_ac4_installed_import_from_outside_repository(
    tmp_path: Path,
) -> None:
    """foundation:AC-4 — installation works without repository-relative imports."""
    result = subprocess.run(
        [sys.executable, "-c", "import mostaza; print(mostaza.__version__)"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=True,
    )
    assert result.stdout.strip() == mostaza.__version__
