"""Run the official harness with LM Studio, or package the same agent for Kaggle."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

import yaml

from mostaza.evaluation.local_imports import (
    snapshot_agent_imports,
    snapshot_verification_imports,
)
from mostaza.packaging import archive_bytes, collect_submission, compile_directory

ROOT = Path(__file__).resolve().parents[2]


def verify_local_model(endpoint: str, model: str, api_key: str | None) -> None:
    """Check the configured catalog before invoking the official evaluator."""
    request = urllib.request.Request(endpoint.rstrip("/") + "/models")
    if api_key:
        request.add_header("Authorization", "Bearer " + api_key)
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            catalog = json.load(response)
    except urllib.error.HTTPError as error:
        if error.code in (401, 403):
            raise ValueError(
                "LM Studio authentication failed; configure MOSTAZA_API_KEY locally"
            ) from None
        raise ValueError(f"LM Studio catalog returned HTTP {error.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        raise ValueError(
            "LM Studio catalog unavailable; check the server and MOSTAZA_API_BASE"
        ) from None
    if not isinstance(catalog, dict) or not isinstance(catalog.get("data"), list):
        raise ValueError("LM Studio returned an invalid model catalog")
    if not any(
        isinstance(item, dict) and item.get("id") == model for item in catalog["data"]
    ):
        raise ValueError(
            f"Configured model {model!r} is absent from the LM Studio catalog; "
            "check MOSTAZA_MODEL without substituting another model"
        )


def write_kaggle_notebook(archive: Path) -> Path:
    """Embed the generated ZIP in a CPU-only Kaggle delivery notebook."""
    payload = base64.b64encode(archive.read_bytes()).decode("ascii")
    source = (
        "from pathlib import Path\nimport base64\n\n"
        "working = (Path('/kaggle/working') if Path('/kaggle').exists()\n"
        "           else Path.cwd())\n"
        "working.mkdir(parents=True, exist_ok=True)\n"
        "output = working / 'submission.zip'\n"
        f"output.write_bytes(base64.b64decode({payload!r}))\n"
        "print(f'Ready: {output} ({output.stat().st_size} bytes)')\n"
    )
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
            "kaggle": {"accelerator": "none", "isInternetEnabled": False},
        },
        "cells": [
            {
                "cell_type": "markdown",
                "id": "delivery",
                "metadata": {},
                "source": [
                    "# Mostaza submission\n",
                    "Import into a Gemma 4 Developer Agent competition notebook.\n",
                    "Keep GPU and Internet disabled. Save Version with Run All.\n",
                    "Submit the generated `submission.zip` "
                    "through the competition UI.\n",
                    "This notebook writes the packaged agent; it runs no model.\n",
                ],
            },
            {
                "cell_type": "code",
                "id": "write-submission",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": source.splitlines(keepends=True),
            },
        ],
    }
    destination = archive.with_suffix(".ipynb")
    destination.write_text(json.dumps(notebook, indent=2) + "\n")
    return destination


def main() -> int:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env", override=False)
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Run one published task using LM Studio")
    run.add_argument("--task", required=True, help="Published task instance ID")
    run.add_argument(
        "--model", default=os.getenv("MOSTAZA_MODEL", "google/gemma-4-12b")
    )
    run.add_argument(
        "--endpoint",
        default=os.getenv("MOSTAZA_API_BASE", "http://127.0.0.1:1234/v1"),
    )
    run.add_argument(
        "--data-dir",
        type=Path,
        default=os.getenv("MOSTAZA_DATA_DIR", str(ROOT / "resources/official")),
    )
    run.add_argument("--results-dir", type=Path)
    run.add_argument(
        "--sandbox", choices=("subprocess", "docker"), default="subprocess"
    )
    pack = commands.add_parser("pack", help="Create the Kaggle submission ZIP")
    pack.add_argument("--output", type=Path, default=ROOT / "dist/submission.zip")
    for command in (run, pack):
        command.add_argument("--agent-dir", type=Path, default=ROOT / "submission")
    args = parser.parse_args()
    agent_root = args.agent_dir.resolve()
    files = collect_submission(agent_root)
    with tempfile.TemporaryDirectory(prefix="mostaza-agent-") as temporary:
        staging = Path(temporary).resolve()
        agent = staging / "agent"
        agent.mkdir()
        for name, data in files.items():
            target = agent / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        if args.command == "pack":
            compile_directory(agent, Path(sys.executable))
            output = args.output.resolve()
            if output.is_relative_to(agent_root):
                parser.error("Archive output must be outside the agent directory")
            output.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(dir=output.parent) as archive_directory:
                built = Path(archive_directory) / "submission.zip"
                archive_bytes(files, built)
                os.replace(built, output)
            print(f"Kaggle submission: {output}")
            print(f"Kaggle upload notebook: {write_kaggle_notebook(output)}")
            return 0

        from adk_submission.yaml_loader import load_yaml
        from swegemma.cli import main as evaluate

        data_dir = args.data_dir.resolve()
        if not (data_dir / "tasks.jsonl").is_file():
            parser.error(
                "Set MOSTAZA_DATA_DIR to the official tasks/snapshots directory"
            )
        api_key = os.getenv("MOSTAZA_API_KEY") or None
        try:
            verify_local_model(args.endpoint, args.model, api_key)
        except ValueError as error:
            parser.error(str(error))
        alias = load_yaml(agent / "agent.yaml", root_dir=agent)["model"]
        mapping = staging / "models.yaml"
        mapping.write_text(
            yaml.safe_dump(
                {
                    "models": {
                        alias: {
                            "path": f"openai/{args.model}",
                            "api_base": args.endpoint,
                            # The official OpenAI adapter requires a nonempty key.
                            # Catalog authentication uses only a configured real key.
                            "api_key": api_key or "local-no-auth",
                        }
                    }
                }
            )
        )
        result_dir = (
            args.results_dir
            or ROOT / "results/local" / datetime.now().strftime("%Y%m%d-%H%M%S")
        )
        arguments = [
            "eval",
            "--tasks",
            str(data_dir / "tasks.jsonl"),
            "--snapshots-dir",
            str(data_dir / "snapshots"),
            "--submission-dir",
            str(agent),
            "--results-dir",
            str(result_dir.resolve()),
            "--models-yaml",
            str(mapping),
            "--sandbox",
            args.sandbox,
            "--task-id",
            args.task,
            "--concurrency",
            "1",
        ]
        if "eval_config.yaml" in files:
            values = yaml.safe_load(files["eval_config.yaml"])["evaluation"]
            for key in (
                "timeout_seconds",
                "verification_timeout_seconds",
                "max_tool_calls",
                "max_time_minutes",
                "max_turns",
            ):
                if key in values:
                    arguments.extend(("--" + key.replace("_", "-"), str(values[key])))
        print(f"Local model: {args.model} (LM Studio catalog verified)", flush=True)
        print(f"Results: {result_dir.resolve()}", flush=True)
        with snapshot_verification_imports(), snapshot_agent_imports():
            return int(evaluate(arguments))


if __name__ == "__main__":
    raise SystemExit(main())
