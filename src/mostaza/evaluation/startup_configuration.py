"""Serial serving profile and allowlisted startup receipts; no model imports."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import subprocess
import sys
from collections.abc import Mapping, MutableMapping
from pathlib import Path
from typing import Any

PROFILE_ID = "serial-memory-v3"
ENVIRONMENT = {
    "TRANSFORMERS_OFFLINE": "1",
    "TRANSFORMERS_NO_TF": "1",
    "TRANSFORMERS_NO_FLAX": "1",
    "VLLM_NO_USAGE_STATS": "1",
    "VLLM_WORKER_MULTIPROC_METHOD": "spawn",
    "VLLM_ENGINE_READY_TIMEOUT_S": "1200",
    "VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS": "1",
    "NCCL_DEBUG": "WARN",
    "PYTORCH_ALLOC_CONF": "expandable_segments:True",
    "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
    "LITELLM_LOCAL_MODEL_COST_MAP": "True",
    "LITELLM_TELEMETRY": "False",
    "LITELLM_LOG": "WARNING",
    "OTEL_SDK_DISABLED": "true",
    "OTEL_PYTHON_DISABLED": "true",
}
EXTRA_ARGS = ["--max-num-seqs", "1"]


def apply_environment(
    environ: MutableMapping[str, str] | None = None,
    modules: Mapping[str, Any] | None = None,
) -> dict[str, str | None]:
    """Apply before torch/vLLM imports; both allocator names have identical values."""
    loaded = sys.modules if modules is None else modules
    if any(
        n == "torch" or n.startswith(("torch.", "vllm.")) or n == "vllm" for n in loaded
    ):
        raise RuntimeError("Serving environment must precede torch/vLLM imports")
    target = os.environ if environ is None else environ
    previous = {key: target.get(key) for key in ENVIRONMENT}
    target.update(ENVIRONMENT)
    return previous


def memory_observation(observer: Any, stage: str) -> None:
    """Driver point sample in MiB; unavailable readings never become zero or peaks."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,memory.total,memory.used,memory.free",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        rows = []
        for line in result.stdout.splitlines():
            index, total, used, free = (int(value.strip()) for value in line.split(","))
            if min(index, total, used, free) < 0:
                raise ValueError("Invalid driver reading")
            rows.append({"index": index, "total": total, "used": used, "free": free})
        if len(rows) != 4 or {row["index"] for row in rows} != {0, 1, 2, 3}:
            raise ValueError("Four distinct GPU readings required")
        observer.event(
            "memory.point_sample", stage=stage, unit="MiB", gpus=rows, reason=None
        )
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        observer.event(
            "memory.point_sample",
            stage=stage,
            unit="MiB",
            gpus=None,
            reason=type(error).__name__,
        )


def package_fingerprints() -> dict[str, Any]:
    """Record installed package identities without importing torch or vLLM."""
    packages: dict[str, Any] = {}
    for package in ("torch", "vllm", "swegemma", "adk-submission", "google-adk"):
        try:
            packages[package] = {
                "version": importlib.metadata.version(package),
                "reason": None,
            }
        except importlib.metadata.PackageNotFoundError:
            packages[package] = {"version": None, "reason": "distribution unavailable"}
    sources = {}
    for name in ("envs.py", "v1/worker/gpu_worker.py", "v1/worker/gpu_model_runner.py"):
        try:
            path = Path(
                str(importlib.metadata.distribution("vllm").locate_file("vllm/" + name))
            )
            sources[name] = {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "reason": None,
            }
        except (OSError, importlib.metadata.PackageNotFoundError):
            sources[name] = {"sha256": None, "reason": "installed source unavailable"}
    return {"packages": packages, "vllm_sources": sources, "python": sys.version}


def observe_server_environment(server: Any, observer: Any) -> None:
    """Observe the mapping returned by the native builder on the real start path."""
    config = server.config
    expected = {
        "tensor_parallel_size": 4,
        "max_model_len": 32768,
        "gpu_memory_utilization": 0.90,
        "dtype": "bfloat16",
        "extra_args": EXTRA_ARGS,
    }
    actual = {key: getattr(config, key) for key in expected}
    if actual != expected:
        raise ValueError("Server differs from the common serial-memory-v3 profile")
    native_build_env = server.build_env

    def build_env() -> dict[str, str]:
        environment: dict[str, str] = native_build_env()
        selected = {key: environment.get(key) for key in ENVIRONMENT}
        if selected != ENVIRONMENT:
            raise RuntimeError("Native child environment differs from serving profile")
        receipt = {
            "profile_id": PROFILE_ID,
            "coverage": (
                "allowlisted actual native build_env return; "
                "not allocator runtime state"
            ),
            "environment": selected,
            "config": actual,
            "installed": package_fingerprints(),
            "allocator_runtime_state": None,
            "allocator_runtime_state_reason": "No worker-internal allocator probe",
        }
        with (observer.root / "startup-configuration.json").open("x") as stream:
            json.dump(receipt, stream, sort_keys=True, indent=2)
            stream.write("\n")
        observer.event(
            "server.environment.captured", profile_id=PROFILE_ID, environment=selected
        )
        memory_observation(observer, "before_server_spawn")
        return environment

    server.build_env = build_env
