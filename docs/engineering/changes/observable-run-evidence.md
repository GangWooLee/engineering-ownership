# 2026-07-25 · Let runs write, and show the judge what they did

Change ID: `observable-run-evidence`
Created: `2026-07-25T15:00:43+09:00`
Risk: R2
Status: Completed
Corrected: 2026-08-05 — "zero tells" was false for one of the two bundles. The
run behind this record's headline verdict named its own arm in the judge-visible
action log; the leak check missed it because the arm names were not in its tell
list. See `close-arm-name-leak`.

## Problem and intended outcome

`rewrite-evaluation-expectations` left eight expectations ungradable. They ask
what survives the session and whether an act of inspection happened, and the
harness could observe neither. The intended outcome is that those expectations
become answerable from evidence rather than from the responder's own account,
without the judge being able to tell which configuration it is grading.

## Success and non-goals

Success is that a run can produce durable artifacts, that the judge is shown an
ordered record of what the run did and the content of what it wrote, and that a
mechanical check confirms that record does not identify the configuration.

Not in scope: fixtures for the remaining seven scenarios, or a sample size that
would support a published number.

## Existing responsibilities searched

The runner already parsed `tool_use` blocks to count tools; the action log is
derived from the same pass rather than a second one. Per-run fixture isolation
already existed - a fresh tree per run, removed afterwards - so allowing writes
needed no new isolation, only capture before the teardown.

`redact()` already existed for home paths and is reused for every field that
reaches a committed artifact.

## System and data flow

Unchanged in shape. What moved is what crosses the boundary into grading:

- The judge receives the response, an ordered action log, the list of changed
  paths, the content of files the run created, and the diff of files it
  modified.
- It does not receive the transcript, `metrics.json`, `timing.json`, or
  `run_meta.json`. Each of those identifies the configuration outright: the
  transcript names this skill in one arm only, `tool_calls` carries a `Skill`
  key on one side, and duration differed threefold in the pilot.

`Skill` entries are dropped from the action log before it is written, so the
distinction cannot be reconstructed downstream.

## Decisions and trade-offs

Recorded in `docs/engineering/decisions/observable-run-evidence.md`. The
load-bearing one is that the capability set is identical in both configurations;
the second is that the judge's explicit request for the transcript was refused
and answered with a derived log instead.

## Failure, security, and recovery

Runs now write. The containment is unchanged in kind and worth restating: each
run gets a fresh fixture built outside this repository and removed afterwards,
the tool allowlist has no network access and no package installation, and Bash
is limited to read-only git verbs plus the fixture's own test command.

Everything captured is passed through `redact()` before being written, because
these artifacts are committed and `AGENTS.md` forbids storing home paths. File
contents are truncated per file.

The new failure mode is a blinding leak. It is handled by refusing to grade: if
the assembled evidence names this project, the run is recorded invalid with the
reason rather than graded and reported.

## Verification evidence

- `python3 -m unittest discover -s tests`: 60 tests pass.
- All four contract commands pass.

Real-runtime evidence, from `engineering-ownership-workspace/iteration-3`:

- **Writes work symmetrically.** Both configurations changed six paths. Both
  created a new decision record, both marked the earlier one superseded, and
  both left its reasoning in place.
- **The action log is populated and neutral.** 32 recorded actions against 22.
  The leak check found nothing identifying in either bundle: 15,061 and 12,217
  characters of evidence, zero tells.

  (Corrected 2026-08-05: the second bundle was not neutral. The 12,217-character
  bundle is `iteration-3/eval-9/without_skill/run-1`, and step 12 of its action
  log reads `find /private/var/.../engo-eval-kqvewaa0/eval-9-without_skill-1
  "*/.git*"` — the fixture directory names the arm. The leak check returned
  nothing because its tell list did not contain the arm names until
  `close-arm-name-leak` added them; run today it returns `['without_skill']`.
  The check was reported honestly and it was blind to this. That run is the one
  whose verdict the next bullet presents as this change's headline finding, so
  the judge that produced it had been shown which arm it was grading. The run is
  now pinned in `tests/test_evals.py` as a known leak.)
- **`skill_loaded` is correct**: true for the treatment, false for the baseline,
  and that field is withheld from the judge.
- **The enriched bundle changed a verdict.** The judge failed the baseline on
  one expectation using the captured file contents - it could see the written
  records carried the bookkeeping but not the reason. That verdict was not
  available from the response text alone.

Guards were exercised rather than assumed: the leak check was given an action
log naming the plugin directory and observed rejecting it, and the workspace
index guard fired for real when `iteration-3` was committed before being
declared, which is how it was noticed.

## Known limits and learning gaps

**The validation run exposed a defect in my own expectation.** The judge
reported that expectation 3 of the ninth scenario bundled two behaviours and
created a tension: correct practice for superseding a decision *requires*
editing the earlier record's status, so "leaves the original intact" read as
forbidding the right answer. It has been split into preservation and
explanation. The grading in `iteration-3` was produced against the unsplit
wording and is labelled accordingly.

This is the second time the judge's critique of an expectation has been more
useful than its verdicts. That field is worth reading first, not last.

**The baseline performed the maintenance behaviour too.** It found the
contradicted decision, marked it superseded, and wrote a replacement. The single
differentiator was explaining why preservation matters. That may say more about
the fixture than the skill: the fixture's decision template already carries a
`Supersession` section, so the convention is visible to anyone who reads it. A
fixture that teaches the answer is a confound, and it should be examined before
these scenarios are used for a published number.

**The response can still leak.** It may name a risk tier or this project's
directories, and it cannot be sanitized without altering the artifact under
review.

**One run per configuration.** No claim follows from it.

**Seven of nine scenarios still have no fixture.**

## References

- Decision record: `docs/engineering/decisions/observable-run-evidence.md`
- The expectations this unblocks: `docs/engineering/changes/rewrite-evaluation-expectations.md`
- Validation artifacts: `engineering-ownership-workspace/iteration-3/`
