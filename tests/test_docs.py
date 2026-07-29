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


if __name__ == "__main__":
    unittest.main()
