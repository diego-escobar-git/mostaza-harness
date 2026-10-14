"Offline observed B180 preparation and exact-version supervision decisions."

from __future__ import annotations

import ast
import hashlib
import json
import math
import re
import subprocess
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from urllib.parse import parse_qs, urlsplit

BASE_NOTEBOOK = "notebooks/mostaza-phase2-budget-retrieval.ipynb"
NOTEBOOK = "notebooks/mostaza-phase2-observed.ipynb"
BASE_SHA256 = "02d410a2cec6d833426eed6cd8fcfee43d8b16c8e537592e92a87ec32cc0c4c2"
POLICY = {
    "id": "B180-observed-v2",
    "startup_seconds": 1800,
    "last_admission_seconds": 5340,
    "work_seconds": 5940,
    "request_stop_seconds": 6240,
    "latest_stop_seconds": 6300,
    "ceiling_seconds": 7200,
    "observer_interval_seconds": 5,
    "supervisor_interval_seconds": 60,
    "evaluations": 6,
    "allocations": 1,
    "retries": 0,
    "gpu_count": 4,
    "minimum_reported_quota_seconds": 28800,
    "paid_purchases_usd": 0,
}

GUARD = r"""import math as observation_math
import re as observation_re
import time as observation_time
import uuid as observation_uuid

BROWSER_AUTHORIZATION = None
OBSERVATION_NAMESPACE = {"__name__": "mostaza_startup_observation"}


def require_launch_ready():
    receipt = BROWSER_AUTHORIZATION
    if not isinstance(receipt, dict) or receipt.get("policy") != __POLICY__:
        raise RuntimeError("New observed-v2 quota authorization is absent")
    if receipt.get("approved") is not True or not receipt.get("approval_id"):
        raise RuntimeError("Explicit new human authorization is required")
    try:
        observation_uuid.UUID(receipt["single_use_id"])
    except (ValueError, TypeError, KeyError, AttributeError):
        raise RuntimeError("Fresh UUID notebook identity is required") from None
    if not isinstance(receipt.get("ref"), str) or not observation_re.fullmatch(
        r"diegofescobar/mostaza-b180-[0-9a-f]{32}", receipt["ref"]
    ):
        raise RuntimeError("Fresh dedicated notebook reference is required")
    if not isinstance(receipt.get("code_commit"), str) or not observation_re.fullmatch(
        r"[0-9a-f]{40}", receipt["code_commit"]
    ):
        raise RuntimeError("Exact code provenance is required")
    if (
        receipt.get("prelaunch_latest_versions_terminal") is not True
        or receipt.get("prelaunch_quota_stable") is not True
    ):
        raise RuntimeError(
            "Prelaunch terminal-version and stable-quota checks required"
        )
    if receipt.get("reserved_quota_seconds") != 0 or receipt.get("active_events") != 0:
        raise RuntimeError("Prelaunch allocation state is missing or nonempty")
    remaining = receipt.get("remaining_quota_seconds")
    if (
        not isinstance(remaining, (int, float))
        or not observation_math.isfinite(remaining)
        or remaining < 28800
    ):
        raise RuntimeError("Insufficient freshly observed quota")
    start = receipt.get("t0_epoch")
    if not isinstance(start, (int, float)) or not observation_math.isfinite(start):
        raise RuntimeError("External prelaunch clock missing")
    quota_time = receipt.get("quota_observed_epoch")
    if (
        not isinstance(quota_time, (int, float))
        or not observation_math.isfinite(quota_time)
        or not 0 <= start - quota_time <= 60
    ):
        raise RuntimeError("Fresh quota observation is required")
    if observation_time.time() < start - 5 or observation_time.time() >= start + 6240:
        raise RuntimeError("External prelaunch clock expired or inconsistent")


require_launch_ready()
exec(
    compile(__OBSERVER_SOURCE__, "startup_observation.py", "exec"),
    OBSERVATION_NAMESPACE,
)
OBSERVATION_PATH = OBSERVATION_NAMESPACE["Path"]
STARTUP_OBSERVER = OBSERVATION_NAMESPACE["StartupObserver"](
    OBSERVATION_PATH("/kaggle/working/private-phase2-evidence")
    / BROWSER_AUTHORIZATION["single_use_id"],
    BROWSER_AUTHORIZATION["t0_epoch"],
)
STARTUP_OBSERVER.start()


class ObservedSession:
    def __init__(self, receipt):
        self.start_epoch = receipt["t0_epoch"]
        self.deadline_epoch = self.start_epoch + 6240
        self.startup_deadline_epoch = self.start_epoch + 1800
        self.code_commit = receipt["code_commit"]
        self.run_url = "https://www.kaggle.com/code/" + receipt["ref"]

    def require_remaining(self, seconds):
        require_launch_ready()
        STARTUP_OBSERVER.check()
        if self.deadline_epoch - observation_time.time() < seconds:
            raise RuntimeError("Insufficient remaining session allowance")

    def require_startup_ready(self):
        self.require_remaining(0)
        if observation_time.time() >= self.startup_deadline_epoch:
            raise RuntimeError("Thirty-minute startup deadline exceeded")

    def record_stop_request(self, directory):
        record = {
            "event": "BROWSER_STOP_REQUIRED",
            "run_url": self.run_url,
            "physical_release_confirmed": None,
        }
        (directory / "browser-stop-request.json").write_text(__JSON__.dumps(record))
        print("MOSTAZA_BROWSER_STOP_REQUIRED", __JSON__.dumps(record), flush=True)


PLATFORM_SESSION = ObservedSession(BROWSER_AUTHORIZATION)
STARTUP_OBSERVER.stage("bootstrap.begin")
"""


@dataclass(frozen=True)
class VersionIdentity:
    """Bind an observed opaque ID; never derive it from a version number."""

    ref: str
    version_number: int
    script_version_id: int
    browser_url: str

    def __post_init__(self) -> None:
        parsed = urlsplit(self.browser_url)
        query = parse_qs(parsed.query)
        if (
            type(self.version_number) is not int
            or self.version_number < 1
            or type(self.script_version_id) is not int
            or self.script_version_id < 1
            or parsed.scheme != "https"
            or parsed.netloc != "www.kaggle.com"
            or parsed.path != "/code/" + self.ref
            or query.get("scriptVersionId") != [str(self.script_version_id)]
        ):
            raise ValueError("Browser URL does not establish the exact saved version")


def supervisor_action(
    elapsed: float,
    *,
    expected_ref: str,
    expected_script_version_id: int,
    observed_ref: str | None,
    observed_script_version_id: int | None,
    sdk_status: str | None,
    browser_status: str | None,
    version_cancel_available: bool,
    model_ready: bool | None,
    active_event_visible: bool,
    observation_failed: bool = False,
    control_unavailable_seconds: float = 0,
) -> str:
    "An absent event is not a stop signal; bind all actions to one version."
    identity = (
        type(expected_script_version_id) is int
        and expected_script_version_id > 0
        and bool(re.fullmatch(r"[^/]+/[^/]+", expected_ref))
        and observed_ref == expected_ref
        and observed_script_version_id == expected_script_version_id
    )
    if not identity:
        return "IDENTIFY_EXACT_VERSION_OR_ESCALATE"
    terminal = {"COMPLETE", "ERROR", "CANCEL_ACKNOWLEDGED"}
    if sdk_status in terminal and sdk_status == browser_status:
        return "VERIFY_QUOTA_STABILITY_AND_CLOSE"
    if sdk_status == "CANCEL_REQUESTED" or browser_status == "CANCEL_REQUESTED":
        if not math.isfinite(elapsed) or elapsed >= 6300:
            return "ESCALATE_UNCONFIRMED_TERMINATION"
        return "WAIT_FOR_TERMINAL_CONFIRMATION"
    stop = (
        not math.isfinite(elapsed)
        or elapsed < 0
        or elapsed >= 6240
        or (elapsed >= 1800 and model_ready is not True)
        or observation_failed
    )
    if stop:
        return (
            "STOP_EXACT_VERSION"
            if version_cancel_available
            else "ESCALATE_STOP_CONTROL"
        )
    if sdk_status in terminal or browser_status in terminal:
        return "RECONCILE_EXACT_VERSION_STATUS"
    if not version_cancel_available:
        if (
            not math.isfinite(control_unavailable_seconds)
            or control_unavailable_seconds >= 60
        ):
            return "ESCALATE_STOP_CONTROL"
        return "RESTORE_EXACT_VERSION_STOP_CONTROL"
    if sdk_status in {None, "QUEUED", "RUNNING"} and browser_status in {
        "QUEUED",
        "RUNNING",
    }:
        return (
            "SUPERVISE_ACTIVE_EVENT"
            if active_event_visible
            else "SUPERVISE_EXACT_VERSION"
        )
    return "RECONCILE_EXACT_VERSION_STATUS"


def _replace_once(code: str, old: str, new: str) -> str:
    if code.count(old) != 1:
        raise ValueError("Notebook transformation anchor changed: " + old[:70])
    return code.replace(old, new, 1)


def validate_launch_receipt(
    receipt: dict[str, Any], now_epoch: float | None = None
) -> None:
    """Check the actual guard without bootstrap or observation IO."""
    allowed = {
        "policy",
        "approved",
        "approval_id",
        "single_use_id",
        "ref",
        "t0_epoch",
        "remaining_quota_seconds",
        "reserved_quota_seconds",
        "active_events",
        "code_commit",
        "prelaunch_latest_versions_terminal",
        "prelaunch_quota_stable",
        "quota_observed_epoch",
    }
    if set(receipt) != allowed:
        raise ValueError("Unknown or missing launch receipt fields")
    json.dumps(receipt, allow_nan=False)
    code = GUARD.replace("__POLICY__", repr(POLICY))
    tree = ast.parse(code)
    function = next(
        n
        for n in tree.body
        if isinstance(n, ast.FunctionDef) and n.name == "require_launch_ready"
    )
    namespace: dict[str, Any] = {
        "BROWSER_AUTHORIZATION": receipt,
        "observation_math": math,
        "observation_re": re,
        "observation_uuid": uuid,
        "observation_time": SimpleNamespace(
            time=lambda: time.time() if now_epoch is None else now_epoch
        ),
    }
    exec(
        compile(ast.Module(body=[function], type_ignores=[]), "launch_guard", "exec"),
        namespace,
    )
    namespace["require_launch_ready"]()


def _source_literal(source: str) -> str:
    "Keep the pinned host module literal readable inside a generated cell."
    pieces = [repr(source[i : i + 30]) for i in range(0, len(source), 30)]
    return "(\n" + "".join("        " + p + "\n" for p in pieces) + ")"


def build_observed_notebook(root: Path, receipt: dict[str, Any] | None = None) -> bytes:
    raw = (root / BASE_NOTEBOOK).read_bytes()
    if hashlib.sha256(raw).hexdigest() != BASE_SHA256:
        raise ValueError("Original preparation notebook changed")
    notebook = json.loads(raw)
    observer_source = (
        root / "src/mostaza/evaluation/startup_observation.py"
    ).read_text()
    guard = GUARD.replace("__POLICY__", repr(POLICY))
    if receipt is not None:
        validate_launch_receipt(receipt)
        guard = guard.replace(
            "BROWSER_AUTHORIZATION = None",
            "BROWSER_AUTHORIZATION = " + repr(receipt),
            1,
        )
    guard = guard.replace("__OBSERVER_SOURCE__", _source_literal(observer_source))
    guard = guard.replace("__JSON__", 'OBSERVATION_NAMESPACE["json"]')
    notebook["cells"][1]["source"] = guard.splitlines(keepends=True)
    notebook["cells"][2]["source"] += [
        '\nSTARTUP_OBSERVER.stage("bootstrap.complete")\n'
    ]
    preflight = "".join(notebook["cells"][3]["source"])
    preflight = _replace_once(
        preflight,
        "# Offline wheel installation",
        ('STARTUP_OBSERVER.stage("inputs.verified")\n# Offline wheel installation'),
    )
    preflight = _replace_once(
        preflight,
        "subprocess.run(\n",
        ('STARTUP_OBSERVER.stage("packages.install.begin")\nsubprocess.run(\n'),
    )
    preflight = _replace_once(
        preflight,
        "for package, expected in [",
        (
            'STARTUP_OBSERVER.stage("packages.install.comp'
            'lete")\nfor package, expected in ['
        ),
    )
    preflight = _replace_once(
        preflight,
        'torch = importlib.import_module("torch")',
        (
            'STARTUP_OBSERVER.stage("torch.import.begin")\n'
            'torch = importlib.import_module("torch")\nSTAR'
            'TUP_OBSERVER.stage("torch.import.complete")'
        ),
    )
    preflight += '\nSTARTUP_OBSERVER.stage("preflight.complete")\n'
    notebook["cells"][3]["source"] = preflight.splitlines(keepends=True)
    code = "".join(notebook["cells"][5]["source"])
    code = _replace_once(
        code,
        (
            "require_launch_ready()  # Authorization alone"
            " never bypasses the allocation blocker."
        ),
        (
            'STARTUP_OBSERVER.stage("execution.imports.com'
            'plete")\nrequire_launch_ready()'
        ),
    )
    code = _replace_once(
        code,
        (
            'RUN_ROOT = Path("/kaggle/working/private-phas'
            'e2-evidence") / str(uuid.uuid4())\nRUN_ROOT.mk'
            "dir(parents=True, exist_ok=False)"
        ),
        ('RUN_ROOT = STARTUP_OBSERVER.root\nSTARTUP_OBSERVER.stage("compiler.begin")'),
    )
    code = _replace_once(
        code,
        "litellm.drop_params = True",
        ('STARTUP_OBSERVER.stage("compiler.complete")\nlitellm.drop_params = True'),
    )
    code = _replace_once(
        code,
        (
            "    PLATFORM_SESSION.require_remaining(1200 +"
            " 6 * 600 + 300)\n    server.start()"
        ),
        (
            "    export_sources()\n    PLATFORM_SESSION.req"
            "uire_startup_ready()\n    PLATFORM_SESSION.req"
            "uire_remaining(2100)\n    server.config.startu"
            "p_timeout = min(1200, max(1, int(PLATFORM_SES"
            "SION.startup_deadline_epoch - time.time())))\n"
            '    OBSERVATION_NAMESPACE["start_observed_ser'
            'ver"](server, STARTUP_OBSERVER)\n    PLATFORM_'
            'SESSION.require_startup_ready()\n    print("MO'
            'STAZA_MODEL_READY", time.time(), flush=True)\n'
            '    STARTUP_OBSERVER.stage("registry.begin")'
        ),
    )
    code = _replace_once(
        code,
        (
            "    tasks = {t.instance_id: t for t in load_t"
            'asks(DATA_DIR / "tasks.jsonl")}'
        ),
        (
            '    STARTUP_OBSERVER.stage("registry.complete'
            '")\n    tasks = {t.instance_id: t for t in loa'
            'd_tasks(DATA_DIR / "tasks.jsonl")}\n    STARTU'
            'P_OBSERVER.stage("tasks.loaded")'
        ),
    )
    code = _replace_once(
        code,
        "                result = await asyncio.wait_for(",
        (
            "                STARTUP_OBSERVER.check()\n    "
            '            STARTUP_OBSERVER.stage("evaluatio'
            'n.task")\n                STARTUP_OBSERVER.eve'
            'nt("task.start", configuration=configuration,'
            ' instance_id=selected["instance_id"])\n       '
            "         result = await asyncio.wait_for("
        ),
    )
    code = _replace_once(
        code,
        "                row.update(",
        (
            '                STARTUP_OBSERVER.event("task.'
            'acquired", configuration=configuration, insta'
            'nce_id=selected["instance_id"])\n             '
            "   row.update("
        ),
    )
    code = _replace_once(
        code,
        (
            "        finally:\n            export_sources()"
            "\n            # Must release allocation even o"
            "n exceptions, not only stop vLLM.\n           "
            " # A notebook-local callback is NOT a verifie"
            "d termination guarantee.\n            PLATFORM"
            "_SESSION.terminate_and_confirm()"
        ),
        (
            "        finally:\n            STARTUP_OBSERVER"
            ".close()\n            PLATFORM_SESSION.record_"
            "stop_request(RUN_ROOT)\n            export_sou"
            "rces()"
        ),
    )
    # Native stop may delete server-source.log; server-retained.log remains linked.
    code = _replace_once(
        code,
        (
            "    # PLATFORM_SESSION remains unavailable; t"
            "his loop cannot start in this delivery.\n    #"
            " Its future verified adapter must account for"
            " startup before this code runs."
        ),
        ("    # External browser supervision includes queue and cold start."),
    )
    code = _replace_once(
        code,
        (
            "# A verified allocation adapter must supply t"
            "hese before this loop can be enabled:\n# absol"
            "ute session-start/deadline, remaining quota, "
            "external termination watchdog,\n# confirmed ca"
            "ncellation/normal completion and single-use b"
            "atch authorization.\n# No manufactured first-c"
            "ell start time, timer receipt or quota estima"
            "te is accepted."
        ),
        (
            "# The browser supervisor uses the prelaunch c"
            "lock and exact version.\n# Notebook observatio"
            "ns do not establish physical GPU release."
        ),
    )
    notebook["cells"][5]["source"] = code.splitlines(keepends=True)
    notebook["cells"][0]["source"] = [
        (
            "# Mostaza observed B180 preparation\n\nNew quot"
            "a authorization required. GPU and internet di"
            "sabled. No evaluation has run.\n"
        )
    ]
    notebook["cells"][4]["source"] = [
        (
            "## Native evaluator with persistent startup o"
            "bservations\n\nOne LlmAgent per original arm. B"
            "rowser stopping is external and version-bound"
            ".\n"
        )
    ]
    notebook["metadata"]["mostaza"]["observed_preparation"] = {
        "policy": POLICY,
        "authorization": None if receipt is None else receipt["approval_id"],
        "physical_release_guaranteed": False,
        "observer_source_sha256": hashlib.sha256(observer_source.encode()).hexdigest(),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    notebook["cells"].insert(
        5,
        {
            "cell_type": "code",
            "id": "observed-imports-stage",
            "metadata": {},
            "execution_count": None,
            "outputs": [],
            "source": ['STARTUP_OBSERVER.stage("execution.imports.begin")\n'],
        },
    )
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            ast.parse("".join(cell["source"]), feature_version=(3, 12))
    formatted = subprocess.run(
        [str(root / ".venv/bin/ruff"), "format", "--stdin-filename", NOTEBOOK, "-"],
        input=json.dumps(notebook).encode(),
        check=True,
        capture_output=True,
        timeout=30,
    ).stdout
    return (
        json.dumps(json.loads(formatted), sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()
