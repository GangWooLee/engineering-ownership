from __future__ import annotations

import json
import subprocess
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

    def test_plugin_has_only_bounded_opt_in_hooks(self) -> None:
        hooks = json.loads((PLUGIN / "hooks" / "hooks.json").read_text())
        self.assertEqual(set(hooks["hooks"]), {"SessionStart", "Stop"})
        script = (PLUGIN / "hooks" / "ownership_hook.py").read_text()
        self.assertIn('session_hooks", "off"', script)
        self.assertNotIn("requests", script)
        self.assertNotIn("urllib", script)
        self.assertNotIn("socket", script)
        self.assertFalse((PLUGIN / ".mcp.json").exists())
        self.assertFalse((PLUGIN / "monitors").exists())

    def test_skill_is_single_router_with_progressive_references(self) -> None:
        skill_dir = PLUGIN / "skills" / "engineering-ownership"
        content = (skill_dir / "SKILL.md").read_text()
        for intent in ("setup", "start", "resume", "check", "handoff", "study"):
            self.assertIn(f"**{intent}**", content)
        for name in ("setup.md", "start.md", "resume.md", "finish.md", "integrations.md"):
            self.assertTrue((skill_dir / "references" / name).is_file())
        self.assertLess(len(content.split()), 5000)

    def test_bundled_cli_runs_without_external_install(self) -> None:
        result = subprocess.run(
            [str(PLUGIN / "bin" / "engineering"), "--version"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("0.2.0", result.stdout)


if __name__ == "__main__":
    unittest.main()
