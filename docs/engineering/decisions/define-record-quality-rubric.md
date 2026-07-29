# 2026-07-29 · Define how record quality is measured

Change ID: `define-record-quality-rubric`
Created: `2026-07-29T17:20:00+09:00`
Status: Accepted

## Context

Record quality has been asserted, never measured. This project has already paid
for that pattern once: it built an evaluation, trusted the numbers, and
retracted the claim when the rubric turned out to be the defect. Applying the
same discipline to its own records means writing the standard before any score
exists, and doubting the standard before automating it.

## Options considered

1. **One quality score per record.** Rejected: it forces every question through
   the expensive input. Whether a link resolves and whether a stranger can reuse
   a record are not the same kind of question, and pricing them the same makes
   the cheap one expensive.
2. **Mechanical checks only.** Rejected: the defects the audit actually found —
   the point arriving after the halfway mark, a term whose first use explains
   nothing — are not countable. A rubric that measures only what is countable
   would report a clean corpus and be wrong.
3. **Three layers, split by what the question needs.** Chosen. Guards on every
   commit, judged dimensions quarterly, reach measured separately because it is
   a property of the structure rather than the prose.

## Decision

The rubric is `docs/validation/record-quality-rubric.md`. Three layers, four
inherited rules (no private vocabulary, silence never passes, discrimination
required, no aggregation).

**Rule 3 is scoped to layer 2, and that scoping is the substantive decision.**
The rule exists because a constant term dilutes a scored denominator — `eval-9`'s
fourth expectation held 20% of one fixed while passing 0 of 8 times. A layer-1
guard contributes to no denominator. It is a tripwire, and a tripwire that has
not fired is not a broken instrument. Applying rule 3 uniformly would delete the
dead-link guard for having zero violations, which inverts what a guard is for.
The admission test for layer 1 is therefore "would a realistic mistake trip it",
and each guard's violation count is recorded so a later reader can tell a
tripwire from a discriminator.

**The rubric lives in `docs/validation/`, not `docs/engineering/`.** That
directory already carries a `Status:` / `Checked:` convention and an index a test
holds current. A readability review of this repository concluded that a new
document in an unwatched directory is a drift generator; putting the standard
where the guard already exists follows that conclusion instead of repeating the
mistake it identified.

**Every layer-1 item was measured against all 56 records before admission**, and
three proposals were deleted by that measurement: `fill-required` markers and
empty sections (0/56, and `check` already blocks both) and the term-definition
link (52/56 would fail — a guard almost everything violates blocks work rather
than catching mistakes).

## Consequences and reversal

Automating a rubric that has not been dry-run is now prohibited by the process
this decision sets up: layer 1 items are admitted only after being run over the
corpus with their hits inspected. That step already earned its place — the
dead-link guard's first implementation flagged a link inside backticks, a defect
it had manufactured itself.

Cost: quarterly judge calls, and one more standard to keep current. If the
rubric stops discriminating, layer 2 says so by construction, because the
all-pass/all-fail check is mandatory and reported whether or not it removes
anything.

Reversal is deleting the rubric and this record; nothing depends on them yet.

## Implementation references

Leave this section empty when the decision is not enforced in code.

## Supersession

Supersedes: None
Superseded by: None
