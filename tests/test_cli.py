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

    def test_complete_records_and_current_verification_pass_without_review_gate(self) -> None:
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
        passed = self.invoke("check", "--mode", "enforce", "--change", "app-value")
        self.assertEqual(passed.returncode, 0, passed.stdout + passed.stderr)

        (self.root / "app.py").write_text("VALUE = 2\n", encoding="utf-8")
        stale = self.invoke("check", "--mode", "enforce", "--change", "app-value")
        self.assertEqual(stale.returncode, 1)
        self.assertIn("current diff", stale.stdout)

    def test_optional_understanding_review_records_gaps_without_blocking(self) -> None:
        self.init()
        self.commit_contract()
        (self.root / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
        self.invoke(
            "change",
            "start",
            "review-later",
            "--risk",
            "R2",
            "--competency",
            "explanation-review-handoff",
        )
        self.fill_artifacts("review-later")
        verified = self.invoke("verify", "review-later")
        self.assertEqual(verified.returncode, 0, verified.stderr)
        reviewed = self.invoke(
            "change",
            "review",
            "review-later",
            "--status",
            "gaps",
            "--gap",
            "Need to revisit retry ownership.",
        )
        self.assertEqual(reviewed.returncode, 0, reviewed.stderr)
        checked = self.invoke(
            "check", "--mode", "enforce", "--change", "review-later"
        )
        self.assertEqual(checked.returncode, 0, checked.stdout + checked.stderr)
        status = self.invoke("status")
        self.assertIn("understanding=gaps", status.stdout)
        self.assertIn("Need to revisit retry ownership.", status.stdout)
        invalid_days = self.invoke(
            "change",
            "review",
            "review-later",
            "--status",
            "gaps",
            "--revisit-days",
            "0",
        )
        self.assertEqual(invalid_days.returncode, 2)
        self.assertIn("revisit-days", invalid_days.stderr)

    def test_prerelease_teach_back_record_is_normalized_on_next_write(self) -> None:
        self.init()
        self.commit_contract()
        (self.root / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
        self.invoke("change", "start", "legacy-review", "--risk", "R1")
        path = self.root / ".engineering" / "evidence" / "legacy-review.json"
        record = json.loads(path.read_text())
        understanding = record.pop("understanding")
        record["teach_back"] = {
            "status": "pending",
            "gaps": understanding["gaps"],
            "review_due": understanding["revisit_after"],
        }
        path.write_text(json.dumps(record))

        verified = self.invoke("verify", "legacy-review")
        self.assertEqual(verified.returncode, 0, verified.stderr)
        normalized = json.loads(path.read_text())
        self.assertNotIn("teach_back", normalized)
        self.assertEqual(
            normalized["understanding"]["status"], "not-reviewed"
        )

    def test_explain_points_to_records_and_is_an_optional_revisit(self) -> None:
        self.init()
        self.commit_contract()
        (self.root / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
        self.invoke("change", "start", "decision-review", "--risk", "R2")
        result = self.invoke("explain", "decision-review")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Optional decision review", result.stdout)
        self.assertIn(
            "docs/engineering/changes/decision-review.md", result.stdout
        )
        self.assertIn(
            "docs/engineering/decisions/decision-review.md", result.stdout
        )
        self.assertIn("not a default completion gate", result.stdout)

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

    def test_status_reports_competencies_gaps_and_revisit_date_without_score(self) -> None:
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
        self.assertIn("revisit_after=", result.stdout)
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

    def test_recorded_r2_is_a_floor_for_document_only_diff(self) -> None:
        self.init()
        self.commit_contract()
        started = self.invoke(
            "change", "start", "docs-architecture", "--risk", "R2"
        )
        self.assertEqual(started.returncode, 0, started.stderr)
        result = self.invoke(
            "check", "--mode", "enforce", "--change", "docs-architecture"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Risk: R2", result.stdout)
        self.assertIn("verification 'unit'", result.stdout)

    def test_detected_r3_requires_explicit_risk_escalation(self) -> None:
        self.init()
        self.commit_contract()
        (self.root / "db").mkdir()
        (self.root / "db" / "schema.sql").write_text("select 1;\n")
        self.invoke("change", "start", "schema-change", "--risk", "R2")
        (self.root / "src" / "auth").mkdir(parents=True)
        (self.root / "src" / "auth" / "session.py").write_text("ENABLED = True\n")
        blocked = self.invoke("verify", "schema-change")
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("set-risk schema-change --risk R3", blocked.stderr)

    def test_set_risk_preserves_existing_records_and_creates_only_missing_r3_docs(self) -> None:
        self.init()
        self.commit_contract()
        self.invoke(
            "change",
            "start",
            "sensitive-flow",
            "--risk",
            "R2",
            "--title",
            "Sensitive flow",
        )
        decision = self.root / "docs/engineering/decisions/sensitive-flow.md"
        decision.write_text(decision.read_text() + "\nPreserve this line.\n")
        raised = self.invoke(
            "change", "set-risk", "sensitive-flow", "--risk", "R3"
        )
        self.assertEqual(raised.returncode, 0, raised.stderr)
        self.assertIn("Preserve this line.", decision.read_text())
        self.assertTrue(
            (self.root / "docs/engineering/security/sensitive-flow.md").is_file()
        )
        self.assertTrue(
            (self.root / "docs/engineering/runbooks/sensitive-flow.md").is_file()
        )
        record = json.loads(
            (self.root / ".engineering/evidence/sensitive-flow.json").read_text()
        )
        self.assertEqual(record["risk"], "R3")
        lower = self.invoke(
            "change", "set-risk", "sensitive-flow", "--risk", "R2"
        )
        self.assertEqual(lower.returncode, 2)

    def test_change_title_and_timestamp_are_human_readable_and_timezone_aware(self) -> None:
        self.init()
        self.commit_contract()
        result = self.invoke(
            "change",
            "start",
            "cache-ai-analysis",
            "--risk",
            "R2",
            "--title",
            "AI analysis cache policy",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(
            (self.root / ".engineering/evidence/cache-ai-analysis.json").read_text()
        )
        self.assertRegex(record["created_at"], r"[+-]\d\d:\d\d$")
        brief = (
            self.root / "docs/engineering/changes/cache-ai-analysis.md"
        ).read_text()
        self.assertIn("· AI analysis cache policy", brief)
        self.assertIn(f"Created: `{record['created_at']}`", brief)
        self.assertEqual(record["title"], "AI analysis cache policy")

    def test_refs_check_accepts_canonical_reference_and_implementation_path(self) -> None:
        self.init()
        self.commit_contract()
        self.invoke("change", "start", "cache-policy", "--risk", "R2")
        app = self.root / "app.py"
        app.write_text(
            "# engineering-decision: cache-policy | "
            "docs/engineering/decisions/cache-policy.md\nVALUE = 1\n"
        )
        adr = self.root / "docs/engineering/decisions/cache-policy.md"
        adr.write_text(
            adr.read_text().replace(
                "Leave this section empty when the decision is not enforced in code.",
                "- `app.py`",
            )
        )
        valid = self.invoke("refs", "check", "--all")
        self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)

        app.write_text(
            "# engineering-decision: cache-policy | docs/wrong.md\nVALUE = 1\n"
        )
        wrong = self.invoke("refs", "check", "--all")
        self.assertEqual(wrong.returncode, 1)
        self.assertIn("canonical ADR", wrong.stdout)

    def test_refs_check_reports_missing_and_superseded_decisions(self) -> None:
        self.init()
        self.commit_contract()
        self.invoke("change", "start", "old-policy", "--risk", "R2")
        app = self.root / "app.py"
        app.write_text(
            "# engineering-decision: missing-policy | "
            "docs/engineering/decisions/missing-policy.md\n"
        )
        missing = self.invoke("refs", "check", "--all")
        self.assertEqual(missing.returncode, 1)
        self.assertIn("has no evidence", missing.stdout)

        app.write_text(
            "# engineering-decision: old-policy | "
            "docs/engineering/decisions/old-policy.md\n"
        )
        adr = self.root / "docs/engineering/decisions/old-policy.md"
        adr.write_text(adr.read_text().replace("Superseded by: None", "Superseded by: new-policy"))
        superseded = self.invoke("refs", "check", "--all")
        self.assertEqual(superseded.returncode, 1)
        self.assertIn("is superseded", superseded.stdout)

    def test_refs_check_rejects_symlinked_implementation_reference(self) -> None:
        self.init()
        self.commit_contract()
        self.invoke("change", "start", "linked-policy", "--risk", "R2")
        target = self.root.parent / f"{self.root.name}-implementation"
        target.write_text("external\n")
        try:
            (self.root / "linked.py").symlink_to(target)
            app = self.root / "app.py"
            app.write_text(
                "# engineering-decision: linked-policy | "
                "docs/engineering/decisions/linked-policy.md\n"
            )
            adr = self.root / "docs/engineering/decisions/linked-policy.md"
            adr.write_text(
                adr.read_text().replace(
                    "Leave this section empty when the decision is not enforced in code.",
                    "- `linked.py`",
                )
            )
            result = self.invoke("refs", "check", "--all")
            self.assertEqual(result.returncode, 1)
            self.assertIn("Symlink paths are not allowed", result.stdout)
        finally:
            target.unlink()

    def test_handoff_save_does_not_change_diff_digest(self) -> None:
        self.init()
        self.commit_contract()
        (self.root / "app.py").write_text("VALUE = 1\n")
        before = self.invoke("handoff").stdout
        before_digest = next(
            line for line in before.splitlines() if "Current diff digest" in line
        )
        saved = self.invoke("handoff", "--save")
        self.assertEqual(saved.returncode, 0, saved.stderr)
        after = self.invoke("handoff").stdout
        after_digest = next(
            line for line in after.splitlines() if "Current diff digest" in line
        )
        self.assertEqual(before_digest, after_digest)

    def test_doctor_is_bounded_and_does_not_leak_home_or_secrets(self) -> None:
        self.init()
        result = self.invoke("doctor", "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("contract", payload)
        self.assertIn("verification_commands", payload)
        self.assertNotIn(str(Path.home()), result.stdout)
        self.assertNotIn("private-value", result.stdout)
        self.assertNotIn("argv", result.stdout)


if __name__ == "__main__":
    unittest.main()
