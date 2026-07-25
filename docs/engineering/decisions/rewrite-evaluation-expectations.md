# 2026-07-25 · Rewrite the evaluation expectations to be passable on merit

Change ID: `rewrite-evaluation-expectations`
Created: `2026-07-25T14:28:50+09:00`
Status: Accepted

## Context

This project had no decision record covering how its skill is evaluated. The
absence is why the withdrawn result was possible: each expectation was written
case by case, and nothing said what made one admissible.

An audit of the 32 expectations then shipping found three that a competent
engineer unfamiliar with this skill could pass on merit. Seven required
vocabulary only this skill supplies. Nine were satisfied by a response that said
nothing. Twelve bundled independently observable things into a single verdict.
One scored a response worse for having fixed the problem it was asked about -
that one is not hypothetical: in the pilot it is exactly why the run that
resolved a stale verification lost to the run that stopped and reported it.

Thirteen of the 32 also duplicated assertions `tests/` already makes
deterministically, which spends a judge call to re-derive a fact a unit test
already proves.

## Decision

Adopt four rules for what may be an expectation, and enforce them in
`tests/test_evals.py` rather than in review.

1. **Passable on merit.** An expectation may not require this skill's private
   vocabulary, including its risk-tier labels. Ask for the judgment and its
   grounds, not for the label.
2. **Not satisfiable by silence.** Restraint is measured by requiring the
   response to show it considered the question and chose, never by the absence
   of a thing.
3. **One observable behaviour per expectation.** Bundled clauses are separated.
4. **Never penalise resolution.** An expectation asks what the final answer
   demonstrates the responder understood, not that an initial defect was still
   present when it answered.

Alongside these: what `tests/` asserts deterministically is not an expectation.
Conformance belongs to the unit tests; the evaluation measures efficacy.

## Options considered

1. **Patch the worst offenders.** Cheapest, and it was the initial framing of
   this work. Rejected once the audit showed 29 of 32 were affected: patching
   would have left the manifest a mixture of two standards with nothing
   recording which was which.
2. **Delete the evaluation.** Honest, and briefly attractive given that the
   published claim had already been withdrawn. Rejected because
   `CONTRIBUTING.md` requires paired evaluation evidence from contributors, and
   a maintainer who cannot produce it is asking for something the project does
   not itself do.
3. **Rewrite against stated rules, enforced by tests.** Chosen. The rules are
   the durable part; the current wording of any single expectation is not.

## Consequences and reversal

Expectation counts now vary between three and five, so the published denominator
is a sum rather than a product. The harness computes it. The uniform-count rule
that previously held was dropped because it forced unrelated observations to be
bundled, which is the defect it was inadvertently protecting.

Some expectations are now only gradable if the run may write files and if the
judge is shown what the run did. Neither holds yet. Until both land, those
expectations will fail for reasons that are not about the responder, and any
iteration run before then must say so rather than reporting the number.

Rewriting the manifest changed a file that ships in the release package, which
forced `0.2.1`. That cost is charged once; it is the reason the ninth scenario
was added in the same change rather than later.

Reversal is `git revert`. The rules would survive it, because they are recorded
here and in the tests rather than only in the manifest text.

## Implementation references

- `plugins/engineering-ownership/skills/engineering-ownership/evals/evals.json`
- `tests/test_evals.py`

## Supersession

Supersedes: None
Superseded by: None
