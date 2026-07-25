# How often the skill engages on a repository it does not manage

Three runs per configuration on two scenarios that both start from the
unmanaged base. Run to answer one question `iteration-4` could not: whether a
single non-engagement was the skill under-triggering or one unlucky sample.

## What was fixed before the runs started

The decision rule was written down before the runs finished, so that the bar
could not be chosen to suit the result: the treatment runs on every
unmanaged-base scenario are read as one sample, and under-triggering counts as
reproduced only if the 95% interval excludes a coin-flip trigger rate.

Pooling is what makes three runs usable. A 0/3 result carries a 95% interval of
[0, 0.71] and rules out almost nothing; the same rate over six runs gives
[0, 0.46]. The assumption pooling buys this with is that the two scenarios share
a trigger rate. They exercise different routes - `eval-5` asks in so many words
for a process to be set up, `eval-9` is a plain change request - but the
hypothesis under test is about the kind of repository, not about either route.

## What the runs recorded

| Scenario | Configuration | Engaged | Turns | Files written |
| --- | --- | --- | --- | --- |
| `eval-5` | treatment | 0 / 3 | 21, 24, 21 | 4, 5, 4 |
| `eval-5` | baseline | 0 / 3 | 21, 21, 25 | 2, 2, 4 |
| `eval-9` | treatment | 0 / 3 | 13, 6, 6 | 3, 0, 0 |
| `eval-9` | baseline | 0 / 3 | 16, 13, 8 | 3, 3, 0 |

Pooled treatment: **0 of 6**, 95% interval [0, 0.46]. With `iteration-4`'s run
on the same base, 0 of 7, [0, 0.41]. Every run completed; none errored, so the
denominator is not a survivor of dropped runs.

The preflight in this iteration records the plugin loaded and the skill visible,
as it did in `iteration-4`. That is now the third independent check that this is
not an availability problem.

Engagement is read from the `Skill` tool call alone. As a check that the finding
is not an artefact of that narrow signal, the action logs were searched for any
run reaching the skill by another route - reading the plugin directly, or
touching anything outside the fixture. One action in one baseline run leaves the
fixture, and it is a `python3 -c` invocation, not a read of the skill.

## What this does and does not establish

It establishes that on a repository carrying ordinary engineering conventions
and none of this skill's artifacts, the skill does not reliably engage. It does
not establish a rate of zero: six runs are consistent with a true rate up to
about 46%, and the interval is the honest form of the result.

It says nothing about whether the skill helps. A run where the skill never
loaded cannot be evidence about what the skill does, which is the same reason
`iteration-4` could not size the fixture confound it was built to size. That
question is still open and still needs a repository where the treatment engages.

Two observations that are visible here but are not measurements. On `eval-5` the
treatment wrote more files than the baseline in every pair, and on `eval-9` two
treatment runs stopped to ask which partner was meant rather than writing
anything - but a baseline run did that too. Neither pattern is attributable to
the skill, because the skill was not part of any of these runs.

## The scenarios are not equally hard

`eval-9` is a plain change request, and reaching the skill from it requires
recognising the work as the kind the skill is for. `eval-5` asks directly to set
up an engineering process for an unfamiliar repository, which is the case the
router's own `setup` intent names. The skill not engaging on `eval-5` is the
stronger half of this result: it is the easiest trigger the scenario set has.
