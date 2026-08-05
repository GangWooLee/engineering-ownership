# 2026-07-29 · Guard the record conventions with tests, not shipped code

Change ID: `guard-record-conventions`
Created: `2026-07-29T18:09:13+09:00`
Risk: R1
Corrected: 2026-08-05 — the headline read "Seven of twenty-four change records",
counting violations as records; seven violations were found across six records,
which the same document lists correctly ten lines earlier.

## Problem and intended outcome

The rubric's layer 1 was written and measured but not enforced, so the seven
records violating it stayed wrong. Two conventions were being broken: three
records correct an earlier claim only in a late paragraph, where a reader who
skims absorbs the withdrawn version and stops; four say `Status: In progress`
while their evidence records are closed.

Intended outcome: the conventions hold because a test says so rather than
because someone remembers, and the seven existing violations are fixed.

## Success and non-goals

Success: the three guards fail on the corpus before the fixes and pass after,
demonstrated in that order; the guard that could manufacture defects has its
false-positive set pinned; the suite grows without any existing test changing.

Non-goals: extending `engineering check` — withdrawn, reasoning below; adding a
`Corrected:` field to the templates; touching ADR `Status:` lines; grading any
record, which is layer 2 and is not yet re-validated.

## Existing responsibilities searched

This is the fourth application of one pattern, not a new mechanism.
`ValidationRecordCase` holds the validation index current, `CommittedArtifactCase`
holds the workspace index current, `RecordIndexCase` holds the record index
current — all in `tests/`, all scoped by `ROOT = Path(__file__).parents[1]` so
they can only ever address this checkout. `evidence_gaps` already covers G4;
this change adds no second implementation of it.

## System and data flow

`tests/test_records.py` reads `docs/engineering/{changes,decisions,runbooks,security}/*.md`
and, for the status check, the matching `.engineering/evidence/<id>.json`. It
writes nothing and imports nothing from the CLI.

## Decisions and trade-offs

**The planned `engineering check` extension was withdrawn.** The original design
put these guards in the shipped gate, on the reasoning that `check` is already
in the workflow so no new command would be needed. Investigation reversed it:

- The precedent is explicit. `exclude-illustrative-references` rejected
  hard-coding this repository's paths into the CLI because "the CLI ships to
  other repositories… Repository-specific paths do not belong in shared code."
  Every optional contract key — `refs`, `automation`, `review_interval_days`,
  `artifacts.handoffs` — defaults to the behaviour that existed before it was
  added. Not one defaults to on.
- The blast radius is inverted. `check` runs in **no** CI job here: `ci.yml` is
  unittest, distribution validation, install, and `--version`. Meanwhile
  `references/finish.md` tells installers CI may run `check --mode enforce`. A
  guard in `check` would therefore be unenforced in the repository that invented
  the convention and blocking in the pipeline of someone who never agreed to it.
- The alternative, a contract-declared key defaulting to off, was considered and
  rejected as premature: it adds shipped surface, schema, and validation for a
  convention with exactly one adopter and no demand.

**G2 deletes contradictions, not fields.** Four `Status: In progress` lines went;
eight `Status: Completed` lines stayed. The rule is that a record must not
contradict its evidence, and "Completed" on a finished change is true history.
ADR `Status:` lines are untouched — `decision_is_superseded` is the one parser
that reads a `Status:` line, it reads ADRs only, and that line is half of the
supersession mechanism.

## Failure, security, and recovery

The failure mode a guard like this creates is manufacturing defects, which the
dead-link guard already did once by ignoring code spans. G1 is the worse case: a
keyword search for "correct" returns 26 hits of which 23 are records whose
subject is correction, including one stating a thing was deliberately *not*
corrected. The detector therefore matches the form every real correction uses,
and a fourth test pins the false-positive set so loosening the pattern fails
loudly.

No security surface: tests and documentation, no shipped code.

## Verification evidence

Order matters here, and it was followed.

1. Guards written first, run against the unfixed corpus: two failed, naming
   exactly the six files predicted — `defensible-skill-evaluation`,
   `describe-when-to-invoke`, `fix-blinding-redaction` (G1) and
   `add-terminal-close-state`, `fix-benchmark-postpass`, `fix-blinding-redaction`,
   `v0-2-immediate-workflow` (G2).
2. Four `Status: In progress` lines deleted; three `Corrected:` header lines
   added. `tests/test_records.py`: 4 passed.
3. Full suite: **92 tests pass**, up from 88, with no existing test modified.
   The index guard fired in between and was satisfied by regenerating — itself a
   demonstration that the guard notices a new record.

**Seven violations across six of twenty-four change records were caught.** That
number is the point: a guard that caught nothing would be measuring nothing.
(Corrected 2026-08-05: this line read "Seven of twenty-four change records",
counting violations as records, which disagrees with the six files listed ten
lines above it.)

## Known limits and learning gaps

- G1 depends on authors using the `(Corrected YYYY-MM-DD: …)` form. A correction
  written another way is invisible to it, and the guard cannot tell the
  difference between a record with no correction and one whose correction is
  phrased freely.
- G3 has never fired. It guards a surface with five links in it; if the corpus
  stays link-free it will keep proving nothing, and the rubric's own rule says a
  never-firing guard on a grown surface should be re-measured rather than
  trusted.
- These guards check form. A record can satisfy all three and still be
  unreadable — that is layer 2's job, and layer 2 failed its dry run and has not
  yet been re-validated.

## References

- `tests/test_records.py`
- `docs/validation/record-quality-rubric.md`
- `docs/engineering/decisions/exclude-illustrative-references.md` — the
  precedent that withdrew the `check` extension
