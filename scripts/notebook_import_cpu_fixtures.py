"""Construct owned diagnostics, then dispatch an isolated relocated native worker."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import platform
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mostaza.evaluation.contracts import canonical_json
from mostaza.evaluation.notebook_import_candidate import (
    NOTEBOOK,
    layout_policy,
    payload_of,
)
from mostaza.evaluation.notebook_import_cpu import SETUP_COVERAGE
from mostaza.evaluation.requests_import_cpu import git, immutable_inputs
from mostaza.evaluation.verify_task_cpu import (
    digest,
    expected_function,
    validate_archive,
)

FAULTY = "def evaluate():\n    return 0\n"


def run_case(root: Path, output: Path, home: Path, case: str) -> None:
    legacy = importlib.import_module("verify_task_cpu_fixtures")
    previous = importlib.import_module("requests_import_cpu_fixtures")
    manifest = immutable_inputs(root)
    output.mkdir()
    home.mkdir()
    scratch = home / "fixture"
    scratch.mkdir()
    fixture = case.startswith("L")
    agent_patch = ""
    if fixture:
        package, module, function = (
            "cpu_import_product",
            "cpu_import_product",
            "evaluate",
        )
        product = "src/cpu_import_product/__init__.py"
        (scratch / product).parent.mkdir(parents=True)
        (scratch / product).write_text(FAULTY)
        git(scratch, "init", "-q")
        git(scratch, "add", ".")
        git(
            scratch,
            "-c",
            "user.name=CPU Fixture",
            "-c",
            "user.email=cpu@invalid",
            "commit",
            "-qm",
            "Owned src package",
        )
        base_commit = git(scratch, "rev-parse", "HEAD")
        tree = git(scratch, "rev-parse", "HEAD^{tree}")
        source = home / "source"
        source.mkdir()
        task_id, repo = "cpu_owned_layout", "mostaza/owned_src_layout"
        snapshot = source / (task_id + ".tgz")
        with tarfile.open(snapshot, "w:gz") as archive:
            archive.add(scratch, arcname=".")
        selected = {"instance_id": task_id, "repo": repo, "base_commit": base_commit}
        policy = {
            **layout_policy(root),
            "package": package,
            "cohort": [selected],
            "snapshots": {
                task_id: {
                    "sha256": digest(snapshot),
                    "bytes": snapshot.stat().st_size,
                    "validation": {"snapshot_head_tree_sha": tree},
                }
            },
        }
        if case in ("L02", "L03"):
            value = 1 if case == "L02" else 2
            agent_patch = legacy.patch(
                FAULTY, f"def evaluate():\n    return {value}\n", product
            )
        nodes = ["test_required"]
    else:
        package, module, function = "requests", "requests.utils", "get_netrc_auth"
        product = "src/requests/utils.py"
        source = root / "resources/official/snapshots"
        snapshot = source / "requests_7205.tgz"
        validate_archive(snapshot)
        with tarfile.open(snapshot) as archive:
            archive.extractall(scratch, filter="data")
        task_id, repo = "requests_7205", "psf/requests"
        base_commit = "1b40fdd004bfc8ba5301bcf8a6908264e9b6b877"
        policy = layout_policy(root)
        nodes = [
            "test_origin_binding",
            "test_empty_machine",
            "test_empty_default",
            "test_missing",
            "test_valid",
        ]
        if case != "R00":
            item = manifest["retained_agent_patches"][int(case[-1]) - 1]
            agent_patch = json.loads((root / item["path"]).read_text())["agent_patch"]
    validate_archive(snapshot)
    baseline_source = (scratch / product).read_text()
    common: dict[str, Any] = {
        "pair": case,
        "package": package,
        "module": module,
        "function": function,
        "relative_file": product,
        "allowed_product_paths": [product, product.removeprefix("src/")],
        "nodes": nodes,
        "python": platform.python_version(),
        "pytest": importlib.metadata.version("pytest"),
    }

    def expected() -> dict[str, Any]:
        contents = (scratch / product).read_text()
        return {
            **common,
            "parent_sha256": digest(scratch / "src" / package / "__init__.py"),
            "file_sha256": hashlib.sha256(contents.encode()).hexdigest(),
            "function_fingerprint": expected_function(contents, function),
        }

    setup_expected = expected()
    setup_receipt = home / "setup-events.json"
    setup_probe = previous.test_source(setup_expected, setup_receipt) + (
        "\ndef setup_check(function, matches):\n"
        '    assert matches, "setup imported the wrong source"\n'
        'observe("setup", setup_check)\n'
    )
    setup_probe = setup_probe.replace(repr(previous.COVERAGE), repr(SETUP_COVERAGE), 1)
    if agent_patch:
        subprocess.run(
            ["git", "-C", str(scratch), "apply", "-"],
            input=agent_patch,
            text=True,
            capture_output=True,
            check=True,
            timeout=30,
        )
    verification_expected = expected()
    verification_receipt = home / "verification-events.json"
    test_file = "test_mostaza_import_diagnostic.py"
    test_patch = legacy.patch(
        "", previous.test_source(verification_expected, verification_receipt), test_file
    )
    payload = payload_of(json.loads((root / NOTEBOOK).read_bytes()))
    host = home / "traslado ñ" / "host"
    for name, data in payload.items():
        path = host / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    worker = home / "worker.py"
    shutil.copyfile(root / "scripts/notebook_import_worker.py", worker)
    launch = home / "otro cwd ñ"
    launch.mkdir()
    job = {
        "case": case,
        "task_id": task_id,
        "repo": repo,
        "base_commit": base_commit,
        "source": str(source),
        "fixture": fixture,
        "policy": policy,
        "output": str(output),
        "agent_patch": agent_patch,
        "test_patch": test_patch,
        "test_file": test_file,
        "nodes": nodes,
        "setup_expected": setup_expected,
        "expected": verification_expected,
        "setup_probe": setup_probe,
        "setup_receipt": str(setup_receipt),
        "verification_receipt": str(verification_receipt),
    }
    (output / "test.patch").write_text(test_patch)
    (output / "job-inputs.json").write_bytes(
        canonical_json(
            {
                "case": case,
                "policy": policy,
                "source": str(source),
                "worker_sha256": digest(worker),
                "payload_sha256": {
                    name: hashlib.sha256(data).hexdigest()
                    for name, data in payload.items()
                },
            }
        )
    )
    job_path = home / "job.json"
    job_path.write_bytes(canonical_json(job))
    # Retain only the two baseline transport inputs used by the later stdlib gate.
    if case in ("L01", "R00"):
        portable = output / "portable"
        portable.mkdir()
        if fixture:
            retained = portable / "base.tgz"
            shutil.copyfile(snapshot, retained)
        else:
            retained = snapshot
        from mostaza.evaluation.notebook_import import delta_bytes

        (portable / "layout.patch").write_bytes(delta_bytes(package))
        (portable / "input.json").write_bytes(
            canonical_json(
                {
                    "schema": "mostaza.layout-transport/v1",
                    "package": package,
                    "snapshot": str(retained),
                    "snapshot_sha256": digest(retained),
                    "delta": str(portable / "layout.patch"),
                    "delta_sha256": digest(portable / "layout.patch"),
                    "product": product,
                    "product_sha256": hashlib.sha256(
                        baseline_source.encode()
                    ).hexdigest(),
                }
            )
        )
    subprocess.run(
        [sys.executable, "-I", str(worker), "--job", str(job_path)],
        cwd=launch,
        check=True,
        timeout=85,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case", choices=("L01", "L02", "L03", "R00", "R01", "R02"), required=True
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--home", type=Path, required=True)
    args = parser.parse_args()
    run_case(
        Path(__file__).resolve().parents[1],
        args.output.resolve(),
        args.home.resolve(),
        args.case,
    )


if __name__ == "__main__":
    main()
