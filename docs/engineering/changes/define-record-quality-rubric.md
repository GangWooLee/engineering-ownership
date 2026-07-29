# 2026-07-29 · Define how record quality is measured

Change ID: `define-record-quality-rubric`
Created: `2026-07-29T17:04:23+09:00`
Risk: R1

## Problem and intended outcome

Fifty-six records exist and their quality has only ever been asserted. Two audits
found specific, repeated defects — corrections sitting below the claims they
withdraw, terms whose first use explains nothing, headings that name the template
rather than the record — but there was no standard to measure against, so
"better" had no meaning.

Intended outcome: a written standard, validated before anything is automated,
that says what is measured, how, and how each item announces it has stopped
working.

## Success and non-goals

Success: a rubric document with every layer-1 item measured against all 56
records before admission, and an ADR recording why the layers are split the way
they are.

Non-goals: producing any score (that is the dry run and the grading pass);
writing any code; changing any existing record. This change adds a standard and
nothing else.

## Existing responsibilities searched

The four rules are not new: they are the skill-evaluation guards in
`tests/test_evals.py` — no private vocabulary, silence never passes,
discrimination required, per-item reporting — applied to records instead of
evals. The rubric's home reuses the `docs/validation/` `Status:` / `Checked:`
convention and its test-enforced index rather than creating a document in a
directory nothing watches, which a readability review identified as the way
glossaries go stale here.

## System and data flow

No runtime path. The rubric is read by a future dry run, then by a test file,
then by a grader — each of which is a separate change.

## Decisions and trade-offs

See `docs/engineering/decisions/define-record-quality-rubric.md`. The
substantive one: the "delete non-discriminating items" rule is scoped to the
scored layer, because a guard that has not fired is a tripwire rather than a
constant diluting a denominator.

## Failure, security, and recovery

The failure mode is a standard that measures nothing while appearing rigorous.
Two things guard it: every layer-1 item carries the violation count that
admitted it, and layer 2's all-pass/all-fail check is mandatory and reported
each round whether or not it removes anything. Recovery is deleting the rubric —
nothing depends on it yet.

No security surface: documentation only, no code, no data.

## Verification evidence

Each layer-1 candidate was run against all 56 records before admission:

| Candidate | Violations | Outcome |
| --- | ---: | --- |
| Correction without a header marker | 3 / 56 | admitted |
| `Status: In progress` after close | 4 / 56 | admitted |
| Dead relative links | 0 / 56 | admitted as a tripwire |
| `fill-required` remaining | 0 / 56 | rejected — `check` already blocks it |
| Empty template sections | 0 / 56 | rejected — same |
| Term first use links to a definition | 52 / 56 would fail | rejected as a guard; kept as a layer-2 expectation |

The four stale statuses were cross-checked against `.engineering/evidence/`: all
22 evidence records are closed, so all four are contradictions rather than
history.

## Known limits and learning gaps

- The rubric has not been dry-run. Nothing here is known to discriminate in
  practice; that is the next change, and it is deliberately not this one.
- Layer 2's dimensions were written against defects found in this corpus. They
  may not generalise to a repository whose records fail differently.
- The dead-link guard's first implementation manufactured a defect by ignoring
  code spans, flagging a link inside backticks. Fixed before admission, and
  recorded in the rubric as the reason every item must be run over the corpus
  first.
- This record's own ADR is not in the evidence record's artifact map: at R1 the
  tier allocates no decision document, so `explain` will not mention it. Same
  product gap recorded in `declare-english-canonical`; noted again rather than
  worked around by inflating the risk tier to obtain a file.

## References

- `docs/validation/record-quality-rubric.md`
- `docs/engineering/decisions/define-record-quality-rubric.md`
