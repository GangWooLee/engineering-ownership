from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "plugins" / "engineering-ownership" / "src"
ENGINEERING = ROOT / "docs" / "engineering"
EVIDENCE = ROOT / ".engineering" / "evidence"
INDEX = ENGINEERING / "README.md"


class RecordIndexCase(unittest.TestCase):
    """An index nobody maintains falls behind; an index nothing checks falls silently.

    docs/validation/README.md and the evaluation workspace index are both held
    current by a test rather than by discipline. This is the same guard for the
    third and largest index, and it is why the index is generated rather than
    hand-written: the generator makes it cheap to be right, the guard makes it
    expensive to be wrong.
    """

    def test_every_change_record_is_reachable_from_an_index(self) -> None:
        self.assertTrue(INDEX.is_file(), "docs/engineering has no index")
        listed = INDEX.read_text(encoding="utf-8")
        for path in sorted(EVIDENCE.glob("*.json")):
            self.assertIn(
                path.stem,
                listed,
                f"{path.stem} has an evidence record but the index does not list it",
            )

    def test_every_engineering_document_is_reachable_from_the_index(self) -> None:
        # A document no record claims — an ADR written at R1, where the risk tier
        # allocates no decision file — is reachable by `ls` and by nothing else.
        # The index is the surface that has to notice it.
        listed = INDEX.read_text(encoding="utf-8")
        for directory in ("changes", "decisions", "runbooks", "security"):
            for path in sorted((ENGINEERING / directory).glob("*.md")):
                self.assertIn(
                    path.stem,
                    listed,
                    f"{directory}/{path.name} exists but the index does not list it",
                )

    def test_index_links_resolve(self) -> None:
        # Links are written relative to the index's own directory. A root-relative
        # path renders as a dead link on any forge, which is worse than no table.
        text = INDEX.read_text(encoding="utf-8")
        targets = [target for _, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)]
        self.assertTrue(targets, "the index contains no links")
        for target in targets:
            self.assertTrue(
                (ENGINEERING / target).resolve().is_file(),
                f"the index links to {target}, which does not resolve from its own directory",
            )

    def test_index_is_current_with_the_records(self) -> None:
        # Regenerating must be a no-op. Without this, the guards above still pass
        # while the table lies about state — a record could close and the index
        # would keep calling it open.
        sys.path.insert(0, str(SOURCE))
        try:
            from engineering_ownership.cli import index_text
            from engineering_ownership.model import read_contract
        finally:
            sys.path.remove(str(SOURCE))
        expected = index_text(
            ROOT, read_contract(ROOT), as_markdown=True, base="docs/engineering"
        )
        self.assertEqual(
            expected,
            INDEX.read_text(encoding="utf-8"),
            "docs/engineering/README.md is stale; regenerate it with "
            "`engineering index --format md --write docs/engineering/README.md`",
        )

    def test_the_index_names_each_record_rather_than_only_its_id(self) -> None:
        # The audit's second reader journey failed at a guess between four
        # plausible ids, because the title is stored and never printed.
        listed = INDEX.read_text(encoding="utf-8")
        checked = 0
        for path in sorted(EVIDENCE.glob("*.json")):
            title = json.loads(path.read_text(encoding="utf-8")).get("title")
            if not title:
                continue
            self.assertIn(title, listed, f"the index omits the title of {path.stem}")
            checked += 1
        self.assertGreater(checked, 0, "no evidence record carries a title")


class GradedSectionsCase(unittest.TestCase):
    """The rubric's list of graded sections and the grader's must agree.

    They agreed once and were both wrong: each named the same five sections, and
    the section that answers the verification dimension was in neither, so a
    full corpus was graded on that dimension without the text that answers it.
    Naming the sections in two places is worth it — one is the standard a reader
    consults, the other is what actually ran — but only if disagreement fails,
    and only if the list is checked against the template rather than itself.
    """

    def graded_sections(self) -> list[tuple[str, bool]]:
        """The (name, required) pairs the grader actually extracts."""
        source = (ROOT / "scripts" / "grade_records.py").read_text(encoding="utf-8")
        block = re.search(
            r"^GRADED_SECTIONS = \((.*?)^\)", source, re.MULTILINE | re.DOTALL
        )
        self.assertIsNotNone(block, "scripts/grade_records.py has no GRADED_SECTIONS")
        pairs = re.findall(r'\(\s*"([^"]+)"\s*,\s*(True|False)\s*\)', block.group(1))
        self.assertTrue(pairs, "GRADED_SECTIONS is not a list of (name, required)")
        return [(name, flag == "True") for name, flag in pairs]

    def test_the_rubric_names_every_section_the_grader_extracts(self) -> None:
        rubric = (ROOT / "docs" / "validation" / "record-quality-rubric.md").read_text(
            encoding="utf-8"
        )
        stated = re.search(
            r"\*\*What is graded\.\*\*(.*?)(?=\n## )", rubric, re.DOTALL
        )
        self.assertIsNotNone(stated, "the rubric has no 'What is graded' paragraph")
        prose = stated.group(1)
        for name, _ in self.graded_sections():
            self.assertIn(
                f"`{name}`",
                prose,
                f"the grader extracts '{name}' but the rubric does not name it",
            )

    def test_the_grader_extracts_every_section_the_template_still_offers(self) -> None:
        # A section the rubric names but the template dropped would be extracted
        # from no record and contribute nothing, silently.
        template = (SOURCE / "engineering_ownership" / "templates.py").read_text(
            encoding="utf-8"
        )
        for name, _ in self.graded_sections():
            self.assertIn(
                f"## {name}",
                template,
                f"'{name}' is graded but the record template no longer offers it",
            )

    def test_a_required_section_is_one_every_record_has(self) -> None:
        # A required section a record lacks makes the grader skip that record
        # silently — it prints one line and moves on, and the corpus shrinks
        # without the results saying so. Found by flipping the optional section
        # to required and watching the other guards stay green.
        records = sorted((ENGINEERING / "changes").glob("*.md"))
        self.assertTrue(records, "no change records to check")
        for name, required in self.graded_sections():
            if not required:
                continue
            missing = [
                path.stem
                for path in records
                if f"## {name}" not in path.read_text(encoding="utf-8")
            ]
            self.assertEqual(
                missing,
                [],
                f"'{name}' is required but {len(missing)} record(s) lack it, so "
                f"they would be dropped from grading unannounced: {missing}",
            )

    def test_an_optional_section_is_one_some_record_is_missing(self) -> None:
        # Optional is a claim about the corpus: it exists so records written
        # before a heading was renamed still grade. If every record has the
        # section, optional is dead configuration and should be tightened.
        records = sorted((ENGINEERING / "changes").glob("*.md"))
        self.assertTrue(records, "no change records to check")
        for name, required in self.graded_sections():
            if required:
                continue
            missing = [
                path.stem
                for path in records
                if f"## {name}" not in path.read_text(encoding="utf-8")
            ]
            self.assertTrue(
                missing,
                f"'{name}' is optional but every record has it — make it required",
            )


if __name__ == "__main__":
    unittest.main()
