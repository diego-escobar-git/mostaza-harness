"""search-code:AC-8: safe snapshot inputs and fail-closed CPU reports."""

import copy
import importlib.util
import io
import sys
import tarfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "check_search_code", ROOT / "scripts/check_search_code.py"
)
DRIVER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DRIVER)


def archive(path, entries):
    with tarfile.open(path, "w:gz") as bundle:
        for name, kind in entries:
            member = tarfile.TarInfo(name)
            if kind == "link":
                member.type = tarfile.SYMTYPE
                member.linkname = "/etc/passwd"
                bundle.addfile(member)
            else:
                data = b"def source_symbol(): return 1\n"
                member.size = len(data)
                bundle.addfile(member, io.BytesIO(data))


@pytest.mark.parametrize(
    "entries",
    [
        [("../escape.py", "file")],
        [("/escape.py", "file")],
        [("source.py", "link")],
        [("source.py", "file"), ("source.py", "file")],
    ],
)
def test_ac8_unsafe_archive_rejected_before_writing(tmp_path, entries):
    path = tmp_path / "source.tgz"
    archive(path, entries)
    target = tmp_path / "out"
    target.mkdir()
    with pytest.raises(ValueError):
        DRIVER.extract_source(path, target)
    assert not list(target.iterdir())


def test_ac8_source_only_archive_provenance(tmp_path):
    path = tmp_path / "source.tgz"
    archive(
        path,
        [
            ("source.py", "file"),
            (".git/private.py", "file"),
            ("solution/secret.py", "file"),
            ("test_patch/secret.py", "file"),
            ("tasks.jsonl", "file"),
            ("graph.json", "file"),
        ],
    )
    target = tmp_path / "out"
    target.mkdir()
    result = DRIVER.extract_source(path, target)
    assert result["files"] == 1
    assert list(target.iterdir()) == [target / "source.py"]
    assert len(result["archive_sha256"]) == len(result["source_sha256"]) == 64


def reports():
    measured = {
        "raw_peak_rss": 1000,
        "raw_unit": "bytes",
        "seconds": 0.01,
        "peak_rss_bytes": 1000,
        "index": {"database_bytes": 100, "reparsed_files": 0},
    }
    case = {
        "top5_match": {
            "name": "source_symbol",
            "path": "source.py",
            "start_line": 1,
            "end_line": 2,
            "rank": 1,
        },
        "query": "source_symbol",
        "query_sha256": DRIVER.digest(b"source_symbol"),
        "path": "source.py",
        "start_line": 1,
        "end_line": 2,
    }
    snapshot = {
        "archive_sha256": "a" * 64,
        "source_sha256": "b" * 64,
        "edited_source_sha256": "c" * 64,
        "status": "PASS",
        "queries": [case] * 3,
        "cold": measured,
        "warm": [measured] * 3,
        "refresh": {**measured, "index": {**measured["index"], "reparsed_files": 1}},
    }
    benchmark = {
        "schema_version": 1,
        "status": "PASS",
        "limits": DRIVER.LIMITS,
        "synthetic": {
            "status": "PASS",
            "expected_edges": [["caller_symbol", "target_symbol", "calls"]],
            "dependent_edges_invalidated": True,
            "ambiguity": "ambiguous",
            "non_python_retrieved": True,
        },
        "snapshots": [
            {**copy.deepcopy(snapshot), "id": name} for name in DRIVER.SNAPSHOTS
        ],
    }
    benchmark["synthetic_python312"] = copy.deepcopy(benchmark["synthetic"])
    validation = {
        "official_witness": {
            "native_tools": [
                "run_command",
                "read_file",
                "edit_file",
                "write_file",
                "get_status",
                "submit_patch",
            ],
            "refresh_reparsed": [0, 1, 1, 1],
            "llm_calls": 0,
            "patch_clean": True,
            "transient_resources_removed": True,
            "docker_execution": "NOT_RUN",
            "kaggle_execution": "NOT_RUN",
        },
        "schema_version": 1,
        "status": "PASS",
        "prerequisites": [
            {
                "path": "/retained/" + str(i),
                "status": "PRESENT_REQUIRES_EXISTING_PIN_CHECKS",
            }
            for i in range(5)
        ],
        "checks": [
            {
                "id": name,
                "status": "PASS",
                "exit_code": 0,
                "argv": ["python", "check"],
                "cwd": str(ROOT),
            }
            for name in DRIVER.EXPECTED_CHECKS
        ],
    }
    return validation, benchmark


def test_ac8_report_accepts_complete_measurements():
    DRIVER.validate_reports(*reports())


@pytest.mark.parametrize(
    "defect",
    [
        "missing_snapshot",
        "missing_check",
        "failed_check",
        "missing_fixture",
        "fake_exit",
        "relaxed_threshold",
        "rss",
        "time",
        "database",
        "warm_reparse",
        "refresh_reparse",
        "query_hash",
        "synthetic",
    ],
)
def test_ac8_report_fails_closed(defect):
    validation, benchmark = reports()
    if defect == "missing_snapshot":
        benchmark["snapshots"].pop()
    elif defect == "missing_check":
        validation["checks"].pop()
    elif defect == "failed_check":
        validation["checks"][0]["status"] = "FAIL"
    elif defect == "missing_fixture":
        validation["prerequisites"][0]["status"] = "MISSING"
    elif defect == "fake_exit":
        validation["checks"][0]["exit_code"] = 1
    elif defect == "relaxed_threshold":
        benchmark["limits"] = {**DRIVER.LIMITS, "warm_seconds": 50}
    elif defect == "rss":
        benchmark["snapshots"][0]["cold"]["peak_rss_bytes"] = 300 * 1024**2
    elif defect == "time":
        benchmark["snapshots"][0]["cold"]["seconds"] = 46
    elif defect == "database":
        benchmark["snapshots"][0]["cold"]["index"]["database_bytes"] = 129 * 1024**2
    elif defect == "warm_reparse":
        benchmark["snapshots"][0]["warm"][0]["index"]["reparsed_files"] = 1
    elif defect == "refresh_reparse":
        benchmark["snapshots"][0]["refresh"]["index"]["reparsed_files"] = 0
    elif defect == "query_hash":
        benchmark["snapshots"][0]["queries"][0]["query_sha256"] = "wrong"
    else:
        benchmark["synthetic"]["status"] = "FAIL"
    with pytest.raises(ValueError):
        DRIVER.validate_reports(validation, benchmark)


def test_ac8_top_five_requires_exact_symbol_location():
    case = {"query": "symbol", "path": "source.py", "start_line": 4, "end_line": 9}
    hit = {"name": "symbol", "path": "source.py", "start_line": 4, "end_line": 9}
    DRIVER.assert_hit({"results": [hit]}, case)
    for result in (
        {"results": [{**hit, "start_line": 3}]},
        {"results": [{}] * 5 + [hit]},
    ):
        with pytest.raises(ValueError):
            DRIVER.assert_hit(result, case)


def test_ac8_archive_link_entries_are_never_materialized(tmp_path):
    path = tmp_path / "source.tgz"
    archive(path, [("source.py", "file"), ("certificates/ca", "link")])
    target = tmp_path / "out"
    target.mkdir()
    report = DRIVER.extract_source(path, target)
    assert report["rejected_entries"] == {"symlink_or_hardlink": 1}
    assert not (target / "certificates").exists()
    assert (target / "source.py").is_file()


@pytest.mark.parametrize(
    "defect",
    ["no_witness", "no312", "rss_units", "no_observed_hit", "no_prerequisites"],
)
def test_ac8_reports_reject_missing_execution_provenance(defect):
    validation, benchmark = reports()
    if defect == "no_witness":
        validation.pop("official_witness")
    elif defect == "no312":
        benchmark.pop("synthetic_python312")
    elif defect == "rss_units":
        benchmark["snapshots"][0]["cold"]["raw_unit"] = "KiB"
    elif defect == "no_observed_hit":
        benchmark["snapshots"][0]["queries"][0].pop("top5_match")
    else:
        validation["prerequisites"] = []
    with pytest.raises(ValueError):
        DRIVER.validate_reports(validation, benchmark)


def test_ac8_skipped_tests_cannot_pass_child_gate(tmp_path):
    report = DRIVER.check_command(
        "unit", [sys.executable, "-c", "print('1 skipped')", "pytest"], tmp_path
    )
    assert report["exit_code"] == 0
    assert report["skipped_tests"] == 1
    assert report["status"] == "FAIL"
