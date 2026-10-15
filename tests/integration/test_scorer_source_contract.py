"""Offline source-contract CLI and retained scorer/GPU uncertainty."""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_public_bootstrap_contract_does_not_promote_scorer_readiness():
    process = subprocess.run(
        [
            str(ROOT / ".venv/bin/python"),
            str(ROOT / "scripts/check_pcv01_scorer_contract.py"),
            "--check",
        ],
        cwd=ROOT,
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
