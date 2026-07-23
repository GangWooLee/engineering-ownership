from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from .errors import EngineeringError


SECRET_PATTERN = re.compile(
    r"(?i)(token|secret|password|passwd|credential|api[_-]?key)"
    r"(\s*[:=]\s*)([^\s,;]+)"
)


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EngineeringError(f"Missing file: {path.name}") from exc
    except json.JSONDecodeError as exc:
        raise EngineeringError(f"Invalid JSON in {path.name}: {exc}") from exc
    if not isinstance(data, dict):
        raise EngineeringError(f"Expected a JSON object in {path.name}")
    return data


def redact(text: str, home: Path | None = None, limit: int = 1200) -> str:
    home = home or Path.home()
    value = text.replace(str(home), "~")
    value = SECRET_PATTERN.sub(lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]", value)
    value = value.replace("\x00", "")
    if len(value) > limit:
        value = value[-limit:]
        value = "[output truncated]\n" + value
    return value


def safe_relative_path(root: Path, raw: str | Path, *, for_write: bool = False) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        raise EngineeringError("Paths must be repository-relative")
    if any(part in {"", ".", ".."} for part in candidate.parts):
        raise EngineeringError(f"Unsafe repository path: {candidate}")

    root_real = root.resolve()
    current = root_real
    parts = candidate.parts
    walk_parts = parts[:-1] if for_write else parts
    for part in walk_parts:
        current = current / part
        if current.is_symlink():
            raise EngineeringError(f"Symlink paths are not allowed: {candidate}")
        if current.exists():
            resolved = current.resolve()
            try:
                resolved.relative_to(root_real)
            except ValueError as exc:
                raise EngineeringError(f"Path escapes repository: {candidate}") from exc

    target = root_real / candidate
    if target.is_symlink():
        raise EngineeringError(f"Symlink paths are not allowed: {candidate}")
    if target.exists():
        try:
            target.resolve().relative_to(root_real)
        except ValueError as exc:
            raise EngineeringError(f"Path escapes repository: {candidate}") from exc
    return target


def write_repo_text(root: Path, relative: str | Path, text: str, *, overwrite: bool = False) -> Path:
    path = safe_relative_path(root, relative, for_write=True)
    if path.exists() and not overwrite:
        raise EngineeringError(f"Refusing to overwrite existing file: {path.relative_to(root)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.parent.is_symlink():
        raise EngineeringError(f"Symlink directory is not allowed: {path.parent.relative_to(root)}")
    path.write_text(text, encoding="utf-8")
    return path


def minimal_subprocess_env(extra: dict[str, str]) -> dict[str, str]:
    allowed = ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "SYSTEMROOT", "WINDIR")
    env = {key: os.environ[key] for key in allowed if key in os.environ}
    env.update(extra)
    return env

