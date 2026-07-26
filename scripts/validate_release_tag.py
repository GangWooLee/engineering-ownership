#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def expected_tag() -> str:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return f"v{project['project']['version']}"


def last_commit_epoch(path: str) -> int:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", path],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    text = result.stdout.strip()
    return int(text) if result.returncode == 0 and text.isdigit() else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("tag")
    args = parser.parse_args()
    expected = expected_tag()
    if args.tag != expected:
        parser.error(f"tag {args.tag!r} does not match package tag {expected!r}")
    notes = ROOT / "docs" / "releases" / f"{args.tag}.md"
    if not notes.is_file():
        parser.error(f"release notes docs/releases/{args.tag}.md do not exist")
    # Stale notes published verbatim are a false document with a version on it.
    # If shipped content changed after the notes were last touched, refuse the
    # tag. Both timestamps must resolve (a shallow clone yields equal times and
    # passes trivially; the release workflow fetches full history for this).
    shipped = last_commit_epoch("plugins")
    documented = last_commit_epoch(f"docs/releases/{args.tag}.md")
    if shipped and documented and shipped > documented:
        parser.error(
            f"shipped content changed after docs/releases/{args.tag}.md was last "
            "amended; update the release notes and CHANGELOG before tagging"
        )
    print(f"release tag matches package: {expected}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
