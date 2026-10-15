"""Offline source review only: never import setup, activate plugins or call a scorer."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import shlex
import subprocess
import zipfile
from pathlib import Path
from typing import Any

BASE = "b3d1f11fc588581aa0fc177aa23f02784629058d"
EVIDENCE = "docs/implementation/evidence/mostaza-pcv01-access"
PUBLIC_ROOT = "resources/official/pcv01-access-20261014"
PUBLIC_URL = "https://www.kaggle.com/competitions/gemma-4-developer-agent/data"
WHEEL_SHA = "9ad876581f3acde8ec3c369858f0834e2b9f41a3cffce3ca42f09cb090aea9d3"
PINS = {
    "sandbox/setup.py": (
        13883,
        "0263995ade90f83c8efa0ab5c7c9b7629696f39bc75274d58fc27ab774568409",
    ),
    "docker/Dockerfile.sandbox": (
        773,
        "2fef37c9275522eea4dc3371c60b54d9ba3cfa7871f89f1749aa92f34beff70a",
    ),
    "docker/Dockerfile.public": (
        988,
        "c92dfd9cd9ce019c4910a5334d6ecac606b612ec736a933b4af36da9c6fdf06c",
    ),
}
NATIVE_FILES = (
    "swegemma/config.py",
    "swegemma/harness/container_setup.py",
    "swegemma/harness/verification.py",
    "swegemma/sandbox/subprocess.py",
)
ATTESTATIONS = (
    "scorer_backend_attested",
    "scorer_source_equivalence_attested",
    "organizer_diagnostic_permission",
    "supported_observation_route",
    "actual_scorer_runtime_parity",
)


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def function(tree: ast.Module, name: str) -> ast.FunctionDef:
    matches = [
        n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name
    ]
    require(len(matches) == 1, "Expected one reviewed function: " + name)
    return matches[0]


def review_native_setup(source: bytes) -> dict[str, Any]:
    tree = ast.parse(source)
    condition = ast.parse(
        "type(docker).__name__ in {'SubprocessManager', 'SubprocessSandbox'}",
        mode="eval",
    ).body
    early = {}
    for name in ("install_editable_package", "install_test_dependencies"):
        fn = function(tree, name)
        body = fn.body[1:] if ast.get_docstring(fn) is not None else fn.body
        require(bool(body), "Missing native setup body")
        first = body[0]
        require(
            isinstance(first, ast.If)
            and ast.dump(first.test) == ast.dump(condition)
            and len(first.body) == 1
            and isinstance(first.body[0], ast.Return)
            and first.body[0].value is None
            and not first.orelse,
            "Subprocess setup must return before any install/dependency operation",
        )
        early[name] = {
            "line": first.lineno,
            "subprocess_action": "RETURN_WITHOUT_INSTALL",
        }
    dependency = function(tree, "install_test_dependencies")
    calls = {
        ast.unparse(n.func) for n in ast.walk(dependency) if isinstance(n, ast.Call)
    }
    require(
        {
            "resolve_sandbox_setup_script",
            "_ensure_container_site_packages",
            "docker.copy_to",
            "docker.exec",
        }
        <= calls,
        "Reviewed non-subprocess setup path changed",
    )
    require(
        any(
            isinstance(n, ast.Constant) and n.value == "--fast-path"
            for n in ast.walk(dependency)
        ),
        "Native fast-path selection changed",
    )
    return {
        "coverage": "STATIC_PINNED_SOURCE_NOT_RUNTIME",
        "subprocess_early_returns": early,
        "other_backend_path": (
            "Stages cached dependencies, resolves/copies "
            "setup and may execute --fast-path"
        ),
        "effective_selected_setup": None,
        "effective_selected_setup_reason": (
            "Resolver depends on runtime environment/config/files; not executed here"
        ),
    }


def review_public_setup(source: bytes) -> dict[str, Any]:
    tree = ast.parse(source)
    main = function(tree, "main")
    direct = [
        ast.unparse(n.value.func)
        for n in main.body
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
    ]
    require("install_editable_package" in direct, "Public main editable call missing")
    fast = function(tree, "execute_fast_path")
    literals = {
        n.value
        for n in ast.walk(fast)
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
    }
    require("workspace_paths.pth" in literals, "Reviewed path injection missing")
    calls = {ast.unparse(n.func) for n in ast.walk(fast) if isinstance(n, ast.Call)}
    require(
        {
            "target_pth.write_text",
            "ws_resolved.iterdir",
            "configure_workspace_pytest_ini",
            "configure_workspace_conftest",
        }
        <= calls,
        "Public fast-path contract changed",
    )
    install = function(tree, "install_editable_package")
    run_calls = [
        n
        for n in ast.walk(install)
        if isinstance(n, ast.Call) and ast.unparse(n.func) == "subprocess.run"
    ]
    require(
        len(run_calls) == 2
        and all(
            any(
                k.arg == "check"
                and isinstance(k.value, ast.Constant)
                and k.value.value is False
                for k in n.keywords
            )
            for n in run_calls
        ),
        "Reviewed unchecked editable/fallback operations changed",
    )
    return {
        "coverage": "STATIC_PUBLIC_DEVELOPMENT_SOURCE_NOT_EXECUTED",
        "main_calls_editable_install": True,
        "fast_path_writes_workspace_paths_pth": True,
        "fast_path_configures_pytest_ini_and_conftest": True,
        "editable_install_result": None,
        "editable_install_result_reason": (
            "Script not executed; unchecked fallback code is not an observed failure"
        ),
    }


def review_docker_recipe(source: bytes) -> dict[str, Any]:
    text = source.decode().replace("\\\n", " ")
    bases = re.findall(r"^FROM\s+(\S+)", text, flags=re.MULTILINE)
    require(bases == ["python:3.13-slim"], "Reviewed public base recipe changed")
    command = re.search(r"\bpip install ([^&]+)", text)
    require(command is not None, "Public pytest installation missing")
    packages = shlex.split(command.group(1)) if command else []
    require("pytest" in packages, "Reviewed unpinned pytest requirement changed")
    return {
        "coverage": "STATIC_RECIPE_NOT_BUILT_OR_RUN",
        "base_tag": bases[0],
        "python_minor_declared": "3.13",
        "python_patch_version": None,
        "pytest_requirement": "pytest",
        "pytest_version": None,
        "image_digest": None,
        "unknown_reason": (
            "Mutable base tag and unpinned pytest; no effective build/runtime manifest"
        ),
    }


def review_runtime_sources(native: dict[str, bytes]) -> dict[str, Any]:
    tree = ast.parse(native["swegemma/sandbox/subprocess.py"])
    cls = next(
        n
        for n in tree.body
        if isinstance(n, ast.ClassDef) and n.name == "SubprocessManager"
    )
    ctor = next(
        n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "__init__"
    )
    defaults = dict(
        zip(
            (a.arg for a in ctor.args.args[-len(ctor.args.defaults) :]),
            ctor.args.defaults,
            strict=True,
        )
    )
    require(
        isinstance(defaults["system_site_packages"], ast.Constant)
        and defaults["system_site_packages"].value is True,
        "Reviewed native inherited site-packages default changed",
    )
    environment = next(
        n
        for n in ast.walk(cls)
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "extra_env" for t in n.targets)
    )
    if not isinstance(environment.value, ast.Dict):
        raise ValueError("Native environment declaration changed")
    fields = {
        k.value: v
        for k, v in zip(environment.value.keys, environment.value.values, strict=True)
        if isinstance(k, ast.Constant)
    }
    require(
        ast.unparse(fields["PYTHONPATH"]) == "str(workspace_dir)",
        "Native workspace import path changed",
    )
    verification = native["swegemma/harness/verification.py"].decode()
    require(
        "PYTHONSAFEPATH=1 PYTHONNOUSERSITE=1 python3 -s -m pytest {test_files_str}"
        in verification,
        "Reviewed fixed verifier command changed",
    )
    config = ast.parse(native["swegemma/config.py"])
    eval_config = next(
        n for n in config.body if isinstance(n, ast.ClassDef) and n.name == "EvalConfig"
    )
    field_names = sorted(
        n.target.id
        for n in eval_config.body
        if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)
    )
    return {
        "coverage": "STATIC_PINNED_SOURCE_NOT_ACTUAL_SCORER_RUNTIME",
        "subprocess_system_site_packages_default": True,
        "subprocess_pythonpath_assignment": "str(workspace_dir)",
        "pytest_command_template": (
            "PYTHONSAFEPATH=1 PYTHONNOUSERSITE=1 python3 "
            "-s -m pytest <native targets/options>"
        ),
        "inspected_eval_config_fields": field_names,
        "host_runtime_vs_verifier_runtime": (
            "Separate identities; Docker Python3.13 recipe"
            " is not a scorer execution manifest"
        ),
        "effective_scorer_python_pytest_image": None,
        "effective_scorer_runtime_reason": (
            "No verified organizer manifest or real scorer-process observation"
        ),
    }


def compatibility_status(metadata: dict[str, Any] | None) -> dict[str, Any]:
    record = metadata or {}
    require(
        record.get("publication_authorized", False) is False
        and record.get("messages_sent", 0) == 0,
        "Organizer publication is outside the approved A/B scope",
    )
    claims = record.get("attestations", {})
    require(
        isinstance(claims, dict) and not set(claims) - set(ATTESTATIONS),
        "Unknown attestation field",
    )
    require(
        all(value is None for value in claims.values()),
        "CPU source review cannot promote unverified organizer/scorer claims",
    )
    reason = (
        "No verified organizer response or actual "
        "scorer-process evidence; public assets and "
        "CPU API parity do not attest scoring"
    )
    return {
        "status": "PENDING_HOST_CONFIRMATION",
        **{key: None for key in ATTESTATIONS},
        "missing_reasons": dict.fromkeys(ATTESTATIONS, reason),
        "unverified_response_url": record.get("response_url"),
        "gpu_readiness": False,
        "gpu_readiness_reason": (
            "Existing verification-origin guard remains "
            "blocked; no real integration authorized"
        ),
        "discussion_publication_authorized": False,
    }


def public_sources(root: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    manifest = json.loads((root / EVIDENCE / "public-sources.json").read_text())
    require(manifest["schema_version"] == 1, "Unsupported public source inventory")
    rows = manifest["sources"]
    require(
        len(rows) == len(PINS) and {r["source_path"] for r in rows} == set(PINS),
        "Only three reviewed public text artifacts are allowed",
    )
    base = root / PUBLIC_ROOT
    actual = {str(p.relative_to(base)) for p in base.rglob("*") if p.is_file()}
    require(actual == set(PINS), "Unexpected file in bounded public source directory")
    sources = {}
    for row in rows:
        name = row["source_path"]
        size, pin = PINS[name]
        require(
            row["local_path"] == PUBLIC_ROOT + "/" + name
            and row["source_url"] == PUBLIC_URL,
            "Unreviewed public source location",
        )
        path = root / row["local_path"]
        require(
            path.resolve() == path.absolute() and not path.is_symlink(),
            "Source must not redirect to another location",
        )
        require(path.stat().st_size == size <= 256 * 1024, "Public source size changed")
        data = path.read_bytes()
        data.decode("utf-8")
        require(
            len(data) == row["bytes"] == size and sha(data) == row["sha256"] == pin,
            "Public source bytes/pin changed",
        )
        require(
            row["numeric_source_version"] is None
            and bool(row["version_missing_reason"]),
            "Do not invent a numeric competition-file version",
        )
        sources[name] = data
    total = sum(map(len, sources.values()))
    require(
        total == manifest["source_download_bytes"] and total <= 1024 * 1024,
        "Download budget exceeded",
    )
    wrapper = manifest["metric_bootstrap_wrapper"]
    require(
        wrapper["value"] is None and bool(wrapper["reason"]),
        "No public metric wrapper was acquired/attested",
    )
    return sources, manifest


def frozen_inputs(root: Path) -> int:
    paths = [
        "submission",
        "experiments",
        "notebooks",
        "pyproject.toml",
        "uv.lock",
        "resources/manifest.json",
        "docs/implementation/evidence",
        "src/mostaza/evaluation/verification_origin.py",
        "src/mostaza/evaluation/context_candidate.py",
        "src/mostaza/evaluation/pytest_origin_receipt.py",
        "scripts/check_pcv01.py",
        "scripts/pcv01_cpu_fixtures.py",
    ]
    names = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", BASE, "--", *paths],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    for name in names:
        old = subprocess.run(
            ["git", "show", f"{BASE}:{name}"], cwd=root, capture_output=True, check=True
        ).stdout
        require(
            (root / name).read_bytes() == old,
            "Protected historical/verifier input changed: " + name,
        )
    readiness = json.loads(
        (
            root
            / "docs/implementation/evidence/mostaza-context-verification/readiness.json"
        ).read_text()
    )
    require(readiness["ready_for_gpu"] is False, "GPU readiness must stay blocked")
    return len(names)


def validate(root: Path) -> dict[str, Any]:
    public, manifest = public_sources(root)
    wheel = root / "resources/official/swegemma-0.2.11-py3-none-any.whl"
    require(sha(wheel.read_bytes()) == WHEEL_SHA, "Official native wheel changed")
    site = root / ".tools/official/lib/python3.13/site-packages"
    require(
        not (site / "mostaza_origin_receipt.py").exists()
        and not (site / "mostaza_origin_receipt_config.json").exists(),
        "Diagnostic plugin must not be installed in the working official environment",
    )
    native = {}
    with zipfile.ZipFile(wheel) as archive:
        for name in NATIVE_FILES:
            source = archive.read(name)
            installed = root / ".tools/official/lib/python3.13/site-packages" / name
            require(
                installed.read_bytes() == source,
                "Installed verifier/bootstrap differs from pinned wheel",
            )
            native[name] = source
    metadata = json.loads((root / EVIDENCE / "organizer-status.json").read_text())
    return {
        "status": "PASS_CPU_STATIC_REVIEW",
        "public_setup_acquired": True,
        "source_hash_verified": True,
        "development_backend_reviewed": True,
        "public_source_bytes": manifest["source_download_bytes"],
        "public_source_sha256": {name: sha(data) for name, data in public.items()},
        "native_source_sha256": {name: sha(data) for name, data in native.items()},
        "native_setup_review": review_native_setup(
            native["swegemma/harness/container_setup.py"]
        ),
        "public_setup_review": review_public_setup(public["sandbox/setup.py"]),
        "docker_recipe_review": {
            name: review_docker_recipe(data)
            for name, data in public.items()
            if name.startswith("docker/")
        },
        "runtime_source_review": review_runtime_sources(native),
        "compatibility": compatibility_status(metadata),
        "protected_files_unchanged": frozen_inputs(root),
        "setup_imported_or_executed": False,
        "docker_images_built_or_downloaded": False,
        "real_verifier_changed": False,
        "model_calls": 0,
        "remote_compute_sessions_started": 0,
    }
