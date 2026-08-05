# 2026-08-05 · Close the arm-name leak the redaction pass and its guard both missed

Change ID: `close-arm-name-leak`
Created: `2026-08-05T22:03:46+09:00`
Status: Accepted

## Context

Two graded runs in the iteration-8 sweep reached their judge with the string
`eval-7-without_skill-1` in the judge-visible action log. The fixture directory
is named `{overlay}-{configuration}-{index}`, so its name states the arm; a shell
token of the form `D=/abs/path/...` carried it into the log because the
normalization pass only recognized paths at the start of a token; and the leak
predicate that should have objected did not contain the arm names.

Four more such logs are already published in `iteration-3` and `iteration-5`.
The defect is not new, only newly noticed.

Excluding the two graded runs moves the baseline from 0.5648 to 0.5700 and the
reported difference from 0.1512 to 0.1460 -- same direction, same magnitude. So
the question is not whether the experiment survives. It is what to do with
artifacts that are, as recorded, evidence of a compromised blind.

## Options considered

**A. Rewrite the six action logs so they no longer name the arm.** The guard
goes green, the published corpus looks clean, and nothing about the reported
numbers changes.

**B. Delete the six runs and re-collect them.** The corpus becomes clean by
construction and the figures are recomputed from runs that were genuinely blind.

**C. Drop the six runs from the published figures but keep the artifacts.**
The numbers describe only clean runs; the leaked runs stay as evidence.

**D. Keep the artifacts and the figures as collected, pin the six runs in the
guard as known leaks, and disclose the defect and its numeric impact wherever
the figures are reported.**

## Decision

**D.**

A is falsification. The action log is the judge's recorded input; editing it
after grading makes the artifact say the judge saw something it did not. A
repository whose subject is evidence discipline cannot make its evidence agree
with its guard by editing the evidence.

B costs a re-collection to move a result by 0.005. The pre-registered analysis
does not turn on that margin, and re-running two arms to change a number in the
fourth decimal buys precision nobody needs while creating a new confound: the
plugin has changed since the sweep.

C is defensible and was close. It was rejected because dropping runs after
seeing them is a researcher degree of freedom, and the exclusion rule would have
been written after the results were known. Reporting as collected, with the
excluded-subset figure stated alongside, gives a reader both numbers and hides
neither.

D's cost is that a guard passes while six known-bad artifacts sit in the tree.
That cost is paid by making the exception list explicit and testable: a pinned
run that stops leaking fails the test, so the list cannot rot into a permanent
suppression.

## Consequences and reversal

The leak is closed at the recording layer, not just at the guard: a path
embedded inside a token is now normalized, so a future run cannot record the
form that leaked. The tell list now contains the arm names, which makes the
class visible to the grader's refusal path and to the suite.

The fixture directory still encodes the configuration in its name. That is the
deepest cause and it is deliberately left alone here, because changing the run
layout cannot be verified without a live sweep and this change is verified
without one. It is recorded as the named next step.

Two nets are still one net. The grader's refusal and the test guard both call
`blinding_leaks`, so a gap in the predicate disables both. The
`fix-blinding-redaction` record describes them as independent; that description
is now wrong and is corrected there.

Reversal is reverting two functions and one frozenset. The disclosures would
then describe a state that no longer holds, so they are reverted together.

## Implementation references

- `scripts/eval/run_skill_evals.py` -- embedded-path normalization in
  `action_target.relative`
- `scripts/eval/grade_skill_evals.py` -- `BLINDING_TELLS`
- `tests/test_evals.py` -- `JudgeBlindingCase.KNOWN_ARM_LEAKS` and the
  tracked-file enumeration
- `.gitignore` -- the abandoned run's data

## Supersession

Supersedes: None
Superseded by: None
