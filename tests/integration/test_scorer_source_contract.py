"""Offline source-contract CLI and retained scorer/GPU uncertainty."""

import json
import subprocess
from pathlib import Path

import pytest


@pytest.mark.historical_evidence
def test_public_bootstrap_contract_does_not_promote_scorer_readiness(
    historical_phase2_root: Path,
):
    root = historical_phase2_root
    process = subprocess.run(
        [
            str(root / ".venv/bin/python"),
            str(root / "scripts/check_pcv01_scorer_contract.py"),
            "--check",
        ],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=60,
        check=True,
    )
    receipt = json.loads(process.stdout)
    assert receipt["status"] == "PASS_CPU_STATIC_REVIEW"
    assert receipt["public_setup_acquired"] is True
    assert receipt["compatibility"]["actual_scorer_runtime_parity"] is None
    assert receipt["compatibility"]["gpu_readiness"] is False
    assert receipt["setup_imported_or_executed"] is False
    assert receipt["real_verifier_changed"] is False
    assert receipt["remote_compute_sessions_started"] == 0
