"""Check the pinned native command/env builders on CPU; never call server.start."""

import ast
import hashlib
import importlib
import json
import os
import sys
import tempfile
from importlib.metadata import version
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mostaza.evaluation.startup_configuration import (
    ENVIRONMENT,
    apply_environment,
    observe_server_environment,
)


def main() -> None:
    apply_environment()
    native = importlib.import_module("adk_submission")
    assert version("adk-submission") == "0.2.13"
    project = Path(__file__).resolve().parents[1]
    notebook = json.loads(
        (project / "notebooks/mostaza-phase2-startup-corrected.ipynb").read_text()
    )
    tree = ast.parse("".join(notebook["cells"][-1]["source"]))
    assignment = next(
        node
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "server_config"
            for target in node.targets
        )
    )
    namespace = {
        "VllmConfig": native.VllmConfig,
        "MODEL_PATH": Path("LOCAL_CPU_NO_MODEL"),
        "torch": SimpleNamespace(cuda=SimpleNamespace(is_bf16_supported=lambda: True)),
    }
    # Execute only the candidate's native config constructor, never any run cell.
    exec(
        compile(
            ast.Module(body=[assignment], type_ignores=[]), "candidate_config", "exec"
        ),
        namespace,
    )
    server = native.VllmServer(namespace["server_config"])
    command = server.build_cmd()
    assert command.count("--max-num-seqs") == 1
    assert command[command.index("--max-num-seqs") + 1] == "1"
    os.environ["OPENAI_API_KEY"] = "LOCAL_SECRET_MUST_NOT_BE_RECORDED"
    with tempfile.TemporaryDirectory(prefix="mostaza-profile-cpu-") as directory:
        root = Path(directory)
        observe_server_environment(
            server, SimpleNamespace(root=root, event=lambda *a, **kw: None)
        )
        actual = server.build_env()
        assert all(actual[key] == value for key, value in ENVIRONMENT.items())
        saved = (root / "startup-configuration.json").read_text()
        assert "LOCAL_SECRET_MUST_NOT_BE_RECORDED" not in saved
        native_file = importlib.import_module("adk_submission.server").__file__
        assert native_file is not None
        native_source = Path(native_file)
        print(
            json.dumps(
                {
                    "kind": "CPU_NATIVE_BUILDERS_ONLY",
                    "adk_submission": version("adk-submission"),
                    "native_source_sha256": hashlib.sha256(
                        native_source.read_bytes()
                    ).hexdigest(),
                    "command": command,
                    "captured_environment": json.loads(saved)["environment"],
                    "gpu_model_started": False,
                    "server_start_called": False,
                }
            )
        )


if __name__ == "__main__":
    main()
