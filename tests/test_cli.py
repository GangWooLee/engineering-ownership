from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "plugins" / "engineering-ownership" / "src"


def git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )


class CliCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        git(self.root, "init", "-q")
        git(self.root, "config", "user.name", "Test")
        git(self.root, "config", "user.email", "test@example.com")
        (self.root / "README.md").write_text("# Example\n", encoding="utf-8")
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_ok.py").write_text(
            "import unittest\n\n"
            "class Ok(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "test: initialize")

    def tearDown(self) -> None:
        self.temp.cleanup()

    def invoke(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(SOURCE)
        return subprocess.run(
            [sys.executable, "-m", "engineering_ownership", *args],
            cwd=self.root,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def init(self, *extra: str) -> dict:
        result = self.invoke("init", *extra)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(
            (self.root / ".engineering" / "contract.json").read_text(encoding="utf-8")
        )

    def commit_contract(self) -> None:
        git(self.root, "add", ".engineering")
        git(self.root, "commit", "-qm", "chore: add engineering contract")

    def fill_artifacts(self, change_id: str) -> None:
        for path in (self.root / "docs" / "engineering").rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace(
                    "<!-- engineering-ownership:fill-required -->",
                    "This decision is filled with project-specific reasoning.",
                ),
                encoding="utf-8",
            )

    def test_init_is_non_destructive_and_pointers_are_opt_in(self) -> None:
        contract = self.init()
        self.assertEqual(contract["version"], 2)
        self.assertFalse((self.root / "AGENTS.md").exists())
        again = self.invoke("init")
        self.assertEqual(again.returncode, 2)
        self.assertIn("non-destructive", again.stderr)

        other = tempfile.TemporaryDirectory()
        try:
            root = Path(other.name)
            git(root, "init", "-q")
            result = self.invoke("--repo", str(root), "init", "--agent-pointers")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("engineering-ownership:start", (root / "AGENTS.md").read_text())
            self.assertIn("engineering-ownership:start", (root / "CLAUDE.md").read_text())
        finally:
            other.cleanup()

    def test_r0_passes_without_brief(self) -> None:
        self.init()
        self.commit_contract()
        (self.root / "README.md").write_text("# Corrected\n", encoding="utf-8")
        result = self.invoke("check", "--mode", "enforce")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Risk: R0", result.stdout)

    def test_r2_and_r3_block_without_current_evidence(self) -> None:
        self.init()
        self.commit_contract()
        (self.root / "db").mkdir()
        (self.root / "db" / "schema.sql").write_text("select 1;\n", encoding="utf-8")
        result = self.invoke("check", "--mode", "enforce")
        self.assertEqual(result.returncode, 1)
        self.assertIn("no change evidence", result.stdout)

        (self.root / "db" / "schema.sql").unlink()
        (self.root / "src" / "auth").mkdir(parents=True)
        (self.root / "src" / "auth" / "session.py").write_text("ENABLED = True\n")
        result = self.invoke("check", "--mode", "enforce")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Risk: R3", result.stdout)

    def test_r3_wins_when_r2_and_r3_paths_change_together(self) -> None:
        self.init()
        self.commit_contract()
        (self.root / "db").mkdir()
        (self.root / "db" / "schema.sql").write_text("select 1;\n")
        (self.root / "src" / "auth").mkdir(parents=True)
        (self.root / "src" / "auth" / "session.py").write_text("ENABLED = True\n")
        result = self.invoke("check")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Risk: R3", result.stdout)

    def test_advise_reports_but_does_not_block(self) -> None:
        self.init()
        self.commit_contract()
        (self.root / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
        result = self.invoke("check")
        self.assertEqual(result.returncode, 0)
        self.assertIn("RESULT: ADVISE", result.stdout)

    def test_verify_is_bound_to_current_diff_and_stales_after_change(self) -> None:
        self.init()
        self.commit_contract()
        (self.root / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
        started = self.invoke(
            "change",
            "start",
            "app-value",
            "--risk",
            "R2",
            "--competency",
            "testing-debugging",
        )
        self.assertEqual(started.returncode, 0, started.stderr)
        self.fill_artifacts("app-value")
        verified = self.invoke("verify", "app-value")
        self.assertEqual(verified.returncode, 0, verified.stdout + verified.stderr)
        reviewed = self.invoke("change", "review", "app-value", "--status", "passed")
        self.assertEqual(reviewed.returncode, 0, reviewed.stderr)
        passed = self.invoke("check", "--mode", "enforce", "--change", "app-value")
        self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)

        (self.root / "app.py").write_text("VALUE = 2\n", encoding="utf-8")
        stale = self.invoke("check", "--mode", "enforce", "--change", "app-value")
        self.assertEqual(stale.returncode, 1)
        self.assertIn("current diff", stale.stdout)

    def test_v1_migration_preview_and_write_preserve_original(self) -> None:
        contract = {
            "version": 1,
            "project": {"name": "old", "kind": "product", "status": "active"},
            "verification": {
                "static": ["python3 -m compileall src"],
                "unit": ["PARALLEL_WORKERS=1 python3 -m unittest"]
            },
            "risk_paths": {"R2": ["db/**"], "R3": ["auth/**"]},
            "artifacts": {
                "briefs": "docs/plans",
                "decisions": "docs/decisions",
                "runbooks": "docs/runbooks",
                "threat_models": "docs/security"
            }
        }
        (self.root / ".engineering").mkdir()
        original = json.dumps(contract, indent=2) + "\n"
        (self.root / ".engineering" / "contract.json").write_text(original)
        preview = self.invoke("contract", "migrate")
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertEqual(
            (self.root / ".engineering" / "contract.json").read_text(), original
        )
        migrated = self.invoke("contract", "migrate", "--write")
        self.assertEqual(migrated.returncode, 0, migrated.stderr)
        self.assertEqual(
            (self.root / ".engineering" / "contract.v1.backup.json").read_text(),
            json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        )
        current = json.loads(
            (self.root / ".engineering" / "contract.json").read_text()
        )
        self.assertEqual(current["version"], 2)
        self.assertEqual(current["verification"][1]["env"], {"PARALLEL_WORKERS": "1"})
        self.assertEqual(current["verification"][1]["argv"][0], "python3")

    def test_path_escape_and_symlink_output_are_rejected(self) -> None:
        self.init()
        escaped = self.invoke("handoff", "--output", "../outside.md")
        self.assertEqual(escaped.returncode, 2)
        self.assertFalse((self.root.parent / "outside.md").exists())

        target = self.root.parent / f"{self.root.name}-target"
        target.mkdir()
        try:
            (self.root / "linked").symlink_to(target, target_is_directory=True)
            linked = self.invoke("handoff", "--output", "linked/handoff.md")
            self.assertEqual(linked.returncode, 2)
            self.assertFalse((target / "handoff.md").exists())
        finally:
            target.rmdir()

    def test_shell_and_secret_environment_contracts_are_rejected(self) -> None:
        contract = self.init()
        contract["verification"][0]["argv"] = ["sh", "-c", "touch pwned"]
        path = self.root / ".engineering" / "contract.json"
        path.write_text(json.dumps(contract))
        result = self.invoke("audit")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / "pwned").exists())

        contract["verification"][0]["argv"] = ["python3", "-m", "unittest"]
        contract["verification"][0]["env"] = {"API_TOKEN": "value"}
        path.write_text(json.dumps(contract))
        secret = self.invoke("audit")
        self.assertEqual(secret.returncode, 2)
        self.assertIn("unsafe env", secret.stderr)

    def test_handoff_is_repo_relative_and_resumable(self) -> None:
        self.init()
        self.commit_contract()
        (self.root / "app.py").write_text("VALUE = 1\n")
        result = self.invoke("handoff")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Current diff digest", result.stdout)
        self.assertIn("`app.py`", result.stdout)
        self.assertNotIn(str(Path.home()), result.stdout)
        self.assertIn("Resume safely", result.stdout)

    def test_status_reports_competencies_gaps_and_due_date_without_score(self) -> None:
        self.init()
        self.commit_contract()
        (self.root / "app.py").write_text("VALUE = 1\n")
        self.invoke(
            "change",
            "start",
            "status-check",
            "--risk",
            "R1",
            "--competency",
            "testing-debugging",
        )
        result = self.invoke("status")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("testing-debugging", result.stdout)
        self.assertIn("verification 'unit'", result.stdout)
        self.assertIn("due=", result.stdout)
        self.assertNotIn("score", result.stdout.lower())

    def test_evidence_stores_no_command_output_or_home_path(self) -> None:
        contract = self.init()
        contract["verification"][0]["argv"] = [
            sys.executable,
            "-c",
            "print('TOKEN=private-value')",
        ]
        path = self.root / ".engineering" / "contract.json"
        path.write_text(json.dumps(contract))
        self.commit_contract()
        (self.root / "app.py").write_text("VALUE = 1\n")
        self.invoke("change", "start", "privacy-check", "--risk", "R1")
        verified = self.invoke("verify", "privacy-check")
        self.assertEqual(verified.returncode, 0, verified.stderr)
        evidence = (
            self.root / ".engineering" / "evidence" / "privacy-check.json"
        ).read_text()
        self.assertNotIn("private-value", evidence)
        self.assertNotIn(str(Path.home()), evidence)
        self.assertNotIn("stdout", evidence)

    def test_failed_command_does_not_echo_or_persist_secret_output(self) -> None:
        contract = self.init()
        contract["verification"][0]["argv"] = [
            sys.executable,
            "-c",
            "import sys; print('unlabelled-private-value', file=sys.stderr); sys.exit(4)",
        ]
        path = self.root / ".engineering" / "contract.json"
        path.write_text(json.dumps(contract))
        self.commit_contract()
        (self.root / "app.py").write_text("VALUE = 1\n")
        self.invoke("change", "start", "failure-output", "--risk", "R1")
        verified = self.invoke("verify", "failure-output")
        self.assertEqual(verified.returncode, 1)
        combined = verified.stdout + verified.stderr
        self.assertNotIn("unlabelled-private-value", combined)
        evidence = (
            self.root / ".engineering" / "evidence" / "failure-output.json"
        ).read_text()
        self.assertNotIn("unlabelled-private-value", evidence)

    def test_invalid_evidence_is_rejected_without_crashing(self) -> None:
        self.init()
        self.commit_contract()
        (self.root / "app.py").write_text("VALUE = 1\n")
        self.invoke("change", "start", "invalid-record", "--risk", "R1")
        path = self.root / ".engineering" / "evidence" / "invalid-record.json"
        evidence = json.loads(path.read_text())
        evidence["risk"] = "R9"
        path.write_text(json.dumps(evidence))
        result = self.invoke("check", "--mode", "enforce", "--change", "invalid-record")
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid risk", result.stderr)

    def test_verification_timeout_is_recorded_as_failure(self) -> None:
        contract = self.init()
        contract["verification"][0]["argv"] = [
            sys.executable,
            "-c",
            "import time; time.sleep(2)",
        ]
        contract["verification"][0]["timeout_seconds"] = 1
        path = self.root / ".engineering" / "contract.json"
        path.write_text(json.dumps(contract))
        self.commit_contract()
        (self.root / "app.py").write_text("VALUE = 1\n")
        self.invoke("change", "start", "timeout-check", "--risk", "R1")
        verified = self.invoke("verify", "timeout-check")
        self.assertEqual(verified.returncode, 1)
        evidence = json.loads(
            (
                self.root / ".engineering" / "evidence" / "timeout-check.json"
            ).read_text()
        )
        self.assertTrue(evidence["verification"][0]["timed_out"])
        self.assertIsNone(evidence["verification"][0]["exit_code"])

    def test_missing_verification_executable_is_a_bounded_failure(self) -> None:
        contract = self.init()
        contract["verification"][0]["argv"] = ["definitely-not-an-installed-command"]
        path = self.root / ".engineering" / "contract.json"
        path.write_text(json.dumps(contract))
        self.commit_contract()
        (self.root / "app.py").write_text("VALUE = 1\n")
        self.invoke("change", "start", "missing-command", "--risk", "R1")
        verified = self.invoke("verify", "missing-command")
        self.assertEqual(verified.returncode, 1)
        self.assertNotIn(str(Path.home()), verified.stdout + verified.stderr)
        evidence = json.loads(
            (
                self.root / ".engineering" / "evidence" / "missing-command.json"
            ).read_text()
        )
        self.assertEqual(evidence["verification"][0]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
