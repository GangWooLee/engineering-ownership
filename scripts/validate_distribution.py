#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "engineering-ownership"


def load(relative: str) -> dict:
    path = ROOT / relative
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"{relative}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"{relative}: expected object")
    return data


def main() -> int:
    codex = load("plugins/engineering-ownership/.codex-plugin/plugin.json")
    claude = load("plugins/engineering-ownership/.claude-plugin/plugin.json")
    codex_market = load(".agents/plugins/marketplace.json")
    claude_market = load(".claude-plugin/marketplace.json")
    catalog = load(
        "plugins/engineering-ownership/src/engineering_ownership/"
        "resources/competencies/catalog.json"
    )
    schemas = [
        load(
            "plugins/engineering-ownership/src/engineering_ownership/"
            "resources/schemas/contract-v2.schema.json"
        ),
        load(
            "plugins/engineering-ownership/src/engineering_ownership/"
            "resources/schemas/evidence-v1.schema.json"
        ),
    ]
    if codex["name"] != claude["name"] or codex["version"] != claude["version"]:
        raise SystemExit("plugin manifests disagree")
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    if project["project"]["version"] != codex["version"]:
        raise SystemExit("package and plugin versions disagree")
    if claude_market["plugins"][0]["version"] != claude["version"]:
        raise SystemExit("Claude marketplace version disagrees with plugin")
    if codex_market["plugins"][0]["source"]["path"] != "./plugins/engineering-ownership":
        raise SystemExit("Codex marketplace path is not repository-relative")
    skill = PLUGIN / "skills" / "engineering-ownership" / "SKILL.md"
    body = skill.read_text(encoding="utf-8")
    if not re.search(r"^name: engineering-ownership$", body, re.MULTILINE):
        raise SystemExit("SKILL.md name is invalid")
    if len(catalog["competencies"]) != 8:
        raise SystemExit("competency catalog must contain exactly eight entries")
    if any(schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema" for schema in schemas):
        raise SystemExit("schemas must use draft 2020-12")
    hooks = load("plugins/engineering-ownership/hooks/hooks.json")
    hook_events = hooks.get("hooks", {})
    if set(hook_events) != {"SessionStart", "Stop"}:
        raise SystemExit("plugin hooks must contain only SessionStart and Stop")
    hook_script = (PLUGIN / "hooks" / "ownership_hook.py").read_text(encoding="utf-8")
    for forbidden_token in ("requests", "urllib", "socket", "engineering_ownership verify"):
        if forbidden_token in hook_script:
            raise SystemExit(f"hook contains forbidden behavior: {forbidden_token}")
    if body.count("engineering-decision:") > 1:
        raise SystemExit("skill should describe one canonical decision marker only")
    if len(body.split()) > 5000:
        raise SystemExit("SKILL.md exceeds the 5,000-token approximation")
    forbidden = [PLUGIN / ".mcp.json", PLUGIN / "monitors"]
    if any(path.exists() for path in forbidden):
        raise SystemExit("v0.2 contains an excluded execution surface")
    print("distribution validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
