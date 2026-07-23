from __future__ import annotations

import json
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
PLUGIN = ROOT / "plugins" / "engineering-ownership"


class DistributionCase(unittest.TestCase):
    def test_dual_plugin_manifests_agree(self) -> None:
        codex = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text())
        claude = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())
        project = tomllib.loads((ROOT / "pyproject.toml").read_text())
        self.assertEqual(codex["name"], claude["name"])
        self.assertEqual(codex["version"], claude["version"])
        self.assertEqual(codex["version"], project["project"]["version"])
        self.assertEqual(codex["license"], "MIT")
        self.assertEqual(codex["skills"], "./skills/")

    def test_marketplaces_point_to_shared_plugin(self) -> None:
        codex = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text())
        claude = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
        self.assertEqual(codex["plugins"][0]["source"]["path"], "./plugins/engineering-ownership")
        self.assertEqual(codex["plugins"][0]["policy"]["authentication"], "ON_INSTALL")
        self.assertEqual(claude["plugins"][0]["source"], "./plugins/engineering-ownership")

    def test_skill_matches_agent_skills_basics(self) -> None:
        skill = PLUGIN / "skills" / "engineering-ownership" / "SKILL.md"
        content = skill.read_text()
        self.assertTrue(content.startswith("---\n"))
        self.assertIn("\nname: engineering-ownership\n", content)
        self.assertIn("\ndescription:", content)
        self.assertLess(len(content.splitlines()), 500)

    def test_plugin_has_no_automatic_execution_surfaces(self) -> None:
        self.assertFalse((PLUGIN / "hooks").exists())
        self.assertFalse((PLUGIN / ".mcp.json").exists())
        self.assertFalse((PLUGIN / "monitors").exists())


if __name__ == "__main__":
    unittest.main()
