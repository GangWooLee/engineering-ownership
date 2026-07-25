# 2026-07-25 · Separate the fixture from the answer key

Change ID: `separate-fixture-from-answer-key`
Created: `2026-07-25T15:23:56+09:00`
Risk: R1
Status: Completed

## Problem and intended outcome

The previous change noted that the baseline had performed the maintenance
behaviour as well as the treatment, and suspected the fixture rather than the
skill. That suspicion was checkable, so it was checked.

It was correct, and worse than suspected. The fixture's decision document
matched this skill's own template section for section - six of six - including a
`## Supersession` block reading `Supersedes: None / Superseded by: None`. That is
a fill-in-the-blank for the exact expectation the scenario grades. The fixture
was not a repository that happened to practise the discipline; it was this
skill's output, handed to both arms as a worked example.

The intended outcome is that a scenario asking whether the skill *produces* a
discipline starts from a repository that does not already carry it, and that the
distinction cannot quietly erode.

## Success and non-goals

Success is a second fixture base with ordinary engineering conventions and none
of this skill's artifacts, the scenarios that ask about producing discipline
moved onto it, and a test that fails if this skill's template fields appear
there.

Not a goal: removing this skill's artifacts from every fixture. A repository
already using the skill is the realistic adoption case, and a scenario asking
whether the skill helps *inside* such a repository is right to start there. The
defect was using one base for both questions without saying so.

## Existing responsibilities searched

`build_fixture.py` already materialized a base plus optional settled and working
layers, so this adds per-overlay base selection rather than a second builder. The
`unmanaged` base reuses the same source files and tests as the managed one, so
the only variable between them is documentation convention.

## System and data flow

`recipe.json` now declares two bases and records, in prose, which question each
is correct for. An overlay names the base it starts from.

- `base` - a repository this skill manages: contract, evidence records, and
  decision documents in its template.
- `unmanaged` - the same service with a plain dated design note in
  `docs/decisions/`, a `CONTRIBUTING.md` convention, and no supersession fields
  to fill in. The note states its own assumption in prose, so recognising that
  the request contradicts it is a judgment rather than bookkeeping.

The ninth scenario and the unfamiliar-repository scenario moved to `unmanaged`.

## Decisions and trade-offs

**Two bases, not one sanitized base.** Stripping this skill's artifacts
everywhere would have made every scenario ask the same question and lost the
adoption case, which is the one most users are actually in.

**The design note states its assumption rather than carrying a field.** A field
can be filled in without understanding; prose has to be read. The trade-off is
that grading now depends on the judge recognising the contradiction, which is why
the note names the condition explicitly.

## Failure, security, and recovery

Fixture data only. Nothing ships; `build_release.py` packages only
`plugins/engineering-ownership/**`. Rollback is `git revert`.

## Verification evidence

- `python3 -m unittest discover -s tests`: 61 tests pass.
- The new guard was given a `Superseded by:` line in the unmanaged base and
  observed rejecting it, then restored.
- Both fixtures rebuild deterministically; the unmanaged one produces a clean
  tree with the decision implemented and its tests passing.

The measurement itself, `engineering-ownership-workspace/iteration-4` against
`iteration-3`. The pass rates are not comparable - an expectation was split
between the runs, so the denominators differ - but `skill_loaded` is:

| Base | treatment | baseline | skill actually invoked |
| --- | --- | --- | --- |
| managed | 4/4 | 3/4 | yes |
| unmanaged | 1/5 | 2/5 | **no** |

## Known limits and learning gaps

**The check did not answer its own question, and found something larger.** On the
unmanaged repository the skill never engaged. `skill_loaded` is false for the
treatment while the preflight in the same iteration records the plugin loaded and
the skill visible, so this is not availability. The treatment took three actions
and wrote nothing; the baseline took thirteen and wrote three files.

So how much of `iteration-3`'s result came from the fixture is still unmeasured.
There was nothing to compare on the unmanaged base, because the skill was not
part of the run.

**This is one observation.** It should be repeated before anything is concluded
from it. What makes it worth recording is that it was visible: the runner tracks
whether the skill was actually invoked, so a run where the treatment did not take
is distinguishable from one where it took and did not help. Any future reporting
has to separate those two, or a non-triggering run will silently dilute a mean.

**If it holds, it is a finding about the skill, not the evaluation.** The skill's
own routing lists setup - "no `.engineering/contract.json`, or the user asks to
adopt the workflow" - as one of its intents, and an unmanaged repository asked
for a change is exactly that case. Under-triggering there would mean the skill is
quietest in the repositories that have not adopted it. That belongs in its own
investigation with repeated runs, not in this change.

## References

- The suspicion this checked: `docs/engineering/changes/observable-run-evidence.md`
- Measurement: `engineering-ownership-workspace/iteration-4/PILOT.md`
- Fixture declarations: `scripts/eval/fixtures/recipe.json`
