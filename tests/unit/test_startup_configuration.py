"""CPU-only startup profile and receipt coverage; no Kaggle client or model imports."""

import ast
import hashlib
import json
import subprocess
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from mostaza.evaluation import startup_configuration as configuration
from mostaza.evaluation.startup_candidate import (
    NOTEBOOK,
    POLICY,
    PREVIOUS_SHA256,
    build_notebook,
    validate_receipt,
)

ROOT = Path(__file__).resolve().parents[2]


def receipt():
    return {
        "policy": POLICY.copy(),
        "approved": True,
        "approval_id": "LOCAL-ONLY-FIXTURE",
        "single_use_id": "00000000-0000-4000-8000-000000000001",
        "ref": "diegofescobar/mostaza-b180-" + "0" * 32,
        "code_commit": "0" * 40,
        "t0_epoch": time.time(),
        "quota_observed_epoch": time.time() - 1,
        "remaining_quota_seconds": 28800,
        "reserved_quota_seconds": 0,
        "active_events": 0,
        "prelaunch_latest_versions_terminal": True,
        "prelaunch_quota_stable": True,
    }


def test_candidate_preserves_history_payloads_and_requires_new_approval():
    original = ROOT / "notebooks/mostaza-phase2-observed.ipynb"
    assert hashlib.sha256(original.read_bytes()).hexdigest() == PREVIOUS_SHA256
    notebook = json.loads(build_notebook(ROOT))
    old = json.loads(original.read_bytes())
    assert notebook["cells"][2] == old["cells"][2]
    assert (
        notebook["metadata"]["mostaza"]["payload_sha256"]
        == old["metadata"]["mostaza"]["payload_sha256"]
    )
    assert notebook["metadata"]["kaggle"] == {
        "isGpuEnabled": False,
        "isInternetEnabled": False,
    }
    assert build_notebook(ROOT) == (ROOT / NOTEBOOK).read_bytes()
    with pytest.raises(RuntimeError, match="authorization is absent"):
        exec("".join(notebook["cells"][1]["source"]), {})
    for cell in notebook["cells"]:
        assert not cell.get("outputs") and cell.get("execution_count") is None
        if cell["cell_type"] == "code":
            ast.parse("".join(cell["source"]), feature_version=(3, 12))
    code = "".join(notebook["cells"][-1]["source"])
    for unchanged in (
        "timeout_seconds=180",
        "verification_timeout_seconds=300",
        "max_tool_calls=30",
        "max_time_minutes=3",
        "max_turns=50",
        "concurrency=1",
    ):
        assert unchanged in code
    assert 'extra_args=["--max-num-seqs", "1"]' in code
    assert code.index('"observe_server_environment"') < code.index(
        '"start_observed_server"'
    )
    assert '"memory_observation"' in code


def test_new_receipt_and_guard_reject_consumed_policy_and_invalid_preflight():
    value = receipt()
    validate_receipt(value)
    bound = json.loads(build_notebook(ROOT, value))
    assert (
        bound["metadata"]["mostaza"]["observed_preparation"]["authorization"]
        == "LOCAL-ONLY-FIXTURE"
    )
    for key, invalid in (
        ("approved", False),
        ("active_events", None),
        ("reserved_quota_seconds", 1),
        ("quota_observed_epoch", 0),
        ("policy", {**POLICY, "id": "B180-observed-v2"}),
        ("policy", {**POLICY, "serving_profile": "different"}),
    ):
        with pytest.raises(RuntimeError):
            validate_receipt({**value, key: invalid})
    with pytest.raises(ValueError):
        validate_receipt({**value, "unexpected_secret": "secret"})


def test_environment_precedes_imports_and_overrides_both_allocator_aliases():
    environment = {
        "PYTORCH_ALLOC_CONF": "backend:cudaMallocAsync",
        "OPENAI_API_KEY": "secret",
    }
    before = configuration.apply_environment(environment, {})
    assert before["PYTORCH_ALLOC_CONF"] == "backend:cudaMallocAsync"
    assert (
        environment["PYTORCH_ALLOC_CONF"]
        == environment["PYTORCH_CUDA_ALLOC_CONF"]
        == "expandable_segments:True"
    )
    assert environment["OPENAI_API_KEY"] == "secret"
    for module in ("torch", "torch.cuda", "vllm", "vllm.envs"):
        with pytest.raises(RuntimeError):
            configuration.apply_environment({}, {module: object()})
    notebook = json.loads(build_notebook(ROOT))
    assert 'STARTUP_CONFIGURATION["apply_environment"]()' in "".join(
        notebook["cells"][1]["source"]
    )
    assert 'torch = importlib.import_module("torch")' in "".join(
        notebook["cells"][3]["source"]
    )


def test_actual_native_environment_mapping_is_observed_and_returned_unchanged(
    tmp_path, monkeypatch
):
    events = []
    observer = SimpleNamespace(
        root=tmp_path, event=lambda *a, **kw: events.append((a, kw))
    )
    monkeypatch.setattr(configuration, "memory_observation", lambda *args: None)
    environment = {**configuration.ENVIRONMENT, "OPENAI_API_KEY": "DO_NOT_RECORD"}
    server = SimpleNamespace(
        config=SimpleNamespace(
            tensor_parallel_size=4,
            max_model_len=32768,
            gpu_memory_utilization=0.90,
            dtype="bfloat16",
            extra_args=configuration.EXTRA_ARGS.copy(),
        ),
        build_env=lambda: environment,
    )
    configuration.observe_server_environment(server, observer)
    assert not (tmp_path / "startup-configuration.json").exists()
    assert server.build_env() is environment
    saved = (tmp_path / "startup-configuration.json").read_text()
    assert "DO_NOT_RECORD" not in saved and "OPENAI_API_KEY" not in saved
    assert json.loads(saved)["environment"] == configuration.ENVIRONMENT
    assert json.loads(saved)["allocator_runtime_state"] is None
    # Environment drift fails before any spawn, without silently repairing it.
    environment["VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS"] = "0"
    with pytest.raises(RuntimeError, match="child environment"):
        server.build_env()


@pytest.mark.parametrize(
    "output", [None, "0, 22528, 100, 22428\n", "0, 22528, 100, 22428\n" * 4]
)
def test_unavailable_or_incomplete_memory_never_becomes_zero(output, monkeypatch):
    def run(*args, **kwargs):
        if output is None:
            raise FileNotFoundError("CPU fixture")
        return SimpleNamespace(stdout=output)

    events = []
    monkeypatch.setattr(configuration.subprocess, "run", run)
    configuration.memory_observation(
        SimpleNamespace(event=lambda *a, **kw: events.append(kw)), "test"
    )
    assert events[0]["gpus"] is None and events[0]["reason"]


def test_memory_units_are_point_samples_with_bounded_driver_query(monkeypatch):
    def run(command, **kwargs):
        assert command[0] == "nvidia-smi" and kwargs["timeout"] == 5
        return SimpleNamespace(
            stdout="".join(f"{i}, 22528, 100, 22428\n" for i in range(4))
        )

    events = []
    monkeypatch.setattr(configuration.subprocess, "run", run)
    configuration.memory_observation(
        SimpleNamespace(event=lambda *a, **kw: events.append(kw)), "test"
    )
    assert events[0]["unit"] == "MiB" and len(events[0]["gpus"]) == 4


def test_cpu_official_builder_accepts_cli_capacity_and_preserves_environment():
    check = subprocess.run(
        [
            str(ROOT / ".tools/official/bin/python"),
            str(ROOT / "scripts/check_startup_configuration.py"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    assert json.loads(check.stdout)["gpu_model_started"] is False
