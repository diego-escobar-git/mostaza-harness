"""Relocated worker: only materialized host payload, native APIs and job data."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import importlib
import json
import shlex
import sys
import time
from pathlib import Path
from typing import Any


def run(job_path: Path) -> None:
    job = json.loads(job_path.read_text())
    home = job_path.parent
    host = home / "traslado ñ" / "host"
    sys.path.insert(0, str(host / "src"))
    import mostaza
    from mostaza.evaluation.notebook_import import prepare_view, validate_view

    if not Path(str(mostaza.__file__)).is_relative_to(host):
        raise ValueError("Developer checkout leaked into relocated worker")
    native = importlib.import_module("swegemma.harness.verification")
    setup = importlib.import_module("swegemma.harness.container_setup")
    manager_type = importlib.import_module(
        "swegemma.sandbox.subprocess"
    ).SubprocessManager
    output = Path(job["output"])
    policy = job["policy"]
    view = prepare_view(
        Path(job["source"]), home / "inputs", policy, fixture=job["fixture"]
    )
    validate_view(view, policy, fixture=job["fixture"])
    resolve = importlib.import_module(
        "swegemma.deduplication"
    ).resolve_task_snapshot_paths
    inputs = resolve(Path(view["root"]), job["task_id"], job["repo"])
    snapshot, base, delta = inputs
    if base != snapshot or delta is None:
        raise ValueError("Notebook preparation did not select base plus delta")
    manager = manager_type(timeout_seconds=30, base_dir=home / "sandboxes")
    empty = home / "empty-wheels"
    empty.mkdir()
    config = importlib.import_module("swegemma.config").EvalConfig(
        tasks_path=home / "owned-tasks.json",
        snapshots_dir=Path(view["root"]),
        results_dir=home / "native",
        submission_dir=home,
        models=importlib.import_module("adk_submission").ModelRegistry(),
        sandbox="subprocess",
        wheels_dir=empty,
        timeout_seconds=30,
        verification_timeout_seconds=30,
        concurrency=1,
    )
    task = importlib.import_module("swegemma.models.task").Task(
        instance_id="import_cpu_" + job["case"],
        repo=job["repo"],
        base_commit=job["base_commit"],
        problem_statement="Owned CPU notebook-layout diagnostic",
        patch="",
        test_patch=job["test_patch"],
        FAIL_TO_PASS=tuple(job["test_file"] + "::" + node for node in job["nodes"]),
    )
    sha = hashlib.sha256(Path(str(native.__file__)).read_bytes()).hexdigest()
    started = time.perf_counter()
    setup_steps = []
    sandbox = None
    try:
        (output / "setup-started.json").write_text(json.dumps({"case": job["case"]}))
        sandbox = manager.start()
        calls = [
            ("setup_container_wheels", (manager, sandbox, config), {}),
            (
                "extract_snapshot",
                (manager, sandbox, snapshot),
                {"base_snapshot_path": base, "patch_path": delta},
            ),
            ("setup_git_exclude", (manager, sandbox), {}),
            ("install_editable_package", (manager, sandbox), {}),
            (
                "install_test_dependencies",
                (manager, sandbox, task.repo),
                {"config": config},
            ),
            ("setup_workspace_test_config", (manager, sandbox), {"repo": task.repo}),
            ("setup_baseline_commit", (manager, sandbox, "baseline"), {}),
        ]
        for name, args, kwargs in calls:
            getattr(setup, name)(*args, **kwargs)
            setup_steps.append(name)
        probe = manager.exec(
            sandbox, "python3 -c " + shlex.quote(job["setup_probe"]), timeout=30
        )
        if probe.exit_code:
            raise ValueError(
                "Setup import probe failed: " + probe.stderr + probe.stdout
            )
        alias = policy["package"]
        baseline = manager.exec(
            sandbox,
            "git ls-tree HEAD -- " + shlex.quote(alias),
            timeout=30,
        )
        clean = manager.exec(sandbox, "git diff HEAD --", timeout=30)
        if (
            baseline.exit_code
            or not baseline.stdout.startswith("120000 ")
            or clean.exit_code
            or clean.stdout.strip()
        ):
            raise ValueError("Alias absent from baseline or leaked into working diff")
        setup_events = json.loads(Path(job["setup_receipt"]).read_text())
        (output / "setup-completed.json").write_text(json.dumps(setup_events))
    finally:
        manager.cleanup_all()
    if sandbox is None or manager.sandboxes:
        raise ValueError("Setup manager cleanup failed")
    validate_view(view, policy, fixture=job["fixture"])
    (output / "native-started.json").write_text(
        json.dumps(
            {
                "case": job["case"],
                "boundary": "Immediately before direct unmodified verify_task",
                "native_verifier_sha256": sha,
            }
        )
    )
    try:
        result = asyncio.run(
            native.verify_task(
                manager,
                config,
                task,
                snapshot,
                base_snapshot_path=base,
                patch_path=delta,
                fast_path=True,
                agent_patch=job["agent_patch"],
                start_time=started,
            )
        )
        (output / "native-completed.json").write_text(
            json.dumps(result.model_dump(mode="json"))
        )
    finally:
        manager.cleanup_all()
    events = json.loads(Path(job["verification_receipt"]).read_text())
    row: dict[str, Any] = {
        "id": job["case"],
        "expected": job["expected"],
        "events": events,
        "setup_expected": job["setup_expected"],
        "setup_events": setup_events,
        "setup_steps": setup_steps,
        "setup_baseline_alias": baseline.stdout,
        "setup_working_diff": clean.stdout,
        "native_result": result.model_dump(mode="json"),
        "manager_class": type(manager).__name__,
        "mock_bypass": False,
        "cleanup_complete": not manager.sandboxes
        and not list((home / "sandboxes").glob("swegemma_sandbox_*")),
        "native_verifier_changed": hashlib.sha256(
            Path(str(native.__file__)).read_bytes()
        ).hexdigest()
        != sha,
        "agent_patch_sha256": hashlib.sha256(job["agent_patch"].encode()).hexdigest(),
        "test_patch_sha256": hashlib.sha256(job["test_patch"].encode()).hexdigest(),
        "layout": view["layout"],
        "view": view,
        "resolver_tuple": [str(p) if p is not None else None for p in inputs],
        "conditions": {
            "timeout_seconds": 30,
            "verification_timeout_seconds": 30,
            "concurrency": 1,
            "backend": "subprocess",
        },
        "relocated_host": str(host),
        "host_module_file": str(Path(str(mostaza.__file__))),
        "launch_cwd": str(Path.cwd()),
        "worker_sys_path": list(sys.path),
        "duration_seconds": time.perf_counter() - started,
        "raw_junit": None,
        "raw_junit_reason": "Native cleanup consumes/removes JUnit",
    }
    (output / "result.json").write_text(
        json.dumps(row, indent=2, sort_keys=True) + "\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job", required=True, type=Path)
    args = parser.parse_args()
    run(args.job.resolve())


if __name__ == "__main__":
    main()
