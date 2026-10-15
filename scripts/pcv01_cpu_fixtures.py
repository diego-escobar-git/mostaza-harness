"""Actual pytest-process CPU controls for P-CV-01; no scorer, model or network calls."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import shlex
import shutil
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

WHEEL = "pytest-8.4.2-py3-none-any.whl"
WHEEL_SHA256 = "872f880de3fc3a5bdc88a11b39c9710c3497a547cfa9320bc3c5e62fbf272e79"
PLUGIN = "src/mostaza/evaluation/pytest_origin_receipt.py"
SECRET = "SYNTHETIC_EXPECTATION_MUST_NOT_ENTER_RECEIPT"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def junit(path: Path) -> dict[str, int]:
    tree = ET.fromstring(path.read_bytes())
    suites = [tree] if tree.tag == "testsuite" else list(tree.findall("testsuite"))
    totals = {
        key: sum(int(s.get(key, "0")) for s in suites)
        for key in ("tests", "failures", "errors", "skipped")
    }
    totals["passed"] = (
        totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"]
    )
    return totals


def run(root: Path, raw: Path) -> dict[str, Any]:
    native = importlib.import_module("swegemma.sandbox.subprocess")
    wheel = root / "resources/official" / WHEEL
    if not wheel.is_file() or digest(wheel) != WHEEL_SHA256:
        raise ValueError(
            "Pinned CPU pytest8.4.2 wheel missing/changed; see P-CV-01 report"
        )
    plugin = root / PLUGIN
    shutil.copyfile(plugin, raw / "plugin-source.py")
    shutil.copyfile(Path(__file__), raw / "driver-source.py")
    runs = []
    cases = (
        "positive",
        "negative",
        "shadow",
        "replaced_function",
        "setup_error",
        "logging_failure",
        "missing_configuration",
    )
    for version in ("9.1.1", "8.4.2"):
        manager = native.SubprocessManager(base_dir=raw / ("sandboxes-" + version))
        sandbox = manager.start()
        try:
            paths = manager.sandboxes[sandbox]
            workspace, site = (
                paths["workspace"],
                next(paths["venv"].glob("lib/python*/site-packages")),
            )
            if version == "8.4.2":
                with zipfile.ZipFile(wheel) as archive:
                    assert (
                        sum(i.file_size for i in archive.infolist()) < 5 * 1024 * 1024
                    )
                    for info in archive.infolist():
                        p = Path(info.filename)
                        assert not p.is_absolute() and ".." not in p.parts
                        assert (info.external_attr >> 16) & 0o170000 != 0o120000
                    archive.extractall(site)
            shutil.copyfile(plugin, site / "mostaza_origin_receipt.py")
            config_path = site / "mostaza_origin_receipt_config.json"
            # Both commands use identical installed files/environment; only -p differs.
            alternative = site / "pcv_product"
            alternative.mkdir()
            shadow_file = alternative / "__init__.py"
            shadow_file.write_text("def evaluate():\n    return 'shadow'\n")
            for case in cases:
                out = raw / version / case
                out.mkdir(parents=True)
                flat = workspace / "pcv_product"
                if flat.exists():
                    shutil.rmtree(flat)
                source = workspace / ("src" if case == "shadow" else "") / "pcv_product"
                source.mkdir(parents=True, exist_ok=True)
                forbidden_access = out / "forbidden_access"
                product = source / "__init__.py"
                product.write_text(
                    (
                        "def evaluate():\n    return 'workspace'\n\ndef "
                        "__getattr__(name):\n    if name == "
                        "'missing_function':\n        from pathlib import "
                        "Path\n        Path("
                    )
                    + repr(str(forbidden_access))
                    + ").write_text('dynamic access')\n    raise AttributeError(name)\n"
                )
                unused = workspace / "pcv_unused.py"
                unused.write_text(
                    "raise RuntimeError('observer must not import an unused product')\n"
                )
                proof = out / "test_process_proof.json"
                conftest = workspace / "conftest.py"
                if conftest.exists():
                    conftest.unlink()
                if case in {"replaced_function", "setup_error"}:
                    body = (
                        "    raise RuntimeError(" + repr(SECRET) + ")\n"
                        if case == "setup_error"
                        else "    pcv_product.evaluate = lambda: 'workspace'\n"
                    )
                    conftest.write_text(
                        (
                            "import pytest, pcv_product\n"
                            "@pytest.fixture(autouse=True)\ndef "
                            "synthetic_setup():\n"
                        )
                        + body
                    )
                expected = (
                    SECRET
                    if case == "negative"
                    else "shadow"
                    if case == "shadow"
                    else "workspace"
                )
                test_file = workspace / "test_synthetic.py"
                test_file.write_text(
                    (
                        "import json, os, pcv_product\nfrom pathlib import"
                        " Path\ndef test_synthetic_control():\n    Path("
                    )
                    + repr(str(proof))
                    + (
                        ").write_text(json.dumps({'pid':os.getpid(), "
                        "'function_identity':id(pcv_product.evaluate)}))"
                        "\n    assert pcv_product.evaluate() == "
                    )
                    + repr(expected)
                    + "\n    pcv_product.evaluate = lambda: 'after_test_body'\n"
                )
                receipt_path = out / "origin.jsonl"
                if case == "logging_failure":
                    receipt_path.mkdir()
                targets = [
                    {
                        "module": "pcv_product",
                        "symbol": "evaluate",
                        "expected_file": str(product),
                        "public_files": [
                            {"path": str(product), "sha256": digest(product)},
                            {"path": str(shadow_file), "sha256": digest(shadow_file)},
                        ],
                    },
                    {
                        "module": "pcv_product",
                        "symbol": "missing_function",
                        "expected_file": str(product),
                        "public_files": [
                            {"path": str(product), "sha256": digest(product)},
                            {"path": str(shadow_file), "sha256": digest(shadow_file)},
                        ],
                    },
                    {
                        "module": "pcv_unused",
                        "symbol": None,
                        "expected_file": str(unused),
                        "public_files": [
                            {"path": str(unused), "sha256": digest(unused)}
                        ],
                    },
                ]
                config = {
                    "schema_version": 1,
                    "output_file": str(receipt_path),
                    "targets": targets,
                }
                config_path.write_text(json.dumps(config, sort_keys=True))
                if case == "missing_configuration":
                    config_path.unlink()
                for original, name in (
                    (product, "fixture-product.py"),
                    (shadow_file, "fixture-shadow.py"),
                    (unused, "fixture-unused.py"),
                    (test_file, "fixture-test.py"),
                ):
                    shutil.copyfile(original, out / name)
                if conftest.exists():
                    shutil.copyfile(conftest, out / "fixture-conftest.py")
                if config_path.exists():
                    shutil.copyfile(config_path, out / "observer-config.json")
                jpath = paths["tmp"] / "pcv01.xml"
                common = (
                    " test_synthetic.py --junitxml="
                    + shlex.quote(str(jpath))
                    + " -p no:anyio -o timeout=0 -o python_classes='Test* *Test' -q"
                )
                prefix = (
                    "cd /workspace && PYTHONSAFEPATH=1 "
                    "PYTHONNOUSERSITE=1 python3 -s -m pytest"
                )
                commands = [
                    prefix + common,
                    prefix + " -p mostaza_origin_receipt" + common,
                ]
                before = {
                    str(p): digest(p)
                    for p in (
                        product,
                        shadow_file,
                        unused,
                        test_file,
                        site / "mostaza_origin_receipt.py",
                    )
                }
                observations = []
                for index, command in enumerate(commands):
                    if proof.exists():
                        proof.unlink()
                    started = time.monotonic()
                    result = manager.exec(sandbox, command, timeout=30)
                    (out / f"command-{index}.log").write_text(
                        result.stdout + "\nSTDERR:\n" + result.stderr
                    )
                    assert result.exit_code in {0, 1}, (
                        case,
                        result.exit_code,
                        result.stderr,
                    )
                    outcomes = junit(jpath)
                    shutil.copyfile(jpath, out / f"junit-{index}.xml")
                    observations.append(
                        {
                            "exit_code": result.exit_code,
                            "outcomes": outcomes,
                            "elapsed_seconds": time.monotonic() - started,
                        }
                    )
                    if index == 0:
                        assert not receipt_path.is_file(), (
                            "Plugin unexpectedly autoloaded"
                        )
                assert observations[0]["exit_code"] == observations[1]["exit_code"]
                assert observations[0]["outcomes"] == observations[1]["outcomes"]
                assert observations[0]["exit_code"] == (
                    1 if case in {"negative", "setup_error"} else 0
                )
                assert before == {
                    str(p): digest(p)
                    for p in (
                        product,
                        shadow_file,
                        unused,
                        test_file,
                        site / "mostaza_origin_receipt.py",
                    )
                }
                assert not forbidden_access.exists(), (
                    "Observer invoked a product dynamic accessor"
                )
                receipt = None
                reason: str | None = (
                    "Call hook not reached, configuration unavailable"
                    " or receipt write failed"
                )
                if receipt_path.is_file():
                    text = receipt_path.read_text()
                    assert (
                        SECRET not in text
                        and "test_synthetic_control" not in text
                        and "synthetic_setup" not in text
                    )
                    records = [json.loads(line) for line in text.splitlines()]
                    assert len(records) == 1
                    receipt = records[0]
                    assert (
                        receipt["coverage"] == "actual_pytest_call_hook_cpu_diagnostic"
                    )
                    assert receipt["pytest_version"] == version
                    process = json.loads(proof.read_text())
                    assert receipt["process_id"] == process["pid"]
                    assert receipt["targets"][2]["status"] == "UNAVAILABLE"
                    assert receipt["targets"][1]["function_code_sha256"] is None
                    target = receipt["targets"][0]
                    assert target["workspace_binding_matches"] is (case != "shadow")
                    if case == "replaced_function":
                        assert target["function_code_sha256"] is None
                        assert (
                            target["function_hash_reason"]
                            == "Function code is outside reviewed public source"
                        )
                    else:
                        assert (
                            target["function_code_sha256"]
                            and target["function_source_sha256"]
                        )
                        assert (
                            target["function_identity"] == process["function_identity"]
                        )
                    reason = None
                else:
                    assert case in {
                        "setup_error",
                        "logging_failure",
                        "missing_configuration",
                    }
                runs.append(
                    {
                        "pytest_version": version,
                        "case": case,
                        "command_delta": ["-p", "mostaza_origin_receipt"],
                        "outcome_parity": True,
                        "observations": observations,
                        "actual_process_receipt": receipt,
                        "receipt_missing_reason": reason,
                    }
                )
        finally:
            manager.cleanup_all()
    return {
        "status": "PASS_PCV01_CPU",
        "scope": (
            "Synthetic CPU pytest processes; not Kaggle verifier or benchmark outcomes"
        ),
        "python_version": sys.version.split()[0],
        "plugin_sha256": digest(plugin),
        "pytest842_wheel_sha256": WHEEL_SHA256,
        "runs": runs,
        "gpu_starts": 0,
        "model_inference_calls": 0,
        "real_kaggle_verifier_changed": False,
        "official_organizer_acceptance": None,
        "gpu_readiness_unlocked": False,
        "raw_directory": str(raw),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.raw_dir:
        raw = args.raw_dir.resolve()
        if not raw.is_relative_to(root / "results"):
            parser.error("Retained raw output must be under ignored results")
        raw.mkdir(parents=True, exist_ok=False)
        print(json.dumps(run(root, raw), sort_keys=True))
    else:
        with tempfile.TemporaryDirectory(prefix="mostaza-pcv01-cpu-") as directory:
            print(json.dumps(run(root, Path(directory)), sort_keys=True))
