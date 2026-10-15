"""Offline, read-only reconciliation of published historical evidence.

No historical Python is imported or executed. --write owns only the two declared
reports; missing raw inputs are data, malformed metadata is a prerequisite error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from collections.abc import Iterator
from pathlib import Path, PurePosixPath
from typing import Any

PR2 = "1b86b19f7654212c1d9f95eeca84d0e2a05db16b"
DEVELOP = "60ad0cec85bb36a1e65609ca2b1a743ba087384d"
ROOT = Path(__file__).resolve().parents[1]
OLD = Path(
    "/Users/diego/.codex/worktrees/mostaza-phase2-budget-retrieval/Mostaza-Harness"
)
PHASE1 = Path("/Users/diego/.codex/worktrees/mostaza-phase1-foundation/Mostaza-Harness")
OUT = Path("docs/implementation/evidence/mostaza-phase2-reconciliation")
MAX_METADATA = 32 * 1024 * 1024
MAX_BYTES = 4 * 1024**3
MAX_ENTRIES = 10000
SPECS = {
    "foundation": 4,
    "agent-retrieval": 6,
    "evaluation": 6,
    "budget-retrieval-calibration": 10,
    "context-verification": 7,
    "pcv01": 10,
}
CPU = ("verify-task-cpu", "requests-import-cpu", "notebook-import-cpu")
BOUNDARIES: dict[str, Any] = {
    "pr2_integrated": False,
    "native_evaluations": 0,
    "gpu_model_calls": 0,
    "discussion_authorized": False,
    "historical_allowances_reusable": False,
    "private_scorer_parity": None,
    "linux_native312_validated": False,
    "real_evaluation_ready": False,
    "hybrid_efficacy": None,
    "research_complete": False,
    "original_closure": "SDD preparation only; published audit 1 "
    "FIX_REQUIRED then audit 2 PASS",
    "cpu_followups": "ORDINARY; independent scoped audits do not "
    "extend historical SDD PASS",
}
ROADMAP = [
    {
        "id": "integration",
        "prerequisite": "Separate user decision on still-unmerged PR2",
        "exit_evidence": "Reviewed integration strategy and "
        "synchronized develop in a fresh worktree",
        "authorization": "Separate integration approval; no "
        "merge/cherry-pick/import here",
    },
    {
        "id": "portable-cpu",
        "prerequisite": "Integrated source and declared clean-worktree resources",
        "exit_evidence": "Linux/native Python3.12 actual Requests "
        "imports, setup/verify_task, "
        "raw/canonical/function witnesses, negative "
        "controls and cleanup",
        "authorization": "New exact gate and finite wall/storage/native"
        " allowance; six historical N allowances spent",
    },
    {
        "id": "private-scorer",
        "prerequisite": "Accessible authoritative contract evidence",
        "exit_evidence": "Source-backed private/public scorer "
        "comparison; otherwise parity null and "
        "readiness false",
        "authorization": "Separate external access decision; no Discussion authority",
    },
    {
        "id": "matched-kaggle",
        "prerequisite": "Readiness review, frozen three tasks and "
        "matched "
        "model/sampling/environment/verification/repair",
        "exit_evidence": "Fresh contemporaneous E0/E1 six records "
        "including failures, native receipts and "
        "paired denominators",
        "authorization": "Separate per-batch GPU quota and enforced "
        "termination; no B300/R180 automatic batch or "
        "reused baseline",
    },
    {
        "id": "hybrid-research",
        "prerequisite": "Fixed calibration and observed retrieval backend evidence",
        "exit_evidence": "Treatment adherence, sourced "
        "graph/similarity/backend measurements and all"
        " inconclusive outcomes",
        "authorization": "New research protocol; no "
        "significance/superiority claim from small "
        "cohort",
    },
]


class Invalid(ValueError):
    "Untrustworthy metadata or an unavailable prerequisite."


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_relative(value: str) -> str:
    p = PurePosixPath(value)
    if (
        not value
        or p.is_absolute()
        or ".." in p.parts
        or "\\" in value
        or str(p) != value
    ):
        raise Invalid(f"Unsafe path: {value!r}")
    return value


def git(root: Path, *args: str) -> bytes:
    # Output is drained to a temporary file, bounding metadata loaded into memory.
    import tempfile

    with tempfile.TemporaryFile() as output:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            stdout=output,
            stderr=subprocess.PIPE,
            timeout=10,
            check=False,
        )
        if result.returncode:
            raise Invalid(
                f"Git source unavailable: {args!r}: "
                f"{result.stderr.decode(errors='replace')[:300]}"
            )
        if output.tell() > MAX_METADATA:
            raise Invalid("Git metadata exceeds 32MiB")
        output.seek(0)
        return output.read()


def blob(root: Path, commit: str, path: str) -> bytes:
    if commit not in (PR2, DEVELOP):
        raise Invalid("Unapproved source commit")
    return git(root, "show", f"{commit}:{safe_relative(path)}")


def objects(value: Any, pointer: str = "") -> Iterator[tuple[str, dict[str, Any]]]:
    if isinstance(value, dict):
        yield pointer, value
        for k, v in sorted(value.items()):
            yield from objects(v, pointer + "/" + str(k))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from objects(v, pointer + "/" + str(i))


def load_json(data: bytes) -> Any:
    if len(data) > MAX_METADATA:
        raise Invalid("JSON exceeds 32MiB")

    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise Invalid(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(data, object_pairs_hook=unique)


def entry_record(value: Any, require_bytes: bool = False) -> dict[str, Any]:
    if not isinstance(value, dict) or not isinstance(value.get("path"), str):
        raise Invalid("Unknown hash-pin schema")
    safe_relative(value["path"])
    if not isinstance(value.get("sha256"), str) or not re.fullmatch(
        r"[0-9a-f]{64}", value["sha256"]
    ):
        raise Invalid("Invalid expected SHA256")
    result = {"path": value["path"], "sha256": value["sha256"]}
    if "bytes" in value:
        if type(value["bytes"]) is not int or value["bytes"] < 0:
            raise Invalid("Invalid expected bytes")
        result["bytes"] = value["bytes"]
    elif require_bytes:
        raise Invalid("Raw inventory lacks bytes")
    return result


def inventory_entries(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, dict) or not isinstance(value.get("files"), list):
        raise Invalid("Unknown raw inventory schema")
    return file_entries(value["files"], require_bytes=True)


def file_entries(value: Any, require_bytes: bool = False) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > MAX_ENTRIES:
        raise Invalid("Unknown/oversized inventory list")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict) or set(item) - {"path", "bytes", "sha256"}:
            raise Invalid("Unknown inventory entry schema")
        record = entry_record(item, require_bytes)
        if record["path"] in seen:
            raise Invalid(f"Duplicate inventory path: {record['path']}")
        seen.add(record["path"])
        result.append(record)
    return result


class HashBudget:
    def __init__(self) -> None:
        self.bytes = 0
        self.entries = 0
        self.references = 0
        self.cache: dict[str, tuple[int, str]] = {}

    def inspect(self, root: Path, relative: str) -> dict[str, Any]:
        safe_relative(relative)
        p = root / relative
        if not p.resolve().is_relative_to(root.resolve()):
            raise Invalid(f"Escaping symlink: {p}")
        if p.is_symlink():
            raise Invalid(f"Symlink raw locator: {p}")
        key = str(p)
        try:
            if key not in self.cache:
                self.entries += 1
                if self.entries > MAX_ENTRIES:
                    raise Invalid("10000 raw entry cap exceeded")
                h = hashlib.sha256()
                size = 0
                with p.open("rb") as handle:
                    if not p.is_file():
                        raise Invalid(f"Nonregular raw source: {p}")
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        size += len(chunk)
                        self.bytes += len(chunk)
                        if self.bytes > MAX_BYTES:
                            raise Invalid("4GiB raw hashing cap exceeded")
                        h.update(chunk)
                self.cache[key] = size, h.hexdigest()
            size, sha = self.cache[key]
            return {"root": str(root), "bytes": size, "sha256": sha}
        except OSError as exc:
            return {"root": str(root), "unavailable": type(exc).__name__}


def raw_result(
    entry: dict[str, Any], roots: tuple[Path, ...], budget: HashBudget
) -> dict[str, Any]:
    entry = entry_record(entry)
    budget.references += 1
    if budget.references > MAX_ENTRIES:
        raise Invalid("10000 inventory reference cap exceeded")
    attempts = [budget.inspect(root, entry["path"]) for root in roots]
    matches = [
        x
        for x in attempts
        if x.get("sha256") == entry["sha256"]
        and ("bytes" not in entry or x.get("bytes") == entry["bytes"])
    ]
    status = (
        "MATCH"
        if matches
        else ("MISMATCH" if any("sha256" in x for x in attempts) else "MISSING")
    )
    return {
        **entry,
        "availability": status,
        "observations": attempts,
        "size_check": (
            "NOT_DECLARED"
            if "bytes" not in entry
            else "MATCH"
            if matches
            else "NOT_VERIFIED"
        ),
        "reason": (
            "SHA256 verified; observed bytes recorded"
            if matches
            else "No retained locator matches the published SHA256/declared size"
        ),
    }


def pointer_value(value: Any, pointer: str) -> Any:
    for part in pointer.strip("/").split("/"):
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def resolve_pin(
    source: str, pointer: str, entry: dict[str, Any], document: Any
) -> tuple[dict[str, Any], str, str | None]:
    "Explicit published format semantics, never search by basename/hash."
    entry = entry_record(entry)
    path = entry["path"]
    parent = str(PurePosixPath(source).parent)
    name = PurePosixPath(source).name
    base = "repository"
    if name == "closure-inventory.json" and isinstance(document, list):
        # Three early closure lists use names relative to their evidence family;
        # startup-correction's later list instead spells repository paths.
        if not path.startswith("docs/"):
            path = f"{parent}/{path}"
            base = "evidence-directory"
    elif name == "index.json" and "/checkpoints/" in source:
        path = f"{parent}/{path}"
        base = "checkpoint-directory"
    elif name == "resource-review.json" and pointer.startswith(
        "/verified_source_review/sample_tree_inventory/files/"
    ):
        path = f"resources/official/{path}"
        base = "official-resource-directory"
    elif name == "cpu-results.json" and (
        "/actual_inputs/tasks/" in pointer
        or (
            "/checkpoints/" in source
            and pointer.startswith("/retained_first_row/view/tasks/")
        )
    ):
        cleanup_complete = True
        if pointer.startswith("/retained_first_row/view/tasks/"):
            retained = document["retained_first_row"]
            view = retained["view"]
            cleanup_complete = retained.get("cleanup_complete") is True
        else:
            prefix = pointer.split("/actual_inputs/tasks/", 1)[0]
            view = pointer_value(document, prefix + "/actual_inputs")
        view_root = view["root"]
        # These were disposable reconstructed inputs, explicitly removed by the
        # historical runner. Never substitute repository roots/original archives.
        if not isinstance(view_root, str) or not Path(view_root).is_absolute():
            raise Invalid("Snapshot component lacks absolute input-view root")
        base = f"snapshot-input-view:{view_root}"
        if not cleanup_complete:
            return entry, base, "UNVERIFIED_TEMPORARY_INPUT_VIEW_RETENTION"
        return entry, base, "NOT_RETAINED_TEMPORARY_INPUT_VIEW"
    safe_relative(path)
    return {**entry, "path": path}, base, None


def check_published_pins(
    texts: dict[str, bytes], roots: tuple[Path, ...], budget: HashBudget
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    inventories: list[dict[str, Any]] = []
    external: list[dict[str, Any]] = []
    for source, data in sorted(texts.items()):
        if not source.startswith(
            "docs/implementation/evidence/"
        ) or not source.endswith(".json"):
            continue
        document = load_json(data)
        if source.endswith("raw-inventory.json"):
            entries = inventory_entries(document)
            results = [raw_result(x, roots, budget) for x in entries]
            inventories.append(inventory_summary(f"{PR2}:{source}", results))
            continue
        for pointer, obj in objects(document):
            if not isinstance(obj.get("path"), str) or not isinstance(
                obj.get("sha256"), str
            ):
                continue
            if "/plans/" in obj["path"]:
                external.append(
                    {
                        "source": source + pointer,
                        "path": obj["path"],
                        "availability": "EXCLUDED_UNPUBLISHED_CONTINUITY",
                        "reason": "Never read old dirty plan bytes",
                    }
                )
                continue
            mapped, base, unavailable = resolve_pin(source, pointer, obj, document)
            if unavailable:
                external.append(
                    {
                        **mapped,
                        "source": source + pointer,
                        "locator_base": base,
                        "availability": unavailable,
                        "reason": (
                            "Historical disposable input view was cleaned; "
                            "not a repository-relative retained locator"
                            if unavailable == "NOT_RETAINED_TEMPORARY_INPUT_VIEW"
                            else "Published cleanup is unconfirmed; current temporary "
                            "paths are not retained evidence"
                        ),
                    }
                )
            else:
                external.append(
                    {
                        "source": source + pointer,
                        "locator_base": base,
                        "published_path": obj["path"],
                        **raw_result(mapped, roots, budget),
                    }
                )
        acquisitions, pins = acquisition_inventories(source, document, roots, budget)
        inventories.extend(acquisitions)
        external.extend(pins)
    return inventories, external


def inventory_summary(source: str, results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "source": source,
        "counts": dict(sorted(Counter(x["availability"] for x in results).items())),
        "expected_bytes": sum(x.get("bytes", 0) for x in results),
        "size_declared_entries": sum("bytes" in x for x in results),
        "size_undeclared_entries": sum("bytes" not in x for x in results),
        "files": results,
    }


def retained_relative(absolute: str, roots: tuple[Path, ...]) -> str:
    p = Path(absolute)
    if not p.is_absolute():
        return safe_relative(absolute)
    for root in roots:
        if p.is_relative_to(root):
            return safe_relative(p.relative_to(root).as_posix())
    raise Invalid(f"Acquisition root outside approved retained roots: {absolute}")


def acquisition_inventories(
    source: str, document: Any, roots: tuple[Path, ...], budget: HashBudget
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    inventories: list[dict[str, Any]] = []
    pins: list[dict[str, Any]] = []
    declarations: list[tuple[dict[str, Any], str, str, int | None]] = []
    if source.endswith("mostaza-phase1-foundation/official-validation.json"):
        record = document["acquisition"]["source_inventory"]
        declarations.append(
            (
                entry_record(record),
                str(PurePosixPath(record["path"]).parent),
                "phase1-source-files-v1",
                record["verified_entries"],
            )
        )
    if source.endswith("mostaza-phase2-startup-run/acquisition.json"):
        bundle = safe_relative(document["source_bundle"])
        declarations.append(
            (
                {
                    "path": bundle + "/download-inventory.json",
                    "sha256": document["download"]["inventory_sha256"],
                },
                bundle + "/downloaded-output",
                "download-list-v1",
                document["download"]["files"],
            )
        )
    if source.endswith("mostaza-phase2-observed-run/acquisition.json"):
        bundle = retained_relative(document["raw_bundle"], roots)
        for path, sha in sorted(document["source_hashes"].items()):
            pins.append(
                {
                    "source": source + "/source_hashes/" + path,
                    "locator_base": bundle,
                    **raw_result(
                        {"path": bundle + "/" + safe_relative(path), "sha256": sha},
                        roots,
                        budget,
                    ),
                }
            )
        declarations.append(
            (
                {
                    "path": bundle + "/download-inventory.json",
                    "sha256": document["source_hashes"]["download-inventory.json"],
                },
                bundle + "/downloaded-output",
                "download-list-v1",
                document["output_files"],
            )
        )
    for record, base, schema, expected_count in declarations:
        pin = raw_result(record, roots, budget)
        pins.append({"source": source, "locator_base": "repository", **pin})
        if pin["availability"] != "MATCH":
            inventories.append(
                {
                    **inventory_summary(source + "::" + record["path"], []),
                    "coverage": "UNVERIFIED_INVENTORY",
                    "reason": pin["reason"],
                }
            )
            continue
        observed = next(
            x for x in pin["observations"] if x.get("sha256") == record["sha256"]
        )
        p = Path(observed["root"]) / record["path"]
        with p.open("rb") as handle:
            data = handle.read(MAX_METADATA + 1)
        if digest(data) != record["sha256"]:
            raise Invalid("Acquisition inventory changed after hashing")
        value = load_json(data)
        if schema == "phase1-source-files-v1":
            if not isinstance(value, dict) or set(value) != {"files", "source_run_id"}:
                raise Invalid("Unknown phase1 acquisition inventory schema")
            entries = file_entries(value["files"])
        else:
            entries = file_entries(value, require_bytes=True)
        if len(entries) != expected_count:
            raise Invalid("Acquisition inventory count differs from published receipt")
        results = [
            raw_result({**x, "path": base + "/" + x["path"]}, roots, budget)
            for x in entries
        ]
        inventories.append(
            {
                **inventory_summary(source + "::" + record["path"], results),
                "schema": schema,
                "locator_base": base,
                "inventory_sha256": record["sha256"],
                "coverage": "HASH_CHECKED",
            }
        )
    return inventories, pins


def assessment(family: str, ac: str) -> tuple[str, str, str]:
    limits = (
        "Historical preparation/receipts only; PR2 is "
        "unmerged. Fresh checkout portability and "
        "actual model adherence are unproven."
    )
    pending = (
        "Review integration separately, then validate "
        "a fresh candidate under a new protocol."
    )
    classification = "supported"
    if family == "foundation":
        classification = "partial"
        limits = (
            "macOS tooling and historical receipts; no "
            "clean Linux/native Python3.12 validation."
        )
    elif family == "agent-retrieval" and ac == "AC-4":
        classification = "partial"
        limits = (
            "Observed trace counters only; backend/pure "
            "model time/repair remain null when "
            "unavailable."
        )
    elif family == "evaluation" and ac in ("AC-4", "AC-5", "AC-6"):
        classification = "partial"
        limits = (
            "Historical phase1/B180 evidence only; C8K-L1 "
            "NOT_RUN; no phase completion or significance."
        )
    elif family == "budget-retrieval-calibration":
        if ac in ("AC-1", "AC-4", "AC-5", "AC-7", "AC-9"):
            classification = "partial"
        limits = {
            "AC-1": "B180 180s/3min/30 calls; B300 300s/5min/50; "
            "max_turns50/verify300 unchanged. startup-v3 "
            "serving differs from phase1; no causal "
            "superiority.",
            "AC-3": "Diagnosis strictly post-generation; "
            "references/tests must stay outside "
            "agent-visible inputs.",
            "AC-4": "Recorded E0 46 events/42 charged/409334 "
            "tokens; E1 64/60/664669. Zero named "
            "graph/similarity in recorded coverage; "
            "backend null.",
            "AC-5": "Host trace instrumentation only; ATIF "
            "empty-call discrepancy retained. "
            "Localization, Recall@K, context ratio, pure "
            "timing/repair null without full evidence.",
            "AC-6": "E1-R180 prepared but NOT_RUN; no demonstrated"
            " exploration adherence.",
            "AC-7": "Historical operational closeout includes "
            "polling gap and unknown physical release; no "
            "transferable quota.",
            "AC-8": "B300/R180 NOT_RUN; each requires a new "
            "contemporaneous pair and explicit "
            "six-evaluation allocation.",
            "AC-9": "Original closure six NOT_RUN; ordinary "
            "startup-v3 six real rows: each arm "
            "PASS0/FAIL2/ERROR1; new candidate NOT_RUN.",
            "AC-10": "Historical gate/audit only; no transferable "
            "PASS to this branch/candidate.",
        }.get(ac, limits)
    elif family == "context-verification":
        classification = "partial"
        limits = (
            "C8K/Q1/R1 preparation and CPU fixtures; "
            "context/retrieval treatment has no new model "
            "evaluation."
        )
    elif family == "pcv01":
        classification = "partial"
        limits = (
            "Public source and local diagnostic evidence; "
            "private scorer parity remains unknown and "
            "readiness false."
        )
    return classification, limits, pending


def source_family(family: str) -> str:
    return {
        "foundation": "mostaza-phase1-foundation",
        "agent-retrieval": "mostaza-phase2-budget-retrieval",
        "evaluation": "mostaza-phase2-startup-run",
        "budget-retrieval-calibration": "mostaza-phase2-budget-retrieval",
        "context-verification": "mostaza-context-verification",
        "pcv01": "mostaza-pcv01-access",
    }[family]


# Each mapping binds a criterion to a concrete implementation/evidence location.
DETAILS: dict[str, list[tuple[str, str, str]]] = {
    "foundation": [
        (
            "scripts/setup.sh",
            "uv",
            "Locked local setup exists; fresh installation is not replayed here.",
        ),
        (
            "pyproject.toml",
            "Apache",
            "Repository packaging/license structure is "
            "versioned; ignored bulk resources stay "
            "external.",
        ),
        (
            "docs/implementation/evidence/mostaza-phase1-foundation/resource-review.json",
            "sha256",
            "Official acquisition identities are "
            "historical pins, not current remote "
            "requirements.",
        ),
        (
            "docs/implementation/evidence/mostaza-phase1-foundation/report.md",
            "92",
            "Historical local validation is separate from native Gemma execution.",
        ),
    ],
    "agent-retrieval": [
        (
            "src/mostaza/packaging.py",
            "def _validate_agent",
            "Packaging enforces declared single-agent "
            "closure and permitted model/tools; model "
            "behavior is not replayed.",
        ),
        (
            "tests/unit/test_retrieval_policy.py",
            "def ",
            "Prompt-policy fixtures cover exploration "
            "constraints; actual adherence remains "
            "unproven.",
        ),
        (
            "tests/unit/test_retrieval_policy.py",
            "def ",
            "Static instruction contract covers context "
            "priorities; no learned ranking efficacy "
            "follows.",
        ),
        (
            "docs/implementation/evidence/mostaza-phase2-startup-run/trace-observations.json",
            "charged",
            "Published ordinary B180 trace observations "
            "distinguish recorded attempts and charged "
            "calls.",
        ),
        (
            "src/mostaza/packaging.py",
            "def build_submission",
            "Deterministic explicit configuration "
            "packaging plus published compiler receipts; "
            "archive validity is not task success.",
        ),
        (
            "tests/integration/test_retrieval_contract.py",
            "def ",
            "Official retrieval contract fixtures cover "
            "tool interfaces; fixtures are not agent "
            "executions.",
        ),
    ],
    "evaluation": [
        (
            "experiments/cohort.json",
            "requests_7205",
            "Frozen Requests/FastAPI/Rich identifiers "
            "remain historical cohort inputs; no task "
            "reselection.",
        ),
        (
            "tests/unit/test_task_isolation.py",
            "def ",
            "Leakage fixtures and allowlist contract "
            "separate agent inputs from post-generation "
            "reference analysis.",
        ),
        (
            "src/mostaza/evaluation/contracts.py",
            "schema",
            "Run/result contract preserves sourced "
            "identity, outcomes and nullable metrics; "
            "unavailable fields are not zero.",
        ),
        (
            "docs/implementation/evidence/mostaza-phase2-startup-run/evaluation-records.json",
            "E0-B180",
            "Six historical B180 records exist; no new C8K-L1 evaluation is implied.",
        ),
        (
            "docs/implementation/evidence/mostaza-phase2-startup-run/comparison.json",
            "E0",
            "Published descriptive paired comparison "
            "retains failures and denominators; no "
            "significance or superiority.",
        ),
        (
            "docs/runbooks/kaggle-execution.md",
            "Kaggle",
            "Versioned operational commands document "
            "historical paths; a new checkout needs fresh "
            "validation/resources.",
        ),
    ],
    "budget-retrieval-calibration": [
        (
            "experiments/E0-B180/manifest.json",
            "180",
            "Pinned B180 manifest; B300/R180 remain "
            "separate prepared configurations and "
            "startup-v3 serving delta prevents a clean "
            "phase1 causal comparison.",
        ),
        (
            "docs/implementation/evidence/mostaza-phase2-budget-retrieval/resource-review.json",
            "retained_inputs",
            "Official wheel/API pins were reviewed "
            "historically; this checker hashes retained "
            "resources only.",
        ),
        (
            "src/mostaza/research/trace_diagnostics.py",
            "def diagnose_historical",
            "Offline trace/patch diagnosis is "
            "post-generation and must not enter prompts or"
            " agent payloads.",
        ),
        (
            "src/mostaza/research/trace_diagnostics.py",
            "def diagnose_trace",
            "Trace classifier separates observable "
            "attempts, responses and availability; backend"
            " remains unknown without evidence.",
        ),
        (
            "tests/unit/test_trace_diagnostics.py",
            "def ",
            "Malformed/missing/native trace fixtures "
            "validate host instrumentation, never real "
            "evaluation or complete recall.",
        ),
        (
            "experiments/E1-R180/manifest.json",
            "R180",
            "Separate recovery variant exists; no R180 "
            "model run or demonstrated adherence.",
        ),
        (
            "src/mostaza/evaluation/phase2.py",
            "def require_launch_ready",
            "Historical fail-closed launch readiness and "
            "notebook preparation do not grant a new GPU "
            "session.",
        ),
        (
            "src/mostaza/evaluation/phase2.py",
            "def scheduling_allowed",
            "Scheduling contract separates later batches; "
            "consumed individual allocations cannot be "
            "reused.",
        ),
        (
            "docs/implementation/evidence/mostaza-phase2-startup-run/evaluation-records.json",
            "E1-B180",
            "Ordinary six-row actual B180 acquisition "
            "succeeds as acquisition, not task resolution;"
            " current candidate NOT_RUN.",
        ),
        (
            "scripts/check_phase2.py",
            "def ",
            "Original local validation entry point is "
            "inspected as source only; no historical gate "
            "is run or transferred.",
        ),
    ],
    "context-verification": [
        (
            "src/mostaza/evaluation/context_variants.py",
            "def expected_manifest",
            "Original variants preserved through new explicit derived manifests.",
        ),
        (
            "src/mostaza/evaluation/verification_origin.py",
            "def observe_origin",
            "Module-origin observation is diagnostic; "
            "origin alone does not prove task semantics.",
        ),
        (
            "src/mostaza/evaluation/context_variants.py",
            "def expected_manifest",
            "C8K context treatment is prepared; no model evaluation tests its effect.",
        ),
        (
            "src/mostaza/evaluation/context_variants.py",
            "def prompt",
            "Q1 generic instruction treatment is distinct "
            "from context calibration; adherence untested.",
        ),
        (
            "src/mostaza/evaluation/context_variants.py",
            "def prompt",
            "R1 exploration-only treatment is prepared; no"
            " contemporaneous comparison executed.",
        ),
        (
            "src/mostaza/evaluation/context_candidate.py",
            "def ",
            "Disabled notebook source/payload checks "
            "establish preparation, not full Linux/model "
            "loop.",
        ),
        (
            "docs/implementation/evidence/mostaza-context-verification/compiler-and-fixtures.json",
            "",
            "Published CPU/compiler fixture receipt is "
            "historical and scoped; no native replay here.",
        ),
    ],
    "pcv01": [
        (
            "src/mostaza/evaluation/pytest_origin_receipt.py",
            "def pytest_runtest_call",
            "Opt-in diagnostic hook observes disposable pytest processes only.",
        ),
        (
            "src/mostaza/evaluation/pytest_origin_receipt.py",
            "def _observe",
            "Loaded public-module observation avoids "
            "treating an import probe as scorer "
            "equivalence.",
        ),
        (
            "src/mostaza/evaluation/pytest_origin_receipt.py",
            "def _configuration",
            "Bounded host-only receipt configuration remains outside agent payloads.",
        ),
        (
            "src/mostaza/evaluation/pytest_origin_receipt.py",
            "def _function_receipt",
            "Function/origin witnesses identify executed "
            "source; semantic result remains separate.",
        ),
        (
            "docs/implementation/evidence/mostaza-pcv01-cpu/cpu-controls.json",
            "",
            "Published local native controls cover this "
            "diagnostic protocol; no full Kaggle parity.",
        ),
        (
            "src/mostaza/evaluation/scorer_contract.py",
            "def review_runtime_sources",
            "Pinned public API/source review is not access"
            " to private scorer deployment.",
        ),
        (
            "tests/integration/test_pcv01_cpu_contract.py",
            "def ",
            "Diagnostic isolation contract keeps "
            "analyst/plugin evidence outside agent inputs.",
        ),
        (
            "docs/implementation/evidence/mostaza-pcv01-access/public-sources.json",
            "",
            "Individually acquired public sources are "
            "retained with provenance; no Discussion "
            "publication.",
        ),
        (
            "src/mostaza/evaluation/scorer_contract.py",
            "def validate",
            "Static source contract checker compares "
            "public/native artifacts; unavailable private "
            "implementation remains unknown.",
        ),
        (
            "src/mostaza/evaluation/scorer_contract.py",
            "def compatibility_status",
            "Public-source review does not promote private"
            " scorer parity or real readiness.",
        ),
    ],
}


def concrete(family: str, number: int, texts: dict[str, bytes]) -> tuple[str, str]:
    path, selector, interpretation = DETAILS[family][number - 1]
    if path not in texts:
        raise Invalid(f"Missing concrete evidence: {path}")
    lines = texts[path].decode().splitlines()
    hits = [i for i, line in enumerate(lines, 1) if selector.lower() in line.lower()]
    if not hits:
        raise Invalid(f"Missing evidence selector: {path}: {selector}")
    return f"{PR2}:{path}#L{hits[0]}", interpretation


# Explicit obligation routing. Paragraph numbers qualify historical prose locators;
# titles, planning status, environment narrative and command introductions are context.
CPU_MANIFEST: dict[str, list[tuple[int, str, str]]] = {
    "verify-task-cpu": [
        (4, "diagnosis", "supported"),
        (5, "boundary", "supported"),
        (8, "inputs", "supported"),
        (9, "archive", "supported"),
        (10, "runtime", "supported"),
        (12, "implementation", "supported"),
        (13, "implementation", "supported"),
        (14, "immutable", "supported"),
        (16, "protocol", "supported"),
        (18, "controls", "supported"),
        (19, "matrix", "supported"),
        (20, "test-isolation", "supported"),
        (21, "diagnostics", "supported"),
        (22, "binding", "supported"),
        (24, "receipts", "supported"),
        (25, "no-execution", "supported"),
        (26, "witnesses", "supported"),
        (27, "acceptance", "supported"),
        (28, "readiness", "supported"),
        (30, "gate", "supported"),
        (32, "gate", "supported"),
        (33, "gate", "supported"),
        (35, "allowances", "supported"),
        (36, "cleanup", "partial"),
        (37, "audit", "supported"),
    ],
    "requests-import-cpu": [
        (4, "diagnosis", "supported"),
        (8, "boundary", "supported"),
        (10, "layout", "supported"),
        (12, "layout", "supported"),
        (13, "trees", "supported"),
        (14, "immutable", "supported"),
        (15, "native", "supported"),
        (17, "implementation", "supported"),
        (18, "implementation", "supported"),
        (19, "immutable", "supported"),
        (21, "controls", "supported"),
        (22, "matrix", "supported"),
        (23, "paired-inputs", "supported"),
        (24, "stale-witness", "supported"),
        (25, "diagnostics", "supported"),
        (26, "canonical-binding", "supported"),
        (27, "witnesses", "supported"),
        (29, "acceptance", "supported"),
        (30, "behavior", "supported"),
        (31, "receipts", "supported"),
        (32, "readiness", "supported"),
        (34, "gate", "supported"),
        (38, "supervision", "supported"),
        (40, "per-gate-limits", "supported"),
        (41, "allowances", "supported"),
        (42, "cleanup", "partial"),
        (43, "audit", "supported"),
    ],
    "notebook-import-cpu": [
        (4, "diagnosis", "supported"),
        (8, "runtime", "supported"),
        (10, "immutable", "supported"),
        (11, "candidate", "supported"),
        (12, "resolver", "supported"),
        (13, "provenance", "supported"),
        (14, "payload", "supported"),
        (16, "implementation", "supported"),
        (18, "relocation", "supported"),
        (19, "matrix", "supported"),
        (20, "setup", "supported"),
        (21, "native", "supported"),
        (22, "behavior", "supported"),
        (23, "allowlist", "supported"),
        (25, "stdlib312", "supported"),
        (26, "portability-boundary", "supported"),
        (28, "gate", "supported"),
        (33, "allowances", "supported"),
        (34, "supervision", "supported"),
        (36, "acceptance", "supported"),
        (37, "per-gate-limits", "supported"),
        (38, "allowances", "supported"),
        (39, "cleanup", "supported"),
        (40, "readiness", "supported"),
        (42, "audit", "supported"),
        (43, "deliverables", "supported"),
    ],
}
CPU_CASES = {
    "verify-task-cpu": [f"V{i:02d}" for i in range(1, 9)] + ["R00", "R01", "R02"],
    "requests-import-cpu": ["L01", "L02", "L03"]
    + [f"R{i:02d}-{stage}" for i in range(3) for stage in ("U", "B")],
    "notebook-import-cpu": ["N-L01", "N-L02", "N-L03", "N-R00", "N-R01", "N-R02"],
}


def expected_cpu_classifications() -> dict[str, str]:
    result: dict[str, str] = {}
    for family, declarations in CPU_MANIFEST.items():
        for paragraph, kind, status in declarations:
            prefix = f"{family}:proposal-paragraph-{paragraph:03d}"
            if kind == "matrix":
                result.update(
                    {prefix + ":" + case: status for case in CPU_CASES[family]}
                )
            else:
                result[prefix] = status
    return result


def cpu_source(family: str, name: str) -> str:
    return f"docs/implementation/evidence/mostaza-{family}/{name}"


def cpu_json(texts: dict[str, bytes], family: str, name: str) -> dict[str, Any]:
    value = load_json(texts[cpu_source(family, name)])
    if not isinstance(value, dict):
        raise Invalid("Unknown CPU evidence schema")
    return value


def cpu_summary(texts: dict[str, bytes], family: str) -> dict[str, Any]:
    results = cpu_json(texts, family, "cpu-results.json")
    gates = cpu_json(texts, family, "gate-attempts.json")
    audit = cpu_json(texts, family, "audit.json")
    attempts = gates["attempts"]
    final = attempts[-1]
    command_count = {
        "verify-task-cpu": 9,
        "requests-import-cpu": 10,
        "notebook-import-cpu": 12,
    }[family]
    if (
        not final["passed"]
        or len(final["commands"]) != command_count
        or any(x["exit_code"] != 0 for x in final["commands"])
    ):
        raise Invalid("CPU final gate receipt disagrees with scoped PASS")
    if audit.get("status", audit.get("verdict")) != "PASS" or audit["findings"]:
        raise Invalid("CPU independent audit is not PASS with zero findings")
    approvals = ["approval.json"]
    if family == "verify-task-cpu":
        approvals.append("additional-attempt-approval.json")
        extra = cpu_json(texts, family, approvals[-1])
        if not extra["approved"] or extra["gate_attempt"] != 3:
            raise Invalid("V corrective attempt lacks separate approval")
        total = 23
    elif family == "requests-import-cpu":
        approvals.append("corrective-attempt.json")
        if cpu_json(texts, family, approvals[-1])["finding_id"] != "RI-A01":
            raise Invalid("R corrective attempt lacks concrete audit repair")
        total = gates["total_native_invocations"]
    else:
        additions = [
            "additional-gate-approval.json",
            "resource-gate-approval.json",
            "source-filter-gate-approval.json",
            "supervision-gate-approval.json",
        ]
        approvals.extend(additions)
        if len(attempts) != 6:
            raise Invalid("N historical attempt count differs")
        for index, name in enumerate(additions):
            attempt = attempts[index + 2]
            if attempt["additional_authorization"]["approval_sha256"] != digest(
                texts[cpu_source(family, name)]
            ):
                raise Invalid("N additional authorization hash differs")
        total = sum(x["actual_counts"]["native_total"]["started"] for x in attempts)
        if total != gates["total_native_started"]:
            raise Invalid("N cumulative native count differs")
    report = texts[cpu_source(family, "report.md")].decode()
    tests = {
        "verify-task-cpu": (306, 45),
        "requests-import-cpu": (328, 49),
        "notebook-import-cpu": (378, 119),
    }[family]
    for index, label in enumerate(("unit", "integration")):
        count = tests[index]
        if not re.search(rf"{count}\s*{label}\s*tests", report):
            raise Invalid("Published CPU test-count assertion changed")
    history = []
    for attempt in attempts:
        row = {
            "attempt": attempt["attempt"],
            "passed": attempt["passed"],
            "wall_seconds": attempt["duration_seconds"],
        }
        if "actual_counts" in attempt:
            c = attempt["actual_counts"]
            row.update(
                {
                    "native_started": c["native_total"]["started"],
                    "native_results": c["native_total"]["completed"],
                    "setup_started": c["setup"]["started"],
                    "stdlib_started": c["stdlib"]["started"],
                    "failure": attempt["failure"],
                }
            )
        history.append(row)
    summary = {
        "protocol_status": results["status"],
        "workflow_kind": "ORDINARY",
        "initial_allowed_attempts": 2,
        "consumed_attempts": len(attempts),
        "separate_additional_attempts": len(attempts) - 2,
        "authorization_receipts": [f"{PR2}:{cpu_source(family, p)}" for p in approvals],
        "final_command_count": command_count,
        "final_gate_wall_seconds": final["duration_seconds"],
        "published_final_tests": {"unit": tests[0], "integration": tests[1]},
        "test_count_source": f"{PR2}:{cpu_source(family, 'report.md')}",
        "cumulative_native_diagnostics": total,
        "history": history,
        "future_native_allowance": 0,
        "audit": {
            "verdict": "PASS",
            "findings": 0,
            "source": f"{PR2}:{cpu_source(family, 'audit.json')}",
        },
    }
    if family == "notebook-import-cpu":
        summary.update(
            {
                "final_counts": results["counts"],
                "cumulative_native_results": gates["retained_native_results"],
                "cumulative_setup": gates["setup_started"],
                "cumulative_stdlib": gates["stdlib_started"],
                "cumulative_gate_wall_seconds": gates["total_gate_wall_seconds"],
                "sampled_peak_bytes": results["sampled_peak_bytes"],
            }
        )
    elif family == "verify-task-cpu":
        summary["history_native_results"] = [7, 5, 11]
        summary["history_assessed"] = [6, 4, 11]
        summary["count_scope"] = (
            "Standalone V attempts only; later R/N regressions counted in those gates"
        )
    else:
        summary["new_native_per_gate"] = results["invocations_assessed"]
        summary["regression_native_per_gate"] = 11
    return summary


def expected_case(family: str, identifier: str) -> dict[str, Any]:
    """Frozen historical observations; diagnostic PASS is distinct from task PASS."""
    short = identifier.removeprefix("N-")
    outcomes: dict[str, str]
    binding: bool | None = True
    resolved = short in ("V02", "L02", "R02-B") or identifier == "N-R02"
    exit_code = 0 if resolved else 1
    if short.startswith(("V", "L")):
        outcomes = {"test_required": "passed" if resolved else "assertion_failed"}
        if short == "V04":
            binding = False
        elif short in ("V05", "V06"):
            binding = None
            outcomes = {}
            exit_code = 0 if short == "V05" else 5
        elif short == "V07":
            outcomes = {"test_required": "premature_exit"}
            exit_code = 0
    else:
        outcomes = {
            "test_empty_default": "passed",
            "test_empty_machine": "passed",
            "test_missing": "passed",
            "test_origin_binding": "passed",
            "test_valid": "passed",
        }
        if family == "verify-task-cpu" or short.endswith("-U"):
            binding = False
            outcomes["test_origin_binding"] = "assertion_failed"
        elif short in ("R00-B", "R00"):
            outcomes.update(
                {
                    "test_empty_default": "assertion_failed",
                    "test_empty_machine": "assertion_failed",
                }
            )
        elif short in ("R01-B", "R01"):
            outcomes["test_missing"] = "exception"
    result: dict[str, Any] = {
        "id": identifier,
        "native_resolved": resolved,
        "test_exit_code": exit_code,
        "node_outcomes": outcomes,
        "workspace_binding" if family == "verify-task-cpu" else "binding": binding,
    }
    if family == "notebook-import-cpu":
        result["setup_binding"] = True
    return result


def validate_case(family: str, row: dict[str, Any]) -> None:
    expected = expected_case(family, row["id"])
    actual = {key: row.get(key) for key in expected}
    if canonical(actual) != canonical(expected):
        raise Invalid(f"Unsupported historical CPU outcome: {family}/{row['id']}")


def compact_case(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: row[key]
        for key in (
            "id",
            "native_resolved",
            "test_exit_code",
            "node_outcomes",
            "workspace_binding",
            "binding",
            "setup_binding",
            "coverage_reason",
            "native_error_message",
        )
        if key in row
    }


def cpu_rows(texts: dict[str, bytes]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family, declarations in CPU_MANIFEST.items():
        proposal_path = cpu_source(family, "plan-for-approval.md")
        paragraphs = [
            p.strip() for p in texts[proposal_path].decode().split("\n\n") if p.strip()
        ]
        summary = cpu_summary(texts, family)
        result = cpu_json(texts, family, "cpu-results.json")
        gate = cpu_json(texts, family, "gate-attempts.json")
        report = texts[cpu_source(family, "report.md")].decode()
        case_key = "rows" if family == "notebook-import-cpu" else "results"
        cases = result[case_key]
        for case in cases:
            validate_case(family, case)
        if [x["id"] for x in cases] != CPU_CASES[family]:
            raise Invalid("CPU matrix omitted/changed obligations")
        for paragraph, kind, status in declarations:
            requirement = paragraphs[paragraph - 1]
            if requirement.startswith("#"):
                raise Invalid("CPU obligation incorrectly routed to a heading")
            prefix = f"{family}:proposal-paragraph-{paragraph:03d}"
            observed: Any
            evidence = [f"{PR2}:{cpu_source(family, 'cpu-results.json')}#/{case_key}"]
            if kind == "matrix":
                proposal_cases = re.findall(
                    r"(?m)^\| (V\d\d|R\d\d(?:-[UB])?|L\d\d|N-[LR]\d\d) \|.*$",
                    requirement,
                )
                if proposal_cases != CPU_CASES[family]:
                    raise Invalid(
                        "Proposal matrix differs from expected obligation map"
                    )
                for index, case in enumerate(cases):
                    line = next(
                        x
                        for x in requirement.splitlines()
                        if x.startswith("| " + case["id"] + " |")
                    )
                    rows.append(
                        cpu_row(
                            prefix + ":" + case["id"],
                            status,
                            line,
                            proposal_path,
                            paragraph,
                            [
                                f"{PR2}:{cpu_source(family, 'cpu-results.json')}"
                                f"#/{case_key}/{index}"
                            ],
                            compact_case(case),
                            "Expected control/observation reached; native "
                            "outcome retained separately from binding.",
                            (
                                "Owned diagnostic nodes only, "
                                "not hidden tests or task scores."
                            ),
                            (
                                "Preserve this scoped diagnostic; "
                                "no rerun allowance transfers."
                            ),
                        )
                    )
                continue
            if kind in (
                "gate",
                "allowances",
                "per-gate-limits",
                "audit",
                "acceptance",
                "deliverables",
            ):
                observed = summary
                evidence = [
                    f"{PR2}:{cpu_source(family, 'gate-attempts.json')}#/attempts",
                    f"{PR2}:{cpu_source(family, 'audit.json')}",
                ]
                interpretation = (
                    "Final corrected full gate and independent "
                    "scoped audit passed; prior failures remain "
                    "failed and each added attempt is separately "
                    "sourced."
                )
                limits = (
                    "Consumed historical CPU allowances; zero "
                    "authorization for another native run or for "
                    "this checkout."
                )
                pending = (
                    "Use a fresh approved scope/budget before any future execution."
                )
            elif kind in ("cleanup", "supervision"):
                observed = {
                    "final_gate_wall_seconds": summary["final_gate_wall_seconds"],
                    "sampled_peak_bytes": result.get(
                        "sampled_peak_bytes", result.get("peak_disk_bytes")
                    ),
                    "process_cpu_seconds": result.get("cpu_time_seconds"),
                    "cleanup_source": (
                        f"{PR2}:{cpu_source(family, 'report.md')}#cleanup"
                    ),
                }
                evidence = [
                    f"{PR2}:{cpu_source(family, 'gate-attempts.json')}"
                    f"#/attempts/{len(gate['attempts']) - 1}"
                ]
                interpretation = (
                    "Corrected final gate reports complete scoped "
                    "cleanup and bounded wall time; original "
                    "interrupted/cap failures remain in the "
                    "history."
                )
                limits = (
                    "Polled limits are not an instantaneous "
                    "physical peak. V/R peak bytes and process CPU"
                    " time were not retained; N peak is sampled "
                    "556434407 bytes."
                )
                pending = (
                    "Retain null reasons and bounded supervision "
                    "requirements in future protocols."
                )
            elif kind in ("stdlib312", "portability-boundary"):
                observed = result["python312_transport"]
                # Avoid duplicating detailed relocated receipts in every row.
                observed = {k: v for k, v in observed.items() if k != "results"}
                evidence = [
                    f"{PR2}:{cpu_source(family, 'cpu-results.json')}"
                    "#/python312_transport"
                ]
                interpretation = (
                    "Two Python3.12.8 stdlib transport probes "
                    "assessed; generic package import only."
                )
                limits = (
                    "Requests import/native verify_task in "
                    "Python3.12 and Linux remain NOT_TESTED; no "
                    "dependencies were installed."
                )
                pending = (
                    "Separately approve actual Linux/native "
                    "Python3.12 Requests validation."
                )
            elif kind in ("readiness", "boundary"):
                observed = {
                    k: result[k]
                    for k in (
                        "gpu_readiness",
                        "private_scorer_parity",
                        "actual_scorer_runtime_parity",
                        "real_evaluations",
                        "linux_runtime_portability",
                        "full_notebook_or_agent_loop_executed",
                    )
                    if k in result
                }
                interpretation = (
                    "Published readiness stays false and scorer "
                    "parity null; scoped CPU milestone does not "
                    "claim a real evaluation or full notebook "
                    "loop."
                )
                limits = (
                    "Historical source review and diagnostic "
                    "success do not establish private scorer or "
                    "hybrid efficacy."
                )
                pending = (
                    "Keep real evaluation blocked until separately"
                    " approved readiness evidence."
                )
            elif kind in (
                "binding",
                "canonical-binding",
                "behavior",
                "diagnosis",
                "controls",
                "no-execution",
                "witnesses",
                "receipts",
                "diagnostics",
                "stale-witness",
                "paired-inputs",
                "setup",
                "native",
                "relocation",
                "runtime",
            ):
                selected = cases
                if kind == "no-execution":
                    selected = [case for case in cases if case["id"] in ("V05", "V06")]
                elif kind == "controls":
                    selected = [
                        case
                        for case in cases
                        if not case["id"].startswith(("R", "N-R"))
                    ]
                elif kind in (
                    "binding",
                    "canonical-binding",
                    "behavior",
                    "diagnostics",
                ):
                    selected = [
                        case for case in cases if case["id"].startswith(("R", "N-R"))
                    ]
                observed = [compact_case(case) for case in selected]
                if kind in ("runtime", "witnesses", "stale-witness"):
                    observed = []
                    for case in selected:
                        witness = case.get("witness")
                        if witness is None:
                            available = case.get("process_witnesses", [])
                            witness = available[0] if available else {}
                        observed.append(
                            {
                                "id": case["id"],
                                "witness_fields": {
                                    k: witness[k]
                                    for k in (
                                        "pid",
                                        "ppid",
                                        "python",
                                        "pytest",
                                        "module_sha256",
                                        "function_fingerprint",
                                        "coverage",
                                        "fingerprint_algorithm",
                                    )
                                    if k in witness
                                },
                                "coverage_reason": case.get("coverage_reason"),
                            }
                        )
                elif kind == "paired-inputs":
                    observed = [
                        {
                            "id": case["id"],
                            "agent_patch_sha256": case["agent_patch_sha256"],
                            "test_patch_sha256": case["test_patch_sha256"],
                        }
                        for case in cases
                        if case["id"].startswith("R")
                    ]
                interpretation = {
                    "verify-task-cpu": "Eight synthetic controls satisfy their "
                    "intended observations; R00/R01/R02 all reach "
                    "five nodes but bind installed Requests "
                    "2.34.2: origin fails and four behavioral "
                    "checks pass. Intended workspace patch "
                    "semantics remain unvalidated.",
                    "requests-import-cpu": "Generic faulty/correct/wrong controls "
                    "discriminate. All U stages reproduce "
                    "installed-code mismatch; all B stages bind "
                    "patched workspace. Bound baseline fails "
                    "empty-machine/default; E0 missing-match "
                    "raises TypeError; E1 passes all five OWN "
                    "checks.",
                    "notebook-import-cpu": "Six separate setup and six verification "
                    "witnesses bind the same resolved inputs; "
                    "baseline fails two empty-credential checks, "
                    "E0 missing-match raises TypeError, E1 passes "
                    "five OWN nodes. Setup observes baseline; "
                    "verification observes retained patch.",
                }[family]
                limits = (
                    "Actual macOS ARM/Python3.13.15/pytest9.1.1 "
                    "diagnostic coverage only; raw JUnit is "
                    "removed by native cleanup and not replaced by"
                    " test-body telemetry."
                )
                pending = (
                    "Preserve native/semantic/binding "
                    "distinctions; separately validate future "
                    "production/scorer portability."
                )
            else:
                source_path = {
                    "verify-task-cpu": "src/mostaza/evaluation/verify_task_cpu.py",
                    "requests-import-cpu": (
                        "src/mostaza/evaluation/requests_import_cpu.py"
                    ),
                    "notebook-import-cpu": "src/mostaza/evaluation/notebook_import.py",
                }[family]
                source_text = texts[source_path].decode()
                evidence = [
                    f"{PR2}:{source_path}",
                    f"{PR2}:{cpu_source(family, 'report.md')}",
                ]
                observed = {
                    "source_sha256": digest(texts[source_path]),
                    "published_implementation_section": report.split("## ")[1][:700],
                }
                interpretation = {
                    "verify-task-cpu": "Bounded archive/input validation and actual "
                    "native fixture path exist; frozen native "
                    "inputs and own-test isolation are preserved. "
                    "No import repair is made in V.",
                    "requests-import-cpu": "Host-only validator enforces the one-link "
                    "120000 delta requests -> src/requests, "
                    "separate original/derived trees, canonical "
                    "module/function binding and exact U/B pair "
                    "matching.",
                    "notebook-import-cpu": "Host adapter creates disabled "
                    "notebook/derived envelope via official "
                    "base-plus-delta resolver; parent C8K closures"
                    " stay byte-identical and actual-input "
                    "provenance is distinct from parent binding.",
                }[family]
                if "def " not in source_text:
                    raise Invalid("CPU implementation source absent")
                limits = (
                    "Static immutable implementation evidence plus"
                    " historical receipts; no execution/import of "
                    "historical product code here."
                )
                pending = (
                    "Separately approve integration before "
                    "transferring this implementation to develop."
                )
            rows.append(
                cpu_row(
                    prefix,
                    status,
                    requirement,
                    proposal_path,
                    paragraph,
                    evidence,
                    observed,
                    interpretation,
                    limits,
                    pending,
                )
            )
    return rows


def cpu_row(
    identifier: str,
    status: str,
    requirement: str,
    path: str,
    paragraph: int,
    evidence: list[str],
    observed: Any,
    interpretation: str,
    limits: str,
    pending: str,
) -> dict[str, Any]:
    return {
        "id": identifier,
        "classification": status,
        "requirement": requirement,
        "source": f"{PR2}:{path}#paragraph-{paragraph:03d}",
        "locator_sha256": digest(requirement.encode()),
        "evidence": evidence,
        "observed": observed,
        "observed_sha256": digest(canonical(observed).encode()),
        "implementation_or_receipt": interpretation,
        "limits": limits,
        "pending": pending,
    }


def acceptance_rows(texts: dict[str, bytes]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for family, count in SPECS.items():
        path = f"docs/specs/{family}.md"
        text = texts[path].decode()
        matches = list(re.finditer(r"(?m)^(AC-(?:CV|P)?\d+):", text))
        if len(matches) != count or len({m[1] for m in matches}) != count:
            raise Invalid(f"Incomplete/duplicate acceptance: {path}")
        for i, match in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            requirement = text[match.start() : end].split("\n## ")[0].strip()
            status, limits, pending = assessment(family, match[1])
            location, interpretation = concrete(family, i + 1, texts)
            if family == "foundation":
                status = "partial" if match[1] == "AC-1" else "supported"
                limits = interpretation
            if status == "supported":
                pending = (
                    "Preserve this historical preparation "
                    "contract during separately approved integration."
                )
            elif family == "foundation":
                pending = (
                    "Validate fresh macOS setup from locked "
                    "tooling under a separate approved environment scope."
                )
            elif family == "context-verification":
                pending = (
                    "Run a separately approved matched "
                    "context/retrieval comparison after readiness."
                )
            elif family == "pcv01":
                pending = (
                    "Keep parity unknown until authoritative "
                    "private scorer evidence is available."
                )
            report = f"docs/implementation/evidence/{source_family(family)}/report.md"
            if report not in texts:
                raise Invalid(f"Missing acceptance evidence: {report}")
            rows.append(
                {
                    "id": family + ":" + match[1],
                    "classification": status,
                    "requirement": requirement,
                    "source": f"{PR2}:{path}",
                    "locator_sha256": digest(texts[path]),
                    "evidence": [location, f"{PR2}:{report}"],
                    "implementation_or_receipt": interpretation,
                    "limits": limits,
                    "pending": pending,
                }
            )
    rows.extend(cpu_rows(texts))
    return rows


def build(root: Path = ROOT, roots: tuple[Path, ...] = (OLD, PHASE1)) -> dict[str, Any]:
    if git(root, "rev-parse", "HEAD").decode().strip() != DEVELOP:
        # A Versioner commit may subsequently contain these exact product files;
        # ancestry, rather than mutable branch names, binds the baseline.
        git(root, "merge-base", "--is-ancestor", DEVELOP, "HEAD")
    paths = git(root, "ls-tree", "-r", "--name-only", PR2).decode().splitlines()
    texts: dict[str, bytes] = {}
    sources: list[dict[str, Any]] = []
    for path in paths:
        if "/plans/" in path:
            continue
        data = blob(root, PR2, path)
        sources.append(
            {"commit": PR2, "path": path, "bytes": len(data), "sha256": digest(data)}
        )
        texts[path] = data
    for family in ("foundation", "agent-retrieval", "evaluation"):
        path = f"docs/specs/{family}.md"
        data = blob(root, DEVELOP, path)
        sources.append(
            {
                "commit": DEVELOP,
                "path": path,
                "bytes": len(data),
                "sha256": digest(data),
            }
        )
    closed = "docs/specs/plans/closed/mostaza-phase2-budget-retrieval.md"
    published = blob(root, PR2, closed)
    sources.append(
        {
            "commit": PR2,
            "path": closed,
            "bytes": len(published),
            "sha256": digest(published),
        }
    )
    fence = re.search(rb"```sdd-execution\n(.*?)\n```", published, re.S)
    if fence is None:
        raise Invalid("Published original SDD closure absent")
    historical = load_json(fence[1])
    verdicts = [x["verdict"] for x in historical["audits"]]
    if (
        verdicts != ["FIX_REQUIRED", "PASS"]
        or historical["versioning"]["status"] != "CLOSED_FOR_COMMIT"
    ):
        raise Invalid("Historical closure differs from approved reconciliation")
    closure = {
        "source": f"{PR2}:{closed}",
        "audit_verdicts": verdicts,
        "candidate": historical["versioning"]["candidate"],
        "recorded_version_status": historical["versioning"]["status"],
        "meaning": "Published historical preparation evidence, "
        "not this workflow state or research "
        "completion",
    }
    budget = HashBudget()
    inventories, external = check_published_pins(texts, roots, budget)
    result = {
        "schema_version": 1,
        "commits": {"develop": DEVELOP, "pr2": PR2},
        "boundaries": BOUNDARIES,
        "sources": sources,
        "acceptance": acceptance_rows(texts),
        "cpu_milestones": {f: cpu_summary(texts, f) for f in CPU},
        "raw_inventories": inventories,
        "other_pins": external,
        "hashing": {
            "unique_readable_files": len(budget.cache),
            "bytes_hashed": budget.bytes,
            "inventory_references": budget.references,
            "byte_unit": "bytes",
            "max_bytes": MAX_BYTES,
            "max_entries": MAX_ENTRIES,
        },
        "roadmap": ROADMAP,
        "historical_closure": closure,
        "limitations": [
            "Source hashes and retained input integrity "
            "are current read-only observations, not "
            "native replay or semantic proof.",
            "Historical assertions belong to their pinned "
            "reports; no transferred PASS or current "
            "official API claim.",
            "Unknown backend/pure "
            "time/repair/localization/Recall@K/context "
            "ratio stay null unless separately evidenced.",
            "All native/GPU evaluation allowances here are"
            " zero; report does not authorize any pending "
            "roadmap action.",
        ],
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    if value.get("schema_version") != 1 or value.get("commits") != {
        "develop": DEVELOP,
        "pr2": PR2,
    }:
        raise Invalid("Unknown schema or incorrect commits")
    if value.get("boundaries") != BOUNDARIES or value.get("roadmap") != ROADMAP:
        raise Invalid("Unsupported integration/workflow/quota/parity/readiness claim")
    ids = [x["id"] for x in value["acceptance"]]
    expected = {
        f"{f}:AC-"
        f"{'CV' if f == 'context-verification' else 'P' if f == 'pcv01' else ''}{i}"
        for f, n in SPECS.items()
        for i in range(1, n + 1)
    }
    cpu_expected = expected_cpu_classifications()
    expected.update(cpu_expected)
    if len(ids) != len(set(ids)) or set(ids) != expected:
        raise Invalid("Duplicate or omitted acceptance rows")
    for row in value["acceptance"]:
        if row["id"] in cpu_expected:
            if row["classification"] != cpu_expected[row["id"]]:
                raise Invalid("Unsupported CPU obligation classification")
            if row.get("observed_sha256") != digest(
                canonical(row.get("observed")).encode()
            ):
                raise Invalid("Unsupported CPU obligation outcome")
        if row["classification"] not in ("supported", "partial", "unmet") or not all(
            row.get(k)
            for k in ("source", "evidence", "limits", "pending", "locator_sha256")
        ):
            raise Invalid("Incomplete acceptance evidence")


def canonical(value: Any) -> str:
    return json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render(value: dict[str, Any]) -> str:
    lines = [
        "# Phase 2 reconciliation",
        "",
        "Reconciliation only; iteration 2 research remains pending.",
        "",
        f"Develop `{DEVELOP}` and unmerged PR2 `{PR2}` remain separate.",
        "",
        "Original SDD closure covers preparation. "
        "Later CPU work is ORDINARY, with its own "
        "scoped audits. No historical allowance or "
        "PASS transfers here.",
        "",
        "## Acceptance reconciliation",
        "",
        "Every source locator below is immutable; "
        "locator SHA256 and full requirement text are "
        "in source-inventory.json.",
        "",
    ]
    for row in value["acceptance"]:
        lines += [
            f"### {row['id']} — {row['classification']}",
            "",
            f"Source: `{row['source']}`.",
            "",
            "Evidence: " + ", ".join(f"`{p}`" for p in row["evidence"]) + ".",
            "",
            "Contract: " + row["requirement"],
            "",
            row.get(
                "implementation_or_receipt",
                "Scoped ordinary CPU proposal; linked "
                "published report records measured coverage.",
            ),
            "",
            row["limits"],
            "",
            "Observed: " + json.dumps(row["observed"], sort_keys=True)
            if isinstance(row.get("observed"), dict) and "id" in row["observed"]
            else "",
            "Pending: " + row["pending"],
            "",
        ]
    lines += ["## CPU milestone receipts", ""]
    for family, milestone in value.get("cpu_milestones", {}).items():
        lines += [f"### {family}", "", json.dumps(milestone, sort_keys=True), ""]
    lines += [
        "## Current retained-input integrity",
        "",
        "Counts are inventory references, including "
        "historical checkpoints; unique files/bytes "
        "hashed are separately deduplicated. MATCH "
        "means SHA256 and size where declared, never "
        "native execution.",
        "",
    ]
    for inv in value["raw_inventories"]:
        lines += [
            f"- `{inv['source']}`: {json.dumps(inv['counts'], sort_keys=True)}; "
            f"{inv['expected_bytes']} declared bytes; "
            f"{inv.get('size_undeclared_entries', 0)} hash-only entries."
        ]
    lines += [
        "",
        "Other published structured path/hash pins: "
        + json.dumps(
            dict(
                sorted(Counter(x["availability"] for x in value["other_pins"]).items())
            ),
            sort_keys=True,
        )
        + ".",
        "",
        "Hash traversal: " + json.dumps(value["hashing"], sort_keys=True) + ".",
        "",
        "Missing/mismatched/incomplete/unresolved pins"
        " have exact reasons in the JSON. Missing "
        "evidence limits reproducibility and never "
        "supports verification. Old unpublished "
        "continuity is excluded.",
        "",
        "## Pending roadmap",
        "",
    ]
    for item in value["roadmap"]:
        lines += [
            f"- {item['id']}: prerequisite: {item['prerequisite']}. "
            f"Exit evidence: {item['exit_evidence']}. "
            f"Authorization: {item['authorization']}."
        ]
    lines += ["", "## Limits", ""] + ["- " + x for x in value["limitations"]]
    lines += [
        "",
        "Independent reconciliation PR targets develop"
        " on sdd/mostaza-phase2-reconciliation after "
        "this deliverable's own gate/audit. PR2 is "
        "historical evidence; future implementation "
        "requires a separately approved integration "
        "strategy and fresh validation.",
        "",
    ]
    return "\n".join(lines)


def verify_reports(expected: dict[str, Any], inventory: bytes, report: str) -> None:
    actual = load_json(inventory)
    validate(actual)
    if actual != expected or report != render(expected):
        raise Invalid("Source facts or deterministic report drift")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    try:
        value = build()
        inventory, report = canonical(value), render(value)
        if len(inventory.encode()) + len(report.encode()) > 4 * 1024**2:
            raise Invalid("Declared reports exceed 4MiB")
        directory = ROOT / OUT
        if args.write:
            directory.mkdir(parents=True, exist_ok=True)
            (directory / "source-inventory.json").write_text(inventory)
            (directory / "report.md").write_text(report)
        else:
            verify_reports(
                value,
                (directory / "source-inventory.json").read_bytes(),
                (directory / "report.md").read_text(),
            )
        print(
            f"Reconciliation verified: {len(value['acceptance'])} rows; "
            f"{len(value['raw_inventories'])} raw inventories; no evaluations"
        )
        return 0
    except (Invalid, OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"Reconciliation prerequisite/validation failure: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
