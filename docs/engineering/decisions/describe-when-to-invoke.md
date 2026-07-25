# 2026-07-25 · Describe when to invoke the skill, and measure whether it does

Change ID: `describe-when-to-invoke`
Created: `2026-07-25T16:21:15+09:00`
Status: Accepted

## Context

The skill engaged in none of seven runs on a repository without its own config
directory, and in both runs on one that has it. The description is the only text
a model reads when deciding whether to consult a skill, so this is a question
about that text.

Its router lists setup as its first and highest-priority intent - "no
`.engineering/contract.json`, or the user asks to adopt the workflow" - while the
description named none of setup, adopt, contract, configure, initialize, onboard,
or unfamiliar. On the population that failed, the only intent that could apply
was the one the selection-time text never mentioned.

Two things had to be decided together: what the description should say, and how
to know whether saying it worked. The second is the harder one, because the same
person writes the text and the test.

## Options considered

1. **Rewrite and check it fires on the failing scenarios.** Rejected. Those
   scenarios were already in hand, so a description written against them proves
   only that it was written against them.
2. **Rewrite, then measure on the capability evals.** Rejected for a subtler
   reason: every eval in that manifest is an implicit positive. A measurement
   over positives alone reports recall with no precision term, so a description
   that fired on everything would score perfectly - which is exactly the failure
   mode a pushier description risks.
3. **Freeze a labelled probe set first, then rewrite against a training half.**
   Chosen.

## Decision

**Write the probes before the description, and commit them first**, so the
ordering is checkable in history rather than asserted. This is the only defence
available to a single author against writing the test around the answer.

**Give the probe set a negative class**, drawn as near misses that share the
domain's vocabulary while asking for no change to the repository. An obviously
unrelated probe is a free pass and measures nothing.

**Leave documentation-only edits unscored.** The router says not to create a
change record "merely because this skill was invoked", which presumes invocation
may happen and asks for restraint afterwards. The project has not decided that
invoking on such an edit is wrong, and scoring an undecided case as a failure
would be scoring an ambiguity rather than a defect.

**Split train and test in the file rather than computing it**, so it cannot
drift, and revise against train only.

**Key every run by a digest of the description it measured.** A trigger rate is a
property of a description. Without this, runs from either side of a rewrite pool
silently and answer a question nobody asked.

**Fix the pass criteria before running**: the positive interval must clear the
prior upper bound of 0.41; the negative interval must stay below 0.5; engagement
on an already-configured repository must not regress.

For the text itself: open on the user's situation rather than the skill's
outputs; name signals the model can check, including the config file and an
unfinished diff; carry literal phrasings with a generalizing clause; say when in
the turn to consult it; mark the boundary against a debugging skill.

Remove the four-stage workflow summary, the risk-tier vocabulary that is only
defined after loading, and the closing instruction to keep documentation edits
light - which was the only imperative in the text, pointed away from invoking,
occupied the most emphatic position, and defended against over-triggering that
measurement shows does not occur.

## Consequences and reversal

The description grew from 391 to 954 characters, within the 1024 limit. Length
was never the constraint; the previous text used a third of what was available.

Removing the risk-tier vocabulary from the description means a reader of the
frontmatter alone no longer sees the R0-R3 model. That model is unchanged and
still governs the work; it is now introduced where it is defined rather than
where it cannot be evaluated.

The probe set is small. Three runs per probe cannot settle much on their own,
which is why intervals are reported rather than point estimates, and why the test
half is measured once at the end and its score disclosed as optimistically
biased by having selected on train.

Reversal is `git revert` of the description commit. The probes and the harness
would survive it and would then measure the restored text.

## Implementation references

- `plugins/engineering-ownership/skills/engineering-ownership/SKILL.md`
- `plugins/engineering-ownership/skills/engineering-ownership/evals/triggers.json`
- `scripts/eval/run_trigger_probes.py`

## Supersession

Supersedes: None
Superseded by: None
