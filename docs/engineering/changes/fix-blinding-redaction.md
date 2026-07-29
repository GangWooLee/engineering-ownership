# 2026-07-25 · Close quoting evasions in the judge-visible action log

Change ID: `fix-blinding-redaction`
Created: `2026-07-25T23:47:42+09:00`
Risk: R2
Corrected: 2026-07-26 — References said the quarantined runs were re-queued for
the next sweep; that iteration was abandoned the same day and they are not kept.

## Problem and intended outcome

A live iteration-7 sweep recorded `cat ~/engineering-ownership/.../references/start.md`
verbatim into eight with-skill action logs. The action log is the judge's view of
what a run did; the runner's own directory name identifies the configuration, so
every one of those runs is inadmissible. `JudgeBlindingCase` caught it — the guard
works; the redaction in front of it had holes.

Two distinct facts. First, the eight recorded leaks came from a stale process:
the sweep had imported the runner before the bare-tilde defense landed, so the
on-disk code already handles the recorded forms. Second, replaying evasion forms
against the current code exposed a real remaining hole: shell quoting.
`cat "~/engineering-ownership/x.md"` passed through untouched, because the token
starts with a quote, is not absolute, and resolves nowhere — `relative()` fell
through to returning the raw token. `$HOME/...` failed the same way.

Intended outcome: no shell-quoting form of the runner's location reaches a
judge-visible target, including forms not anticipated here.

## Success and non-goals

Success: the full suite passes including a regression test that drives
`action_target` + `redact` over bare, quoted, `$HOME`, absolute, flag, and
in-fixture-filename forms of the runner location; replaying the eight
quarantined leak commands through the fixed code yields zero residual leaks.

Non-goals: scrubbing the response, transcript, or fixture contents. Those are
agent-authored material; altering them would distort what is graded. A run whose
own response names the skill is inadmissible by the grader's refusal check, not
silently rewritten.

## Existing responsibilities searched

The token normalization already lived in `action_target.relative()`; it was
extended rather than duplicated. The backstop was placed in `action_target`
itself, not in `redact()`, because `redact()` also runs over transcripts and
fixture deltas where replacing the repository name would rewrite agent-authored
content (see non-goals).

## System and data flow

`parse_stream` → `action_target(name, input, cwd)` → `redact(...)` →
`actions.json` → judge bundle. The fix narrows what survives the second step:
tokens are stripped of surrounding quotes before the path check, `$`-prefixed
tokens are treated as outside the fixture, and any target still carrying
`ROOT.name` after the token pass is scrubbed wholesale.

## Decisions and trade-offs

See `docs/engineering/decisions/fix-blinding-redaction.md` — enumerate-and-catch
versus name-based backstop; both are used, in that order.

## Failure, security, and recovery

Failure mode if this regresses: contaminated runs are recorded, caught by
`JudgeBlindingCase` at test time and by the grader's leak refusal at grading
time — two independent nets behind this fix. Recovery for already-recorded
contamination is quarantine and re-run (`--resume` re-runs any run directory
that was moved out), exercised today for eight runs now in `/tmp/eo-quarantine/`.

## Verification evidence

- `python3 -m unittest discover -s tests`: 71 tests pass (70 pre-existing after
  quarantine, 1 new: `test_action_targets_never_carry_the_runner_location`).
- Replay: the eight quarantined leak commands passed through the fixed
  `action_target` + `redact` produce zero targets containing the runner name.

## Known limits and learning gaps

The stale-process hazard is untouched: a sweep launched before a redaction fix
keeps the old code in memory for its whole life. The mitigation is operational,
not code — stop the sweep before changing the runner, restart with `--resume`.

## References

- `scripts/eval/run_skill_evals.py` — `action_target`
- `tests/test_evals.py` — `JudgeBlindingCase.test_action_targets_never_carry_the_runner_location`
- Quarantine: 8 runs moved out of `iteration-7` to a temporary directory
  outside the repository. (Corrected 2026-07-26: this line originally said
  they were "re-queued for the next sweep by removal". They are not —
  `iteration-7` was abandoned the same day because the plugin changed
  mid-sweep, so the replacement iteration starts from scratch and these runs
  are not preserved. The claim that replaying their commands through the
  fixed normalization yields zero leaks was executed and recorded above; it
  does not depend on the files still existing.)
