#!/usr/bin/env python3
"""Opt-in, non-blocking reminders for Codex and Claude plugin hosts."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


PLUGIN_ROOT = Path(
    os.environ.get("CLAUDE_PLUGIN_ROOT")
    or os.environ.get("PLUGIN_ROOT")
    or Path(__file__).resolve().parents[1]
).resolve()
SOURCE = PLUGIN_ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from engineering_ownership.evidence import list_evidence  # noqa: E402
from engineering_ownership.errors import EngineeringError  # noqa: E402
from engineering_ownership.model import read_contract  # noqa: E402
from engineering_ownership.repository import diff_digest, repo_root  # noqa: E402


def input_cwd() -> Path:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        payload = {}
    raw = payload.get("cwd") if isinstance(payload, dict) else None
    return Path(raw) if isinstance(raw, str) else Path.cwd()


def enabled(root: Path) -> tuple[bool, dict]:
    try:
        contract = read_contract(root)
    except EngineeringError:
        return False, {}
    return (
        contract.get("automation", {}).get("session_hooks", "off") == "remind",
        contract,
    )


def session_start(root: Path, contract: dict) -> None:
    digest, paths = diff_digest(root)
    records = list_evidence(root, contract)
    current = [
        record for record in records if record.get("diff", {}).get("digest") == digest
    ]
    lines = [
        "Engineering Ownership reminder:",
        f"- Changed paths: {len(paths)}",
    ]
    if current:
        for record in current[:3]:
            lines.append(f"- Current change: {record['change_id']} ({record['risk']})")
    elif paths:
        lines.append("- No change record is bound to the current diff.")
    stale = sum(
        1
        for record in records
        for result in record.get("verification", [])
        if result.get("status") == "passed" and result.get("diff_digest") != digest
    )
    lines.append(f"- Stale passing verification records: {stale}")
    lines.append(
        "- Next safe action: resume the current change or start one before R1+ implementation."
    )
    print("\n".join(lines[:20]))


def stop(root: Path) -> None:
    env = {
        key: value
        for key, value in os.environ.items()
        if key in {"PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "SYSTEMROOT", "WINDIR"}
    }
    env["PYTHONPATH"] = str(SOURCE)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "engineering_ownership", "--repo", str(root), "check"],
            cwd=root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return
    lines = result.stdout.splitlines()
    if lines:
        print("\n".join(lines[:20]))


def main() -> int:
    try:
        root = repo_root(input_cwd())
        is_enabled, contract = enabled(root)
        if not is_enabled:
            return 0
        if len(sys.argv) > 1 and sys.argv[1] == "session-start":
            session_start(root, contract)
        elif len(sys.argv) > 1 and sys.argv[1] == "stop":
            stop(root)
    except (EngineeringError, OSError):
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
