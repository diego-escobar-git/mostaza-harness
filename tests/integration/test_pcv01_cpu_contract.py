"""Actual native CPU pytest compatibility and process-identity controls."""

import json
import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.historical_evidence
def test_pcv01_actual_pytest_process_and_payload_isolation(
    historical_phase2_root: Path,
):
    root = historical_phase2_root
    # search-code:AC-8: only this authenticated historical child uses old imports.
    child = r"""
import contextlib
import io
import json
import os
import runpy
import sys
from pathlib import Path

root = Path.cwd().resolve()
assert os.environ["PYTHONPATH"] == str(root / "src")
sys.path.insert(0, str(root / "scripts"))
script = root / "scripts/check_pcv01.py"
sys.argv = [str(script), "--check"]
output = io.StringIO()
with contextlib.redirect_stdout(output):
    executed = runpy.run_path(str(script), run_name="__main__")
assert Path(executed["__file__"]).resolve() == script
bindings = {
    name: str(Path(module.__file__).resolve())
    for name, module in sys.modules.items()
    if (name == "mostaza" or name.startswith("mostaza."))
    and getattr(module, "__file__", None)
}
assert bindings
assert all(Path(path).is_relative_to(root / "src") for path in bindings.values())
receipt = json.loads(output.getvalue())
receipt["historical_imports"] = bindings
print(json.dumps(receipt))
"""
    result = subprocess.run(
        [str(root / ".venv/bin/python"), "-c", child],
        cwd=root,
        env={**os.environ, "PYTHONPATH": str(root / "src")},
        capture_output=True,
        text=True,
        timeout=240,
    )
    assert result.returncode == 0, (
        f"Historical PCV checker exited {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    receipt = json.loads(result.stdout)
    for module in (
        "mostaza",
        "mostaza.evaluation.context_variants",
        "mostaza.packaging",
    ):
        relative = module.replace(".", "/")
        if module == "mostaza":
            relative += "/__init__"
        assert receipt["historical_imports"][module] == str(
            root / "src" / (relative + ".py")
        )
    assert receipt["status"] == "PASS_PCV01_CPU_ONLY"
    assert receipt["real_kaggle_verifier_changed"] is False
    assert receipt["real_kaggle_compatibility_confirmed"] is False
    assert receipt["cpu_controls"]["gpu_starts"] == 0
    assert len(receipt["cpu_controls"]["runs"]) == 14
