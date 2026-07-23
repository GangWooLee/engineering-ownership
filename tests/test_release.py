from __future__ import annotations

import hashlib
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).parents[1]
ARCHIVE = ROOT / "dist" / "engineering-ownership-v0.1.0.zip"


class ReleaseCase(unittest.TestCase):
    def build(self) -> str:
        result = subprocess.run(
            [sys.executable, "scripts/build_release.py", "--version", "0.1.0"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        self.assertIn("engineering-ownership-v0.1.0.zip", result.stdout)
        return hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()

    def test_release_archive_is_deterministic_and_clean(self) -> None:
        first = self.build()
        second = self.build()
        self.assertEqual(first, second)
        with zipfile.ZipFile(ARCHIVE) as archive:
            names = archive.namelist()
        self.assertIn(".codex-plugin/plugin.json", names)
        self.assertIn(".claude-plugin/plugin.json", names)
        self.assertIn("skills/engineering-ownership/SKILL.md", names)
        self.assertTrue(all("__pycache__" not in name for name in names))
        self.assertTrue(all(".egg-info" not in name for name in names))

    def test_release_tag_validation_has_no_shell_quoting_dependency(self) -> None:
        valid = subprocess.run(
            [sys.executable, "scripts/validate_release_tag.py", "v0.1.0"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(valid.returncode, 0, valid.stderr)
        invalid = subprocess.run(
            [sys.executable, "scripts/validate_release_tag.py", "v9.9.9"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("does not match package tag", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
