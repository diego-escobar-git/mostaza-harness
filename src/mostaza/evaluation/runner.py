"""Thin execution and provenance adapter to pinned official Kaggle APIs."""

from __future__ import annotations

import dataclasses
import importlib
import zipfile
from importlib.metadata import version
from pathlib import Path
from typing import Any

from mostaza.evaluation.contracts import (
    MODEL,
    canonical_json,
    require,
    sha256,
    validate_manifest,
)
from mostaza.evaluation.tasks import load_agent_tasks, validate_snapshot_history
from mostaza.packaging import collect_submission

WHEEL_PINS = {
    "swegemma-0.2.11-py3-none-any.whl": (
        "9ad876581f3acde8ec3c369858f0834e2b9f41a3cffce3ca42f09cb090aea9d3"
    ),
    "adk_submission-0.2.13-py3-none-any.whl": (
        "f156f0bd84580ccb9334726d114d7a5481f16d3a6e2887cc4d276ced0ef8d99d"
    ),
    "adk_eval_core-0.1.0-py3-none-any.whl": (
        "e614e1b2fe8d886a634871e4c57f9887e1cc66e8c27300f8503a43c6e3ca82f3"
    ),
}


def file_digest(path: Path) -> str:
    import hashlib

    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def describe_runtime(config: Any, vllm_config: Any) -> dict[str, Any]:
    """Capture actual organizer configuration objects, without endpoint credentials."""
    loader = importlib.import_module("adk_submission.yaml_loader")
    raw = loader.load_yaml(
        Path(config.submission_dir) / "agent.yaml",
        root_dir=Path(config.submission_dir),
        limits=config.limits,
    )

    def model_dump(value: Any) -> Any:
        return None if value is None else value.model_dump(mode="json")

    value = {
        "inference": {
            "server": dataclasses.asdict(vllm_config),
            "agent_generate_content_config": raw.get("generate_content_config"),
            "official_generation_defaults": config.generation_constraints.defaults,
            "cache": model_dump(config.context_cache_config),
            "compaction": model_dump(config.events_compaction_config),
        },
        "budgets": {
            "evaluation": dataclasses.asdict(config.budget),
            "harness": dataclasses.asdict(config.harness),
        },
        "config_sha256": sha256(
            canonical_json(
                {
                    name: sha256(data)
                    for name, data in collect_submission(
                        Path(config.submission_dir)
                    ).items()
                }
            )
        ),
    }
    # Normalize tuples in official dataclasses exactly as persisted JSON does.
    import json

    result: dict[str, Any] = json.loads(canonical_json(value))
    return result


def snapshot_digest(
    snapshots_dir: Path, instance_id: str, repo: str, data_root: Path
) -> str:
    """Bind all official reconstruction inputs; roles follow organizer resolution."""
    resolve = importlib.import_module(
        "swegemma.deduplication"
    ).resolve_task_snapshot_paths
    effective, base, delta = resolve(snapshots_dir, instance_id, repo)
    components = []
    for role, path in (("effective", effective), ("base", base), ("delta", delta)):
        if path is not None:
            path = Path(path)
            require(path.is_file(), "Frozen snapshot component missing")
            components.append(
                {
                    "role": role,
                    "path": str(path.relative_to(data_root)),
                    "sha256": file_digest(path),
                }
            )
    return sha256(canonical_json(components))


def validate_bindings(
    config: Any,
    manifest: dict[str, Any],
    *,
    server: Any,
    archive_path: Path,
    wheelhouse_dir: Path,
) -> None:
    """Fail before any agent call if declarations differ from effective inputs."""
    validate_manifest(manifest)
    require(
        manifest["run_kind"] == "real_kaggle", "Official runner requires real run kind"
    )
    require(not config.skip_agent_patch, "Patch generation cannot be skipped")
    require(config.sandbox == "subprocess", "Use the official notebook sandbox backend")
    require(
        not config.shard_index and not config.num_shards and config.concurrency == 1,
        "Phase 1 runs the complete cohort serially without shards",
    )
    require(
        config.task_ids is None
        or config.task_ids == [t["instance_id"] for t in manifest["cohort"]],
        "Configured task IDs differ from cohort",
    )
    model_path = Path(server.config.model)
    require(
        model_path.name == "2" and model_path.parent.name == MODEL,
        "Required pinned 31B model path missing",
    )
    require(
        server.config.tensor_parallel_size == 4
        and not server.config.enable_lora
        and server.config.host == "127.0.0.1",
        "Official L4x4 local model serving required",
    )
    require(
        config.models.list_available() == [MODEL],
        "Registry must contain only the required model",
    )
    binding = config.models.get(MODEL)
    require(
        getattr(binding, "model", None)
        == "openai/"
        + str(getattr(server, "effective_model_path", server.config.model)),
        "Registry model does not match the actual server",
    )
    require(
        getattr(binding, "_additional_args", {}).get("api_base") == server.base_url,
        "Registry endpoint does not match the local server",
    )
    runtime = describe_runtime(config, server.config)
    for field in ("inference", "budgets", "config_sha256"):
        require(
            canonical_json(runtime[field]) == canonical_json(manifest[field]),
            f"Actual runtime differs from manifest {field}",
        )
    require(
        file_digest(archive_path) == manifest["archive_sha256"], "Archive hash mismatch"
    )
    files = collect_submission(Path(config.submission_dir))
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        require(
            len(names) == len(set(names)) and set(names) == set(files),
            "Archive differs from executed submission closure",
        )
        for name, content in files.items():
            require(
                archive.read(name) == content, "Archive/executed config bytes differ"
            )
    discovery = importlib.import_module("adk_submission.discovery")
    require(
        discovery.discover_declared_models(Path(config.submission_dir)) == {MODEL},
        "Every declarative agent must use the required model",
    )
    for package, expected in (
        ("swegemma", "0.2.11"),
        ("adk-submission", "0.2.13"),
        ("adk-eval-core", "0.1.0"),
    ):
        require(version(package) == expected, "Pinned official packages required")
    for name, expected in WHEEL_PINS.items():
        require(
            file_digest(wheelhouse_dir / name) == expected,
            "Pinned official wheel changed",
        )
    require(
        manifest["resources"]["harness"]["sha256"]
        == WHEEL_PINS["swegemma-0.2.11-py3-none-any.whl"],
        "Harness declaration differs from verified wheel",
    )
    wheel_inventory = [
        {"name": p.name, "sha256": file_digest(p)}
        for p in sorted(wheelhouse_dir.glob("*.whl"))
    ]
    require(
        sha256(canonical_json(wheel_inventory))
        == manifest["resources"]["wheelhouse"]["sha256"],
        "Wheelhouse inventory differs from manifest",
    )
    tasks_path = Path(config.tasks_path)
    require(
        file_digest(tasks_path) == manifest["resources"]["dataset"]["sha256"],
        "Dataset changed after selection",
    )
    visible = {task.instance_id: task for task in load_agent_tasks(tasks_path)}
    for selected in manifest["cohort"]:
        task = visible.get(selected["instance_id"])
        require(
            task is not None
            and task.base_commit == selected["base_commit"]
            and task.repo == selected["repo"],
            "Frozen task metadata mismatch",
        )
        require(
            snapshot_digest(
                Path(config.snapshots_dir),
                selected["instance_id"],
                selected["repo"],
                tasks_path.parent,
            )
            == selected["snapshot_sha256"],
            "Frozen reconstruction inputs changed",
        )
        receipts = manifest["environment"].get("snapshot_validation", {})
        require(selected["instance_id"] in receipts, "Snapshot history receipt missing")
        resolve = importlib.import_module(
            "swegemma.deduplication"
        ).resolve_task_snapshot_paths
        effective, base, delta = resolve(
            config.snapshots_dir, selected["instance_id"], selected["repo"]
        )
        require(
            base is None and delta is None,
            "History receipt requires reviewed standalone snapshot",
        )
        validate_snapshot_history(
            Path(effective), selected, receipts[selected["instance_id"]]
        )


async def evaluate_official(
    config: Any,
    manifest: dict[str, Any],
    *,
    server: Any = None,
    archive_path: Path | None = None,
    wheelhouse_dir: Path | None = None,
) -> list[Path]:
    """Delegate to official evaluate_task and persist source-normalizable raw results.

    Model startup remains the official notebook's VllmServer responsibility. The
    raw extension records exactly which generated patch the organizer verified;
    no reference patch/test contents enter these outputs.
    """
    validate_manifest(manifest)
    require(
        manifest["run_kind"] == "real_kaggle", "Official runner requires real run kind"
    )
    require(Path("/kaggle/input").is_dir(), "Official execution requires Kaggle")
    require(
        server is not None and archive_path is not None and wheelhouse_dir is not None,
        "Actual server, archive and wheelhouse bindings are required",
    )
    require(
        server.process is not None and server.process.poll() is None,
        "Actual model server process must be running",
    )
    require(Path(server.config.model).is_dir(), "Actual required model mount missing")
    assert archive_path is not None and wheelhouse_dir is not None
    validate_bindings(
        config,
        manifest,
        server=server,
        archive_path=archive_path,
        wheelhouse_dir=wheelhouse_dir,
    )
    official_models = importlib.import_module("swegemma.models")
    official_evaluate = importlib.import_module("swegemma.evaluate")
    verification = importlib.import_module("swegemma.harness.verification")
    tasks = {
        task.instance_id: task
        for task in official_models.load_tasks(Path(config.tasks_path))
    }
    output = Path(config.results_dir)
    require(
        not output.exists() or not any(output.iterdir()),
        "Result directory must be fresh",
    )
    output.mkdir(parents=True, exist_ok=True)
    evaluator = official_evaluate.Evaluator(config)
    paths: list[Path] = []
    try:
        for index, selected in enumerate(manifest["cohort"], start=1):
            # Use the pinned evaluator's own host-only secret hydration so the
            # recorded effective patch matches its protected target-test paths.
            task = evaluator._hydrate_task_from_secret(tasks[selected["instance_id"]])
            result = await evaluator.evaluate_task(
                task=task, task_index=index, total_tasks=len(manifest["cohort"])
            )
            if not result.trace_path and result.trace is not None:
                result.trace_path = verification.save_trace_artifact(
                    result.trace, output, task.instance_id
                )
            raw = result.model_dump(mode="json", exclude={"trace"})
            effective = verification.strip_protected_files_from_patch(
                result.agent_patch,
                extra_protected_paths=task.test_files,
            )
            raw["_mostaza"] = {
                "schema_version": 1,
                "effective_agent_patch": effective,
                "original_patch_sha256": sha256(result.agent_patch.encode()),
            }
            path = output / f"official-result-{index:04d}.json"
            with path.open("xb") as stream:
                stream.write(canonical_json(raw))
            paths.append(path)
    finally:
        evaluator.docker.cleanup_all()
    return paths
