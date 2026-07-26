# 2026-07-26 · Rename the unreleased 0.2.1 to 0.3.0

Change ID: `rename-pending-release-030`
Created: `2026-07-26T11:26:58+09:00`
Risk: R2

## Problem and intended outcome

The pending release was labelled `0.2.1` — a patch — while its content grew to
include a breaking CLI change (`--competency` removed), a new verb
(`change close`), and changed default behaviour in `status`, `handoff`, and
the session hook. A patch label on that content misinforms anyone reading the
version alone. `0.2.1` was never tagged or published, so renaming costs
nothing but the edit.

Intended outcome: every version stamp reads `0.3.0`, the notes file is
renamed, and the release path validates end to end under the new label.

## Success and non-goals

Success: `pyproject.toml`, both plugin manifests, `marketplace.json`,
`SKILL.md` metadata, `__init__.py`, and the contract's `release-package`
command all read `0.3.0`; `docs/releases/v0.3.0.md` exists;
`validate_release_tag.py v0.3.0` passes including the new currency check; the
suite passes with the version-pinned release tests updated.

Non-goals: creating the tag or publishing the release — still the owner's
call, and the notes must be reviewed first.

## Existing responsibilities searched

`validate_distribution.py` already asserts that every manifest agrees with
`pyproject.toml`, so it is the check that proves the rename is complete rather
than a new one being added for the purpose.

## System and data flow

Mechanical substitution across the version-bearing files plus a `git mv` of
the notes file. `tests/test_release.py` and `tests/test_distribution.py` pin
the version literally and were updated with it.

## Decisions and trade-offs

Semver: a removed CLI flag is breaking, and pre-1.0 convention puts breaking
changes in the minor position. The repository's earlier "charged once"
decision permits editing shipped content under an unreleased label; it does
not require the label to stay a patch once the content outgrows it.

## Failure, security, and recovery

The realistic failure is a missed stamp, which `validate_distribution.py`
catches by comparing all manifests against `pyproject.toml` — it passes.
Reversal is the inverse substitution; nothing is published yet.

## Verification evidence

- `python3 -m unittest discover -s tests`: 81 tests pass.
- `python3 scripts/validate_distribution.py`: passed (all manifests agree —
  this is the check that proves the rename is complete).
- `python3 scripts/validate_release_tag.py v0.3.0`: passed, including the
  notes-exist and notes-currency checks added earlier today.
- `dist/engineering-ownership-v0.3.0.zip` builds with its `.sha256`.

**Not bound to the current diff, and why.** `engineering verify` refused:
a concurrent session is editing `cli.py` and `model.py` in this same working
tree, so the tree-wide diff detects R3 and exceeds this record's declared R2.
Escalating this record to R3 would attach another change's work to it, which
is worse than an unbound record. The four commands above were therefore run
directly and their results recorded here rather than in the evidence file.
This record stays open until the tree settles and verification can be bound.

## Known limits and learning gaps

- Historical documents (`docs/releases/v0.2.0.md`, older CHANGELOG entries,
  closed change records) still mention `0.2.1` as the label the work carried
  at the time. Left as written — history is not edited.
- Concurrency limit discovered here: risk detection and diff binding are
  tree-wide, so two agents sharing one working tree cannot both bind clean
  evidence. The tool has no per-change diff scoping and no worktree guidance.
  Worth a decision record if shared-tree work becomes normal.

## References

- `.engineering/contract.json` (release-package command pin)
- `docs/releases/v0.3.0.md`
