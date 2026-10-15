"""Generate or check the unapproved startup-corrected notebook; never starts Kaggle."""

import argparse
import json
from pathlib import Path

from mostaza.evaluation.startup_candidate import NOTEBOOK, build_notebook


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.receipt and (args.output is None or args.check):
        parser.error("A bound notebook requires --output and cannot use --check")
    if args.output is not None:
        resolved = args.output.resolve()
        if not resolved.is_relative_to(root / "results") or resolved.is_symlink():
            parser.error("Operational output must be a new file inside project results")
    receipt = None if args.receipt is None else json.loads(args.receipt.read_text())
    expected = build_notebook(root, receipt)
    if args.check:
        if (root / NOTEBOOK).read_bytes() != expected:
            raise ValueError("Startup-corrected notebook/source mismatch")
        print(
            "Startup-corrected notebook provenance verified; GPU authorization absent"
        )
    else:
        target = root / NOTEBOOK if args.output is None else args.output
        if args.output is not None:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(expected)
        else:
            target.write_bytes(expected)
        print("Prepared local notebook; no remote execution; GPU remains disabled")


if __name__ == "__main__":
    main()
