"""search-code:AC-1/2/7: actual pinned skill/native execution, without inference."""

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

import yaml

from mostaza.development import write_kaggle_notebook
from mostaza.packaging import (
    ACTIVE_TOOLS,
    IncludeLoader,
    archive_bytes,
    collect_submission,
    compile_directory,
)

ROOT = Path(__file__).resolve().parents[2]
COMPILER = ROOT / ".tools/official/bin/python"
PYTHON312 = Path("/Users/diego/.pyenv/versions/3.12.8/bin/python3.12")

# Execute in the pinned environment, not the host test interpreter. All skill,
# compiler, executor, context and native tool objects below are official classes.
OFFICIAL_WITNESS = r"""
import asyncio
import hashlib
import importlib.metadata as metadata
import inspect
import json
import shlex
import sys
from pathlib import Path
from adk_submission import ModelRegistry, compile_submission, validate_directory
from adk_submission.schema import SandboxedAgentConfig
from adk_submission.yaml_loader import load_yaml
from adk_eval_core.sandbox import AdkSandboxCodeExecutor
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService
from google.adk.tools.skill_toolset import SkillToolset
from google.adk.tools.tool_context import ToolContext
from swegemma.config import EvalConfig, build_submission_limits
from swegemma.context import SwegemmaContext
from swegemma.sandbox.subprocess import SubprocessManager
from swegemma.sandbox.docker import ContainerManager


async def main():
    versions = {
        name: metadata.version(name)
        for name in ("swegemma", "adk-submission", "google-adk")
    }
    assert versions == {
        "swegemma": "0.2.11",
        "adk-submission": "0.2.13",
        "google-adk": "1.36.1",
    }
    delivery, base = map(Path, sys.argv[1:3])
    limits, constraints = build_submission_limits()
    validate_directory(delivery, limits=limits)
    raw = load_yaml(delivery / "agent.yaml", root_dir=delivery, limits=limits)
    SandboxedAgentConfig.model_validate(raw)
    import yaml

    values = yaml.safe_load((delivery / "eval_config.yaml").read_text())["evaluation"]
    assert values == {
        "timeout_seconds": 60,
        "max_time_minutes": 5,
        "max_tool_calls": 20,
        "max_turns": 50,
    }
    models = ModelRegistry()
    models.register(raw["model"], "inert-no-model-invocation")
    config = EvalConfig(
        tasks_path=None,
        snapshots_dir=base,
        results_dir=base,
        submission_dir=delivery,
        models=models,
        **values,
    )
    with SubprocessManager(base_dir=base, timeout_seconds=60) as manager:
        manager.initialize(
            {"path with spaces/source.py": "def original_symbol():\n    return 1\n"}
        )
        sandbox_id = next(iter(manager.sandboxes))
        ctx = SwegemmaContext(
            docker_manager=manager,
            container_id=sandbox_id,
            budget=config.budget,
            harness=config.harness,
            repo="test/mock_repo/search-code",
        )
        tools = ctx.create_tools()
        executor = AdkSandboxCodeExecutor(
            sandbox=ctx.sandbox,
            timeout_seconds=60,
            start_time=ctx.task_start_time,
            max_time_minutes=5,
            budget_check_fn=ctx.check_budget,
        )
        agent = compile_submission(
            delivery,
            tools,
            models,
            limits=limits,
            generation_constraints=constraints,
            code_executor=executor,
            script_timeout=60,
        )
        skillsets = [tool for tool in agent.tools if isinstance(tool, SkillToolset)]
        assert len(skillsets) == 1
        native = sorted(
            tool.__name__ if callable(tool) else tool.name
            for tool in agent.tools
            if not isinstance(tool, SkillToolset)
        )
        assert native == sorted(
            [
                "run_command",
                "read_file",
                "write_file",
                "edit_file",
                "get_status",
                "submit_patch",
            ]
        )
        helpers = {tool.name: tool for tool in await skillsets[0].get_tools()}
        assert set(helpers) == {
            "list_skills",
            "load_skill",
            "load_skill_resource",
            "run_skill_script",
        }
        sessions = InMemorySessionService()
        session = await sessions.create_session(app_name="cpu", user_id="fixture")
        invocation = InvocationContext(
            session_service=sessions,
            invocation_id="cpu-no-inference",
            agent=agent,
            session=session,
        )
        context = ToolContext(invocation)
        assert tools["get_status"]()["tool_calls_used"] == 0
        listing = await helpers["list_skills"].run_async(args={}, tool_context=context)
        assert "search-code" in listing
        loaded = await helpers["load_skill"].run_async(
            args={"skill_name": "search-code"}, tool_context=context
        )
        assert "error" not in loaded, loaded
        resource = await helpers["load_skill_resource"].run_async(
            args={"skill_name": "search-code", "file_path": "scripts/search_code.py"},
            tool_context=context,
        )
        assert "error" not in resource, resource
        helper_calls = ctx.tool_calls_used
        assert helper_calls == 0
        # A native shell /workspace alias is translated; Python receives the real
        # cwd. This is the same discovery command taught by the active skill.
        discovered = tools["run_command"](
            command='python3 -c "import os; print(os.getcwd())"'
        )
        assert discovered["status"] == "ok", discovered
        physical_root = Path(discovered["stdout"].strip())
        assert physical_root == Path(manager.work_dir)
        root = physical_root / "path with spaces"
        assert root.is_dir() and root.is_absolute()
        # Git mutations are restricted to this disposable synthetic task repo.
        setup = manager.run_command(
            "git init -q && git -c user.name=Fixture "
            "-c user.email=fixture@example.invalid "
            "add . && git -c user.name=Fixture -c user.email=fixture@example.invalid "
            "commit -qm fixture"
        )
        assert setup.exit_code == 0, setup
        sandbox_tmp = manager.sandboxes[sandbox_id]["tmp"]
        before = set(sandbox_tmp.iterdir())
        used = ctx.tool_calls_used
        first = await helpers["run_skill_script"].run_async(
            args={
                "skill_name": "search-code",
                "file_path": "scripts/search_code.py",
                "args": [
                    "bootstrap",
                    "--root",
                    str(root),
                    "--query",
                    "original_symbol",
                ],
            },
            tool_context=context,
        )
        assert first["status"] == "success" and first["stderr"] == "", first
        payload = json.loads(first["stdout"])
        assert payload["status"] == "ok" and payload["results"], payload
        assert len(first["stdout"]) <= 4500
        assert ctx.tool_calls_used == used + 1
        executable = Path(payload["executable_path"])
        assert executable.is_file() and root not in executable.parents
        assert (
            executable.read_bytes()
            == (delivery / "skills/search-code/scripts/search_code.py").read_bytes()
        )
        assert set(sandbox_tmp.iterdir()) - before == {executable.parent}
        # The official TemporaryDirectory and .adk_exec wrapper have disappeared.
        assert not list(physical_root.glob(".adk_exec_*"))
        assert sorted(p.name for p in root.iterdir()) == ["source.py"]

        def query(text):
            argv = shlex.split(payload["command"])
            assert argv[-1] == "QUERY"
            argv[-1] = text
            previous = ctx.tool_calls_used
            response = tools["run_command"](command=shlex.join(argv))
            assert response["status"] == "ok" and response["stderr"] == "", response
            assert ctx.tool_calls_used == previous + 1
            assert len(response["stdout"]) <= 4500
            result = json.loads(response["stdout"])
            assert result["status"] == "ok", result
            return result

        warm = query("original_symbol")
        assert warm["results"] and warm["index"]["reparsed_files"] == 0, warm
        assert (
            tools["write_file"](
                filepath="/workspace/path with spaces/added.py",
                content="def written_symbol():\n    return 2\n",
            )["status"]
            == "ok"
        )
        written = query("written_symbol")
        assert written["index"]["reparsed_files"] == 1 and written["results"], written
        assert (
            tools["edit_file"](
                filepath="/workspace/path with spaces/added.py",
                old_string="written_symbol",
                new_string="edited_symbol",
            )["status"]
            == "ok"
        )
        edited = query("edited_symbol")
        assert edited["index"]["reparsed_files"] == 1 and edited["results"], edited
        assert "written_symbol" not in json.dumps(query("written_symbol")["results"])
        assert (
            tools["run_command"](
                command=("printf 'def command_symbol():\\n    return 3\\n' > "
                         "'/workspace/path with spaces/added.py'")
            )["status"]
            == "ok"
        )
        commanded = query("command_symbol")
        assert commanded["index"]["reparsed_files"] == 1 and commanded["results"], (
            commanded
        )
        assert "edited_symbol" not in json.dumps(query("edited_symbol")["results"])
        submitted = tools["submit_patch"]()
        assert submitted["status"] == "ok" and submitted["files_changed"] == 1, (
            submitted
        )
        patch = ctx.submitted_patch
        assert "path with spaces/added.py" in patch and "command_symbol" in patch
        assert all(
            word not in patch
            for word in (
                "mostaza-search-code",
                "index.sqlite",
                "writer.lock",
                ".adk_exec",
            )
        )
        assert sorted(p.name for p in root.iterdir()) == ["added.py", "source.py"]
        status = tools["get_status"]()
        assert status["max_tool_calls"] == 20 and status["max_time_minutes"] == 5
        assert status["max_turns"] == 50 and status["command_timeout_seconds"] == 60
        assert ctx.llm_calls_used == 0 and status["tool_calls_used"] == 11, status
        # Budget denial is the real official executor callback, not a stub.
        while ctx.tool_calls_used < 20:
            assert ctx.check_budget() is None
        denied = await helpers["run_skill_script"].run_async(
            args={
                "skill_name": "search-code",
                "file_path": "scripts/search_code.py",
                "args": ["status", "--root", str(root)],
            },
            tool_context=context,
        )
        assert denied["status"] == "error" and "BudgetExceeded" in denied["stderr"], (
            denied
        )
        assert tools["run_command"](command="true")["error_type"] == "BudgetExceeded"
        docker_source = inspect.getsource(ContainerManager.run_command)
        assert "shlex.quote(wd)" in docker_source and "self.exec(" in docker_source
        print(
            json.dumps(
                {
                    "versions": versions,
                    "native_tools": native,
                    "helper_tools": sorted(helpers),
                    "helper_native_calls": helper_calls,
                    "bootstrap_native_calls": 1,
                    "observed_native_calls": 11,
                    "budgets": values,
                    "llm_calls": ctx.llm_calls_used,
                    "persistent_cli_sha256": hashlib.sha256(
                        executable.read_bytes()
                    ).hexdigest(),
                    "transient_resources_removed": True,
                    "patch_clean": True,
                    "refresh_reparsed": [
                        warm["index"]["reparsed_files"],
                        written["index"]["reparsed_files"],
                        edited["index"]["reparsed_files"],
                        commanded["index"]["reparsed_files"],
                    ],
                    "python_workspace_mapping": "physical absolute path with spaces",
                    "docker_command_sha256": hashlib.sha256(
                        docker_source.encode()
                    ).hexdigest(),
                    "docker_execution": "NOT_RUN",
                    "kaggle_execution": "NOT_RUN",
                }
            )
        )


asyncio.run(main())
"""


def official_witness(delivery: Path, base: Path) -> dict:
    """Return inspectable facts for the CPU gate, failing on any execution error."""
    result = subprocess.run(
        [str(COMPILER), "-c", OFFICIAL_WITNESS, str(delivery), str(base)],
        capture_output=True,
        text=True,
        timeout=180,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return json.loads(result.stdout)


def test_search_code_ac1_active_policy_and_budgets() -> None:
    raw = yaml.load((ROOT / "submission/agent.yaml").read_text(), Loader=IncludeLoader)
    assert set(raw["tools"]) == ACTIVE_TOOLS and len(raw["tools"]) == 6
    assert raw["skills"] == ["skills/search-code"]
    original = yaml.load(
        subprocess.check_output(
            ["git", "--no-optional-locks", "show", "HEAD:submission/agent.yaml"],
            cwd=ROOT,
        ),
        Loader=IncludeLoader,
    )
    assert raw["model"] == original["model"]
    assert raw["generate_content_config"] == original["generate_content_config"]
    prompt = (ROOT / "submission/prompts/baseline.md").read_text()
    assert all(
        name not in prompt
        for name in ("get_code_neighbors", "search_similar_code", "get_code_subgraph")
    )
    assert "run_skill_script" in prompt and "grep -n -F" in prompt


def test_search_code_ac2_ac7_official_execution_and_delivery_parity(
    tmp_path: Path,
) -> None:
    files = collect_submission(ROOT / "submission")
    assert set(files) == {
        "agent.yaml",
        "eval_config.yaml",
        "prompts/baseline.md",
        "skills/search-code/SKILL.md",
        "skills/search-code/scripts/search_code.py",
    }
    first, second = tmp_path / "first.zip", tmp_path / "second.zip"
    assert archive_bytes(files, first) == archive_bytes(files, second)
    assert first.read_bytes() == second.read_bytes()
    delivery = (tmp_path / "delivery").resolve()
    delivery.mkdir()
    with zipfile.ZipFile(first) as archive:
        assert {name: archive.read(name) for name in archive.namelist()} == files
        archive.extractall(delivery)
    compile_directory(delivery, COMPILER)
    notebook = json.loads(write_kaggle_notebook(first).read_text())
    code = "".join(notebook["cells"][1]["source"])
    # Exercise the actual generated delivery cell in a disposable cwd.
    replay = tmp_path / "replay"
    replay.mkdir()
    subprocess.run([sys.executable, "-c", code], cwd=replay, check=True, timeout=30)
    assert (replay / "submission.zip").read_bytes() == first.read_bytes()
    witness = official_witness(delivery, tmp_path.resolve())
    assert witness["refresh_reparsed"] == [0, 1, 1, 1]
    assert witness["patch_clean"] and witness["transient_resources_removed"]


def test_search_code_ac2_python312_absolute_workspace_with_spaces(
    tmp_path: Path,
) -> None:
    root = (tmp_path / "workspace" / "path with spaces").resolve()
    root.mkdir(parents=True)
    (root / "source.py").write_text("async def portable_symbol():\n    return 1\n")
    script = ROOT / "submission/skills/search-code/scripts/search_code.py"
    result = subprocess.run(
        [
            str(PYTHON312),
            str(script),
            "bootstrap",
            "--root",
            str(root),
            "--query",
            "portable_symbol",
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    first = json.loads(result.stdout)
    assert result.stderr == "" and first["status"] == "ok" and first["results"]
    assert Path(first["executable_path"]).read_bytes() == script.read_bytes()
    import shlex

    argv = [str(PYTHON312), *shlex.split(first["command"])[1:-1], "portable_symbol"]
    warm = subprocess.run(argv, capture_output=True, text=True, check=True, timeout=60)
    assert warm.stderr == ""
    assert json.loads(warm.stdout)["index"]["reparsed_files"] == 0
