# 2026-08-05 · Grade the verification section the verification dimension asks about

Change ID: `grade-verification-sections`
Created: `2026-08-05T19:36:20+09:00`
Risk: R1
Corrected: 2026-08-05 — Known limits said the corpus was not re-graded and that
the published table still described the old extraction. Both were true when
written and false by the time this record was committed, in the same commit that
reports the full rerun.

## Problem and intended outcome

The record grader extracts five sections of each change record and hands only
those to the judge. `Verification evidence` is not among them. One of the four
dimensions being judged, D2, asks what the record says was checked and what the
check produced -- so the dimension about verification was measured on text that
structurally excludes the record's verification report. 25 of 27 records have
that section.

The first full-corpus run shipped with this defect. Both judges reported
`add-record-index` as deferring its verification entirely, quoting a pointer
sentence from a different section; its actual `Verification evidence` section
reports four checks with outcomes. They were right about what they could see.

Intended outcome: the judge sees the section, the two records that predate the
section's current heading still get graded, and the disagreement that hid this
becomes something a test fails on.

## Success and non-goals

Success is that the extract for a record with the section now contains it, that
the two records without it still produce an extract rather than being skipped,
and that a future edit which puts the grader and the rubric out of step fails
the suite. The last of those could plausibly have gone the other way: a guard
comparing prose to code can be written so loosely that it passes on any input,
and the first version of one of these guards did exactly that.

Non-goals: re-grading the corpus, revising any dimension's wording, or changing
what the earlier run reported. That run's numbers stand as what was measured
under the extraction it used, and the document reporting them already says the
D2 column is not usable.

## Existing responsibilities searched

`tests/test_docs.py` already owns consistency between a generated artifact and
the documents it describes -- `RecordIndexCase` fails when the index and the
records disagree. The new guards are the same shape applied to a different pair,
so they live there rather than in a new file.

Nothing existing owned the grader's section list. The list was named in two
places, `scripts/grade_records.py` and the rubric's *What is graded* paragraph,
with a source comment asserting that a disagreement between them is a defect and
no test enforcing it. That unenforced assertion is why the omission survived
design, dry runs, a negative-control pass, and a full corpus run.

## System and data flow

`GRADED_SECTIONS` becomes a tuple of `(name, required)` pairs in the order a
reader meets them, with `Verification evidence` inserted at its document
position and marked optional. `extract_sections` skips a missing optional
section and continues; a missing required section still returns `None`, which is
what makes the grader report a record as ungradeable rather than score a
fragment.

`--only` is added so a change to extraction can be checked against named records
without paying for a full run. It validates its arguments against the record
directory and exits on an unknown id, so a typo cannot silently grade nothing.

Four guards in `tests/test_docs.py` read the list out of the grader source and
check it against the rubric prose, against the shipped record template, and
against the corpus in both directions.

## Decisions and trade-offs

`Verification evidence` is optional rather than required. Required would drop
`documentation-first-workflow` and `v0-1-0-public-release` from grading, because
both were written before the heading was renamed from `Verification plan` and
have no section under the current name. Losing two records to gain a stricter
rule is the wrong trade when their absence of a reported check is exactly what
D2 should catch, and optional lets the judge see that absence.

The rubric's reason for the original exclusion -- that scoring a section whose
template instructions moved would measure the template -- does not reach this
section. `Verification evidence` has never carried instruction text; it is a
bare heading in the template, as three of the five required sections are. The
only thing that changed was the heading itself, once, and the records affected
by that rename are the two that simply do not have it.

The earlier results document is corrected in place rather than superseded. It
already reports the defect and names this fix; superseding it would replace a
document whose conclusions about D1, D3 and D4 are unaffected.

## Failure, security, and recovery

The failure this introduces is a guard that passes on anything, which is worse
than no guard because it reads as coverage. It nearly happened: the first
rubric-agreement guard checked that each section name appears somewhere in a
long paragraph that mentions those names repeatedly, so deleting a name from the
list left it green. It was found by breaking it and watching nothing fail, then
re-broken from the grader side, where it does fail.

The second gap was found the same way. Flipping the optional section to required
left every guard green while silently removing two records from the corpus, so a
guard for required sections was added; it now names the two records.

Recovery for the change as a whole is reverting one file: no data is migrated,
and the earlier run's output is untouched in its own directory.

## Verification evidence

| Check | Result |
| --- | --- |
| Extraction, `add-record-index` | Now contains `## Verification evidence` with its four reported checks; extract is 3,218 characters |
| Extraction, the two records without the section | Still extract, 2,135 and 2,006 characters; not skipped |
| Guard proved by breaking it, rubric agreement | Adding `Rollout notes` to the grader fails `test_the_rubric_names_every_section_the_grader_extracts` |
| Guard proved by breaking it, template agreement | The same edit fails `test_the_grader_extracts_every_section_the_template_still_offers` |
| Guard proved by breaking it, required sections | Flipping `Verification evidence` to required fails `test_a_required_section_is_one_every_record_has`, naming `documentation-first-workflow` and `v0-1-0-public-release` |
| First version of the rubric guard | Did **not** fail when a name was deleted from the rubric; recorded here rather than quietly rewritten |
| Suite | 96 tests, all passing |
| Contract commands | `unit` and `distribution` pass via `engineering verify` |

Re-graded under the fixed extraction, blind, two judges, same model:
`add-record-index`, `documentation-first-workflow`, `v0-1-0-public-release`.
Results in `engineering-ownership-workspace/record-quality-verify/`, written to a
separate directory so the corpus run is not overwritten.

**No verdict changed.** All twelve cells landed where they did before. That is
the honest headline and it is not an argument that the fix was unnecessary:

- `add-record-index` passes D2 as it did, but on different text. Before, both
  judges quoted an audit count from the data-flow section -- the only
  check-with-outcome they could see. Now both quote the section that reports
  checks: "88 tests pass (83 before, 5 added)" and the guard proved by breaking
  it. The verdict was right for the wrong reason, and now it is right.
- The two lowest records fail D2 under both extractions, which is what should
  happen. Neither has a `Verification evidence` section, so the fix gave the
  judge nothing new to read, and their failure was never an artifact.

Three records cannot say whether the corpus-wide D2 rate moves. The full rerun
that followed says it does, and says something the probe was too small to see.

**Full corpus re-graded**, 29 records, 58 passes, reported in
[record-quality-2026-08-rerun.md](../../validation/record-quality-2026-08-rerun.md).
On the 27 records both runs graded, D2 went from 44 to 48 cells and two records
moved both-fail to both-pass, each with a `Verification evidence` section the
first run withheld. That part is the fix working.

The part the probe missed is that the other three dimensions moved too, in both
directions, with almost no net change: D1 31 to 30 cells with four records
moving, D3 4 to 5 with five moving, D4 42 to 44 with three moving. D1 reads only
the opening section, which this change did not touch, so its four moves are the
instrument re-rolling on identical input. That is a floor on what any
single-run difference can mean, and the first run published a table without it.

## Known limits and learning gaps

- **D1, D3 and D4 did move, and not in one direction.** The rerun shows four,
  five and three records changing verdict with almost no net change in any of
  them. D1 reads only the opening section, which this change did not touch, so
  its four moves are the instrument re-rolling. Everything the rerun reports
  about those three dimensions sits above that floor only for D2.
  (Corrected 2026-08-05: these two bullets said the corpus was not re-graded and
  that the published table still described the old extraction. That was true
  when written and false by the time this record was committed, in the same
  commit that reports the rerun.)
- Three records was a probe, not a measurement, and it under-reported. It found
  no verdict changes; the full rerun found eleven records moving. A probe that
  reaches the diagnosed record says the fix works, not how far it reaches.
- The guards compare a list in Python source to prose in Markdown by regex. They
  catch a name present in one and absent from the other. They do not catch a
  rubric paragraph that names the right sections and describes them wrongly.
- The `--only` flag makes a partial run easy, which makes it easy to report a
  partial run as if it were a full one. Nothing prevents that but the habit of
  saying which records were graded.

## References

- `docs/validation/record-quality-rubric.md` -- the corrected *What is graded*
- `docs/validation/record-quality-2026-08.md` -- the run that carried the defect
- `docs/engineering/changes/grade-the-record-corpus.md` -- where it was found
- `scripts/grade_records.py`, `tests/test_docs.py`
