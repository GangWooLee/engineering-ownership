# 2026-08-05 · Stop naming the arm in the directory the run lives in

Change ID: `unname-the-fixture-arm`
Created: `2026-08-05T22:29:07+09:00`
Status: Accepted

## Context

Each evaluation run executes in a fixture directory named
`{overlay}-{configuration}-{index}`, and the run's `HOME` is set to that
directory. The arm was therefore written into the one path a run quotes whenever
it says anything about its own filesystem, and two graded runs reached their
judge with that path in the action log.

`close-arm-name-leak` closed the recording hole: a path embedded inside a token
is now normalized, and the arm names are in the tell list. That change named
this one as its own next step, because the deeper cause was still in place — the
name still held the answer, and only a scrub stood between it and the judge.
That scrub has had two holes in three weeks.

## Options considered

**A. Leave it.** The redaction pass is fixed and the tell list now sees the
class, so nothing should reach the judge unscrubbed.

**B. Hash the configuration into the name.** `{overlay}-{index}-{hash}` keeps
the arms in separate directories and makes the name unreadable.

**C. Drop the configuration from the name.** Both arms of a run share one
directory, used one after the other.

**D. Randomize per run.** A uuid or timestamp per run directory.

## Decision

**C.**

A was rejected on the record of the scrub itself. It is the only thing standing
between the name and the judge, it is a matcher over shell text, and it has
failed twice — once on quoted tilde forms, once on paths embedded after `=`. A
third shape is a matter of time. A name that never held the answer cannot leak
it, and that property does not depend on a matcher being complete.

B keeps a mapping from arm to directory. It is unreadable to a judge but it is
still a function of the configuration, so it is still a channel: identical
inputs land in different places, and anything comparing paths across runs can
recover the split. Obscuring a signal is weaker than not producing one.

D removes the signal and also removes the one thing the name is genuinely useful
for — telling, from a scratch directory left behind by an interrupted sweep,
which scenario and run it belongs to.

C keeps that and removes only the part the filesystem never needed. The arm is
still recorded, in the output directory the judge does not read.

## Consequences and reversal

Both arms of the same `(overlay, index)` now use one path, one after the other.
This is safe by construction rather than by timing: `build_fixture.build`
removes an existing destination before building, so the second arm cannot
inherit anything from the first even if the earlier cleanup failed.

A scratch directory left behind by an interrupted sweep no longer says which arm
was running when it stopped. The run output directory does.

The guard lives in two parts, because one part alone is not a guard: the helper
must not produce a path naming the arm, and the sweep must actually build its
fixture through that helper. The first version checked only the helper, and
passed while the call site was reverted to the interpolation that caused the
original leak.

Reversal is restoring the interpolation at the call site. The guard fails on
exactly that, which is the point.

## Implementation references

- `scripts/eval/run_skill_evals.py` -- `fixture_dir` and its single call site
- `tests/test_evals.py` -- `JudgeBlindingCase.test_the_fixture_directory_does_not_name_the_arm`
  and `test_no_run_directory_is_built_by_interpolating_the_arm`

## Supersession

Supersedes: None
Superseded by: None
