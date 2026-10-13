"""Fetch only explicit pinned small public official resources."""

import argparse
from pathlib import Path

from mostaza.resources import ResourceError, fetch_resource, require_resources


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource", action="append", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        if args.check:
            require_resources(root, args.resource)
        else:
            for resource_id in args.resource:
                fetch_resource(root, resource_id)
    except (ResourceError, OSError) as error:
        parser.exit(1, f"Official resource prerequisite failed: {error}\n")


if __name__ == "__main__":
    main()
