"""Run the genuine native CPU contracts, never inference or remote sessions."""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_native_source_binding_adk_context_and_monitor_controls():
    result = subprocess.run(
        [
            str(ROOT / ".tools/official/bin/python"),
            str(ROOT / "scripts/context_cpu_fixtures.py"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=True,
    )
    receipt = json.loads(result.stdout)
    assert receipt["status"] == "PASS_CPU_FIXTURES"
    assert [r["binding_matches"] for r in receipt["origins"]] == [True, False, True]
    assert receipt["gpu_starts"] == receipt["model_inference_calls"] == 0
