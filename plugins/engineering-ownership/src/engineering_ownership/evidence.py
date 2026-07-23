from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .errors import EngineeringError
from .io import json_text, read_json, safe_relative_path, write_repo_text
from .model import COMPETENCIES, RISK_ORDER


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def validate_change_id(change_id: str) -> str:
    allowed = set("abcdefghijklmnopqrstuvwxyz0123456789-_")
    if not 3 <= len(change_id) <= 80 or any(char not in allowed for char in change_id):
        raise EngineeringError(
            "change-id must be 3..80 lowercase letters, numbers, hyphens, or underscores"
        )
    return change_id


def evidence_path(root: Path, contract: dict[str, Any], change_id: str) -> Path:
    relative = Path(contract["artifacts"]["evidence"]) / f"{validate_change_id(change_id)}.json"
    return safe_relative_path(root, relative, for_write=True)


def read_evidence(root: Path, contract: dict[str, Any], change_id: str) -> dict[str, Any]:
    path = evidence_path(root, contract, change_id)
    return validate_evidence(read_json(path), expected_change_id=change_id)


def validate_evidence(
    data: dict[str, Any], *, expected_change_id: str | None = None
) -> dict[str, Any]:
    change_id = data.get("change_id")
    if data.get("schema_version") != 1 or not isinstance(change_id, str):
        raise EngineeringError("Evidence record requires schema_version 1 and change_id")
    validate_change_id(change_id)
    if expected_change_id is not None and change_id != expected_change_id:
        raise EngineeringError("Evidence record change_id does not match its filename")
    if data.get("risk") not in RISK_ORDER:
        raise EngineeringError(f"Evidence record '{change_id}' has invalid risk")
    competencies = data.get("competencies")
    if (
        not isinstance(competencies, list)
        or any(not isinstance(item, str) or item not in COMPETENCIES for item in competencies)
    ):
        raise EngineeringError(f"Evidence record '{change_id}' has invalid competencies")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict) or any(
        not isinstance(value, str)
        or Path(value).is_absolute()
        or ".." in Path(value).parts
        for value in artifacts.values()
    ):
        raise EngineeringError(f"Evidence record '{change_id}' has unsafe artifact paths")
    diff = data.get("diff")
    if (
        not isinstance(diff, dict)
        or not isinstance(diff.get("digest"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", diff["digest"])
        or not isinstance(diff.get("paths"), list)
        or any(not isinstance(item, str) or Path(item).is_absolute() for item in diff["paths"])
    ):
        raise EngineeringError(f"Evidence record '{change_id}' has invalid diff data")
    verification = data.get("verification")
    if not isinstance(verification, list) or any(
        not isinstance(item, dict)
        or item.get("status") not in {"passed", "failed"}
        or not isinstance(item.get("command_id"), str)
        for item in verification
    ):
        raise EngineeringError(f"Evidence record '{change_id}' has invalid verification data")
    understanding = data.get("understanding")
    if not isinstance(understanding, dict):
        legacy = data.get("teach_back")
        legacy_status = legacy.get("status") if isinstance(legacy, dict) else None
        status_map = {
            "pending": "not-reviewed",
            "passed": "reviewed",
            "gaps": "gaps",
        }
        if isinstance(legacy, dict) and legacy_status in status_map:
            understanding = {
                "status": status_map[legacy_status],
                "gaps": legacy.get("gaps", []),
                "revisit_after": legacy.get("review_due"),
            }
            for field in ("reviewed_at", "self_attested"):
                if field in legacy:
                    understanding[field] = legacy[field]
            data = dict(data)
            data.pop("teach_back", None)
            data["understanding"] = understanding
    if (
        not isinstance(understanding, dict)
        or understanding.get("status") not in {
            "not-reviewed",
            "reviewed",
            "gaps",
        }
        or not isinstance(understanding.get("gaps"), list)
        or any(
            not isinstance(item, str)
            for item in understanding.get("gaps", [])
        )
        or not isinstance(understanding.get("revisit_after"), str)
    ):
        raise EngineeringError(
            f"Evidence record '{change_id}' has invalid understanding state"
        )
    return data


def list_evidence(root: Path, contract: dict[str, Any]) -> list[dict[str, Any]]:
    directory = safe_relative_path(root, contract["artifacts"]["evidence"], for_write=True)
    if not directory.exists():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        if path.is_symlink():
            continue
        try:
            data = validate_evidence(
                read_json(path), expected_change_id=path.stem
            )
        except EngineeringError:
            continue
        records.append(data)
    return records


def new_evidence(
    change_id: str,
    risk: str,
    competencies: list[str],
    digest: str,
    paths: list[str],
    artifacts: dict[str, str],
    review_days: int,
) -> dict[str, Any]:
    if risk not in RISK_ORDER:
        raise EngineeringError(f"Unknown risk: {risk}")
    unknown = sorted(set(competencies) - COMPETENCIES)
    if unknown:
        raise EngineeringError(f"Unknown competencies: {', '.join(unknown)}")
    created = now_iso()
    return {
        "schema_version": 1,
        "change_id": validate_change_id(change_id),
        "risk": risk,
        "competencies": sorted(set(competencies)),
        "artifacts": artifacts,
        "diff": {"digest": digest, "paths": paths},
        "verification": [],
        "understanding": {
            "status": "not-reviewed",
            "gaps": [],
            "revisit_after": (
                date.today() + timedelta(days=review_days)
            ).isoformat(),
        },
        "created_at": created,
        "updated_at": created,
    }


def save_evidence(
    root: Path,
    contract: dict[str, Any],
    record: dict[str, Any],
    *,
    overwrite: bool,
) -> Path:
    path = evidence_path(root, contract, record["change_id"])
    relative = path.relative_to(root)
    return write_repo_text(root, relative, json_text(record), overwrite=overwrite)
