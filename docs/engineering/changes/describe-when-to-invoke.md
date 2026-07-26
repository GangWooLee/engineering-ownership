# 2026-07-25 · Describe when to invoke the skill, and measure whether it does

Change ID: `describe-when-to-invoke`
Created: `2026-07-25T16:21:15+09:00`
Risk: R2
Status: Completed

## Problem and intended outcome

The skill engaged in none of seven runs on a repository without its own config
directory, and in both runs on one that has it. The description is the only text
a model reads when deciding whether to consult a skill, so this was a question
about that text.

The router lists setup as its first and highest-priority intent - "no
`.engineering/contract.json`, or the user asks to adopt the workflow" - while the
description named none of setup, adopt, contract, configure, initialize, onboard,
or unfamiliar. On the population that failed, the only intent that could apply
was the one the selection-time text never mentioned.

The intended outcome is a description that is consulted when it should be, left
alone when it should not, and a measurement that can tell the difference.

## Success and non-goals

Success is all three pre-registered criteria: the positive interval clears the
prior upper bound of 0.41, the negative interval stays below 0.5, and engagement
on an already-configured repository does not regress.

Not a goal: showing that the skill *helps*. A trigger rate says whether it runs,
never how well. The efficacy question is still open and still needs a repository
where the treatment engages - which, until this change, did not exist for the
unmanaged case.

## Existing responsibilities searched

The probe schema follows the one shipped with `skill-creator`; its runner was not
reused, because it measures a synthetic slash-command stand-in rather than the
plugin and writes into the repository under test. The interval arithmetic is
imported from `summarize_trigger_rate.py` rather than reimplemented.

The description was rewritten against six structural patterns extracted from
twenty-five installed skill descriptions, not invented. The rules and the corpus
evidence are recorded in the decision record.

## System and data flow

`triggers.json` carries labelled probes. `run_trigger_probes.py` builds a fixture
on a named base, runs the treatment only - the baseline cannot invoke a skill it
was not given - and records whether the `Skill` tool was used.
`summarize_trigger_probes.py` reports both directions with exact intervals.

Runs are keyed by a digest of the description they measured. Without that, runs
from either side of a rewrite pool silently and answer a question nobody asked.

## Decisions and trade-offs

Recorded in `docs/engineering/decisions/describe-when-to-invoke.md`. The
load-bearing one is that the probes were written and committed before the
description was touched, so the ordering is checkable in history rather than
asserted. For a single author writing both the text and its test, that is the
only defence available.

## Failure, security, and recovery

Probe runs use the same containment as the evaluation runs: a fresh fixture per
run built outside this repository and removed afterwards, no network, and a tool
allowlist. Nothing here ships; `build_release.py` packages only the plugin
directory, and `triggers.json` ships with it as documentation of intended
triggering.

Rollback is `git revert` of the description commit. The probes and harness would
survive and would then measure the restored text.

## Verification evidence

All three pre-registered criteria pass. The bars were fixed in
`summarize_trigger_probes.py` before any run against the new text.

| Repository | Class | Engaged | 95% interval | Criterion | Result |
| --- | --- | ---: | --- | --- | --- |
| unmanaged | should trigger | 16/17 | [0.71, 1.00] | lower bound above 0.41 | pass |
| unmanaged | should not | 0/12 | [0.00, 0.27] | upper bound below 0.5 | pass |
| managed | should trigger | 6/6 | [0.54, 1.00] | no regression | pass |
| managed | should not | 0/6 | [0.00, 0.46] | upper bound below 0.5 | pass |

Against the same question before this change: 0 of 7 on an unmanaged repository,
interval [0, 0.41]. Those runs used the capability prompts rather than these
probes, so this is two measurements of one question and not a paired comparison
of one prompt - which is why the criterion was written as an absolute bar rather
than a difference.

**The held-out half passes on its own**, measured once after train:

| Class | Engaged | 95% interval | Result |
| --- | ---: | --- | --- |
| should trigger | 5/5 | [0.48, 1.00] | clears 0.41 |
| should not | 0/6 | [0.00, 0.46] | stays under 0.5 |

The description was revised once and measured once. No selection across attempts
took place, so the test figure is not inflated by picking the best of several -
the bias the split was there to bound did not arise. Its lower bound of 0.48
clears the bar by a small margin on five usable runs, which is thin, and the
interval is the honest form of it.

Contract commands, run against the final tree:

- `python3 -m unittest discover -s tests`: 68 tests pass.
- `python3 scripts/validate_distribution.py`: passed.
- `claude plugin validate --strict .`: passed.
- `python3 scripts/build_release.py --version 0.2.1`: built.

The description is 954 of 1024 characters, ASCII, no angle brackets.

Measured usage for the whole evaluation effort to date is about $38, of which
roughly $22 is this change's probe runs.

Three new guards were each given a violation and observed rejecting it: a
description with angle brackets, one over the 1024 character limit, and a probe
set with its negatives removed. Two more were added after the run and likewise
exercised: a failed run recorded without a reason, and runs mixing more than one
description digest.

## Known limits and learning gaps

**A waiting loop of mine idled for three hours and twenty-one minutes.** It
matched processes by name with `pgrep -f "run_trigger_probes.py"`, and the
waiting shell's own command line contains that string, so the condition could
never become false. Two shells spun until they were killed, and the managed-base
regression run queued behind one of them never started.

This is the exact failure the owner's own working rules name - "must exclude its
own PID when matching processes" - and an earlier wait in this same session, on
a specific PID with `kill -0`, worked correctly. Switching to a name pattern for
convenience reintroduced it. The fix was not a better pattern but removing the
waiter: the runner is backgrounded directly and the harness reports its exit, so
there is nothing left to match against.

**Six runs produced no result — five lost to rate limiting, one to a
timeout — and the harness could not say so.** (Corrected 2026-07-26: this
heading originally said "eight runs", contradicting `iteration-6/PILOT.md`.)
They failed three seconds apart while successful runs were fifteen to twenty
seconds apart, and the same probes succeeded on retry. The runner had been
discarding the failure detail, so diagnosing it meant reproducing the failures by
hand. Detail is now retained, runs are spaced, and a test rejects a recorded
failure that carries no reason.

The first hypothesis for those failures - that a run ending in a clarifying
question exits non-zero - was wrong, and testing it directly is what showed that.

**One probe is ill-posed against its fixture.** `Fix the typo in the README
heading` presupposes a typo the unmanaged base does not contain, so the agent
correctly looks, finds none, and asks. It is an unscored probe and does not touch
any verdict. It has deliberately not been corrected: the probe set was frozen
before the description was written, and editing it now would spend the only
guarantee this design has.

**Five unscored runs still have no result** from the rate-limited stretch. They
are recorded as unusable rather than as non-engagement.

**The samples are small.** Three runs per probe, and the test half is smaller
still. Intervals are reported throughout rather than point estimates, and the
test score is biased by having selected on train.

## References

- Decision record: `docs/engineering/decisions/describe-when-to-invoke.md`
- Probes: `plugins/engineering-ownership/skills/engineering-ownership/evals/triggers.json`
- Runs: `engineering-ownership-workspace/iteration-6/triggers/`
- The measurement this responds to: `docs/engineering/changes/separate-fixture-from-answer-key.md`
