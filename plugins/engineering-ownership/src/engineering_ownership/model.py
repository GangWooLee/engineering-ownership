from __future__ import annotations

import fnmatch
import re
import shlex
from copy import deepcopy
from pathlib import Path
from typing import Any

from .errors import EngineeringError
from .io import read_json


RISK_ORDER = {"R0": 0, "R1": 1, "R2": 2, "R3": 3}
COMPETENCIES = {
    "problem-framing-requirements",
    "system-data-flow-design",
    "responsibility-reuse-code-design",
    "testing-debugging",
    "security-privacy",
    "reliability-observability-recovery",
    "git-delivery-change-management",
    "explanation-review-handoff",
}
SECRET_ENV = re.compile(r"(?i)(token|secret|password|passwd|credential|api.?key)")
ENV_KEY = re.compile(r"^[A-Z_][A-Z0-9_]{0,63}$")
FORBIDDEN_COMMANDS = {
    "bash",
    "cmd",
    "cmd.exe",
    "fish",
    "powershell",
    "pwsh",
    "sh",
    "xargs",
    "zsh",
}


def default_contract(project_name: str) -> dict[str, Any]:
    return {
        "version": 2,
        "project": {"name": project_name, "kind": "product", "status": "active"},
        "verification": [
            {
                "id": "unit",
                "argv": ["python3", "-m", "unittest", "discover", "-s", "tests"],
                "env": {},
                "timeout_seconds": 300,
                "required_for": ["R1", "R2", "R3"],
            }
        ],
        "risk_paths": {
            "R2": ["api/**", "db/**", "migrations/**", "src/services/**"],
            "R3": [
                "**/auth/**",
                "**/authorization/**",
                "**/crypto/**",
                "**/payments/**",
                "**/secrets/**",
            ],
        },
        "artifacts": {
            "changes": "docs/engineering/changes",
            "decisions": "docs/engineering/decisions",
            "runbooks": "docs/engineering/runbooks",
            "threat_models": "docs/engineering/security",
            "evidence": ".engineering/evidence",
        },
        "review_interval_days": 7,
    }


def contract_version(data: dict[str, Any]) -> int:
    version = data.get("version", data.get("schema_version"))
    if version not in (1, 2):
        raise EngineeringError("Contract version must be 1 or 2")
    return int(version)


def validate_contract(data: dict[str, Any], *, allow_v1: bool = True) -> dict[str, Any]:
    version = contract_version(data)
    if version == 1:
        if not allow_v1:
            raise EngineeringError("Contract v1 must be migrated before verification")
        for key in ("project", "verification", "risk_paths", "artifacts"):
            if key not in data:
                raise EngineeringError(f"Contract v1 missing '{key}'")
        return data

    project = data.get("project")
    if not isinstance(project, dict) or not isinstance(project.get("name"), str):
        raise EngineeringError("Contract v2 requires project.name")

    commands = data.get("verification")
    if not isinstance(commands, list):
        raise EngineeringError("Contract v2 verification must be an array")
    seen: set[str] = set()
    for command in commands:
        if not isinstance(command, dict):
            raise EngineeringError("Each verification command must be an object")
        command_id = command.get("id")
        argv = command.get("argv")
        if not isinstance(command_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", command_id):
            raise EngineeringError("Verification command id must be lowercase and stable")
        if command_id in seen:
            raise EngineeringError(f"Duplicate verification command id: {command_id}")
        seen.add(command_id)
        if not isinstance(argv, list) or not argv or not all(
            isinstance(part, str) and part and "\x00" not in part for part in argv
        ):
            raise EngineeringError(f"Verification '{command_id}' requires a non-empty argv array")
        executable = Path(argv[0]).name.lower()
        if executable in FORBIDDEN_COMMANDS:
            raise EngineeringError(
                f"Verification '{command_id}' cannot invoke a command shell or xargs"
            )
        timeout = command.get("timeout_seconds", 300)
        if not isinstance(timeout, int) or not 1 <= timeout <= 3600:
            raise EngineeringError(f"Verification '{command_id}' timeout must be 1..3600 seconds")
        required = command.get("required_for", [])
        if not isinstance(required, list) or any(item not in RISK_ORDER for item in required):
            raise EngineeringError(f"Verification '{command_id}' has invalid required_for")
        env = command.get("env", {})
        if not isinstance(env, dict):
            raise EngineeringError(f"Verification '{command_id}' env must be an object")
        for key, value in env.items():
            if (
                not isinstance(key, str)
                or not ENV_KEY.fullmatch(key)
                or SECRET_ENV.search(key)
                or not isinstance(value, str)
                or len(value) > 256
                or any(token in value for token in ("$", "`", "\x00"))
            ):
                raise EngineeringError(f"Verification '{command_id}' has unsafe env entry: {key}")

    risk_paths = data.get("risk_paths")
    if not isinstance(risk_paths, dict) or any(
        not isinstance(risk_paths.get(risk), list) for risk in ("R2", "R3")
    ):
        raise EngineeringError("Contract v2 requires R2 and R3 risk path arrays")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict):
        raise EngineeringError("Contract v2 requires artifact paths")
    for key in ("changes", "decisions", "runbooks", "threat_models", "evidence"):
        value = artifacts.get(key)
        if not isinstance(value, str) or Path(value).is_absolute() or ".." in Path(value).parts:
            raise EngineeringError(f"Contract v2 artifact path '{key}' must be repository-relative")
    interval = data.get("review_interval_days", 7)
    if not isinstance(interval, int) or not 1 <= interval <= 365:
        raise EngineeringError("review_interval_days must be 1..365")
    return data


def read_contract(root: Path) -> dict[str, Any]:
    return validate_contract(read_json(root / ".engineering" / "contract.json"))


def migrate_v1(data: dict[str, Any]) -> dict[str, Any]:
    if contract_version(data) != 1:
        raise EngineeringError("Only contract v1 can be migrated")
    result = default_contract(str(data.get("project", {}).get("name", "project")))
    result["project"] = deepcopy(data["project"])
    result["risk_paths"] = deepcopy(data["risk_paths"])
    old_artifacts = data["artifacts"]
    result["artifacts"] = {
        "changes": old_artifacts.get("briefs", "docs/engineering/changes"),
        "decisions": old_artifacts.get("decisions", "docs/engineering/decisions"),
        "runbooks": old_artifacts.get("runbooks", "docs/engineering/runbooks"),
        "threat_models": old_artifacts.get("threat_models", "docs/engineering/security"),
        "evidence": ".engineering/evidence",
    }
    commands: list[dict[str, Any]] = []
    required_by_category = {
        "static": ["R1", "R2", "R3"],
        "unit": ["R1", "R2", "R3"],
        "integration": ["R2", "R3"],
        "build": ["R2", "R3"],
        "smoke": ["R2", "R3"],
    }
    for category, values in data.get("verification", {}).items():
        for index, value in enumerate(values):
            if not isinstance(value, str) or any(token in value for token in ("|", ";", "&&", "||", ">", "<", "`", "$(")):
                raise EngineeringError(
                    f"Cannot safely migrate shell syntax in {category}-{index + 1}; edit it manually"
                )
            parts = shlex.split(value)
            env: dict[str, str] = {}
            while parts and re.fullmatch(r"[A-Z_][A-Z0-9_]*=.*", parts[0]):
                key, env_value = parts.pop(0).split("=", 1)
                env[key] = env_value
            if not parts:
                raise EngineeringError(f"Cannot migrate empty command in {category}-{index + 1}")
            commands.append(
                {
                    "id": f"{category}-{index + 1}",
                    "argv": parts,
                    "env": env,
                    "timeout_seconds": 300,
                    "required_for": required_by_category.get(category, ["R2", "R3"]),
                    "migration_note": "Converted with shlex; review argv and environment before verify.",
                }
            )
    result["verification"] = commands
    return result


def classify_risk(contract: dict[str, Any], paths: list[str], explicit: str | None) -> str:
    if explicit:
        if explicit not in RISK_ORDER:
            raise EngineeringError(f"Unknown risk: {explicit}")
        return explicit
    highest = "R0"
    for relative in paths:
        if any(
            fnmatch.fnmatch(relative, pattern)
            for pattern in contract["risk_paths"].get("R3", [])
        ):
            highest = "R3"
            continue
        if any(
            fnmatch.fnmatch(relative, pattern)
            for pattern in contract["risk_paths"].get("R2", [])
        ):
            if RISK_ORDER[highest] < RISK_ORDER["R2"]:
                highest = "R2"
            continue
        suffix = Path(relative).suffix.lower()
        if (
            RISK_ORDER[highest] < RISK_ORDER["R1"]
            and suffix not in {".md", ".txt", ".rst"}
            and not relative.startswith("docs/")
        ):
            highest = "R1"
    return highest


def required_command_ids(contract: dict[str, Any], risk: str) -> list[str]:
    return [
        command["id"]
        for command in contract.get("verification", [])
        if risk in command.get("required_for", [])
    ]
