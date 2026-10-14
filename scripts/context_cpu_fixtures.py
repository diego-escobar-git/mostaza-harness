"""Native CPU failure-mode fixtures; no network, server, scorer or model inference."""

from __future__ import annotations

import ast
import asyncio
import hashlib
import importlib
import json
import os
import shutil
import sys
import tarfile
import tempfile
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from mostaza.evaluation.browser_supervision import VersionIdentity
from mostaza.evaluation.context_diagnostics import context_fit, read_action
from mostaza.evaluation.supervision_monitor import ReadOnlyMonitor
from mostaza.evaluation.verification_origin import binding_readiness, observe_origin


def run(root: Path) -> dict[str, Any]:
    native = importlib.import_module("swegemma.sandbox.subprocess")
    tool_type = importlib.import_module("google.adk.tools.function_tool").FunctionTool
    request_type = importlib.import_module("google.adk.models.llm_request").LlmRequest
    genai = importlib.import_module("google.genai.types")
    with tempfile.TemporaryDirectory(prefix="mostaza-context-fixtures-") as directory:
        temporary = Path(directory)
        manager = native.SubprocessManager(base_dir=temporary / "sandboxes")
        sandbox_id = manager.start()
        origin_records = []
        try:
            workspace = manager.sandboxes[sandbox_id]["workspace"]
            site = next(
                manager.sandboxes[sandbox_id]["venv"].glob("lib/python*/site-packages")
            )
            package = "mostaza_origin_fixture"
            shadow = site / package
            shadow.mkdir()
            (shadow / "__init__.py").write_text("VALUE = 'installed_shadow'\n")
            for layout in ("flat", "src"):
                source = workspace / ("src" if layout == "src" else "") / package
                source.mkdir(parents=True)
                target = source / "__init__.py"
                target.write_text("VALUE = 'edited_workspace'\n")
                expected = hashlib.sha256(target.read_bytes()).hexdigest()
                if layout == "src":
                    # Remove only our previous fixture, exposing the controlled shadow.
                    shutil.rmtree(workspace / package)
                receipt = observe_origin(
                    manager,
                    sandbox_id,
                    module=package,
                    expected_relative_file=str(target.relative_to(workspace)),
                    expected_sha256=expected,
                    phase="verification",
                )
                assert receipt["workspace_binding_matches"] is (layout == "flat")
                origin_records.append(
                    {
                        "layout": layout,
                        "binding_matches": receipt["workspace_binding_matches"],
                        "coverage": receipt["coverage"],
                    }
                )
                assert (
                    binding_readiness([receipt], editable_install_exit_code=0)[
                        "ready_for_real_evaluation"
                    ]
                    is False
                )
                if layout == "src":
                    # CPU control only, emulating a working editable source binding.
                    # This never modifies an official setup or verifier environment.
                    (site / "_fixture_source.pth").write_text(
                        "import sys; sys.path.insert(0, "
                        + repr(str(workspace / "src"))
                        + ")\n"
                    )
                    bound = observe_origin(
                        manager,
                        sandbox_id,
                        module=package,
                        expected_relative_file=str(target.relative_to(workspace)),
                        expected_sha256=expected,
                        phase="agent",
                    )
                    assert bound["workspace_binding_matches"] is True
                    origin_records.append(
                        {
                            "layout": "src_control_binding",
                            "binding_matches": True,
                            "coverage": bound["coverage"],
                        }
                    )
                    for exit_code in (None, 1):
                        result = binding_readiness(
                            [bound], editable_install_exit_code=exit_code
                        )
                        assert any(
                            "installation" in item for item in result["blockers"]
                        )
        finally:
            manager.cleanup_all()

        # Exercise actual ADK argument filtering and native read_file range handling.
        fixture_file = temporary / "fixture.py"
        fixture_file.write_text("\n".join(f"line_{i}" for i in range(1, 401)))

        class CopyOnly:
            def copy_from(self, _id: str, _source: str, target: Path) -> None:
                target.write_bytes(fixture_file.read_bytes())

        ctx = importlib.import_module("swegemma.context").SwegemmaContext(
            max_tool_calls=20, max_time_minutes=1
        )
        ctx.docker = CopyOnly()
        ctx.container_id = "cpu_fixture"
        tools = importlib.import_module("swegemma.tools").create_tools(ctx)

        async def read_fixture() -> list[dict[str, Any]]:
            tool = tool_type(tools["read_file"])
            malformed = {"filepath": "fixture.py", 'start_line"': 300}
            bad = await tool.run_async(args=malformed, tool_context=None)
            repeated = await tool.run_async(args=malformed, tool_context=None)
            good = await tool.run_async(
                args={"filepath": "fixture.py", "start_line": 300, "end_line": 330},
                tool_context=None,
            )
            assert bad["start_line"] == repeated["start_line"] == 1
            assert bad["end_line"] == 150 and bad["is_truncated"] is True
            assert good["start_line"] == 300 and good["end_line"] == 330
            assert read_action(malformed, bad, duplicate=False) == "CHECK_ARGUMENT_KEYS"
            assert (
                read_action(malformed, repeated, duplicate=True)
                == "USE_BOUNDED_SHELL_READ"
            )
            return [
                {
                    "malformed_start": bad["start_line"],
                    "valid_start": good["start_line"],
                    "truncated": bad["is_truncated"],
                }
            ]

        reads = asyncio.run(read_fixture())

        class BoundaryModel:
            def generate(self, request: Any, input_tokens: int) -> str:
                # Independent rejection rule, not implemented via context_fit.
                if input_tokens + request.config.max_output_tokens > 32768:
                    raise ValueError("ContextWindowExceededError")
                return "synthetic response"

        model = BoundaryModel()
        request = request_type(
            model="fixture_no_model",
            config=genai.GenerateContentConfig(max_output_tokens=16384),
        )
        try:
            model.generate(request, 16385)
            raise AssertionError("Known rejection boundary was accepted")
        except ValueError:
            pass
        request.config.max_output_tokens = 8192
        assert model.generate(request, 16385) == "synthetic response"
        assert context_fit(16385)["status"] == "FITS_OBSERVED_REQUEST"
        assert context_fit(16385, lower_bound=True)["status"] == "UNKNOWN"
        assert context_fit(None)["status"] == "UNKNOWN"
        assert context_fit(24577)["status"] == "EXCEEDS_CONTEXT"
        # Large observed file output is not converted from characters to fake tokens.
        fixture_file.write_text("x" * 11000)
        clipped = tools["read_file"]("fixture.py")
        assert clipped["is_truncated"] is True and len(clipped["content"]) <= 10000

        with tarfile.open(
            root / "resources/official/snapshots/requests_7205.tgz"
        ) as archive:
            member = archive.extractfile("./src/requests/utils.py")
            assert member is not None
            source = member.read().decode()
        node = next(
            n
            for n in ast.parse(source).body
            if isinstance(n, ast.FunctionDef) and n.name == "get_netrc_auth"
        )
        function = ast.get_source_segment(source, node)
        assert function is not None
        from urllib.parse import urlparse

        previous = os.environ.get("NETRC")
        netrc_path = temporary / "independent_netrc_fixture"
        cases = {
            "empty_machine": "machine diag.invalid\n",
            "empty_default": (
                "machine other.invalid login user password pass\ndefault\n"
            ),
            "missing": "machine other.invalid login user password pass\n",
            "valid": "machine diag.invalid login user password pass\n",
        }
        netrc_results = []
        try:
            os.environ["NETRC"] = str(netrc_path)
            for name, condition in (
                ("baseline", "if _netrc:"),
                ("E0_patch", "if any(_netrc):"),
                ("E1_patch", "if _netrc and any(_netrc):"),
            ):
                namespace: dict[str, Any] = {
                    "os": os,
                    "urlparse": urlparse,
                    "NETRC_FILES": (),
                }
                exec(
                    compile(
                        function.replace("if _netrc:", condition),
                        "snapshot_function",
                        "exec",
                    ),
                    namespace,
                )
                for case, contents in cases.items():
                    netrc_path.write_text(contents)
                    try:
                        value, error = (
                            namespace["get_netrc_auth"]("https://diag.invalid/"),
                            None,
                        )
                    except TypeError:
                        value, error = None, "TypeError"
                    assert error == (
                        "TypeError" if (name, case) == ("E0_patch", "missing") else None
                    )
                    if case == "valid":
                        assert value == ("user", "pass")
                    elif name != "baseline":
                        assert value is None
                    netrc_results.append(
                        {"variant": name, "case": case, "error": error}
                    )
        finally:
            if previous is None:
                os.environ.pop("NETRC", None)
            else:
                os.environ["NETRC"] = previous

        ref, opaque = "owner/fixture", 12345
        observation = {
            "ref": ref,
            "script_version_id": opaque,
            "sdk_status": "RUNNING",
            "browser_status": "RUNNING",
            "model_ready": True,
            "version_cancel_available": True,
            "active_event_visible": False,
        }
        monitor = ReadOnlyMonitor(
            [sys.executable, "-c", "print(" + repr(json.dumps(observation)) + ")"],
            temporary / "monitor.jsonl",
            timeout_seconds=1,
            interval_seconds=0.02,
        )
        try:
            try:
                monitor.prelaunch(time.monotonic())
                raise AssertionError("Stopped monitor allowed external T0")
            except RuntimeError:
                pass
            monitor.start()
            receipt = monitor.prelaunch(time.monotonic())
            assert receipt["first_success_precedes_t0"] is True
            monitor.bind(
                VersionIdentity(
                    ref,
                    1,
                    opaque,
                    "https://www.kaggle.com/code/"
                    + ref
                    + "?scriptVersionId="
                    + str(opaque),
                )
            )
            assert monitor.action(10) == "SUPERVISE_EXACT_VERSION"
            assert monitor.action(6240) == "STOP_EXACT_VERSION"
        finally:
            monitor.close()
        hung = ReadOnlyMonitor(
            [sys.executable, "-c", "import time; time.sleep(5)"],
            temporary / "hung.jsonl",
            timeout_seconds=0.04,
            interval_seconds=0,
        )
        started = time.monotonic()
        record = hung.sample()
        assert record["status"] == "UNAVAILABLE" and time.monotonic() - started < 2
        return {
            "status": "PASS_CPU_FIXTURES",
            "scope": "Synthetic CPU controls; not real benchmark results",
            "python": sys.version.split()[0],
            "origins": origin_records,
            "native_read_ranges": reads,
            "independent_netrc_cases": netrc_results,
            "context_known_unknown_boundaries": "PASS",
            "monitor_started_before_t0": True,
            "exact_version_fallback_without_active_event": "PASS",
            "hung_reader_timeout": "PASS",
            "gpu_starts": 0,
            "model_inference_calls": 0,
        }


if __name__ == "__main__":
    print(json.dumps(run(Path(__file__).resolve().parents[1]), sort_keys=True))
