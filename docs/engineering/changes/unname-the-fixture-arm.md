# 2026-08-05 · Stop naming the arm in the directory the run lives in

Change ID: `unname-the-fixture-arm`
Created: `2026-08-05T22:29:07+09:00`
Risk: R2

## Problem and intended outcome

Each evaluation run is executed in a fixture directory named
`{overlay}-{configuration}-{index}`, and `build_fixture` sets the run's `HOME`
to that directory. Every `~` a run writes down expands to it, and anything the
run reports about its own filesystem quotes it. So the arm was written into the
one path most likely to appear in the judge-visible log, and two graded runs
reached their judge with `eval-7-without_skill-1` in it.

`close-arm-name-leak` fixed the recording side and named this as its next step,
because after that fix the name still held the answer and a scrub was the only
thing between the name and the judge. That scrub is a matcher over shell text
and has failed twice in three weeks: once on quoted tilde forms, once on paths
embedded after `=`.

Intended outcome: the fixture path stops being a function of the arm, so the
scrub stops being the only line of defence.

## Success and non-goals

Success is that the two arms of a run produce the same fixture path, that the
path contains no spelling of a configuration name, and that reverting either the
helper or its call site fails the suite. The last of those could have gone the
other way, and did on the first attempt — a guard on the helper alone passed
while the call site was reverted to the interpolation that caused the leak.

Non-goals: re-running the sweep; changing where run outputs are written, which
do encode the arm and are not judge-visible; touching the redaction pass or the
tell list, both of which stay as the second line.

## Existing responsibilities searched

`JudgeBlindingCase` already owns "the judge must not be able to infer which
configuration it is grading", so the new guards join it rather than starting a
class. The path was constructed inline at one call site and nowhere else --
`grep` for `{configuration}` across `scripts/` and `tests/` returns that line
and two print statements -- so extracting it into a named function created one
place to guard rather than moving a problem around.

`build_fixture.build` already owns clearing a destination before building. That
is what makes a shared path safe, so nothing new was written for it.

## System and data flow

`fixture_dir(scratch, overlay, index)` returns `scratch / f"{overlay}-{index}"`.
It does not take the configuration, so it cannot encode it. The sweep calls it
where it previously interpolated.

Both arms of the same `(overlay, index)` now resolve to one directory, used one
after the other inside the run loop. `build_fixture.build` removes an existing
destination before building, so the second arm starts clean regardless of
whether the first arm's cleanup succeeded.

The arm remains in `eval_dir / configuration / run-N`, which is where outputs
are written and which the judge never reads.

## Decisions and trade-offs

The full decision is in
[`unname-the-fixture-arm`](../decisions/unname-the-fixture-arm.md). Hashing the
configuration into the name was the close alternative and was rejected because
a hash is still a function of the arm: identical inputs would still land in
different directories, so the channel survives while looking closed.

## Failure, security, and recovery

The failure mode this introduces is two arms colliding on one path. It is
prevented by construction rather than by ordering: the destination is cleared
before each build, so a failed cleanup after the first arm cannot leak state
into the second. The runs are sequential in any case.

The second failure mode is the guard being theatre. It was, at first. A case
that checked only `fixture_dir` passed while the call site was reverted, because
the helper it checked was no longer the thing building the path. The suite now
also reads the source and refuses a filesystem path interpolating
`{configuration}`, and asserts the sweep still calls `fixture_dir` -- otherwise
the first check guards a function nothing uses.

Recovery is one line at the call site. The guard fails on exactly that.

## Verification evidence

Runtime, without a sweep. `build_fixture` needs no model call, so the fixture
this change affects was actually built and inspected.

| Check | Result |
| --- | --- |
| Path per arm | `with_skill` and `without_skill` both resolve to `eval-7-1`; one distinct path |
| Arm name in the path | None, for either spelling |
| Fixture actually built | 66 files created at `.../engo-probe-*/eval-7-1`; that path is the run's `HOME` |
| The token shape that leaked, recorded from inside it | `MEMFILE="~/…"` → `MEMFILE=(outside the repository) cat "$MEMFILE"`; `D=<fixture> find …` → `D=(outside the repository) find "$D" -type f \| sort`. No arm name in either |
| Sequential reuse of the shared path | Rebuilt into the same directory; 66 files, no collision, no residue |
| Guard proved by breaking it, helper | Restoring `{configuration}` inside `fixture_dir` fails `test_the_fixture_directory_does_not_name_the_arm` |
| Guard proved by breaking it, call site | Restoring the interpolation at the call site while leaving `fixture_dir` intact fails `test_no_run_directory_is_built_by_interpolating_the_arm` |
| First version of the call-site guard | Did **not** exist; the helper-only guard passed on a reverted call site. Recorded rather than quietly added |
| Suite | 97 tests |
| Contract commands | Recorded via `engineering verify` |

## Known limits and learning gaps

- **No sweep has run under this change.** The fixture was built and inspected,
  and the run loop's use of the path is one line, but no model has executed
  inside the renamed directory. The first live sweep is where a surprise would
  appear.
- The guard reads source text for the offending shape. It catches
  `{configuration}` interpolated into a path. It would not catch the arm reaching
  a path by another name -- a variable assigned from `configuration` first, for
  instance.
- Two arms sharing a directory is safe because `build_fixture.build` clears it.
  Nothing asserts that property; if that clearing were removed, this change would
  become a contamination risk and no test here would say so.
- The overlay name is still in the path. Both arms share it, so it identifies the
  scenario and not the condition, but it is a name in a place names have already
  caused trouble.

## References

- [`unname-the-fixture-arm`](../decisions/unname-the-fixture-arm.md) -- the decision
- `docs/engineering/changes/close-arm-name-leak.md` -- the recording-side fix
  that named this as its next step
- `scripts/eval/run_skill_evals.py`, `scripts/eval/build_fixture.py`,
  `tests/test_evals.py`
