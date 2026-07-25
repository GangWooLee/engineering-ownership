from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SKILL = ROOT / "plugins" / "engineering-ownership" / "skills" / "engineering-ownership"
EVALS = SKILL / "evals" / "evals.json"
VALIDATION = ROOT / "docs" / "validation"
WORKSPACE = ROOT / "engineering-ownership-workspace"

ALLOWED_STATUS = {"Current", "Superseded", "Withdrawn"}

# Tokens that belong to this skill's own vocabulary. An evaluation that requires
# them cannot be passed on merit by a baseline that has never seen the skill, so
# a grader must never match on them. See docs/validation/skill-evaluation.md.
PRIVATE_VOCABULARY = ("teach-back", "engineering-decision:", "runbook")

RESULTS_BLOCK = re.compile(r"```json\s*(\{[^`]*?\"with_skill_mean\"[^`]*?\})\s*```", re.DOTALL)
STATUS_LINE = re.compile(r"^Status:\s*(\S+)", re.MULTILINE)
CHECKED_LINE = re.compile(r"^Checked:\s*\d{4}-\d{2}-\d{2}", re.MULTILINE)
SUPERSEDED_LINE = re.compile(r"^Superseded by:\s*\S+", re.MULTILINE)
RETIRED_STATUS = re.compile(r"^Status:\s*(Withdrawn|Superseded)", re.MULTILINE)


def load_evals() -> dict:
    return json.loads(EVALS.read_text(encoding="utf-8"))


def validation_documents() -> list[Path]:
    return sorted(path for path in VALIDATION.glob("*.md") if path.name != "README.md")


class EvalManifestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.data = load_evals()
        self.evals = self.data["evals"]

    def test_skill_name_matches_the_skill_it_evaluates(self) -> None:
        frontmatter = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        declared = re.search(r"^name:\s*(\S+)$", frontmatter, re.MULTILINE)
        self.assertIsNotNone(declared)
        self.assertEqual(self.data["skill_name"], declared.group(1))

    def test_every_eval_declares_the_required_fields(self) -> None:
        self.assertTrue(self.evals)
        for item in self.evals:
            for field in ("id", "name", "prompt", "expected_output", "expectations"):
                self.assertIn(field, item, f"{item.get('name', '?')} is missing {field}")
            self.assertTrue(item["expectations"], f"{item['name']} has no expectations")

    def test_identifiers_are_unique_and_stable(self) -> None:
        names = [item["name"] for item in self.evals]
        identifiers = [item["id"] for item in self.evals]
        self.assertEqual(len(set(names)), len(names))
        self.assertEqual(len(set(identifiers)), len(identifiers))
        for name in names:
            self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$")

    def test_every_eval_carries_the_same_expectation_count(self) -> None:
        counts = {len(item["expectations"]) for item in self.evals}
        self.assertEqual(len(counts), 1, f"expectation counts diverge: {sorted(counts)}")

    def test_prompts_and_expectations_are_english_only(self) -> None:
        # The withdrawn evaluation compared Korean with-skill responses against
        # English baseline responses, so language and skill availability varied
        # together. Restricting the manifest to ASCII keeps language a constant.
        for item in self.evals:
            for field in ("prompt", "expected_output"):
                self.assertTrue(
                    str(item[field]).isascii(),
                    f"{item['name']}.{field} is not ASCII",
                )
            for index, expectation in enumerate(item["expectations"]):
                self.assertTrue(
                    expectation.isascii(),
                    f"{item['name']}.expectations[{index}] is not ASCII",
                )


class EvalGraderCase(unittest.TestCase):
    """Guard the two grader defects that produced the withdrawn result."""

    def grader_sources(self) -> list[Path]:
        candidates = list((ROOT / "scripts").glob("*eval*.py"))
        candidates.extend((ROOT / "scripts" / "eval").glob("*.py"))
        return [path for path in candidates if path.is_file()]

    def test_no_grader_hardcodes_individual_eval_names(self) -> None:
        # The withdrawn grader branched on four eval names and raised for the
        # rest, so half the suite was silently ungraded and the denominator was
        # wrong. A grader must iterate the manifest instead.
        names = [item["name"] for item in load_evals()["evals"]]
        for source in self.grader_sources():
            text = source.read_text(encoding="utf-8")
            for name in names:
                self.assertNotIn(
                    name,
                    text,
                    f"{source.name} hardcodes eval '{name}'; iterate evals.json instead",
                )

    def test_no_grader_matches_on_the_skill_private_vocabulary(self) -> None:
        # Matching on the skill's own terms makes the baseline structurally
        # unable to pass, which is what inflated the withdrawn delta.
        for source in self.grader_sources():
            text = source.read_text(encoding="utf-8").lower()
            for token in PRIVATE_VOCABULARY:
                self.assertNotIn(
                    token,
                    text,
                    f"{source.name} matches on private vocabulary '{token}'",
                )

    def test_no_grader_contains_non_ascii_matching_terms(self) -> None:
        for source in self.grader_sources():
            self.assertTrue(
                source.read_text(encoding="utf-8").isascii(),
                f"{source.name} contains non-ASCII terms; grading must be language-neutral",
            )


class ValidationRecordCase(unittest.TestCase):
    def test_every_validation_document_declares_a_status(self) -> None:
        for path in validation_documents():
            text = path.read_text(encoding="utf-8")
            status = STATUS_LINE.search(text)
            self.assertIsNotNone(status, f"{path.name} has no Status line")
            self.assertIn(status.group(1), ALLOWED_STATUS, f"{path.name} status is unknown")
            self.assertIsNotNone(
                CHECKED_LINE.search(text), f"{path.name} has no dated Checked line"
            )

    def test_superseded_documents_name_their_replacement(self) -> None:
        for path in validation_documents():
            text = path.read_text(encoding="utf-8")
            status = STATUS_LINE.search(text)
            if status is not None and status.group(1) == "Superseded":
                self.assertIsNotNone(
                    SUPERSEDED_LINE.search(text),
                    f"{path.name} is superseded but names no replacement",
                )

    def test_the_index_lists_every_validation_document(self) -> None:
        index = (VALIDATION / "README.md").read_text(encoding="utf-8")
        for path in validation_documents():
            self.assertIn(path.name, index, f"{path.name} is missing from the index")


class PublishedResultCase(unittest.TestCase):
    """A published number must be backed by a committed artifact."""

    def test_no_efficacy_number_is_published_without_supporting_artifacts(self) -> None:
        document = VALIDATION / "skill-evaluation.md"
        text = document.read_text(encoding="utf-8")
        block = RESULTS_BLOCK.search(text)
        if block is None:
            # No machine-readable result is published. The document must then say
            # so explicitly rather than leaving a bare table for a reader to
            # mistake for a current claim.
            self.assertIsNotNone(
                RETIRED_STATUS.search(text),
                "no results are published, so the document must be marked "
                "Withdrawn or Superseded rather than left ambiguous",
            )
            return

        published = json.loads(block.group(1))
        benchmark = WORKSPACE / published["iteration"] / "benchmark.json"
        self.assertTrue(
            benchmark.is_file(),
            f"published results cite {published['iteration']} but no benchmark.json is committed",
        )
        summary = json.loads(benchmark.read_text(encoding="utf-8"))["run_summary"]
        for configuration in ("with_skill", "without_skill"):
            self.assertAlmostEqual(
                published[f"{configuration}_mean"],
                summary[configuration]["pass_rate"]["mean"],
                places=4,
                msg=f"published {configuration} mean disagrees with the committed benchmark",
            )
        self.assertEqual(
            published["denominator"],
            published["evals"] * published["assertions_per_eval"] * published["n_runs"],
            "published denominator is not the product of its own factors",
        )
