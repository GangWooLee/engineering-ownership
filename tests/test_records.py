from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
ENGINEERING = ROOT / "docs" / "engineering"
EVIDENCE = ROOT / ".engineering" / "evidence"
RECORD_DIRS = ("changes", "decisions", "runbooks", "security")

# The form every in-place correction in this repository actually uses. A keyword
# search for "correct" finds 26 hits of which 23 are records whose *subject* is
# correction — one of them literally says "deliberately not been corrected". A
# guard that cannot tell those apart manufactures defects, which is the mistake
# the dead-link guard made once already by ignoring code spans.
CORRECTION = re.compile(r"\(Corrected \d{4}-\d{2}-\d{2}:")
HEADER_MARKER = re.compile(r"^Corrected:", re.MULTILINE)
IN_PROGRESS = re.compile(r"^Status:\s*In progress\s*$", re.MULTILINE)
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def records() -> list[Path]:
    return sorted(
        path
        for directory in RECORD_DIRS
        for path in (ENGINEERING / directory).glob("*.md")
    )


def header_block(text: str) -> str:
    """The lines between the H1 and the first section heading."""
    body = text.split("\n## ", 1)[0]
    return body.split("\n", 1)[1] if "\n" in body else ""


def prose(text: str) -> str:
    """Markdown with fenced blocks and inline code spans removed."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return re.sub(r"`[^`\n]*`", "", text)


class RecordConventionCase(unittest.TestCase):
    """Conventions this repository holds itself to, enforced here rather than in the CLI.

    These are house rules, not product behaviour. The CLI ships to other
    repositories, and an earlier decision established that repository-specific
    policy belongs in the contract or in tests rather than in shared code —
    otherwise a convention invented here would block a stranger's merge. Tests do
    not ship: the release archive is bounded to plugins/engineering-ownership.
    """

    def test_a_corrected_record_says_so_in_its_header(self) -> None:
        # A correction at the bottom means a reader who skims absorbs the
        # withdrawn claim and stops before the retraction. The three records
        # that carried one had it at 65%, 82% and 93% depth.
        offenders = []
        for path in records():
            text = path.read_text(encoding="utf-8")
            if CORRECTION.search(text) and not HEADER_MARKER.search(header_block(text)):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(
            offenders,
            [],
            "these records correct a claim without saying so in their header: "
            + ", ".join(offenders),
        )

    def test_no_change_record_claims_in_progress_after_closing(self) -> None:
        # The markdown status is parsed by nothing, so nothing corrects it. Four
        # records said "In progress" while their evidence said closed. The rule
        # is no contradiction, not no field: "Completed" on a finished change is
        # history and stays.
        offenders = []
        for path in sorted((ENGINEERING / "changes").glob("*.md")):
            if not IN_PROGRESS.search(path.read_text(encoding="utf-8")):
                continue
            evidence = EVIDENCE / f"{path.stem}.json"
            if not evidence.is_file():
                continue
            if json.loads(evidence.read_text(encoding="utf-8")).get("closed"):
                offenders.append(path.relative_to(ROOT).as_posix())
        self.assertEqual(
            offenders,
            [],
            "these records say In progress but their evidence is closed: "
            + ", ".join(offenders),
        )

    def test_relative_links_resolve_from_the_record(self) -> None:
        # Links are written relative to the file that holds them. The generated
        # index is excluded because tests/test_docs.py already resolves its links
        # against a different base; two guards disagreeing about the same links
        # is worse than one guard.
        broken = []
        for path in records():
            for _, target in LINK.findall(prose(path.read_text(encoding="utf-8"))):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                if not (path.parent / target).resolve().is_file():
                    broken.append(f"{path.relative_to(ROOT).as_posix()} -> {target}")
        self.assertEqual(broken, [], "these record links do not resolve: " + ", ".join(broken))

    def test_the_correction_guard_does_not_fire_on_records_about_correcting(self) -> None:
        # The guard's own failure mode, pinned. These records discuss correction
        # as their subject; one of them says a thing was deliberately NOT
        # corrected. A keyword-based guard flags all of them.
        subjects = [
            "changes/correct-git-attribution.md",
            "changes/fix-benchmark-postpass.md",
            "changes/withdraw-unsupported-evaluation-claim.md",
            "changes/revise-rubric-after-dry-run.md",
            "changes/define-record-quality-rubric.md",
        ]
        for relative in subjects:
            path = ENGINEERING / relative
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            self.assertRegex(text.lower(), r"correct", f"{relative} no longer discusses correction")
            self.assertIsNone(
                CORRECTION.search(text),
                f"{relative} is a record about correcting, not a corrected record; "
                "the guard must not claim otherwise",
            )


if __name__ == "__main__":
    unittest.main()
