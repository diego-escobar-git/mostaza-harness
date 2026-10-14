"""Actual native CPU pytest compatibility and process-identity controls."""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_pcv01_actual_pytest_process_and_payload_isolation():
    result = subprocess.run(
        [
            str(ROOT / ".venv/bin/python"),
            str(ROOT / "scripts/check_pcv01.py"),
            "--check",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=240,
        check=True,
    )
    receipt = json.loads(result.stdout)
    assert receipt["status"] == "PASS_PCV01_CPU_ONLY"
    assert receipt["real_kaggle_verifier_changed"] is False
    assert receipt["real_kaggle_compatibility_confirmed"] is False
    assert receipt["cpu_controls"]["gpu_starts"] == 0
    assert len(receipt["cpu_controls"]["runs"]) == 14
