"""Review authorized public bootstrap sources offline; never invoke a real scorer."""

import argparse
import json
from pathlib import Path

from mostaza.evaluation.scorer_contract import validate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", required=True)
    parser.parse_args()
    print(json.dumps(validate(Path(__file__).resolve().parents[1]), sort_keys=True))


if __name__ == "__main__":
    main()
