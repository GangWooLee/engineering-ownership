# Skill evaluation

Status: Withdrawn
Checked: 2026-07-25
Superseded by: pending — a rebuilt evaluation is in progress

This document previously published a paired skill/baseline comparison. That
comparison is withdrawn. The measured numbers are preserved below together with
the reasons they cannot be defended, because deleting the record of a retracted
claim would itself be a documentation-integrity failure.

No replacement number is published yet. Until one is, this project makes **no
quantitative efficacy claim** for the skill.

## Withdrawn: initial paired comparison

Date run: 2026-07-23. Withdrawn: 2026-07-25.

The withdrawn result, quoted verbatim from the earlier version of this file:

| Configuration | Passed expectations |
| --- | ---: |
| With skill | 16 / 16 |
| Without skill | 5 / 16 |

The local benchmark artifact additionally reported this as `100%` versus `31%`,
a `+69%` delta.

### Why it is withdrawn

Six defects were found. Each was confirmed by inspection or execution, not
inferred.

1. **Language confound.** Every with-skill response was written in Korean and
   every baseline response in English. The two configurations therefore differed
   in language as well as in skill availability, so the delta cannot be
   attributed to the skill. Measured: 167 and 479 Hangul characters in the
   with-skill responses against 0 in both baseline responses.

2. **The grader was keyed to the skill's own vocabulary.** Assertions were
   graded by case-insensitive substring matching for tokens such as `R0`, `R2`,
   `R3`, `teach-back`, and `runbook`. A baseline that has never seen the skill
   cannot produce those tokens regardless of how well it reasons, so it could
   not pass on merit. The matcher also had no word boundaries: the synonym group
   `("lint", "link", "spell", "검사")` is satisfied by the ordinary English word
   *link*, and the group intended to detect optionality was satisfied by the
   Korean word `선택` inside `선택한 설계`, where it means *chosen*, not
   *optional*.

3. **Only half the evaluation set was graded.** `evals.json` defines eight
   evals; the grader implemented assertions for four and raised `ValueError` for
   the rest. The correct denominator is 8 evals x 4 expectations = **32**, not
   16. The published fraction used the wrong denominator.

4. **Four checks emitted a fixed evidence string regardless of outcome.** The
   committed artifacts therefore contain self-contradicting records such as
   `"passed": false` beside `"evidence": "The response explicitly names R2 or
   R3."` Any reader auditing those files by eye is told the opposite of the
   truth.

5. **Single run per configuration.** `runs_per_configuration` was 1, so no
   variance was measured and reported standard deviation was 0 by construction.
   This repository's own `CONTRIBUTING.md` states that a principle should be
   promoted "only after it survives repeated use"; a single sample does not meet
   the bar this project sets for its contributors.

6. **The result was graded against a criterion this project has since
   rejected.** The benchmark artifact names "required R3 teach-back" as the
   largest source of separation. The owner subsequently clarified that retained
   decision records, not a mandatory oral exam, are the intended default, and
   `docs/engineering/decisions/documentation-first-workflow.md` records that
   decision. The withdrawn number therefore does not merely predate the current
   design — it credits the skill for behavior the project deliberately removed.

### Two further limitations of that evaluation

These are not grading defects, but they bound what the result could ever have
shown.

- **It measured stated intent, not behavior.** Each run was a single turn of
  text with no repository and no tool use (`total_tool_calls: 0`,
  `transcript_chars: 0`). Proportionality, current-diff verification, and
  rollback discipline are execution properties that a description cannot
  demonstrate.

- **Timing and token costs were never measured.** The committed values were
  hardcoded zeros carrying the note "Unavailable from collaboration task
  notifications", and the benchmark reported `"n/a"` for both. No statement
  about the skill's cost was supported.

### Reproducibility status of the withdrawn result

The result cannot be regenerated from the committed grader. `grade_skill_evals.py`
points at a workspace directory (`iteration-2`) that does not exist, so it exits
with `FileNotFoundError`; and it has no branch for four of the eight evals. The
on-disk artifacts were produced by an earlier version of the grader and still
use the superseded eval name `teach-back-review-due`.

## Retained: documentation-first regression

The following observation is **not** withdrawn. It was a targeted live check,
reported qualitatively without a score, and it does not depend on the withdrawn
comparison.

After the owner clarified that retained decision records—not a mandatory oral
exam—are the intended default, the changed handoff/revisit scenario was run
against the revised local skill.

The first run correctly linked a change brief, ADR, and runbook and treated
review as optional, but still produced a provisional maturity score. The skill
was strengthened to prohibit translating artifacts, checks, review state, or
competency tags into a person score. A fresh run then:

- linked canonical records in the handoff;
- marked old verification as stale until refreshed;
- offered optional `explain` and review commands without blocking other work;
- recorded gaps and a revisit date;
- refused the requested maturity score and reported specific missing evidence.

This targeted live regression passed after one observed-and-fixed failure. It is
a single qualitative observation of one scenario, and it is not evidence of
efficacy relative to a baseline.

## What replaces it

A rebuilt evaluation is planned with the defects above addressed at the design
level rather than patched:

- one language (English) for both configurations, machine-enforced;
- behavior-based expectations that a baseline can pass on merit, with no
  requirement to emit the skill's private vocabulary;
- grading by an independent judge that never learns which configuration produced
  a response;
- at least three runs per configuration, reported as mean with standard
  deviation;
- all nine evals, with the denominator computed by the harness rather than
  written down by hand;
- real duration and token measurements taken from the runner;
- the full evaluation workspace committed to this repository so that a third
  party can audit the responses and the grading rather than trusting a summary.

Until those results exist and are committed, this file publishes no number.
