"""phase2-reconciliation:AC-5: synthetic metadata, never evaluation results."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from typing import Any
from unittest.mock import patch

PATH = Path(__file__).resolve().parents[2] / "scripts/check_phase2_reconciliation.py"
SPEC = importlib.util.spec_from_file_location("reconciliation", PATH)
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def fixture() -> dict[str, Any]:
    rows = []
    for family, count in checker.SPECS.items():
        prefix = (
            "CV"
            if family == "context-verification"
            else "P"
            if family == "pcv01"
            else ""
        )
        for index in range(1, count + 1):
            rows.append(
                {
                    "id": f"{family}:AC-{prefix}{index}",
                    "classification": "partial",
                    "source": checker.PR2 + ":synthetic.md",
                    "evidence": ["synthetic"],
                    "requirement": "Synthetic acceptance fixture",
                    "limits": "Synthetic fixture only",
                    "pending": "No evaluation",
                    "locator_sha256": "a" * 64,
                }
            )
    for identifier, classification in checker.expected_cpu_classifications().items():
        rows.append(
            {
                "id": identifier,
                "classification": classification,
                "source": checker.PR2 + ":synthetic-proposal.md",
                "evidence": ["synthetic"],
                "requirement": "Synthetic obligation",
                "limits": "Synthetic only",
                "pending": "No evaluation",
                "locator_sha256": "a" * 64,
                "observed": {"synthetic": True},
                "observed_sha256": checker.digest(
                    checker.canonical({"synthetic": True}).encode()
                ),
            }
        )
    return {
        "schema_version": 1,
        "commits": {"develop": checker.DEVELOP, "pr2": checker.PR2},
        "boundaries": deepcopy(checker.BOUNDARIES),
        "acceptance": rows,
        "roadmap": deepcopy(checker.ROADMAP),
        "raw_inventories": [],
        "other_pins": [],
        "hashing": {},
        "limitations": ["Synthetic only"],
    }


def synthetic_sources(root: Path) -> dict[str, bytes]:
    """Synthetic source tree for complete generation; no product/native execution."""
    texts: dict[str, bytes] = {}
    selectors: dict[str, list[str]] = {}
    for declarations in checker.DETAILS.values():
        for path, selector, _ in declarations:
            selectors.setdefault(path, []).append(selector)
    for path, values in selectors.items():
        texts[path] = (
            json.dumps({x: "synthetic" for x in values}).encode()
            if path.endswith(".json")
            else "\n".join(values).encode()
        )
    for family, count in checker.SPECS.items():
        prefix = (
            "CV"
            if family == "context-verification"
            else "P"
            if family == "pcv01"
            else ""
        )
        texts[f"docs/specs/{family}.md"] = "\n".join(
            f"AC-{prefix}{n}: Synthetic obligation." for n in range(1, count + 1)
        ).encode()
        texts.setdefault(
            f"docs/implementation/evidence/{checker.source_family(family)}/report.md",
            b"Synthetic report",
        )
    for family, declarations in checker.CPU_MANIFEST.items():
        paragraphs = [
            f"Synthetic obligation {i}"
            for i in range(1, max(x[0] for x in declarations) + 1)
        ]
        for paragraph, kind, _ in declarations:
            if kind == "matrix":
                paragraphs[paragraph - 1] = "\n".join(
                    f"| {case} | Synthetic contract |"
                    for case in checker.CPU_CASES[family]
                )
        texts[checker.cpu_source(family, "plan-for-approval.md")] = "\n\n".join(
            paragraphs
        ).encode()
        tests = {
            "verify-task-cpu": (306, 45),
            "requests-import-cpu": (328, 49),
            "notebook-import-cpu": (378, 119),
        }[family]
        texts[checker.cpu_source(family, "report.md")] = (
            f"Synthetic receipt only\n## Implementation\n{tests[0]} unit tests; "
            f"{tests[1]} integration tests"
        ).encode()
        source = "src/mostaza/evaluation/" + family.replace("-", "_") + ".py"
        if family == "notebook-import-cpu":
            source = "src/mostaza/evaluation/notebook_import.py"
        texts[source] = b"def synthetic_fixture(): pass\n"
        cases = [
            checker.expected_case(family, case) for case in checker.CPU_CASES[family]
        ]
        for case in cases:
            case["agent_patch_sha256"] = "a" * 64
            case["test_patch_sha256"] = "b" * 64
        result: dict[str, Any] = {
            "status": "SYNTHETIC_ONLY",
            "rows" if family == "notebook-import-cpu" else "results": cases,
            "invocations_assessed": len(cases),
            "gpu_readiness": False,
            "actual_scorer_runtime_parity": None,
        }
        attempts: list[dict[str, Any]] = []
        count = {
            "verify-task-cpu": 3,
            "requests-import-cpu": 2,
            "notebook-import-cpu": 6,
        }[family]
        commands = {
            "verify-task-cpu": 9,
            "requests-import-cpu": 10,
            "notebook-import-cpu": 12,
        }[family]
        additions = [
            "additional-gate-approval.json",
            "resource-gate-approval.json",
            "source-filter-gate-approval.json",
            "supervision-gate-approval.json",
        ]
        for i in range(1, count + 1):
            attempt = {
                "attempt": i,
                "passed": i == count,
                "duration_seconds": float(i),
                "commands": [{"exit_code": 0} for _ in range(commands)],
            }
            if family == "notebook-import-cpu":
                attempt["actual_counts"] = {
                    "native_total": {
                        "started": [20, 21, 0, 23, 24, 26][i - 1],
                        "completed": [19, 21, 0, 23, 24, 26][i - 1],
                    },
                    "setup": {"started": [0, 1, 0, 3, 4, 6][i - 1]},
                    "stdlib": {"started": 2 if i == 6 else 0},
                }
                attempt["failure"] = None if i == count else "Synthetic failure"
                if i >= 3:
                    name = additions[i - 3]
                    approval_data = json.dumps(
                        {"status": "APPROVED", "synthetic": i}
                    ).encode()
                    texts[checker.cpu_source(family, name)] = approval_data
                    attempt["additional_authorization"] = {
                        "approval_sha256": checker.digest(approval_data)
                    }
            attempts.append(attempt)
        gates = {
            "attempts": attempts,
            "total_native_invocations": 40,
            "total_native_started": 114,
            "retained_native_results": 113,
            "setup_started": 14,
            "stdlib_started": 2,
            "total_gate_wall_seconds": 21.0,
        }
        if family == "notebook-import-cpu":
            result.update(
                {
                    "counts": attempts[-1]["actual_counts"],
                    "sampled_peak_bytes": 100,
                    "python312_transport": {
                        "assessed": 2,
                        "synthetic": True,
                        "results": [],
                    },
                }
            )
        texts[checker.cpu_source(family, "cpu-results.json")] = json.dumps(
            result
        ).encode()
        texts[checker.cpu_source(family, "gate-attempts.json")] = json.dumps(
            gates
        ).encode()
        texts[checker.cpu_source(family, "audit.json")] = json.dumps(
            {"status": "PASS", "findings": [], "synthetic": True}
        ).encode()
        texts[checker.cpu_source(family, "approval.json")] = b'{"synthetic": true}'
        if family == "verify-task-cpu":
            texts[checker.cpu_source(family, "additional-attempt-approval.json")] = (
                b'{"approved": true, "gate_attempt": 3}'
            )
        if family == "requests-import-cpu":
            texts[checker.cpu_source(family, "corrective-attempt.json")] = (
                b'{"finding_id": "RI-A01"}'
            )
    # A real hash-only nested file traversal inside the synthetic source tree.
    base = root / "results/synthetic-full"
    base.mkdir(parents=True)
    (base / "trace").write_bytes(b"synthetic retained input")
    inventory = json.dumps(
        {
            "files": [
                {"path": "trace", "sha256": checker.digest(b"synthetic retained input")}
            ],
            "source_run_id": "synthetic",
        }
    ).encode()
    (base / "source-inventory.json").write_bytes(inventory)
    texts[
        (
            "docs/implementation/evidence/"
            "mostaza-phase1-foundation/official-validation.json"
        )
    ] = json.dumps(
        {
            "acquisition": {
                "source_inventory": {
                    "path": "results/synthetic-full/source-inventory.json",
                    "sha256": checker.digest(inventory),
                    "verified_entries": 1,
                }
            }
        }
    ).encode()
    closed = {
        "audits": [{"verdict": "FIX_REQUIRED"}, {"verdict": "PASS"}],
        "versioning": {"status": "CLOSED_FOR_COMMIT", "candidate": {"synthetic": True}},
    }
    texts["docs/specs/plans/closed/mostaza-phase2-budget-retrieval.md"] = (
        "```sdd-execution\n" + json.dumps(closed) + "\n```"
    ).encode()
    return texts


class ReconciliationTests(unittest.TestCase):
    def test_valid_and_deterministic_fixture(self) -> None:
        value = fixture()
        checker.validate(value)
        checker.verify_reports(
            value, checker.canonical(value).encode(), checker.render(value)
        )
        self.assertEqual(checker.render(value), checker.render(deepcopy(value)))

    def test_missing_duplicate_acceptance(self) -> None:
        for change in ("missing", "duplicate"):
            value = fixture()
            if change == "missing":
                value["acceptance"].pop()
            else:
                value["acceptance"].append(value["acceptance"][0])
            with self.assertRaises(checker.Invalid):
                checker.validate(value)

    def test_false_claims_and_workflow_confusion(self) -> None:
        for key, wrong in {
            "pr2_integrated": True,
            "cpu_followups": "SDD PASS",
            "historical_allowances_reusable": True,
            "native_evaluations": 1,
            "private_scorer_parity": True,
            "real_evaluation_ready": True,
            "hybrid_efficacy": "superior",
            "research_complete": True,
        }.items():
            with self.subTest(key=key):
                value = fixture()
                value["boundaries"][key] = wrong
                with self.assertRaises(checker.Invalid):
                    checker.validate(value)

    def test_wrong_commit_unknown_schema(self) -> None:
        for key, wrong in (("schema_version", 77), ("commits", {"pr2": "HEAD"})):
            value = fixture()
            value[key] = wrong
            with self.assertRaises(checker.Invalid):
                checker.validate(value)

    def test_report_and_inventory_drift(self) -> None:
        value = fixture()
        with self.assertRaises(checker.Invalid):
            checker.verify_reports(
                value,
                checker.canonical(value).encode(),
                checker.render(value) + "drift",
            )
        changed = deepcopy(value)
        changed["acceptance"][0]["limits"] = "unsupported assertion"
        with self.assertRaises(checker.Invalid):
            checker.verify_reports(
                value, checker.canonical(changed).encode(), checker.render(value)
            )

    def test_missing_corrupt_and_valid_raw(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            entry = {"path": "source", "bytes": 3, "sha256": checker.digest(b"abc")}
            self.assertEqual(
                checker.raw_result(entry, (root,), checker.HashBudget())[
                    "availability"
                ],
                "MISSING",
            )
            (root / "source").write_bytes(b"bad")
            self.assertEqual(
                checker.raw_result(entry, (root,), checker.HashBudget())[
                    "availability"
                ],
                "MISMATCH",
            )
            (root / "source").write_bytes(b"abc")
            self.assertEqual(
                checker.raw_result(entry, (root,), checker.HashBudget())[
                    "availability"
                ],
                "MATCH",
            )

    def test_malicious_paths_and_symlink(self) -> None:
        for value in (
            "../secret",
            "/etc/passwd",
            "a/../../secret",
            "a\\b",
            "a//b",
            "./a",
        ):
            with self.assertRaises(checker.Invalid):
                checker.safe_relative(value)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "escape").symlink_to("/etc/passwd")
            with self.assertRaises(checker.Invalid):
                checker.HashBudget().inspect(root, "escape")

    def test_duplicate_inventory_and_unknown_entry(self) -> None:
        entry = {"path": "a", "bytes": 0, "sha256": checker.digest(b"")}
        self.assertEqual(checker.inventory_entries({"files": [entry]}), [entry])
        invalid: tuple[dict[str, Any], ...] = (
            {"files": [entry, entry]},
            {"files": [{**entry, "trust_me": True}]},
            {"unknown": []},
        )
        for value in invalid:
            with self.assertRaises(checker.Invalid):
                checker.inventory_entries(value)
        with self.assertRaises(checker.Invalid):
            checker.load_json(b'{"files": [], "files": []}')

    def test_git_source_rejected(self) -> None:
        with self.assertRaises(checker.Invalid):
            checker.blob(Path("/not/a/repository"), "HEAD", "file")
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(checker.Invalid):
                checker.blob(Path(temp), checker.PR2, "missing")

    def test_caps_and_deduplication(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "input").write_bytes(b"a")
            budget = checker.HashBudget()
            budget.inspect(root, "input")
            budget.inspect(root, "input")
            self.assertEqual(budget.bytes, 1)
            budget = checker.HashBudget()
            budget.bytes = checker.MAX_BYTES
            with self.assertRaises(checker.Invalid):
                budget.inspect(root, "input")
            budget = checker.HashBudget()
            budget.entries = checker.MAX_ENTRIES
            with self.assertRaises(checker.Invalid):
                budget.inspect(root, "input")

    def test_schema_specific_relative_closure_and_resource_pins(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = (
                "docs/implementation/evidence/"
                "mostaza-context-verification/closure-inventory.json"
            )
            parent = root / Path(source).parent
            parent.mkdir(parents=True)
            (parent / "approval.json").write_bytes(b"approved")
            pin = {
                "path": "approval.json",
                "bytes": 8,
                "sha256": checker.digest(b"approved"),
            }
            texts = {source: json.dumps([pin]).encode()}
            _, results = checker.check_published_pins(
                texts, (root,), checker.HashBudget()
            )
            self.assertEqual(results[0]["availability"], "MATCH")
            self.assertEqual(results[0]["locator_base"], "evidence-directory")
            (parent / "approval.json").write_bytes(b"corrupt!")
            _, results = checker.check_published_pins(
                texts, (root,), checker.HashBudget()
            )
            self.assertEqual(results[0]["availability"], "MISMATCH")
            (parent / "approval.json").unlink()
            _, results = checker.check_published_pins(
                texts, (root,), checker.HashBudget()
            )
            self.assertEqual(results[0]["availability"], "MISSING")
            resource = root / "resources/official/sample_submission/agent.yaml"
            resource.parent.mkdir(parents=True)
            resource.write_bytes(b"agent")
            source = (
                "docs/implementation/evidence/"
                "mostaza-phase1-foundation/resource-review.json"
            )
            document: dict[str, Any] = {
                "verified_source_review": {
                    "sample_tree_inventory": {
                        "files": [
                            {
                                "path": "sample_submission/agent.yaml",
                                "sha256": checker.digest(b"agent"),
                            }
                        ]
                    }
                }
            }
            _, results = checker.check_published_pins(
                {source: json.dumps(document).encode()}, (root,), checker.HashBudget()
            )
            self.assertEqual(results[0]["availability"], "MATCH")
            self.assertEqual(results[0]["locator_base"], "official-resource-directory")

    def test_hash_only_pins_are_verified_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "raw").write_bytes(b"abc")
            source = "docs/implementation/evidence/synthetic/source-inventory.json"
            texts = {
                source: json.dumps(
                    {"files": [{"path": "raw", "sha256": checker.digest(b"abc")}]}
                ).encode()
            }
            for state in ("MATCH", "MISMATCH", "MISSING"):
                if state == "MISMATCH":
                    (root / "raw").write_bytes(b"bad")
                elif state == "MISSING":
                    (root / "raw").unlink()
                _, results = checker.check_published_pins(
                    texts, (root,), checker.HashBudget()
                )
                self.assertEqual(results[0]["availability"], state)
                self.assertEqual(results[0]["size_check"], "NOT_DECLARED")
                if state == "MATCH":
                    self.assertEqual(results[0]["observations"][0]["bytes"], 3)

    def test_nested_acquisition_hash_only_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "results/synthetic-acquisition"
            base.mkdir(parents=True)
            (base / "raw").write_bytes(b"observed")
            raw_inventory = json.dumps(
                {
                    "files": [{"path": "raw", "sha256": checker.digest(b"observed")}],
                    "source_run_id": "synthetic-not-evaluation",
                }
            ).encode()
            (base / "source-inventory.json").write_bytes(raw_inventory)
            source = (
                "docs/implementation/evidence/"
                "mostaza-phase1-foundation/official-validation.json"
            )
            document: dict[str, Any] = {
                "acquisition": {
                    "source_inventory": {
                        "path": "results/synthetic-acquisition/source-inventory.json",
                        "sha256": checker.digest(raw_inventory),
                        "verified_entries": 1,
                    }
                }
            }
            texts = {source: json.dumps(document).encode()}
            for state in ("MATCH", "MISMATCH", "MISSING"):
                if state == "MISMATCH":
                    (base / "raw").write_bytes(b"corrupt")
                elif state == "MISSING":
                    (base / "raw").unlink()
                inventories, _ = checker.check_published_pins(
                    texts, (root,), checker.HashBudget()
                )
                self.assertEqual(inventories[0]["counts"], {state: 1})
                self.assertEqual(inventories[0]["size_undeclared_entries"], 1)
                self.assertEqual(
                    inventories[0]["files"][0]["path"],
                    "results/synthetic-acquisition/raw",
                )
            (base / "source-inventory.json").write_bytes(b"corrupt inventory")
            inventories, _ = checker.check_published_pins(
                texts, (root,), checker.HashBudget()
            )
            self.assertEqual(inventories[0]["coverage"], "UNVERIFIED_INVENTORY")
            self.assertEqual(inventories[0]["counts"], {})

    def test_download_inventory_relative_output_base(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "results/synthetic-download"
            output = base / "downloaded-output"
            output.mkdir(parents=True)
            (output / "trace").write_bytes(b"trace")
            raw_inventory = json.dumps(
                [{"path": "trace", "bytes": 5, "sha256": checker.digest(b"trace")}]
            ).encode()
            (base / "download-inventory.json").write_bytes(raw_inventory)
            source = (
                "docs/implementation/evidence/"
                "mostaza-phase2-startup-run/acquisition.json"
            )
            document: dict[str, Any] = {
                "source_bundle": "results/synthetic-download",
                "download": {
                    "inventory_sha256": checker.digest(raw_inventory),
                    "files": 1,
                },
            }
            inventories, _ = checker.check_published_pins(
                {source: json.dumps(document).encode()}, (root,), checker.HashBudget()
            )
            self.assertEqual(inventories[0]["counts"], {"MATCH": 1})
            self.assertEqual(
                inventories[0]["files"][0]["path"],
                "results/synthetic-download/downloaded-output/trace",
            )
            document["download"]["files"] = 2
            with self.assertRaises(checker.Invalid):
                checker.check_published_pins(
                    {source: json.dumps(document).encode()},
                    (root,),
                    checker.HashBudget(),
                )

    def test_snapshot_components_are_not_repository_locators(self) -> None:
        source = (
            "docs/implementation/evidence/mostaza-notebook-import-cpu/cpu-results.json"
        )
        view_root = "/private/tmp/mostaza-notebook-import-01234567/R00/inputs"
        entry = {
            "path": "base_snapshots/base_psf_requests.tgz",
            "bytes": 3,
            "sha256": checker.digest(b"abc"),
        }
        document = {
            "rows": [
                {
                    "actual_inputs": {
                        "root": view_root,
                        "tasks": {"requests_7205": [entry]},
                    }
                }
            ]
        }
        mapped, base, unavailable = checker.resolve_pin(
            source, "/rows/0/actual_inputs/tasks/requests_7205/0", entry, document
        )
        self.assertEqual(mapped, entry)
        self.assertEqual(base, "snapshot-input-view:" + view_root)
        self.assertEqual(unavailable, "NOT_RETAINED_TEMPORARY_INPUT_VIEW")
        with self.assertRaises(checker.Invalid):
            checker.resolve_pin(
                source,
                "/rows/0/actual_inputs/tasks/requests_7205/0",
                {**entry, "path": "../escape"},
                document,
            )

    def test_cpu_obligations_cannot_be_omitted_or_reclassified(self) -> None:
        for change in ("omitted", "classification", "outcome"):
            value = fixture()
            row = next(
                x
                for x in value["acceptance"]
                if x["id"].startswith("notebook-import-cpu:")
            )
            if change == "omitted":
                value["acceptance"].remove(row)
            elif change == "classification":
                row["classification"] = "unmet"
            else:
                row["observed"] = {"unsupported": "scorer equivalent"}
            with self.assertRaises(checker.Invalid):
                checker.validate(value)

    def test_rehashed_unsupported_cpu_outcome_still_fails_recomputation(self) -> None:
        expected = fixture()
        changed = deepcopy(expected)
        row = next(
            x
            for x in changed["acceptance"]
            if x["id"].startswith("requests-import-cpu:")
        )
        row["observed"] = {"native_resolved": True, "claim": "official task score"}
        row["observed_sha256"] = checker.digest(
            checker.canonical(row["observed"]).encode()
        )
        with self.assertRaises(checker.Invalid):
            checker.verify_reports(
                expected, checker.canonical(changed).encode(), checker.render(expected)
            )

    def test_full_generation_with_nested_hash_only_and_cpu_obligations(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            texts = synthetic_sources(root)

            def fake_git(project: Path, *args: str) -> bytes:
                if args[0] == "rev-parse":
                    return str(checker.DEVELOP).encode()
                if args[0] == "ls-tree":
                    return "\n".join(sorted(texts)).encode()
                raise AssertionError(args)

            def fake_blob(project: Path, commit: str, path: str) -> bytes:
                self.assertIn(commit, (checker.PR2, checker.DEVELOP))
                return texts[path]

            with (
                patch.object(checker, "git", fake_git),
                patch.object(checker, "blob", fake_blob),
            ):
                value = checker.build(root, (root,))
                checker.verify_reports(
                    value, checker.canonical(value).encode(), checker.render(value)
                )
                self.assertEqual(value["raw_inventories"][0]["counts"], {"MATCH": 1})
                self.assertEqual(
                    value["raw_inventories"][0]["size_undeclared_entries"], 1
                )
                self.assertEqual(
                    len(
                        [
                            r
                            for r in value["acceptance"]
                            if ":proposal-paragraph-" in r["id"]
                        ]
                    ),
                    len(checker.expected_cpu_classifications()),
                )
                # Even a fully rehashed exported forgery cannot pass recomputation.
                changed = deepcopy(value)
                row = next(
                    r for r in changed["acceptance"] if r["id"].endswith(":N-R02")
                )
                row["observed"]["native_resolved"] = False
                row["observed_sha256"] = checker.digest(
                    checker.canonical(row["observed"]).encode()
                )
                with self.assertRaises(checker.Invalid):
                    checker.verify_reports(
                        value,
                        checker.canonical(changed).encode(),
                        checker.render(value),
                    )
                # Changing a source receipt to claim a wrong diagnostic outcome
                # fails generation itself, before rendering or report comparison.
                path = checker.cpu_source("notebook-import-cpu", "cpu-results.json")
                receipt = json.loads(texts[path])
                receipt["rows"][-1]["native_resolved"] = False
                texts[path] = json.dumps(receipt).encode()
                with self.assertRaises(checker.Invalid):
                    checker.build(root, (root,))

    def test_retained_checkpoint_view_uses_cleanup_and_never_reads_tmp(self) -> None:
        view_root = (
            "/private/tmp/mostaza-notebook-import-"
            "61156e75-759a-46f6-8081-8d2d5f09c975/L01/inputs"
        )
        component = {
            "path": "base_snapshots/base_mostaza_owned_src_layout.tgz",
            "bytes": 3,
            "sha256": checker.digest(b"abc"),
            "role": "base",
        }
        document = {
            "retained_first_row": {
                "cleanup_complete": True,
                "view": {
                    "root": view_root,
                    "tasks": {"cpu_owned_layout": [component]},
                },
            }
        }
        source = (
            "docs/implementation/evidence/mostaza-notebook-import-cpu/checkpoints/"
            "before-additional-gate/cpu-results.json"
        )
        # The complete pin collector must never inspect repository or historical
        # temporary files for a published disposable view marked cleaned.
        budget = checker.HashBudget()
        with patch.object(
            budget, "inspect", side_effect=AssertionError("unexpected file read")
        ):
            inventories, pins = checker.check_published_pins(
                {source: json.dumps(document).encode()}, (Path("/synthetic"),), budget
            )
        self.assertEqual(inventories, [])
        self.assertEqual(len(pins), 1)
        self.assertEqual(pins[0]["availability"], "NOT_RETAINED_TEMPORARY_INPUT_VIEW")
        self.assertEqual(pins[0]["locator_base"], "snapshot-input-view:" + view_root)
        self.assertEqual(pins[0]["path"], component["path"])
        document["retained_first_row"]["cleanup_complete"] = False
        _, pins = checker.check_published_pins(
            {source: json.dumps(document).encode()},
            (Path("/synthetic"),),
            checker.HashBudget(),
        )
        self.assertEqual(
            pins[0]["availability"], "UNVERIFIED_TEMPORARY_INPUT_VIEW_RETENTION"
        )
        self.assertNotIn("was cleaned", pins[0]["reason"])

    def test_canonical_json(self) -> None:
        value = fixture()
        self.assertEqual(json.loads(checker.canonical(value)), value)


if __name__ == "__main__":
    unittest.main()
