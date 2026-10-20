"""Offline phase-2 preparation; no API in this module starts a remote session."""

from __future__ import annotations

import ast
import base64
import inspect
import json
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from mostaza.evaluation.contracts import canonical_json, require, sha256
from mostaza.evaluation.import_results import retained_path
from mostaza.packaging import VARIANTS, archive_bytes, configuration_files

NOTEBOOK = "notebooks/mostaza-phase2-preparation.ipynb"
EVIDENCE = "docs/implementation/evidence/mostaza-phase2-budget-retrieval"
HOST_MODULES = (
    "src/mostaza/__init__.py",
    "src/mostaza/resources.py",
    "src/mostaza/packaging.py",
    "src/mostaza/evaluation/__init__.py",
    "src/mostaza/evaluation/contracts.py",
    "src/mostaza/evaluation/tasks.py",
    "src/mostaza/evaluation/runner.py",
)
CONFIGURATIONS = ("E0-B180", "E1-B180")
TASKS = ("requests_7205", "fastapi_15589", "rich_3061")
QUOTA: dict[str, Any] = {
    "batch": "B180-initial",
    "configurations": list(CONFIGURATIONS),
    "tasks": list(TASKS),
    "evaluations": 6,
    "gpu_model": "NVIDIA L4",
    "gpu_count": 4,
    "concurrency": 1,
    "retries": 0,
    "generation_seconds": 1080,
    "verification_seconds": 1800,
    "session_seconds": 7200,
    "gpu_device_hours": 8,
    "paid_purchases_usd": 0,
    "export_reserve_seconds": 300,
    "task_overhead_reserve_seconds": 120,
    "deadline_basis": "GPU allocation start, including startup/install/export",
}
PLATFORM: dict[str, Any] = {
    "status": "BLOCKED",
    "quota_observed": None,
    "allocation_start_observed": None,
    "allocation_termination_verified": False,
    "reason": (
        "No authenticated allocation-start clock and allocation-termination "
        "adapter verified for this offline Kaggle session. A Python timer or "
        "VllmServer.stop does not release the Kaggle GPU allocation."
    ),
    "sources": [
        {
            "url": "https://github.com/Kaggle/kaggle-cli/blob/main/skills/references/kernels.md",
            "locator": "kernels push --timeout; kernels status",
            "observation": (
                "Runtime timeout option exists; allocation-start coverage and "
                "confirmed resource release are not established by this interface."
            ),
        },
        {
            "url": "https://www.kaggle.com/docs/efficient-gpu-usage",
            "locator": "GPU quota monitoring",
            "observation": "Check actual remaining accelerator quota before launch.",
        },
    ],
}

# This is an execution precondition, not a placeholder for an authorization flag.
# No currently verified platform adapter is available; even human authorization
# cannot make a notebook timer prove when the allocated GPU session started.
LAUNCH_GUARD = """ALLOW_GPU = False
HUMAN_QUOTA_AUTHORIZATION = None
PLATFORM_SESSION = None


def require_launch_ready():
    if not ALLOW_GPU or not HUMAN_QUOTA_AUTHORIZATION:
        raise RuntimeError("GPU quota authorization is absent; no remote execution")
    raise RuntimeError(
        "Launch blocked: authenticated allocation-start/deadline and confirmed "
        "Kaggle allocation termination are not implemented or verified. "
        "A first-cell timer, process exit or server.stop is insufficient."
    )


require_launch_ready()
"""

BOOTSTRAP = """import base64
import hashlib
import json
import sys
import uuid
from pathlib import Path

assert set(EMBEDDED_PAYLOAD) == set(EMBEDDED_HASHES)
EMBEDDED_ROOT = Path("/kaggle/working") / ("mostaza-phase2-" + str(uuid.uuid4()))
assert Path("/kaggle/input").is_dir(), "Kaggle only; no local model download"
EMBEDDED_ROOT.mkdir(exist_ok=False)
for name, encoded in EMBEDDED_PAYLOAD.items():
    assert not Path(name).is_absolute() and ".." not in Path(name).parts
    assert "\\\\" not in name and ":" not in name
    data = base64.b64decode(encoded, validate=True)
    assert hashlib.sha256(data).hexdigest() == EMBEDDED_HASHES[name]
    path = EMBEDDED_ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)
sys.path.insert(0, str(EMBEDDED_ROOT / "src"))
"""

PREFLIGHT = r"""import importlib
import os
import shutil
import subprocess
import time
import zipfile
from importlib.metadata import version

from mostaza.evaluation.contracts import MODEL, canonical_json, require, sha256
from mostaza.evaluation.runner import file_digest, snapshot_digest
from mostaza.evaluation.tasks import load_agent_tasks, validate_snapshot_history

# This cell is deliberately after the fail-closed quota/allocation guard.
DATA_DIR = Path("/kaggle/input/competitions/gemma-4-developer-agent")
WHEELHOUSE = Path("/kaggle/input/datasets/metric/gemma-4-developer-agent-wheelhouse")
MODEL_PATH = Path(f"/kaggle/input/models/google/gemma-4/other/{MODEL}/2")
require(sys.version_info[:2] == (3, 12), "Review changed Kaggle Python before running")
require(MODEL_PATH.is_dir(), "Pinned 31B revision 2 mount required")
resource_index = json.loads((EMBEDDED_ROOT / "resources/manifest.json").read_text())
cohort = json.loads((EMBEDDED_ROOT / "experiments/cohort.json").read_text())
selection = json.loads((EMBEDDED_ROOT / "selected-input-pins.json").read_text())
quota = json.loads((EMBEDDED_ROOT / "quota-proposal.json").read_text())
for entry in resource_index["resources"]:
    if entry["id"] in {"swegemma", "adk_submission", "adk_eval_core"}:
        path = WHEELHOUSE / Path(entry["path"]).name
    elif entry["id"] == "tasks":
        path = DATA_DIR / "tasks.jsonl"
    else:
        continue
    require(file_digest(path) == entry["sha256"], "Mounted official input changed")
for pin in selection:
    path = DATA_DIR / pin["official_file_path"]
    require(file_digest(path) == pin["sha256"], "Selected graph/snapshot/input changed")
visible = {
    task.instance_id: task for task in load_agent_tasks(DATA_DIR / "tasks.jsonl")
}
for selected in cohort["tasks"]:
    task = visible[selected["instance_id"]]
    require(
        task.repo == selected["repo"] and task.base_commit == selected["base_commit"],
        "Frozen task metadata mismatch",
    )
# Offline wheel installation from the attached organizer wheelhouse only.
wheel_temp = EMBEDDED_ROOT / "wheelhouse"
wheel_temp.mkdir(exist_ok=False)
for wheel in sorted(WHEELHOUSE.glob("*.whl")):
    if "cutlass" in wheel.name.lower():
        continue
    name = (
        wheel.name.replace("cu128", "+cu128") if "+" not in wheel.name else wheel.name
    )
    (wheel_temp / name).symlink_to(wheel)
os.environ.update(
    TRANSFORMERS_OFFLINE="1",
    VLLM_NO_USAGE_STATS="1",
    VLLM_WORKER_MULTIPROC_METHOD="spawn",
    LITELLM_TELEMETRY="False",
    LITELLM_LOCAL_MODEL_COST_MAP="True",
    OTEL_SDK_DISABLED="true",
    TRANSFORMERS_NO_TF="1",
    TRANSFORMERS_NO_FLAX="1",
)
subprocess.run(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--no-index",
        "--no-deps",
        "--force-reinstall",
        *map(str, sorted(wheel_temp.glob("*.whl"))),
    ],
    check=True,
    timeout=600,
)
for package, expected in [
    ("swegemma", "0.2.11"),
    ("adk-submission", "0.2.13"),
    ("adk-eval-core", "0.1.0"),
    ("google-adk", "1.36.1"),
]:
    require(version(package) == expected, "Pinned official package required")
torch = importlib.import_module("torch")
resolve_task_snapshot_paths = importlib.import_module(
    "swegemma.deduplication").resolve_task_snapshot_paths

require(
    torch.cuda.device_count() == 4
    and all(torch.cuda.get_device_name(i) == "NVIDIA L4" for i in range(4)),
    "L4 x4 required",
)
for selected in cohort["tasks"]:
    require(
        snapshot_digest(
            DATA_DIR / "snapshots", selected["instance_id"], selected["repo"], DATA_DIR
        )
        == selected["snapshot_sha256"],
        "Frozen snapshot reconstruction mismatch",
    )
    effective, base, delta = resolve_task_snapshot_paths(
        DATA_DIR / "snapshots", selected["instance_id"], selected["repo"]
    )
    require(base is None and delta is None, "Reviewed standalone snapshots required")
    history = next(
        pin
        for pin in selection
        if pin.get("instance_id") == selected["instance_id"]
        and pin["kind"] == "snapshot"
    )
    validate_snapshot_history(Path(effective), selected, history)
"""

EXECUTION = r"""import asyncio
from datetime import UTC, datetime

import litellm
from adk_submission import ModelRegistry, VllmConfig, VllmServer, compile_submission
from adk_submission import validate_directory
from adk_submission.yaml_loader import load_yaml
from swegemma.config import EvalConfig, build_submission_limits
from swegemma.evaluate import Evaluator
from swegemma.harness import verification
from swegemma.models import load_tasks

from mostaza.evaluation.contracts import validate_manifest
from mostaza.evaluation.runner import describe_runtime, validate_bindings
from mostaza.packaging import MAX_BYTES, MAX_FILES, collect_submission

require_launch_ready()  # Authorization alone never bypasses the allocation blocker.
# A verified allocation adapter must supply these before this loop can be enabled:
# absolute session-start/deadline, remaining quota, external termination watchdog,
# confirmed cancellation/normal completion and single-use batch authorization.
# No manufactured first-cell start time, timer receipt or quota estimate is accepted.
RUN_ROOT = Path("/kaggle/working/private-phase2-evidence") / str(uuid.uuid4())
RUN_ROOT.mkdir(parents=True, exist_ok=False)
limits, constraints = build_submission_limits()
agent_dirs, compiler_receipts = {}, {}
for configuration in quota["configurations"]:
    directory = RUN_ROOT / configuration / "submission"
    directory.mkdir(parents=True, exist_ok=False)
    archive_path = EMBEDDED_ROOT / "archives" / (configuration + ".zip")
    with zipfile.ZipFile(archive_path) as archive:
        entries = archive.infolist()
        require(
            len(entries) <= MAX_FILES
            and sum(e.file_size for e in entries) <= MAX_BYTES,
            "Oversized archive",
        )
        require(len({e.filename for e in entries}) == len(entries), "Duplicate archive")
        for entry in entries:
            name = entry.filename
            require(
                not entry.is_dir()
                and not Path(name).is_absolute()
                and ".." not in Path(name).parts
                and "\\" not in name
                and (entry.external_attr >> 16) & 0o170000 != 0o120000,
                "Unsafe archive member",
            )
            path = directory / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(archive.read(entry))
    require(
        set(collect_submission(directory)) == {e.filename for e in entries},
        "Unused/forbidden submission content",
    )
    validate_directory(directory, limits=limits)
    raw = load_yaml(directory / "agent.yaml", root_dir=directory, limits=limits)
    inert = ModelRegistry()
    inert.register(MODEL, "compiler-only-inert-model")

    def inert_tool(**kwargs):
        raise RuntimeError("Compiler-only tool must never execute")

    compile_submission(
        directory,
        {name: inert_tool for name in raw["tools"]},
        inert,
        limits=limits,
        generation_constraints=constraints,
    )
    compiler_receipts[configuration] = {
        "status": "PASS",
        "archive_sha256": file_digest(archive_path),
    }
    agent_dirs[configuration] = directory

litellm.drop_params = True
server_config = VllmConfig(
    model=str(MODEL_PATH),
    tensor_parallel_size=4,
    tool_call_parser="gemma4",
    reasoning_parser="gemma4",
    max_model_len=32768,
    dtype="bfloat16" if torch.cuda.is_bf16_supported() else "auto",
    gpu_memory_utilization=0.90,
    enable_auto_tool_choice=True,
    enable_lora=False,
    max_loras=1,
    max_lora_rank=128,
    scheduler_reserve_full_isl=False,
    startup_timeout=1200,
    host="127.0.0.1",
    port=8000,
    extra_args=[],
)
server = VllmServer(server_config)
acquired = []
# All six rows begin as NOT_RUN; errors/deadline preserve the unscheduled rows.
rows = [
    {
        "configuration_id": c,
        "instance_id": t["instance_id"],
        "status": "NOT_RUN",
        "reason": "Not scheduled",
        "result": None,
    }
    for c in quota["configurations"]
    for t in cohort["tasks"]
]


def export_sources():
    with (RUN_ROOT / "schedule.json").open("w") as stream:
        json.dump(rows, stream, sort_keys=True)
    inventory = [
        {"path": p.relative_to(RUN_ROOT).as_posix(), "sha256": file_digest(p)}
        for p in sorted(RUN_ROOT.rglob("*"))
        if p.is_file() and p.name != "source-inventory.json"
    ]
    with (RUN_ROOT / "source-inventory.json").open("w") as stream:
        json.dump(inventory, stream, sort_keys=True)


try:
    # PLATFORM_SESSION remains unavailable; this loop cannot start in this delivery.
    # Its future verified adapter must account for startup before this code runs.
    PLATFORM_SESSION.require_remaining(1200 + 6 * 600 + 300)
    server.start()
    models = server.create_model_registry(
        aliases=[MODEL], model_prefix="openai/", api_key="EMPTY"
    )
    tasks = {t.instance_id: t for t in load_tasks(DATA_DIR / "tasks.jsonl")}
    wheel_inventory = [
        {"name": p.name, "sha256": file_digest(p)}
        for p in sorted(WHEELHOUSE.glob("*.whl"))
    ]
    index = {p["id"]: p for p in resource_index["resources"]}
    resources = {
        "harness": {
            "version": "0.2.11",
            "sha256": index["swegemma"]["sha256"],
            "source": index["swegemma"]["url"],
        },
        "wheelhouse": {
            "version": "31",
            "sha256": sha256(canonical_json(wheel_inventory)),
            "source": index["swegemma"]["url"],
        },
        "dataset": {
            "version": "sha256:" + file_digest(DATA_DIR / "tasks.jsonl"),
            "sha256": file_digest(DATA_DIR / "tasks.jsonl"),
            "source": index["tasks"]["url"],
        },
    }
    for configuration in quota["configurations"]:
        output = RUN_ROOT / configuration / "results"
        config = EvalConfig(
            tasks_path=DATA_DIR / "tasks.jsonl",
            snapshots_dir=DATA_DIR / "snapshots",
            results_dir=output,
            submission_dir=agent_dirs[configuration],
            models=models,
            sandbox="subprocess",
            limits=limits,
            generation_constraints=constraints,
            concurrency=1,
            context_cache_config=None,
            events_compaction_config=None,
            graph_dir=str(DATA_DIR / "graphs"),
            embeddings_dir=str(DATA_DIR / "embeddings"),
            wheels_dir=DATA_DIR / "wheels",
            verbose=False,
            timeout_seconds=180,
            verification_timeout_seconds=300,
            max_tool_calls=30,
            max_time_minutes=3,
            max_turns=50,
        )
        runtime = describe_runtime(config, server_config)
        manifest = {
            "schema_version": 1,
            "experiment_id": configuration,
            "run_id": str(uuid.uuid4()),
            "arm": configuration[:2],
            "run_kind": "real_kaggle",
            "timestamp": datetime.now(UTC).isoformat(),
            "code_commit": PLATFORM_SESSION.code_commit,
            "working_tree_sha256": sha256(canonical_json(EMBEDDED_HASHES)),
            "config_sha256": runtime["config_sha256"],
            "archive_sha256": file_digest(
                EMBEDDED_ROOT / "archives" / (configuration + ".zip")
            ),
            "model": MODEL,
            "resources": resources,
            "cohort": cohort["tasks"],
            "inference": runtime["inference"],
            "budgets": runtime["budgets"],
            "environment": {
                "platform": "kaggle",
                "gpu_count": 4,
                "gpu_model": "NVIDIA L4",
                "snapshot_validation": {
                    p["instance_id"]: p for p in selection if p["kind"] == "snapshot"
                },
                "embedded_input_hashes": EMBEDDED_HASHES,
            },
            "source_run_id": PLATFORM_SESSION.run_url,
            "limitations": ["Exploratory cohort; no significance or superiority claim"],
        }
        validate_manifest(manifest)
        validate_bindings(
            config,
            manifest,
            server=server,
            archive_path=EMBEDDED_ROOT / "archives" / (configuration + ".zip"),
            wheelhouse_dir=WHEELHOUSE,
        )
        with (RUN_ROOT / configuration / "manifest.json").open("xb") as stream:
            stream.write(canonical_json(manifest))
        evaluator = Evaluator(config)
        try:
            for i, selected in enumerate(cohort["tasks"], 1):
                row = next(
                    r
                    for r in rows
                    if r["configuration_id"] == configuration
                    and r["instance_id"] == selected["instance_id"]
                )
                # 180 generation + 300 verification + 120 orchestration + 300 export.
                if not scheduling_allowed(time.time(), PLATFORM_SESSION.deadline_epoch):
                    row["reason"] = (
                        "Insufficient worst-case allowance before session deadline"
                    )
                    continue
                row["status"], row["reason"] = "ERROR", "Attempt interrupted; no retry"
                export_sources()
                task = evaluator._hydrate_task_from_secret(
                    tasks[selected["instance_id"]]
                )
                result = await asyncio.wait_for(
                    evaluator.evaluate_task(task=task, task_index=i, total_tasks=3),
                    timeout=600,
                )
                if not result.trace_path and result.trace is not None:
                    result.trace_path = verification.save_trace_artifact(
                        result.trace, output, task.instance_id
                    )
                raw = result.model_dump(mode="json", exclude={"trace"})
                strip_patch = verification.strip_protected_files_from_patch
                raw["_mostaza"] = {
                    "schema_version": 1,
                    "effective_agent_patch": strip_patch(
                        result.agent_patch, extra_protected_paths=task.test_files
                    ),
                    "original_patch_sha256": sha256(result.agent_patch.encode()),
                }
                path = output / f"official-result-{i:04d}.json"
                with path.open("xb") as stream:
                    stream.write(canonical_json(raw))
                row.update(
                    status="ACQUIRED",
                    reason="Native result; resolution pending replay",
                    result=path.relative_to(RUN_ROOT).as_posix(),
                )
                export_sources()
        finally:
            evaluator.docker.cleanup_all()
finally:
    try:
        log = Path(server.log_path)
        if log.is_file():
            shutil.copyfile(log, RUN_ROOT / "vllm-server.log")
    finally:
        try:
            server.stop()
        finally:
            export_sources()
            # Must release allocation even on exceptions, not only stop vLLM.
            # A notebook-local callback is NOT a verified termination guarantee.
            PLATFORM_SESSION.terminate_and_confirm()
"""


def scheduling_allowed(now_epoch: float, deadline_epoch: float) -> bool:
    """AC-7: full task plus export must fit the allocation-anchored deadline."""
    import math

    if not math.isfinite(now_epoch) or not math.isfinite(deadline_epoch):
        return False
    # 180 generation + 300 verification + 120 overhead + 300 export.
    return deadline_epoch - now_epoch >= 900


def _cell(kind: str, source: str) -> dict[str, Any]:
    cell: dict[str, Any] = {
        "cell_type": kind,
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }
    if kind == "code":
        ast.parse(source, feature_version=(3, 12))
        cell.update(execution_count=None, outputs=[])
    return cell


def payload_files(root: Path) -> dict[str, bytes]:
    """Exact positive allowlist; no raw task data, diagnosis or verifier material."""
    payload = {name: retained_path(root, name).read_bytes() for name in HOST_MODULES}
    for name, content in payload.items():
        ast.parse(content.decode(), filename=name, feature_version=(3, 12))
    cohort = json.loads(retained_path(root, "experiments/cohort.json").read_text())
    require(tuple(t["instance_id"] for t in cohort["tasks"]) == TASKS, "Cohort changed")
    payload["experiments/cohort.json"] = canonical_json(cohort)
    payload["resources/manifest.json"] = retained_path(
        root, "resources/manifest.json"
    ).read_bytes()
    # Only asset pins/history checks from the pre-existing pre-outcome review.
    legacy_review = json.loads(
        retained_path(
            root,
            "docs/implementation/evidence/mostaza-phase1-foundation/resource-review.json",
        ).read_text()
    )
    payload["selected-input-pins.json"] = canonical_json(
        legacy_review["selected_resources"]
    )
    payload["quota-proposal.json"] = canonical_json(QUOTA)
    with tempfile.TemporaryDirectory(prefix="mostaza-phase2-payload-") as temporary:
        for config in CONFIGURATIONS:
            files = configuration_files(root, config)
            path = Path(temporary) / f"{config}.zip"
            archive_bytes(files, path)
            payload[f"archives/{config}.zip"] = path.read_bytes()
    return payload


def build_notebook(root: Path) -> bytes:
    payload = payload_files(root)
    hashes = {name: sha256(data) for name, data in sorted(payload.items())}

    def literal_mapping(name: str, values: dict[str, str]) -> str:
        lines = [name + " = {"]
        for key, value in values.items():
            lines.append("    " + repr(key) + ": (")
            lines.extend(
                "        " + repr(value[i : i + 68]) for i in range(0, len(value), 68)
            )
            lines.append("    ),")
        return "\n".join([*lines, "}", ""])

    literals = literal_mapping(
        "EMBEDDED_PAYLOAD",
        {
            name: base64.b64encode(data).decode()
            for name, data in sorted(payload.items())
        },
    ) + literal_mapping("EMBEDDED_HASHES", hashes)
    imports, bootstrap = BOOTSTRAP.split("assert set", 1)
    execution = EXECUTION.replace(
        "require_launch_ready()  # Authorization",
        inspect.getsource(scheduling_allowed)
        + "\nrequire_launch_ready()  # Authorization",
        1,
    )
    notebook: dict[str, Any] = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python", "version": "3.12.13"},
            "kaggle": {"isInternetEnabled": False, "isGpuEnabled": False},
            "mostaza": {
                "kind": "unexecuted_phase2_preparation",
                "payload_sha256": hashes,
                "quota": QUOTA,
                "platform_enforcement": PLATFORM,
                "generator_sources": {
                    "src/mostaza/evaluation/phase2.py": sha256(
                        Path(__file__).read_bytes()
                    )
                },
            },
        },
        "cells": [
            _cell(
                "markdown",
                "# Mostaza phase 2: private offline B180 preparation\n\n"
                "Six evaluations, E0-B180/E1-B180 on the frozen three tasks. "
                "No GPU execution is authorized. Keep accelerator disabled and "
                "notebook private. "
                "Obtain a separate human decision and a verified allocation "
                "deadline/termination "
                "mechanism before any GPU start. All new outcomes are NOT_RUN.\n",
            ),
            _cell("code", LAUNCH_GUARD),
            _cell("code", imports + literals + "assert set" + bootstrap),
            _cell("code", PREFLIGHT),
            _cell(
                "markdown",
                "## Prepared official execution loop (blocked)\n\n"
                "The pinned native compiler, one VllmServer and "
                "Evaluator.evaluate_task "
                "are used below. Runtime records, traces and generated patches remain "
                "private, outside submissions. No reference answers or diagnostics "
                "enter prompts. "
                "The external platform watchdog must cover cold start and all failure"
                " paths; "
                "server.stop alone does not release Kaggle GPU quota.\n",
            ),
            _cell("code", execution),
        ],
    }
    for i, cell in enumerate(notebook["cells"]):
        cell["id"] = f"phase2-{i}"
    # The unchanged repository gate formats/lints notebooks too. Use the pinned
    # host formatter to make generation match that exact policy, without execution.
    command = [str(root / ".venv/bin/ruff")]
    sorted_code = subprocess.run(
        [
            *command,
            "check",
            "--select",
            "I",
            "--fix",
            "--stdin-filename",
            NOTEBOOK,
            "-",
        ],
        input=canonical_json(notebook),
        capture_output=True,
        check=True,
        timeout=30,
    ).stdout
    formatted = subprocess.run(
        [*command, "format", "--stdin-filename", NOTEBOOK, "-"],
        input=sorted_code,
        capture_output=True,
        check=True,
        timeout=30,
    ).stdout
    return canonical_json(json.loads(formatted))


def check_notebook(root: Path) -> dict[str, str]:
    """Compare all code/metadata/decoded payload bytes to current explicit inputs."""
    expected = build_notebook(root)
    require(
        retained_path(root, NOTEBOOK).read_bytes() == expected,
        "Notebook/source/payload provenance mismatch; regenerate locally",
    )
    notebook = json.loads(expected)
    values: dict[str, Any] = {}
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        for node in ast.parse("".join(cell["source"])).body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.startswith(
                        "EMBEDDED_"
                    ):
                        if target.id in {"EMBEDDED_PAYLOAD", "EMBEDDED_HASHES"}:
                            require(
                                target.id not in values, "Duplicate payload assignment"
                            )
                            values[target.id] = ast.literal_eval(node.value)
    payload = payload_files(root)
    require(
        set(values["EMBEDDED_PAYLOAD"]) == set(payload), "Unexpected notebook payload"
    )
    for name, data in payload.items():
        require(
            base64.b64decode(values["EMBEDDED_PAYLOAD"][name], validate=True) == data,
            "Decoded notebook payload differs from source",
        )
    hashes: dict[str, str] = values["EMBEDDED_HASHES"]
    require(
        hashes == {name: sha256(data) for name, data in payload.items()},
        "Notebook payload digest mismatch",
    )
    return hashes


def pending_rows() -> list[dict[str, Any]]:
    return [
        {
            "configuration_id": c,
            "arm": c[:2],
            "instance_id": task,
            "status": "NOT_RUN",
            "reason": "Separate GPU quota authorization absent; "
            "allocation deadline/termination not verified",
            "metrics": None,
            "patch": None,
            "verification": None,
            "native_acquisition": None,
        }
        for c in CONFIGURATIONS
        for task in TASKS
    ]


def operator_commands(root: Path) -> dict[str, list[str]]:
    uv = str(root / ".tools/uv/bin/uv")
    python = [uv, "run", "--project", str(root), "--frozen", "--no-sync", "python"]
    return {
        "prepare": python + [str(root / "scripts/prepare_phase2.py")],
        "check": python
        + [
            str(root / "scripts/check_phase2.py"),
            "--check",
            "--cohort",
            str(root / "experiments/cohort.json"),
            "--evidence-dir",
            str(root / EVIDENCE),
        ],
        "repository_validation": ["bash", str(root / "scripts/validate.sh")],
    }


def readiness(root: Path) -> dict[str, Any]:
    hashes = check_notebook(root)
    return {
        "schema_version": 1,
        "kind": "local_phase2_readiness",
        "local_preparation": "READY",
        "real_evaluation": "NOT_RUN",
        "gpu_authorization": "ABSENT",
        "platform_enforcement": PLATFORM,
        "quota_proposal": QUOTA,
        "notebook": {
            "path": NOTEBOOK,
            "sha256": sha256((root / NOTEBOOK).read_bytes()),
            "payload_sha256": hashes,
        },
        "configuration_sources": {
            config: {
                "manifest_sha256": sha256(
                    (root / "experiments" / config / "manifest.json").read_bytes()
                ),
                "members_sha256": {
                    name: sha256(data)
                    for name, data in configuration_files(root, config).items()
                },
            }
            for config in VARIANTS
        },
        "source_sha256": {
            name: sha256(retained_path(root, name).read_bytes())
            for name in (
                *HOST_MODULES,
                "src/mostaza/evaluation/phase2.py",
                "scripts/prepare_phase2.py",
                "scripts/check_phase2.py",
            )
        },
        "operator_commands": operator_commands(root),
        "records": pending_rows(),
        "real_acquisition": None,
    }


def comparison(diagnosis: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "kind": "historical_diagnosis_and_pending_phase2",
        "historical_source_sha256": sha256(canonical_json(diagnosis)),
        "historical_evidence": diagnosis["historical_evidence"],
        "historical_tasks": [
            {
                key: task[key]
                for key in (
                    "arm",
                    "instance_id",
                    "normalized_status",
                    "timeout",
                    "metrics",
                    "generated_patch",
                    "effective_patch",
                    "verification",
                    "requests_postrun_finding",
                )
            }
            for task in diagnosis["tasks"]
        ],
        "phase2": {
            "status": "NOT_RUN",
            "records": pending_rows(),
            "measured_pairs": 0,
            "planned_pairs": 3,
            "outcome_delta": None,
            "retrieval_adherence": None,
            "reason": "No phase-2 model execution or native acquisition",
        },
        "limitations": diagnosis["limitations"]
        + [
            "B180 readiness is not phase-2 real benchmark completion.",
            "B300 and E1-R180 are separate later six-run quota decisions.",
            "Native cost_usd=0 is not a quota measurement or unlimited allowance.",
        ],
    }


def report_markdown(ready: dict[str, Any], compared: dict[str, Any]) -> str:
    lines = [
        "# Phase-2 preparation and historical diagnosis",
        "",
        "Local preparation: READY. Phase-2 real evaluation: NOT_RUN. "
        "Separate GPU authorization is absent. No phase-2 outcomes or retrieval "
        "benefit are claimed.",
        "",
        "## Historical observations",
        "",
        "All six phase-1 sessions exhausted the 60-second budget. Each arm had "
        "PASS 0, FAIL 1, ERROR 2. Requests generated only reproduction scripts; "
        "their caught assertions and zero shell exits did not establish a fix. "
        "Official verification still failed. FastAPI/Rich had no patch. E1 used "
        "neither similarity nor graphs; E0 made one similarity attempt whose "
        "backend remains unproven. These observations justify a small matched "
        "three-minute/30-call pilot, not an efficacy conclusion.",
        "",
        "Historical native sources, patch findings and detailed metric coverage "
        "are hash-bound in trace-diagnosis.json and comparison.json. Event gaps "
        "do not isolate model/tool wall time. Unknown telemetry remains null.",
        "",
        "## Exact quota proposal (not authorized)",
        "",
        "Six evaluations: E0-B180 and E1-B180, each on requests_7205, "
        "fastapi_15589, rich_3061 in that order. One private offline NVIDIA L4 x4 "
        "session; concurrency 1; zero retries. Each generation: 180 seconds, "
        "3 minutes, 30 charged tools, 50 turns; verification: 300 seconds. "
        "Generation upper bound 18 minutes; verification upper bound 30 minutes. "
        "Total ceiling 120 wall-clock minutes from GPU allocation start, "
        "including cold start/loading/compiler/export: at most 8 GPU-device-hours "
        "and $0 paid purchases. Check the actual remaining platform quota and "
        "its accounting units before launch; quota units may differ from "
        "device-hours. Reserve 120 seconds task overhead and 300 seconds export; "
        "stop scheduling unless the full remaining per-task allowance fits.",
        "",
        "## Technical launch blocker",
        "",
        PLATFORM["reason"],
        "",
        "The official Kaggle CLI exposes a run timeout, but verified coverage "
        "of allocation startup and reliable resource termination are unavailable "
        "for this prepared offline route. No allocation clock/quota was observed. "
        "The notebook launch guard therefore refuses even a manually set "
        "authorization flag. A verified external platform watchdog, remaining "
        "quota and allocation start/deadline/termination evidence are required "
        "before enabling execution. Generic GPU approval cannot waive this "
        "technical precondition. No remote notebook was pushed or started.",
        "",
        "Official interfaces: [Kaggle kernels CLI]("
        + PLATFORM["sources"][0]["url"]
        + "), [Kaggle GPU quota]("
        + PLATFORM["sources"][1]["url"]
        + ").",
        "",
        "## Reproduce local preparation",
        "",
        "```sh",
    ]
    for command in ready["operator_commands"].values():
        lines.append(shlex.join(command))
    lines += [
        "```",
        "",
        "The preparation command writes only the generated notebook "
        "and declared readiness/comparison/report evidence. The checker is "
        "read-only: it replays authentic historical evidence, recompiles all "
        "five new closures twice and verifies exact notebook/source/payload "
        "bytes. It does not start Kaggle, install a model or infer outcomes.",
        "",
        "B300 is proposed only if B180 is still time/tool constrained before "
        "implementation/verification. E1-R180 requires analyzed budget calibration "
        "and a new contemporaneous E0-B180 baseline. Each is a distinct later "
        "six-run batch with a separate 120-minute/8-device-hour/$0 authorization; "
        "none is launched automatically. Preserve failures; no success selection.",
        "",
        "## Comparison limitations",
        "",
    ]
    lines += [f"- {line}" for line in compared["limitations"]]
    return "\n".join(lines) + "\n"
