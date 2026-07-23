#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def expected_tag() -> str:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return f"v{project['project']['version']}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tag")
    args = parser.parse_args()
    expected = expected_tag()
    if args.tag != expected:
        parser.error(f"tag {args.tag!r} does not match package tag {expected!r}")
    print(f"release tag matches package: {expected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
