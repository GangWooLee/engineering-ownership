# 2026-07-29 · Revise the record rubric after its dry run

Change ID: `revise-rubric-after-dry-run`
Created: `2026-07-29T17:18:32+09:00`
Risk: R1

## Problem and intended outcome

The record-quality rubric was written but never tried. Its own design said a
standard must be doubted before it is automated, so layer 2 was dry-run on six
records with two independent judges — and it failed. Three of four dimensions
produced no signal, and the one that discriminated was measuring the wrong
property.

Intended outcome: dimensions revised against what the run found, with the run
itself recorded so a later reader can see the first version was wrong rather
than inferring that it was always this way.

## Success and non-goals

Success: each revised dimension traceable to the specific failure that caused
the revision, and the rubric stating plainly that the revised dimensions have
not themselves been dry-run.

Non-goals: automating anything; grading the corpus; changing any record. The
revised dimensions are untested and must not skip the step the first ones just
failed.

## Existing responsibilities searched

No new grading machinery. The run reused the existing judge output contract —
quoted evidence, no partial credit, a critique channel where the judge attacks
the expectations themselves. That critique channel produced most of this
change's content, which is the argument for having it.

## System and data flow

Six records, stratified by risk tier and revision history. Five sections
extracted per record — the five whose template instructions never changed — with
titles, dates, and identifiers stripped. Two judges, each blind to the other.
Verdicts compared cell by cell; agreement and per-dimension pass counts computed
before any dimension was rewritten.

## Decisions and trade-offs

Grading moved from as-authored text to HEAD, decided during preparation and
before any score existed. The original plan said to grade each record at its add
commit so a later audit's corrections would not leak in. Extracting that version
showed the flaw: `change start` creates the record before the work is done, so
the add-commit version of one sampled record was a 252-character template
skeleton with instruction text still in it. "As authored" and "at the add
commit" are not the same thing in this workflow. HEAD is also what a reader
actually meets, and a well-placed correction is part of a record's current
quality rather than noise in it.

## Failure, security, and recovery

The failure this guards against is a standard that looks rigorous and measures
nothing — which is what the first layer 2 was. It is caught by the mandatory
all-pass/all-fail check, which is exactly what caught it here. The same check
applies to the revised dimensions before they are automated.

No security surface: documentation only.

## Verification evidence

Two judges, six records, four dimensions — 24 cells each.

- **Agreement: 22/24 (92%)**, and both disagreements fell on dimensions the
  judges independently flagged as ambiguous. Divergence tracked vagueness.
- **Pass counts across both graders:** D1 11/12, D2 2/12, **D3 0/12**, D4 11/12.
  One dimension separated the set; one was a constant; two were near-constants.
- Both judges independently reported that D1 is guaranteed by the template
  (every record opens with `Success and non-goals`) and that its
  "consequential fact after the halfway mark" clause fires on records that put
  caveats in `Known limits` — where the template instructs authors to put them.
- Both independently reported that D3 was unsatisfiable for any in-repository
  record and had no defined reader; each narrowed it to proceed, and each
  narrowed it differently.

## Known limits and learning gaps

- **The revised dimensions have not been dry-run.** They were written against
  one run's critique and may fail differently. Running them is required before
  automation, and the rubric says so.
- Six records and two judges is a small basis for rewriting four dimensions.
  The rewrites follow findings both judges reached independently, which is
  stronger than either alone, but it is not a large sample.
- The judges were the same model family. Agreement between them measures
  rubric clarity less well than agreement between different families would.
- D2's revision asks the judge to separate "the record's account of a check"
  from "whether the check is deterministic". That distinction was clear in the
  critique and may prove hard to apply consistently in practice.

## References

- `docs/validation/record-quality-rubric.md` — revised dimensions and the
  dry-run record
- `docs/engineering/decisions/define-record-quality-rubric.md` — why the layers
  are split as they are
