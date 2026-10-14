"""AC-7/AC-8/AC-9/AC-10: local-only defaults, provenance and finite limits."""

import ast
import base64
import json
from pathlib import Path

import pytest

from mostaza.evaluation.phase2 import (
    CONFIGURATIONS,
    HOST_MODULES,
    LAUNCH_GUARD,
    NOTEBOOK,
    QUOTA,
    TASKS,
    build_notebook,
    check_notebook,
    operator_commands,
    payload_files,
    pending_rows,
    scheduling_allowed,
)

ROOT = Path(__file__).resolve().parents[2]


def test_ac7_launch_stops_before_import_install_or_model_even_with_manual_flag():
    with pytest.raises(RuntimeError, match="authorization is absent"):
        exec(LAUNCH_GUARD, {})
    altered = LAUNCH_GUARD.replace("ALLOW_GPU = False", "ALLOW_GPU = True").replace(
        "HUMAN_QUOTA_AUTHORIZATION = None", "HUMAN_QUOTA_AUTHORIZATION = 'manual-claim'"
    )
    with pytest.raises(RuntimeError, match="allocation-start/deadline"):
        exec(altered, {})


def test_ac7_quota_includes_startup_and_no_implicit_batches():
    assert CONFIGURATIONS == ("E0-B180", "E1-B180")
    assert QUOTA["evaluations"] == len(CONFIGURATIONS) * len(TASKS) == 6
    assert QUOTA["generation_seconds"] == 6 * 180
    assert QUOTA["verification_seconds"] == 6 * 300
    assert QUOTA["gpu_count"] * QUOTA["session_seconds"] / 3600 == 8
    assert QUOTA["concurrency"] == 1 and QUOTA["retries"] == 0
    assert QUOTA["paid_purchases_usd"] == 0
    assert "allocation start" in QUOTA["deadline_basis"]


def test_ac9_all_six_outcomes_are_pending_not_synthetic_measurements():
    rows = pending_rows()
    assert len(rows) == 6
    assert {(r["configuration_id"], r["instance_id"]) for r in rows} == {
        (c, t) for c in CONFIGURATIONS for t in TASKS
    }
    for row in rows:
        assert row["status"] == "NOT_RUN" and row["reason"]
        for field in ("metrics", "patch", "verification", "native_acquisition"):
            assert row[field] is None


def test_ac10_notebook_payload_is_positive_allowlist_without_postrun_data():
    payload = payload_files(ROOT)
    assert set(payload) == set(HOST_MODULES) | {
        "experiments/cohort.json",
        "resources/manifest.json",
        "selected-input-pins.json",
        "quota-proposal.json",
        "archives/E0-B180.zip",
        "archives/E1-B180.zip",
    }
    assert not any(
        "research" in p or "diagnos" in p or "import_results" in p for p in payload
    )
    notebook = json.loads(build_notebook(ROOT))
    assert not notebook["metadata"]["kaggle"]["isGpuEnabled"]
    assert not notebook["metadata"]["kaggle"]["isInternetEnabled"]
    assert "require_launch_ready()" in "".join(notebook["cells"][1]["source"])
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            assert not cell["outputs"] and cell["execution_count"] is None
            ast.parse("".join(cell["source"]), feature_version=(3, 12))
    assert "base64.b64decode" in "".join(notebook["cells"][2]["source"])
    assert "Evaluator(config)" in "".join(notebook["cells"][5]["source"])


def test_ac10_notebook_literal_payload_roundtrip():
    notebook = json.loads(build_notebook(ROOT))
    values = {}
    for node in ast.parse("".join(notebook["cells"][2]["source"])).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {
                    "EMBEDDED_HASHES",
                    "EMBEDDED_PAYLOAD",
                }:
                    values[target.id] = ast.literal_eval(node.value)
    assert {
        name: base64.b64decode(data, validate=True)
        for name, data in values["EMBEDDED_PAYLOAD"].items()
    } == payload_files(ROOT)


def test_ac10_full_notebook_code_and_metadata_are_bound(tmp_path):
    # Keep repository inputs authentic while replacing only the generated artifact.
    original = ROOT / NOTEBOOK
    if not original.exists():
        pytest.fail("Generate the notebook before checking provenance")
    check_notebook(ROOT)
    # Byte comparison rejects output injection, changed guard and forged hashes.
    expected = build_notebook(ROOT)
    assert expected == original.read_bytes()
    for replacement in (b'"isGpuEnabled":true', b'"execution_count":1'):
        assert replacement not in expected


def test_absolute_operator_commands_are_local_only():
    commands = operator_commands(ROOT)
    assert all(
        Path(argv[0]).is_absolute() or argv[0] == "bash" for argv in commands.values()
    )
    assert all("kaggle" not in argv for argv in commands.values())


@pytest.mark.parametrize(
    "elapsed,expected",
    [
        (0, True),
        (6299, True),
        (6300, True),
        (6300.01, False),
        (7200, False),
        (7300, False),
    ],
)
def test_ac7_scheduling_counts_startup_and_preserves_worst_case_allowance(
    elapsed, expected
):
    start = 1000000.0
    assert scheduling_allowed(start + elapsed, start + 7200) is expected


@pytest.mark.parametrize(
    "now,deadline", [(float("nan"), 7200), (0, float("inf")), (7200, 0)]
)
def test_ac7_unknown_or_expired_deadline_is_closed(now, deadline):
    assert not scheduling_allowed(now, deadline)
