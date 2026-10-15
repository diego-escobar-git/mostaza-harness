"""Actual treatment isolation and prompt invariants; no policy adherence claim."""

import hashlib
import json
from pathlib import Path

import yaml

from mostaza.packaging import IncludeLoader, collect_submission

ROOT = Path(__file__).resolve().parents[2]


def manifest(arm: str) -> dict:
    name = "E0-baseline" if arm == "E0" else "E1-hybrid-retrieval"
    return json.loads((ROOT / "experiments" / name / "manifest.json").read_text())


def test_ac2_ac4_actual_treatment_isolation() -> None:
    e0, e1 = manifest("E0"), manifest("E1")
    assert e1["status"] == "ready" and e1["ready_for_evaluation"] is True
    assert e1["treatment"] == "exploration_instructions_only"
    for field in (
        "model",
        "generation_parameters",
        "tools",
        "budgets",
        "repair_policy",
        "environment",
        "shared_conditions",
        "shared_conditions_sha256",
        "baseline_source_sha256",
        "source_prompt_sha256",
        "source_sampling_sha256",
        "source_eval_sha256",
    ):
        assert e0[field] == e1[field], field
    config0, config1 = [
        collect_submission(ROOT / "submission", m["prompt"]) for m in (e0, e1)
    ]
    yaml0, yaml1 = [
        yaml.load(c["agent.yaml"], Loader=IncludeLoader) for c in (config0, config1)
    ]
    assert yaml0.pop("instruction").path == e0["prompt"]
    assert yaml1.pop("instruction").path == e1["prompt"]
    assert yaml0 == yaml1
    assert config0["eval_config.yaml"] == config1["eval_config.yaml"]
    assert yaml0["generate_content_config"] == e0["generation_parameters"]
    assert yaml0["tools"] == e0["tools"]
    assert yaml.safe_load(config0["eval_config.yaml"])["evaluation"] == e0["budgets"]
    prompt0, prompt1 = [c[m["prompt"]] for c, m in ((config0, e0), (config1, e1))]
    for prompt, m in ((prompt0, e0), (prompt1, e1)):
        assert hashlib.sha256(prompt).hexdigest() == m["prompt_sha256"]
    assert hashlib.sha256(prompt0).hexdigest() == e1["baseline_prompt_sha256"]
    prefix0, tail0 = prompt0.split(b"### 1. ", 1)
    prefix1, tail1 = prompt1.split(b"### 1. ", 1)
    explore0, suffix0 = tail0.split(b"### 2. Implement the Solution Directly", 1)
    explore1, suffix1 = tail1.split(b"### 2. Implement the Solution Directly", 1)
    assert prefix0 == prefix1 and suffix0 == suffix1
    assert explore0 != explore1
    shared_suffix = e0["derivation"]["changes"][-1]["added_text"].encode()
    assert prompt0.endswith(shared_suffix) and prompt1.endswith(shared_suffix)
    assert e1["validation"]["real_gemma_execution"] == "NOT_RUN"


def test_ac2_ac3_ac6_prompt_records_native_policy_limits() -> None:
    e1 = manifest("E1")
    assert e1["retrieval_policy"] == {
        "max_neighbors": 10,
        "similarity_k": 5,
        "default_graph_depth": 1,
        "two_hop_requires_evidence": True,
        "parameters_basis": "conservative pilot policy, not learned optima",
    }
    prompt = (ROOT / "submission" / e1["prompt"]).read_text()
    for requirement in (
        "max_neighbors=10",
        "k=5",
        "one-hop",
        "Two-hop expansion requires",
        "Disambiguate ambiguous suffixes lexically",
        "visited-symbol",
        "Stop unproductive searches",
        "get_status",
        "minimum sufficient code",
        "not establish that a real agent",
        "Missing graph/embedding resources",
        "lexical fallback",
        "run_command",
    ):
        assert requirement in prompt


def test_phase2_ac1_calibration_pair_rendered_conditions() -> None:
    from mostaza.packaging import configuration_files, load_manifest

    for family in ("B180", "B300"):
        ids = [f"E0-{family}", f"E1-{family}"]
        manifests = [load_manifest(ROOT, config) for config in ids]
        assert manifests[0]["shared_conditions"] == manifests[1]["shared_conditions"]
        closures = [configuration_files(ROOT, config) for config in ids]
        agents = [
            yaml.load(files["agent.yaml"], Loader=IncludeLoader) for files in closures
        ]
        for agent in agents:
            agent.pop("instruction")
        assert agents[0] == agents[1]
        assert closures[0]["eval_config.yaml"] == closures[1]["eval_config.yaml"]
        for m, files in zip(manifests, closures, strict=True):
            assert (
                files[m["prompt"]]
                == (ROOT / "submission" / manifest(m["arm"])["prompt"]).read_bytes()
            )


def test_phase2_ac6_recovery_exact_exploration_diff() -> None:
    import difflib

    from mostaza.packaging import configuration_files, load_manifest

    original = configuration_files(ROOT, "E1-B180")
    recovered = configuration_files(ROOT, "E1-R180")
    m = load_manifest(ROOT, "E1-R180")
    a = original["prompts/hybrid-retrieval.md"]
    b = recovered["prompts/hybrid-recovery.md"]
    assert a.split(b"### 1. ")[0] == b.split(b"### 1. ")[0]
    assert (
        a.split(b"### 2. Implement the Solution Directly")[1]
        == b.split(b"### 2. Implement the Solution Directly")[1]
    )
    assert original["eval_config.yaml"] == recovered["eval_config.yaml"]
    assert m["exploration_diff"] == "".join(
        difflib.unified_diff(
            a.decode().splitlines(keepends=True),
            b.decode().splitlines(keepends=True),
            fromfile="prompts/hybrid-retrieval.md",
            tofile="prompts/hybrid-recovery.md",
        )
    )
    assert m["calibration_eligible"] is False
    for phrase in (
        b"After unsuccessful exact lexical lookup",
        b"fully qualified symbol",
        b"k=5",
        b"max_neighbors=10",
        b"one-hop",
        b"second hop requires",
        b"never force",
        b"Stop",
        b"lexical fallback",
    ):
        assert phrase in b
