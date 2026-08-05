#!/usr/bin/env python3
"""Grade this repository's change records against the layer-2 rubric.

The rubric text is read at run time rather than embedded here. Two reasons.
The standard has one home, so a dimension cannot be tightened in the document
and stay loose in the grader. And the dimension prose contains typographic
characters, which a guard on this file's source would reject -- reading the
document sidesteps that without weakening the guard.

The criteria are not parsed. The whole layer-2 section is handed to the judge,
the way the eval grader hands over its instruction file. That document holds
five other tables, one of which still lists the dimension names that were
measured and rejected; a parser keyed on a table or on row labels can pick the
superseded set and grade against it silently.

One thing is parsed: `dimension_ids` reads the identifiers out of the layer-2
table for the arity check, so a judge returning the wrong number of verdicts is
rejected. That parse is confined to the already-extracted layer-2 section, which
is why it cannot reach the superseded table -- but it is the same regex shape as
the hazard above, and widening its input would reintroduce it.

Judges see only the graded sections. No filename, no date, no risk tier, no
commit message: a judge that can identify a record can score its author.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "docs" / "engineering" / "changes"
RUBRIC = ROOT / "docs" / "validation" / "record-quality-rubric.md"

# The sections handed to the judge, in the order a reader meets them, each with
# whether the record must have it. Scoring a section whose template instructions
# moved would measure the template rather than the writing, which is why most of
# the template is left out. The rubric states this list in prose; a disagreement
# between the two is a defect, and `tests/test_evals.py` fails on one.
#
# `Verification evidence` is optional rather than required. It has never carried
# instruction text -- it is a bare heading, as three of the required sections are
# -- so the reason the other sections were dropped does not reach it. Its heading
# was renamed once, from `Verification plan`, and the two records written before
# that rename have no section under the new name. Requiring it would drop those
# two from grading entirely; leaving it out of the extract, as the first run did,
# blinds the verification dimension in the 25 records that do have it. Optional
# gives the judge the section when it exists and lets its absence read as what it
# is.
GRADED_SECTIONS = (
    ("Success and non-goals", True),
    ("Existing responsibilities searched", True),
    ("System and data flow", True),
    ("Failure, security, and recovery", True),
    ("Verification evidence", False),
    ("Known limits and learning gaps", True),
)

RUBRIC_SECTION = "Layer 2"

OUTPUT_CONTRACT = """
Return only a JSON object of this exact shape:

```json
{
  "dimensions": [
    {"id": "D1", "passed": true, "evidence": "<verbatim quotation, or what you searched for and did not find>"}
  ],
  "rubric_feedback": "<optional: any dimension a clearly bad record would also have passed>"
}
```

One entry per dimension, in the order given. Every verdict is true or false --
no partial credit. Evidence must be a verbatim quotation from the record, or
for a failure, a specific statement of what you searched for and did not find.
Restating the dimension is not evidence.

The rubric_feedback field is where you criticise the dimensions themselves.
Use it when one is unfalsifiable, ambiguous, or satisfiable without doing the
work. That feedback is as valuable as the verdicts.
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def extract_json(text: str) -> dict | None:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("```")[1]
        if stripped.startswith("json"):
            stripped = stripped[4:]
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(stripped[start : end + 1])
    except json.JSONDecodeError:
        return None


def rubric_section() -> str:
    """The layer-2 section, verbatim, from its heading to the next one."""
    text = RUBRIC.read_text(encoding="utf-8")
    match = re.search(
        r"^## [^\n]*" + re.escape(RUBRIC_SECTION) + r"[^\n]*\n(.*?)(?=\n## |\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise SystemExit(f"no '{RUBRIC_SECTION}' section in {RUBRIC.name}")
    return match.group(1).strip()


def dimension_ids(section: str) -> list[str]:
    """Dimension identifiers, in the order the rubric lists them."""
    return re.findall(r"\|\s*\*\*(D\d)[^*]*\*\*\s*\|", section)


UNFILLED = "<!-- engineering-ownership:fill-required -->"


def extract_sections(path: Path) -> str | None:
    """The graded sections of one record, or None when it cannot be graded.

    A record still carrying the template's unfilled marker is skipped rather
    than scored. The gate already treats that marker as a gap, and a verdict on
    a skeleton says nothing about writing.
    """
    text = path.read_text(encoding="utf-8")
    if UNFILLED in text:
        return None
    parts = []
    for name, required in GRADED_SECTIONS:
        match = re.search(
            r"^## " + re.escape(name) + r"\s*?\n(.*?)(?=\n## |\Z)",
            text,
            re.MULTILINE | re.DOTALL,
        )
        if match is None:
            if required:
                return None
            continue
        parts.append(f"## {name}\n{match.group(1).rstrip()}")
    return "\n\n".join(parts)


def compose_prompt(section: str, record: str) -> str:
    return (
        "You are judging one engineering record against the criteria below. You "
        "have no tools; everything you need is here.\n\n"
        "You are an engineer new to this repository: competent, with no prior "
        "knowledge of its vocabulary, history, or conventions. Judge from that "
        "seat. You know nothing about who wrote this or when. Do not speculate "
        "about its origin, and do not let its length influence a verdict.\n\n"
        f"## The criteria\n\n{section}\n\n"
        "## The record under review\n\n"
        "<record>\n"
        f"{record}\n"
        "</record>\n\n"
        f"{OUTPUT_CONTRACT}"
    )


def judge(prompt: str, model: str, timeout: int) -> dict:
    env = {**subprocess.os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"}
    env.pop("CLAUDECODE", None)
    started = time.monotonic()
    try:
        completed = subprocess.run(
            [
                "claude",
                "-p",
                prompt,
                "--model",
                model,
                "--output-format",
                "json",
                "--tools",
                "",
                "--no-session-persistence",
            ],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {"error": "judge timed out"}
    if completed.returncode != 0:
        return {"error": f"judge exited {completed.returncode}"}
    try:
        envelope = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"error": "judge returned unparseable output"}
    verdict = extract_json(envelope.get("result", ""))
    if verdict is None:
        return {"error": "judge returned no JSON object"}
    verdict["_elapsed"] = round(time.monotonic() - started, 3)
    return verdict


def grade_record(
    path: Path, section: str, ids: list[str], model: str, graders: int, timeout: int
) -> dict:
    record = extract_sections(path)
    if record is None:
        return {"error": "record is missing one of the graded sections"}
    prompt = compose_prompt(section, record)
    passes: list[dict] = []
    for index in range(graders):
        verdict = judge(prompt, model, timeout)
        if "error" in verdict:
            return {"error": f"grader {index + 1}: {verdict['error']}"}
        graded = verdict.get("dimensions") or []
        if len(graded) != len(ids):
            return {
                "error": f"grader {index + 1} returned {len(graded)} verdicts for {len(ids)}"
            }
        entries = []
        # The judge's own id field is discarded: order is the contract, and a
        # judge that renames a dimension must not silently remap a verdict.
        for dimension, item in zip(ids, graded, strict=True):
            entries.append(
                {
                    "dimension": dimension,
                    "passed": bool(item.get("passed")),
                    "evidence": str(item.get("evidence", "")).strip(),
                }
            )
        passes.append(
            {
                "grader": index + 1,
                "dimensions": entries,
                "rubric_feedback": str(verdict.get("rubric_feedback", "")).strip(),
            }
        )
    return {"graders": passes}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="judge model id, pinned")
    parser.add_argument("--graders", type=int, default=2)
    parser.add_argument("--out", default="engineering-ownership-workspace/record-quality")
    parser.add_argument("--timeout", type=int, default=420)
    parser.add_argument("--resume", action="store_true", help="skip records already graded")
    parser.add_argument(
        "--only",
        action="append",
        metavar="RECORD_ID",
        help="grade just this record; repeatable. For checking a change to "
        "extraction against known records without paying for a full run.",
    )
    args = parser.parse_args()

    section = rubric_section()
    ids = dimension_ids(section)
    if not ids:
        raise SystemExit("no dimensions found in the rubric section")
    out = ROOT / args.out

    wanted = set(args.only or ())
    if wanted:
        present = {path.stem for path in RECORDS.glob("*.md")}
        unknown = sorted(wanted - present)
        if unknown:
            raise SystemExit(f"no such record(s): {', '.join(unknown)}")

    graded = 0
    for path in sorted(RECORDS.glob("*.md")):
        if wanted and path.stem not in wanted:
            continue
        target = out / f"{path.stem}.json"
        if args.resume and target.is_file():
            print(f"{path.stem}: cached")
            graded += 1
            continue
        outcome = grade_record(path, section, ids, args.model, args.graders, args.timeout)
        if "error" in outcome:
            print(f"{path.stem}: not graded ({outcome['error']})")
            continue
        write_json(
            target,
            {
                "record": path.stem,
                "dimensions_graded": ids,
                "graders": outcome["graders"],
                "judge_model": args.model,
                "graded_at": now(),
            },
        )
        marks = "".join(
            "".join("O" if d["passed"] else "X" for d in g["dimensions"])
            for g in outcome["graders"]
        )
        print(f"{path.stem}: {marks}")
        graded += 1

    if not graded:
        raise SystemExit("no records were graded")
    print(f"graded {graded} record(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
