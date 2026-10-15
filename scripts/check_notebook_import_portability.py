"""Stdlib-only3.12 layout checks; no native verifier or Requests imports."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tarfile
import time
from pathlib import Path
from typing import Any


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(tree: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(tree), *args],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    ).stdout.strip()


def probe(record: dict[str, Any], tree: Path) -> dict[str, Any]:
    if record["schema"] != "mostaza.layout-transport/v1":
        raise ValueError("Unknown transport input")
    package = record["package"]
    if package not in ("cpu_import_product", "requests"):
        raise ValueError("Unknown package")
    snapshot, delta = Path(record["snapshot"]), Path(record["delta"])
    if (
        digest(snapshot) != record["snapshot_sha256"]
        or digest(delta) != record["delta_sha256"]
    ):
        raise ValueError("Transport input drift")
    expected_delta = (
        f"diff --git a/{package} b/{package}\nnew file mode 120000\n"
        f"--- /dev/null\n+++ b/{package}\n@@ -0,0 +1 @@\n"
        f"+src/{package}\n\\ No newline at end of file\n"
    ).encode()
    if delta.read_bytes() != expected_delta:
        raise ValueError("Not the reviewed layout delta")
    tree.mkdir()
    with tarfile.open(snapshot) as archive:
        members = archive.getmembers()
        if len(members) > 10000 or sum(m.size for m in members) > 128 * 1024**2:
            raise ValueError("Transport archive ceiling")
        for member in members:
            path = Path(member.name)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("Archive path escape")
            if not (
                member.isfile() or member.isdir() or member.issym() or member.islnk()
            ):
                raise ValueError("Unsupported archive member")
            if member.issym() or member.islnk():
                target = Path(member.linkname)
                base = path.parent if member.issym() else Path(".")
                if (
                    target.is_absolute()
                    or ".." in Path(os.path.normpath(base / target)).parts
                    or any(
                        Path(m.name) != path and path in Path(m.name).parents
                        for m in members
                    )
                ):
                    raise ValueError("Unsafe archive link")
        archive.extractall(tree, filter="data")
    alias = tree / package
    if alias.exists() or alias.is_symlink():
        raise ValueError("Transport alias conflict")
    subprocess.run(
        ["git", "-C", str(tree), "apply", str(delta)],
        check=True,
        capture_output=True,
        timeout=30,
    )
    git(tree, "add", "--", package)
    if (
        git(tree, "diff", "--cached", "--name-only") != package
        or git(tree, "ls-files", "--stage", "--", package).split()[0] != "120000"
        or not alias.is_symlink()
        or os.readlink(alias) != "src/" + package
        or alias.resolve() != tree / "src" / package
        or digest(tree / record["product"]) != record["product_sha256"]
    ):
        raise ValueError("Transport layout differs")
    imported = None
    if package == "cpu_import_product":
        command = (
            "import cpu_import_product as p, json, platform; "
            "print(json.dumps({'file':p.__file__, 'value':p.evaluate(), "
            "'python':platform.python_version()}))"
        )
        observed = subprocess.run(
            [sys.executable, "-S", "-c", command],
            cwd=tree,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        imported = json.loads(observed.stdout)
        if (
            Path(imported["file"]).resolve() != tree / "src" / package / "__init__.py"
            or imported["value"] != 0
            or imported["python"] != "3.12.8"
        ):
            raise ValueError("Generic3.12 import failed")
    return {
        "package": package,
        "python": sys.version.split()[0],
        "snapshot_sha256": record["snapshot_sha256"],
        "delta_sha256": record["delta_sha256"],
        "alias_target": os.readlink(alias),
        "canonical_package": str(alias.resolve()),
        "product_sha256": digest(tree / record["product"]),
        "generic_import": imported,
        "requests_imported": False,
        "native_verifier_executed": False,
    }


def run(receipt: Path, output: Path) -> dict[str, Any]:
    if sys.version_info[:3] != (3, 12, 8):
        raise ValueError("Pinned stdlib-only Python3.12.8 required")
    if any("site-packages" in p for p in sys.path):
        raise ValueError("Non-stdlib environment leaked into3.12 checker")
    summary = json.loads(receipt.read_text())
    if summary["failure"] or summary["rows_assessed"] != 6:
        raise ValueError("Native matrix not validated")
    scratch = Path(os.environ["MOSTAZA_NOTEBOOK_IMPORT_SCRATCH"])
    owner = json.loads((scratch / "owner.json").read_text())
    if owner["gate"] != str(output.parent) or scratch != scratch.resolve():
        raise ValueError("Transport scratch ownership")
    output.mkdir()
    rows = []
    failure = None
    try:
        for index, path in enumerate(summary["portable_inputs"]):
            if time.monotonic() + 90 > float(os.environ["MOSTAZA_CPU_DEADLINE"]):
                raise TimeoutError("Insufficient transport-probe allowance")
            tree = scratch / f"portabilidad ñ {index}"
            started = time.monotonic()
            (output / f"{index}-started.json").write_text(
                json.dumps(
                    {
                        "input": path,
                        "input_sha256": digest(Path(path)),
                    }
                )
            )
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-I",
                    "-S",
                    str(Path(__file__).resolve()),
                    "--probe",
                    path,
                    "--tree",
                    str(tree),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True,
            )
            try:
                stdout, stderr = process.communicate(timeout=90)
                (output / f"{index}-completed.json").write_text(
                    json.dumps(
                        {
                            "exit_code": process.returncode,
                            "stdout": stdout.decode(),
                            "stderr": stderr.decode(),
                        }
                    )
                )
                if process.returncode:
                    raise ValueError("Transport worker failed: " + stderr.decode())
                row = json.loads(stdout)
                if (
                    row["python"] != "3.12.8"
                    or row["native_verifier_executed"] is not False
                    or row["requests_imported"] is not False
                ):
                    raise ValueError("Transport worker coverage mismatch")
                rows.append({**row, "duration_seconds": time.monotonic() - started})
                (output / f"{index}-assessed.json").write_text(json.dumps(rows[-1]))
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait(timeout=3)
                if tree.exists():
                    shutil.rmtree(tree)
        if [r["package"] for r in rows] != ["cpu_import_product", "requests"]:
            raise ValueError("Missing/extra transport probes")
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
    result = {
        "status": "BLOCKED" if failure else "PASS_PY312_LAYOUT_TRANSPORT_ONLY",
        "failure": failure,
        "results": rows,
        "started": len(list(output.glob("*-started.json"))),
        "completed": len(list(output.glob("*-completed.json"))),
        "assessed": len(list(output.glob("*-assessed.json"))),
        "native_matrix_summary_sha256": digest(receipt),
        "linux_runtime_portability": "NOT_TESTED",
        "private_scorer_parity": None,
        "requests_import_coverage": None,
        "requests_import_coverage_reason": "No Requests dependencies installed in3.12",
    }
    (output / "summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n"
    )
    if failure:
        raise ValueError(f"{failure}; evidence: {output}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--probe", type=Path)
    parser.add_argument("--tree", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.probe is not None and args.tree is not None:
        print(
            json.dumps(probe(json.loads(args.probe.read_text()), args.tree.resolve()))
        )
    elif args.check and args.receipt is not None and args.output is not None:
        print(json.dumps(run(args.receipt.resolve(), args.output.resolve())))
    else:
        parser.error("Select --check/--receipt/--output or owned --probe/--tree")


if __name__ == "__main__":
    main()
