#!/usr/bin/env python3
"""Explicitly install Hybrid Team into a project while preserving owned content."""

import argparse
import json
import sys
from pathlib import Path

SOURCE = Path(__file__).resolve().parent
sys.path.insert(0, str(SOURCE / "runtime"))
from okms_team.adoption import install
from okms_team.state import TeamError


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--docs", help="Explicit new/Hybrid Team documentation directory")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(install(SOURCE, args.project, args.docs, dry_run=args.dry_run), indent=2))
        return 0
    except (TeamError, OSError, ValueError) as error:
        print(json.dumps({"error": str(error), "incomplete": True}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
