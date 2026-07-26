# 2026-07-25 · Let runs write, and show the judge what they did

Change ID: `observable-run-evidence`
Created: `2026-07-25T15:00:43+09:00`
Status: Accepted

## Context

Eight of the rewritten expectations were not gradable. They concern what
survives the session and acts of inspection, and the harness could observe
neither: runs were nominally read-only, and the judge received only the response
text. A response asserting "I checked the changes" was indistinguishable from
one that had.

The judge said so itself during the pilot: *"grading it fairly requires the
transcript, which is not provided here."*

Granting that request directly would have ended the blinding. The transcript is
written by the model under test; in the pilot the treatment's names this skill
four times and the baseline's never does. `metrics.json` carries a `Skill` key
on one side only, and `timing.json` showed 312 seconds against 104.

## Options considered

1. **Keep runs read-only and drop the eight expectations.** Cheapest. Rejected
   because they are the ones aimed at this project's stated focus, and because
   the restriction did not hold anyway - a pilot run edited a file with the tool
   set nominally excluding it.
2. **Give the judge the transcript, and instruct it to ignore the tells.**
   Rejected. Blinding that depends on the judge choosing not to notice is not
   blinding, and it fails silently.
3. **Derived action log with a mechanical leak check.** Chosen.

## Decision

**Runs may write, with an identical capability set in both configurations.**
What survives a session cannot be measured if the run cannot produce it. The
symmetry is the load-bearing part: a capability the treatment has and the
baseline lacks would invalidate the comparison the way the language confound
invalidated the first one.

**The judge is shown a derived action log, never the transcript.** Tool calls
are reduced to an ordered list of `read` / `search` / `write` / `run` entries
with repository-relative targets. Entries only the treatment can produce are
dropped, and paths resolving outside the fixture are recorded as such rather
than by name. The log cannot editorialize, because it is built from tool calls
rather than written by the model under test.

**What the run changed is captured with its content**, not only its paths. A
path list says a record was written; it does not say whether the record is
usable, which is what the expectations actually ask.

**A leak check refuses to grade** rather than grading and hoping. If the
assembled evidence contains anything naming this project, the run is recorded
invalid with the reason.

## Consequences and reversal

Runs now cost more, because they do the work rather than describing it: the
validation run recorded 32 actions against 22, and roughly three times the
spend.

One leak is not closed. The response itself may name a risk tier or cite this
project's directories, and it cannot be altered without changing the artifact
under review. The judge is never told two configurations exist and is instructed
not to pass on vocabulary, but this is a residual, and the validation document
has to say so.

Allowing writes also moves this further from a text comparison. That boundary
was already crossed when fixtures were introduced; this states the move rather
than letting it drift.

Reversal is `git revert`. The action log would survive even if writes were
withdrawn, since it is derived independently of them.

## Implementation references

- `scripts/eval/run_skill_evals.py`
- `scripts/eval/grade_skill_evals.py`
- `tests/test_evals.py`

## Supersession

Supersedes: None
Superseded by: None
