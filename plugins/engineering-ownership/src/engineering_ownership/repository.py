from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from .errors import EngineeringError

IGNORED_DIFF_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
}


def run_git(root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise EngineeringError(f"git {' '.join(args)} failed: {detail}")
    return result


def repo_root(path: str | Path | None = None) -> Path:
    start = Path(path or Path.cwd()).expanduser().resolve()
    result = run_git(start, "rev-parse", "--show-toplevel", check=False)
    if result.returncode:
        raise EngineeringError(f"Not inside a Git repository: {start}")
    return Path(result.stdout.decode().strip()).resolve()


def changed_paths(root: Path) -> list[str]:
    result = run_git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    entries = result.stdout.split(b"\0")
    paths: list[str] = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        index += 1
        if not entry:
            continue
        decoded = entry.decode("utf-8", errors="surrogateescape")
        status = decoded[:2]
        path = decoded[3:]
        if "R" in status or "C" in status:
            if index < len(entries) and entries[index]:
                path = entries[index].decode("utf-8", errors="surrogateescape")
                index += 1
        if (
            not path.startswith(".engineering/evidence/")
            and not any(part in IGNORED_DIFF_PARTS for part in Path(path).parts)
            and not path.endswith((".pyc", ".pyo"))
        ):
            paths.append(path)
    return sorted(set(paths))


def diff_digest(root: Path) -> tuple[str, list[str]]:
    paths = changed_paths(root)
    digest = hashlib.sha256()
    digest.update(b"engineering-ownership-diff-v1\0")
    for relative in paths:
        digest.update(relative.encode("utf-8", errors="surrogateescape"))
        digest.update(b"\0")
        path = root / relative
        if path.is_symlink():
            digest.update(b"symlink:")
            digest.update(path.readlink().as_posix().encode())
        elif path.is_file():
            try:
                digest.update(path.read_bytes())
            except OSError:
                digest.update(b"[unreadable]")
        elif not path.exists():
            digest.update(b"[deleted]")
        else:
            digest.update(b"[non-file]")
        digest.update(b"\0")
    return digest.hexdigest(), paths


def head_revision(root: Path) -> str:
    result = run_git(root, "rev-parse", "--verify", "HEAD", check=False)
    return result.stdout.decode().strip() if result.returncode == 0 else "unborn"
