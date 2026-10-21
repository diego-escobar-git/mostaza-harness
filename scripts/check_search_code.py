"""search-code:AC-8 deterministic CPU evidence; never runs a model or Kaggle."""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "submission/skills/search-code/scripts/search_code.py"
SNAPSHOTS = (
    "requests_7205",
    "requests_7315",
    "requests_7502",
    "fastapi_15589",
    "rich_3061",
)
LIMITS = {
    "cold_seconds": 45,
    "warm_seconds": 3,
    "refresh_seconds": 10,
    "peak_rss_bytes": 256 * 1024**2,
    "database_bytes": 128 * 1024**2,
}
EXCLUDED = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "vendor",
    "solution",
    "reference",
    "test_patch",
    "task.json",
    "tasks.jsonl",
}
EXPECTED_CHECKS = {
    "format",
    "lint",
    "types",
    "unit",
    "integration",
    "build",
    "official-historical",
    "paired-evidence",
    "official-active",
    "python312",
    "standalone-lint",
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def environment() -> dict[str, str]:
    return {
        **os.environ,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": str(ROOT / "src"),
    }


def extract_source(archive: Path, destination: Path) -> dict[str, Any]:
    """Extract regular source only, validating every member before any write."""
    with tarfile.open(archive) as bundle:
        members = bundle.getmembers()
        seen: set[str] = set()
        rejected_links = 0
        for member in members:
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts or "\\" in member.name:
                raise ValueError(f"Unsafe archive path: {member.name}")
            if member.issym() or member.islnk():
                rejected_links += 1
                continue
            if not (member.isdir() or member.isfile()):
                raise ValueError(f"Nonregular archive entry: {member.name}")
            if member.isfile() and str(name) in seen:
                raise ValueError(f"Duplicate archive entry: {member.name}")
            seen.add(str(name))
        hashes: dict[str, str] = {}
        for member in members:
            name = PurePosixPath(member.name)
            if not member.isfile() or any(part in EXCLUDED for part in name.parts):
                continue
            # Source snapshots alone are inputs; never task rows/graphs/patches.
            if name.suffix not in {
                ".py",
                ".md",
                ".rst",
                ".txt",
                ".toml",
                ".cfg",
                ".ini",
            }:
                continue
            if member.size > 1024**2:
                raise ValueError(f"Oversized source member: {member.name}")
            source = bundle.extractfile(member)
            if source is None:
                raise ValueError("Missing regular archive data")
            data = source.read()
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                continue
            target = destination.joinpath(*name.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            hashes[str(name)] = digest(data)
    if not hashes:
        raise ValueError("Snapshot contains no source")
    return {
        "archive_sha256": digest(archive.read_bytes()),
        "files": len(hashes),
        "rejected_entries": {"symlink_or_hardlink": rejected_links},
        "source_sha256": digest(json.dumps(hashes, sort_keys=True).encode()),
    }


def source_queries(root: Path) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if len(node.name) >= 8 and not node.name.startswith("_"):
                    candidates.append(
                        {
                            "query": node.name,
                            "path": path.relative_to(root).as_posix(),
                            "start_line": node.lineno,
                            "end_line": node.end_lineno,
                        }
                    )
    counts = Counter(case["query"] for case in candidates)
    cases = sorted(
        (case for case in candidates if counts[case["query"]] == 1),
        key=lambda case: (case["path"], case["start_line"]),
    )[:3]
    if len(cases) != 3:
        raise ValueError("Three unambiguous source-derived queries required")
    for case in cases:
        case["query_sha256"] = digest(case["query"].encode())
    return cases


# Resource measurement runs inside each individual CLI child, never the driver.
MEASURE = r"""
import atexit, json, resource, runpy, sys
metrics, script, *arguments = sys.argv[1:]
@atexit.register
def report():
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    with open(metrics, "w") as output:
        json.dump({"raw_peak_rss": peak,
                   "raw_unit": "bytes" if sys.platform == "darwin" else "KiB",
                   "peak_rss_bytes": peak if sys.platform == "darwin" else peak * 1024,
                   "python_version": sys.version}, output)
sys.argv = [script, *arguments]
runpy.run_path(script, run_name="__main__")
"""


def measure(
    python: Path,
    script: Path,
    root: Path,
    temporary: Path,
    mode: str,
    arguments: list[str],
    limit: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    metrics = temporary / "child-metrics.json"
    metrics.unlink(missing_ok=True)
    argv = [
        str(python),
        "-c",
        MEASURE,
        str(metrics),
        str(script),
        mode,
        "--root",
        str(root),
        *arguments,
    ]
    started = time.monotonic()
    process = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        timeout=limit + 5,
        env={**environment(), "TMPDIR": str(temporary)},
    )
    elapsed = time.monotonic() - started
    if process.returncode or process.stderr or len(process.stdout) > 4500:
        raise ValueError(
            f"CLI failure: {process.returncode}: "
            f"{process.stdout[:500]} {process.stderr[:500]}"
        )
    value = json.loads(process.stdout)
    if value.get("schema_version") != 1 or value.get("status") != "ok":
        raise ValueError(f"Non-successful CLI: {value}")
    record = {
        **json.loads(metrics.read_text()),
        "seconds": elapsed,
        "index": value["index"],
        "mode": mode,
        "cli_argv": [str(python), str(script), mode, "--root", str(root), *arguments],
        "measurement_launcher_sha256": digest(MEASURE.encode()),
    }
    if elapsed > limit or record["peak_rss_bytes"] > LIMITS["peak_rss_bytes"]:
        raise ValueError(f"CPU/RSS limit exceeded: {record}")
    if value["index"]["database_bytes"] > LIMITS["database_bytes"]:
        raise ValueError("Database limit exceeded")
    return value, record


def assert_hit(value: dict[str, Any], case: dict[str, Any]) -> None:
    if not any(
        all(hit.get(key) == case[key] for key in ("path", "start_line", "end_line"))
        and hit.get("name") == case["query"]
        for hit in value.get("results", [])[:5]
    ):
        raise ValueError(f"Exact top-5 source location missing: {case}")


def benchmark_snapshot(archive: Path, python: Path, base: Path) -> dict[str, Any]:
    root, temporary = base / "workspace with spaces", base / "temporary"
    root.mkdir(parents=True)
    temporary.mkdir()
    provenance = extract_source(archive, root)
    cases = source_queries(root)
    cold, cold_measure = measure(
        python,
        SCRIPT,
        root,
        temporary,
        "bootstrap",
        ["--query", cases[0]["query"], "--limit", "5"],
        45,
    )
    assert_hit(cold, cases[0])
    executable = Path(cold["executable_path"])
    if executable.read_bytes() != SCRIPT.read_bytes():
        raise ValueError("Bootstrap source differs")
    warm_records = []
    for case in cases:
        value, measured = measure(
            python,
            executable,
            root,
            temporary,
            "search",
            ["--query", case["query"], "--limit", "5"],
            3,
        )
        assert_hit(value, case)
        case["top5_match"] = next(
            {
                "rank": rank,
                **{key: hit[key] for key in ("name", "path", "start_line", "end_line")},
            }
            for rank, hit in enumerate(value["results"][:5], 1)
            if hit.get("name") == case["query"]
            and hit.get("path") == case["path"]
            and hit.get("start_line") == case["start_line"]
        )
        if measured["index"]["reparsed_files"] != 0:
            raise ValueError("Unchanged warm operation reparsed files")
        warm_records.append(measured)
    edited = root / cases[0]["path"]
    edited.write_bytes(
        edited.read_bytes() + b"\n# deterministic source-only refresh witness\n"
    )
    value, refresh = measure(
        python,
        executable,
        root,
        temporary,
        "search",
        ["--query", cases[0]["query"], "--limit", "5"],
        10,
    )
    assert_hit(value, cases[0])
    if (
        refresh["index"]["reparsed_files"] != 1
        or refresh["index"]["updated_files"] != 1
    ):
        raise ValueError("Single-file refresh must reparse exactly one file")
    return {
        "id": archive.stem,
        "status": "PASS",
        **provenance,
        "queries": cases,
        "cold": cold_measure,
        "warm": warm_records,
        "refresh": refresh,
        "edited_source_sha256": digest(edited.read_bytes()),
    }


def synthetic(python: Path, base: Path) -> dict[str, Any]:
    root, temporary = base / "workspace with spaces", base / "temporary"
    root.mkdir(parents=True)
    temporary.mkdir()
    (root / "callee.py").write_text("def target_symbol():\n    return 1\n")
    (root / "caller.py").write_text(
        "from callee import target_symbol\n"
        "def caller_symbol():\n    return target_symbol()\n"
    )
    (root / "nested.py").write_text(
        "async def async_symbol():\n    def nested_symbol():\n        return 1\n"
        "    return nested_symbol()\n\ndef duplicate(): pass\ndef duplicate(): pass\n"
    )
    (root / "notes.txt").write_text("nonpython_unique_marker\n")
    operations = []

    def invoke(mode: str, *args: str) -> dict[str, Any]:
        value, measured = measure(python, SCRIPT, root, temporary, mode, list(args), 10)
        operations.append(measured)
        return value

    graph = invoke("neighbors", "--symbol", "caller_symbol", "--edge-kind", "callees")
    names = {node["id"]: node["name"] for node in graph["nodes"]}
    edges = {
        (names[edge["source"]], names[edge["target"]], edge["kind"])
        for edge in graph["edges"]
    }
    if edges != {("caller_symbol", "target_symbol", "calls")}:
        raise ValueError(f"Unexpected supported graph: {edges}")
    nested = invoke("subgraph", "--symbol", "async_symbol", "--hops", "1")
    names = {node["id"]: node["name"] for node in nested["nodes"]}
    nested_edges = {
        (names[e["source"]], names[e["target"]], e["kind"]) for e in nested["edges"]
    }
    if nested_edges != {
        ("async_symbol", "nested_symbol", "calls"),
        ("async_symbol", "nested_symbol", "contains"),
        ("nested.py", "async_symbol", "contains"),
    }:
        raise ValueError("Nested/async containment missing")
    text = invoke("search", "--query", "nonpython_unique_marker")
    if not any(hit["path"] == "notes.txt" for hit in text["results"]):
        raise ValueError("Non-Python lexical retrieval failed")
    # Ambiguity is an expected handled non-ok response; measure it separately.
    ambiguous = subprocess.run(
        [
            str(python),
            str(SCRIPT),
            "neighbors",
            "--root",
            str(root),
            "--symbol",
            "duplicate",
        ],
        capture_output=True,
        text=True,
        timeout=15,
        env={**environment(), "TMPDIR": str(temporary)},
    )
    if (
        ambiguous.stderr
        or len(ambiguous.stdout) > 4500
        or json.loads(ambiguous.stdout).get("status") != "ambiguous"
    ):
        raise ValueError("Duplicate definitions must be explicitly ambiguous")
    (root / "callee.py").write_text("def renamed_symbol():\n    return 1\n")
    refreshed = invoke(
        "neighbors", "--symbol", "caller_symbol", "--edge-kind", "callees"
    )
    if (
        refreshed["edges"]
        or refreshed["index"]["reparsed_files"] != 1
        or not refreshed["unresolved_count"]
    ):
        raise ValueError("Dependent call edge did not invalidate")
    return {
        "status": "PASS",
        "expected_edges": [list(edge) for edge in sorted(edges)],
        "nested_edges": [list(edge) for edge in sorted(nested_edges)],
        "ambiguity": "ambiguous",
        "dependent_edges_invalidated": True,
        "non_python_retrieved": True,
        "operations": operations,
    }


def check_command(identifier: str, argv: list[str], cwd: Path = ROOT) -> dict[str, Any]:
    started = time.monotonic()
    print(json.dumps({"check": identifier, "event": "start"}), flush=True)
    try:
        result = subprocess.run(
            argv,
            cwd=cwd,
            env=environment(),
            capture_output=True,
            text=True,
            timeout=600,
        )
        skipped = (
            max(
                (int(value) for value in re.findall(r"(\d+) skipped", result.stdout)),
                default=0,
            )
            if "pytest" in argv
            else 0
        )
        return {
            "id": identifier,
            "argv": argv,
            "cwd": str(cwd),
            "exit_code": result.returncode,
            "status": "PASS" if result.returncode == 0 and skipped == 0 else "FAIL",
            "skipped_tests": skipped,
            "seconds": time.monotonic() - started,
            "output_tail": (result.stdout + result.stderr)[-5000:],
            "failure_lines": [
                line
                for line in (result.stdout + result.stderr).splitlines()
                if line.startswith(("E ", "FAILED ", "ERROR ", "tests/"))
            ][:100],
        }
    except (OSError, subprocess.TimeoutExpired) as error:
        return {
            "id": identifier,
            "argv": argv,
            "cwd": str(cwd),
            "status": "FAIL",
            "exit_code": None,
            "error": str(error),
            "seconds": time.monotonic() - started,
        }


def preflight() -> list[dict[str, Any]]:
    historical = Path(
        os.environ.get(
            "MOSTAZA_HISTORICAL_PHASE2_ROOT",
            "/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness",
        )
    )
    packet = ROOT / "results/kaggle-v2-358139443"
    paths = [
        historical,
        packet
        / "private-run-evidence/99c637be-d945-4dd7-85d8-4042cfcc2bad"
        / "source-inventory.json",
        packet / "mostaza-reviewed-input-836a861c-0811-4de8-b386-a2cedc7861d7",
        packet / "results.zip",
        packet / "mostaza-e0-e1-phase-1-paired-benchmark.ipynb",
    ]
    return [
        {
            "path": str(path),
            "status": "PRESENT_REQUIRES_EXISTING_PIN_CHECKS"
            if path.exists()
            else "MISSING",
        }
        for path in paths
    ]


def validate_reports(validation: dict[str, Any], benchmark: dict[str, Any]) -> None:
    """Reject missing, forged-clean, malformed and incomplete evidence."""
    if validation.get("schema_version") != 1 or benchmark.get("schema_version") != 1:
        raise ValueError("Unsupported report schema")
    checks = validation.get("checks", [])
    if {check.get("id") for check in checks} != EXPECTED_CHECKS or len(checks) != len(
        EXPECTED_CHECKS
    ):
        raise ValueError("Required child checks missing or duplicated")
    if any(
        not isinstance(check.get("argv"), list)
        or not check["argv"]
        or any(not isinstance(arg, str) or not arg for arg in check["argv"])
        or check.get("cwd") != str(ROOT)
        or check.get("status") not in {"PASS", "FAIL"}
        or (
            check["status"] == "PASS"
            and (check.get("exit_code") != 0 or check.get("skipped_tests", 0) != 0)
        )
        for check in checks
    ):
        raise ValueError("Invalid child status")
    prerequisites = validation.get("prerequisites", [])
    if len(prerequisites) != 5 or any(
        not item.get("path")
        or item.get("status") not in {"MISSING", "PRESENT_REQUIRES_EXISTING_PIN_CHECKS"}
        for item in prerequisites
    ):
        raise ValueError("Five explicit historical prerequisite checks required")
    snapshots = benchmark.get("snapshots", [])
    if [record.get("id") for record in snapshots] != list(SNAPSHOTS):
        raise ValueError("Exactly five mandatory snapshots required")
    if benchmark.get("limits") != LIMITS:
        raise ValueError("Unapproved CPU thresholds")
    for record in snapshots:
        if record.get("status") != "PASS":
            raise ValueError(f"Snapshot failed: {record.get('id')}")
        if any(
            not isinstance(record.get(key), str)
            or len(record[key]) != 64
            or any(char not in "0123456789abcdef" for char in record[key])
            for key in ("archive_sha256", "source_sha256", "edited_source_sha256")
        ):
            raise ValueError("Source hashes missing or invalid")
        if len(record.get("queries", [])) != 3:
            raise ValueError("Source query provenance missing")
        for case in record["queries"]:
            if (
                case.get("query_sha256") != digest(case["query"].encode())
                or not case.get("path")
                or not isinstance(case.get("start_line"), int)
                or not isinstance(case.get("end_line"), int)
                or not 1 <= case["start_line"] <= case["end_line"]
            ):
                raise ValueError("Invalid source query provenance")
            match = case.get("top5_match", {})
            if (
                not 1 <= match.get("rank", 0) <= 5
                or any(
                    match.get(key) != case[key]
                    for key in ("path", "start_line", "end_line")
                )
                or match.get("name") != case["query"]
            ):
                raise ValueError("Observed top-5 exact location witness missing")
        for measured, limit in [
            (record["cold"], 45),
            (record["refresh"], 10),
            *[(warm, 3) for warm in record["warm"]],
        ]:
            raw = measured.get("raw_peak_rss", 0)
            unit = measured.get("raw_unit")
            normalized = raw if unit == "bytes" else raw * 1024
            if unit not in {"bytes", "KiB"} or normalized != measured.get(
                "peak_rss_bytes"
            ):
                raise ValueError("Child RSS unit normalization invalid")
            if not (
                0 <= measured["seconds"] <= limit
                and 0 < measured["peak_rss_bytes"] <= LIMITS["peak_rss_bytes"]
                and 0 < measured["index"]["database_bytes"] <= LIMITS["database_bytes"]
            ):
                raise ValueError("Measured limit exceeded")
        if (
            len(record["warm"]) != 3
            or any(warm["index"]["reparsed_files"] != 0 for warm in record["warm"])
            or record["refresh"]["index"]["reparsed_files"] != 1
        ):
            raise ValueError("Invalid incremental counters")
    if (
        benchmark.get("synthetic", {}).get("status") != "PASS"
        or benchmark.get("synthetic_python312", {}).get("status") != "PASS"
        or benchmark.get("status") != "PASS"
    ):
        raise ValueError("Synthetic/CPU evidence incomplete")
    for key in ("synthetic", "synthetic_python312"):
        fixture = benchmark[key]
        if (
            fixture.get("expected_edges")
            != [["caller_symbol", "target_symbol", "calls"]]
            or not fixture.get("dependent_edges_invalidated")
            or fixture.get("ambiguity") != "ambiguous"
            or not fixture.get("non_python_retrieved")
        ):
            raise ValueError("Synthetic behavior witnesses missing")
    witness = validation.get("official_witness", {})
    if (
        set(witness.get("native_tools", []))
        != {
            "run_command",
            "read_file",
            "edit_file",
            "write_file",
            "get_status",
            "submit_patch",
        }
        or witness.get("refresh_reparsed") != [0, 1, 1, 1]
        or witness.get("llm_calls") != 0
        or not witness.get("patch_clean")
        or not witness.get("transient_resources_removed")
        or witness.get("docker_execution") != "NOT_RUN"
        or witness.get("kaggle_execution") != "NOT_RUN"
    ):
        raise ValueError("Official execution witness incomplete")
    expected_status = (
        "PASS"
        if all(check["status"] == "PASS" for check in checks)
        and all(
            item["status"] != "MISSING" for item in validation.get("prerequisites", [])
        )
        else "FAIL"
    )
    if validation.get("status") != expected_status:
        raise ValueError("Validation status contradicts failed checks/prerequisites")
    if validation.get("status") != "PASS":
        raise ValueError("Full regression gate failed; inspect exact child results")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.add_argument("--source-assets", type=Path, required=True)
    parser.add_argument("--official-python", type=Path, required=True)
    parser.add_argument("--python312", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    args = parser.parse_args()
    evidence = (ROOT / args.evidence_dir).resolve()
    if evidence != ROOT / "docs/implementation/evidence/2026-10-20-search-code":
        parser.error("Evidence output must be the two approved report paths")
    import mostaza

    if Path(mostaza.__file__).resolve().parent != ROOT / "src/mostaza":
        raise ValueError("mostaza must import from the current worktree")
    validation: dict[str, Any] = {
        "schema_version": 1,
        "status": "FAIL",
        "prerequisites": preflight(),
        "python": sys.version,
        "project_path": str(ROOT),
        "source_assets": str(args.source_assets.resolve()),
        "checks": [],
        "standalone_sha256": digest(SCRIPT.read_bytes()),
        "environment": {
            key: environment().get(key)
            for key in (
                "PYTHONDONTWRITEBYTECODE",
                "PYTHONPATH",
                "MOSTAZA_HISTORICAL_PHASE2_ROOT",
            )
        },
        "limitations": [
            "Local CPU only",
            "Docker source reviewed; Docker not executed",
            "Kaggle and model efficacy not executed",
        ],
    }
    benchmark: dict[str, Any] = {
        "schema_version": 1,
        "status": "FAIL",
        "limits": LIMITS,
        "platform": platform.platform(),
        "python": sys.version,
        "query_basis": (
            "Visible source AST only; no tasks, patches, solutions "
            "or precomputed graphs"
        ),
        "snapshots": [],
        "limitations": validation["limitations"],
    }
    python = Path(sys.executable)
    with tempfile.TemporaryDirectory(prefix="mostaza-search-validation-") as directory:
        temporary = Path(directory).resolve()
        checks = validation["checks"]
        commands = [
            ("format", ["-m", "ruff", "format", "--check", "."]),
            ("lint", ["-m", "ruff", "check", "."]),
            ("types", ["-m", "mypy", "src", "scripts"]),
            ("unit", ["-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/unit"]),
            (
                "integration",
                ["-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/integration"],
            ),
        ]
        for identifier, argv in commands:
            checks.append(check_command(identifier, [str(python), *argv]))
        project = temporary / "project"
        (project / "src").mkdir(parents=True)
        for name in ("pyproject.toml", "README.md", "LICENSE"):
            shutil.copyfile(ROOT / name, project / name)
        shutil.copytree(
            ROOT / "src/mostaza",
            project / "src/mostaza",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        checks.append(
            check_command(
                "build",
                [
                    str(python),
                    "-m",
                    "build",
                    "--no-isolation",
                    "--outdir",
                    str(temporary / "dist"),
                    str(project),
                ],
            )
        )
        checks.append(
            check_command(
                "official-historical",
                [
                    str(python),
                    "scripts/check_official.py",
                    "--check",
                    "--experiments",
                    "E0",
                    "E1",
                    "--compiler-python",
                    str(args.official_python),
                ],
            )
        )
        checks.append(
            check_command(
                "paired-evidence",
                [
                    str(python),
                    "scripts/check_evidence.py",
                    "--require-real-paired",
                    "--cohort",
                    "experiments/cohort.json",
                    "--evidence-dir",
                    "docs/implementation/evidence/mostaza-phase1-foundation",
                ],
            )
        )
        checks.append(
            check_command(
                "standalone-lint", [str(python), "-m", "ruff", "check", str(SCRIPT)]
            )
        )
        checks.append(
            check_command(
                "python312",
                [
                    str(python),
                    "-m",
                    "pytest",
                    "-q",
                    "-p",
                    "no:cacheprovider",
                    "tests/integration/test_search_code_official.py::test_search_code_ac2_python312_absolute_workspace_with_spaces",
                ],
            )
        )
        official_check = check_command(
            "official-active",
            [
                str(python),
                "-m",
                "pytest",
                "-q",
                "-p",
                "no:cacheprovider",
                "tests/integration/test_search_code_official.py",
            ],
        )
        checks.append(official_check)
        if official_check["status"] == "PASS":
            try:
                spec = importlib.util.spec_from_file_location(
                    "search_official",
                    ROOT / "tests/integration/test_search_code_official.py",
                )
                assert spec and spec.loader
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                from mostaza.packaging import collect_submission

                delivery = temporary / "delivery"
                for name, data in collect_submission(ROOT / "submission").items():
                    target = delivery / name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                validation["official_witness"] = module.official_witness(
                    delivery, temporary
                )
            except Exception as error:
                official_check.update(status="FAIL", exit_code=None, error=str(error))
        for identifier in SNAPSHOTS:
            try:
                archive = (
                    args.source_assets
                    / "resources/official/snapshots"
                    / f"{identifier}.tgz"
                )
                benchmark["snapshots"].append(
                    benchmark_snapshot(archive, python, temporary / identifier)
                )
            except Exception as error:
                benchmark["snapshots"].append(
                    {"id": identifier, "status": "FAIL", "error": str(error)}
                )
        try:
            benchmark["synthetic"] = synthetic(python, temporary / "synthetic")
            # Execute identical graph contract with the actual 3.12 interpreter.
            benchmark["synthetic_python312"] = synthetic(
                args.python312, temporary / "synthetic312"
            )
        except Exception as error:
            benchmark["synthetic"] = {"status": "FAIL", "error": str(error)}
    benchmark["status"] = (
        "PASS"
        if all(record["status"] == "PASS" for record in benchmark["snapshots"])
        and benchmark["synthetic"]["status"] == "PASS"
        and benchmark.get("synthetic_python312", {}).get("status") == "PASS"
        else "FAIL"
    )
    validation["status"] = (
        "PASS"
        if benchmark["status"] == "PASS"
        and all(check["status"] == "PASS" for check in checks)
        and all(item["status"] != "MISSING" for item in validation["prerequisites"])
        else "FAIL"
    )
    try:
        validate_reports(validation, benchmark)
    except (ValueError, KeyError, TypeError) as error:
        validation["status"] = "FAIL"
        validation["report_validation_error"] = str(error)
    evidence.mkdir(parents=True, exist_ok=True)
    for name, report in (
        ("validation.json", validation),
        ("benchmark.json", benchmark),
    ):
        (evidence / name).write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
    print(
        json.dumps(
            {
                "validation": validation["status"],
                "benchmark": benchmark["status"],
                "evidence_dir": str(evidence),
            }
        )
    )
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
