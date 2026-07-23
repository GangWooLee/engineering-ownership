from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
HOOK = ROOT / "plugins" / "engineering-ownership" / "hooks" / "ownership_hook.py"
SOURCE = ROOT / "plugins" / "engineering-ownership" / "src"


def git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", *args],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


class HookCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test")
        git(self.root, "config", "user.email", "test@example.com")
        (self.root / "README.md").write_text("# Example\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "init")
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SOURCE)
        subprocess.run(
            [sys.executable, "-m", "engineering_ownership", "init"],
            cwd=self.root,
            env=env,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def invoke(self, event: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["CLAUDE_PLUGIN_ROOT"] = str(HOOK.parents[1])
        return subprocess.run(
            [sys.executable, str(HOOK), event],
            input=json.dumps({"cwd": str(self.root), "hook_event_name": event}),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )

    def test_hooks_are_complete_noop_until_project_opts_in(self) -> None:
        before = subprocess.run(
            ["git", "status", "--porcelain=v1"],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            check=True,
        ).stdout
        start = self.invoke("session-start")
        stop = self.invoke("stop")
        after = subprocess.run(
            ["git", "status", "--porcelain=v1"],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            check=True,
        ).stdout
        self.assertEqual(start.returncode, 0)
        self.assertEqual(stop.returncode, 0)
        self.assertEqual(start.stdout, "")
        self.assertEqual(stop.stdout, "")
        self.assertEqual(before, after)

    def test_remind_mode_only_reports_bounded_context(self) -> None:
        contract_path = self.root / ".engineering" / "contract.json"
        contract = json.loads(contract_path.read_text())
        contract["automation"]["session_hooks"] = "remind"
        contract_path.write_text(json.dumps(contract))
        (self.root / "app.py").write_text("VALUE = 1\n")

        start = self.invoke("session-start")
        stop = self.invoke("stop")
        self.assertEqual(start.returncode, 0)
        self.assertEqual(stop.returncode, 0)
        self.assertLessEqual(len(start.stdout.splitlines()), 20)
        self.assertLessEqual(len(stop.stdout.splitlines()), 20)
        self.assertIn("Engineering Ownership reminder", start.stdout)
        self.assertIn("Risk:", stop.stdout)
        self.assertFalse((self.root / ".engineering" / "evidence").exists())


if __name__ == "__main__":
    unittest.main()
