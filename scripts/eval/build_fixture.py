#!/usr/bin/env python3
"""Materialize a deterministic repository state for one evaluation prompt.

Several evaluation prompts presuppose repository state: an in-progress diff, a
prior decision record, verification that has gone stale. Without that state both
configurations can only describe what they would do, which is the limitation
that made the withdrawn evaluation unable to measure behaviour at all.

The fixture is stored as plain files plus this recipe rather than as a nested
Git repository, because a nested `.git` cannot be committed to the parent. The
commit identity and dates are pinned so the resulting revision is reproducible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "scripts" / "eval" / "fixtures"
RECIPE = FIXTURES / "recipe.json"


def read_recipe() -> dict:
    try:
        return json.loads(RECIPE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"unreadable fixture recipe: {exc}") from exc


def git(cwd: Path, *args: str, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        raise SystemExit(f"git {args[0]} failed in the fixture")
    return completed.stdout.strip()


def copy_tree(source: Path, destination: Path) -> None:
    shutil.copytree(source, destination, dirs_exist_ok=True)


def file_digests(root: Path) -> dict[str, str]:
    digests: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or ".git" in path.parts:
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        digests[path.relative_to(root).as_posix()] = digest
    return digests


def build(overlay: str, destination: Path) -> dict:
    recipe = read_recipe()
    overlays = recipe.get("overlays", {})
    if overlay not in overlays:
        known = ", ".join(sorted(overlays)) or "none"
        raise SystemExit(f"unknown fixture overlay '{overlay}'; known: {known}")

    base = FIXTURES / "base"
    if not base.is_dir():
        raise SystemExit("fixture base directory is missing")
    # An overlay directory is optional. A scenario that starts from a settled,
    # clean repository has no uncommitted work to lay down.
    overlay_dir = FIXTURES / "overlays" / overlay

    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)

    commit = recipe["commit"]
    stamp = commit["date"]
    env = {
        "PATH": subprocess.os.environ.get("PATH", ""),
        "HOME": str(destination),
        "GIT_AUTHOR_DATE": stamp,
        "GIT_COMMITTER_DATE": stamp,
        "GIT_AUTHOR_NAME": commit["author_name"],
        "GIT_AUTHOR_EMAIL": commit["author_email"],
        "GIT_COMMITTER_NAME": commit["author_name"],
        "GIT_COMMITTER_EMAIL": commit["author_email"],
    }

    copy_tree(base, destination)

    # An overlay may need part of its state already committed rather than sitting
    # as uncommitted work. A scenario about superseding an accepted decision, for
    # instance, needs that decision already implemented and settled, so that the
    # request contradicts working code rather than a plan.
    settled = overlays[overlay].get("settled")
    if settled:
        settled_dir = FIXTURES / "settled" / settled
        if not settled_dir.is_dir():
            raise SystemExit(f"unknown settled state '{settled}'")
        copy_tree(settled_dir, destination)

    git(destination, "init", "-q", f"--initial-branch={commit['branch']}", env=env)
    git(destination, "config", "commit.gpgsign", "false", env=env)
    git(destination, "add", "-A", env=env)
    git(destination, "commit", "-q", "-m", commit["message"], env=env)
    revision = git(destination, "rev-parse", "HEAD", env=env)

    # The overlay lands after the commit, so the run starts with uncommitted
    # work exactly as a resumed session would find it.
    if overlay_dir.is_dir():
        copy_tree(overlay_dir, destination)
    dirty = git(destination, "status", "--porcelain", env=env)

    return {
        "overlay": overlay,
        "commit": revision,
        # Porcelain v1 prefixes each line with a two-character status field. Slice
        # past it rather than splitting, because paths may contain spaces.
        "dirty_paths": sorted(
            line[2:].strip() for line in dirty.splitlines() if line.strip()
        ),
        "files": file_digests(destination),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("overlay")
    parser.add_argument("--into", required=True)
    parser.add_argument("--manifest")
    args = parser.parse_args()

    destination = Path(args.into).resolve()
    manifest = build(args.overlay, destination)
    if args.manifest:
        Path(args.manifest).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(f"fixture {manifest['overlay']} at {manifest['commit'][:12]}")
    for path in manifest["dirty_paths"]:
        print(f"  uncommitted: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
