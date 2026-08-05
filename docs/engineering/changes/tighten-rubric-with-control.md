# 2026-07-29 · Tighten the rubric using a negative control

Change ID: `tighten-rubric-with-control`
Created: `2026-07-29T21:29:00+09:00`
Risk: R1

## Problem and intended outcome

The second dry run cleared its bar but could not answer its own central
question. Five of six records passed almost everything, which is equally
consistent with a lenient rubric and a uniform corpus, and nothing in a sample
of real records separates those. Both judges could only answer "what would a
clearly bad record also pass?" by speculation, having never been shown one.

Intended outcome: a bad record built on purpose, run blind among the real ones,
so the leniencies are located by demonstration rather than argument.

## Success and non-goals

Success: the control fails the dimensions it was built to game and passes the
one it was not, and any dimension it slips through is tightened using wording a
judge proposed and checked against the corpus.

Non-goals: grading the full corpus; adding dimensions; treating the control as a
record of real work — it documents nothing and says so in its own header.

## Existing responsibilities searched

The negative-control idea is not new here: `tests/test_records.py` already pins a
false-positive set for the correction guard, and the eval harness already runs a
baseline arm so a treatment cannot be scored against nothing. This applies the
same shape to a prose rubric. The control lives under `docs/validation/fixtures/`
so it is outside every guard that globs the record directories, and outside the
non-recursive glob that indexes validation documents — verified by the suite
staying green with it present.

## System and data flow

`docs/validation/fixtures/negative-control-record.md` is written to game three
named leniencies: a non-goals list containing only features not built, "the full
suite passes" placed inside a success clause and never reported as run, and
preferences carrying a bare `because`. It deliberately does not game D3 — every
identifier is glossed where it appears — so a D3 pass isolates the other three
dimensions instead of confounding them.

Seven extracts were built, the control at position four, and graded by two blind
judges under the current dimensions.

## Decisions and trade-offs

The tightenings are the judges' own wording, not mine. Each was proposed by a
judge who then checked it against all seven documents and named which would
still pass — that verification is why the edits were applied without a further
round. The alternative, inventing tighter wording myself and testing it in a
fourth run, would have cost another two judge passes to reach the same place.

The control is committed rather than kept in a scratch directory. A negative
control that exists only in one session's temporary files cannot be re-run
against a future rubric, which is the one thing it is for.

## Failure, security, and recovery

The failure mode a control introduces is being mistaken for a real record. Three
things prevent it: it lives outside every record directory, its own first
paragraph states it documents no real work, and no guard or index picks it up.
Recovery is deleting the file; nothing depends on it.

## Verification evidence

Prediction fixed before the run: the control fails D1, D2, D4 and passes D3.

| | Result |
| --- | --- |
| Control | **6 of 8 cells failed** — D1, D2, D4 by both judges; D3 passed by both |
| Prediction | met exactly |
| Agreement | 26 / 28 (93%) |
| Control's rank | worst of seven by rubric score |

The rubric catches a record built to beat it, so the leniencies the previous run
speculated about are narrower than feared.

**The finding the control was not designed to produce.** Asked separately from
the rubric which document they would least want to inherit, both judges named
the same one — and it was not the control. It was a real record that scores
better than the control on the rubric. One judge: "The rubric over-penalizes
legible thinness and under-penalizes abstraction with no referent." The control
is thin but every term is glossed and the change is reconstructable; the
rejected record covers an entire release, names no file, no command, and no
number, and delegates its assurance to "exercised by tests" — yet passed D1 and
D4.

Three tightenings applied, each judge-proposed and checked against all seven
records: a deferred-feature list no longer satisfies D1; a check named only by
pointing at another document counts as no check under D2; a scope disclaimer is
not a stopping condition under D4.

## Known limits and learning gaps

- **The tightenings carry predicted verdicts, not measured ones.** Each judge
  stated which records their edit would newly fail; the full pass tests those
  predictions, and a miss is a finding about the rubric.
- One control is one point. It probes the three leniencies that were named and
  says nothing about leniencies nobody has thought of yet.
- The control was written by the same author as the rubric, which is the weakest
  possible adversary. A control written by someone trying to beat a rubric they
  did not design would be a stronger test.
- Both judges remain the same model family, so 93% agreement measures rubric
  clarity less well than cross-family agreement would.

## References

- `docs/validation/fixtures/negative-control-record.md`
- `docs/validation/record-quality-rubric.md` — all three runs
