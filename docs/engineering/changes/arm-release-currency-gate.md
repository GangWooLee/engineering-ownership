# 2026-07-26 · Fail a tag whose release notes predate shipped content

Change ID: `arm-release-currency-gate`
Created: `2026-07-26T10:52:39+09:00`
Risk: R3

## Problem and intended outcome

An armed trap sat in the release path: `release.yml` publishes
`docs/releases/<tag>.md` verbatim via `--notes-file` with no currency check.
The staged v0.2.1 notes said "No runtime behaviour changes" — true when
written, silently invalidated hours later by the description rewrite, and
further by this branch's close verb and competency removal. Tagging would have
published a false document. The v0.2.0 release already failed once on the
adjacent hazard (a missing notes path), and was hand-published a minute later.

Intended outcome: a tag cannot be cut when the notes file is missing or when
shipped content (`plugins/**`) changed after the notes were last amended. Also:
the republication gate in `tests/test_evals.py` matched only a JSON block with
`with_skill_mean`; the withdrawn claim's original markdown-table form is now
also caught on README and validation surfaces.

## Success and non-goals

Success: `validate_release_tag.py` refuses missing or stale notes; the full
suite passes including the widened gate; the release workflow fetches full
history so the timestamp comparison is real in CI, not trivially equal on a
shallow clone.

Non-goals: creating the v0.2.1 tag (explicitly out of scope); deciding the
version label (whether the pending release should be 0.3.0 given the breaking
change is an open owner decision); gating trigger-rate numbers in release
notes and change records, which are backed by committed probe runs.

## Existing responsibilities searched

The check extends the existing `validate_release_tag.py` — already the release
workflow's first step — rather than adding a new script; the missing-notes
case is exactly the failure that broke the v0.2.0 release run. The
republication check extends the existing `PublishedResultCase` rather than
adding a parallel mechanism.

## System and data flow

Tag push → checkout (now `fetch-depth: 0`) → `validate_release_tag.py <tag>`:
tag must match `pyproject.toml`; `docs/releases/<tag>.md` must exist; the last
commit touching `plugins/**` must not be newer than the last commit touching
the notes. Test-side: any README/validation surface pairing a
with/without-skill comparison with score-shaped numbers must carry either the
machine-readable results block or a Withdrawn/Superseded status.

## Decisions and trade-offs

See `docs/engineering/decisions/arm-release-currency-gate.md`.

## Failure, security, and recovery

A false refusal (notes current but timestamps mislead) is recoverable by
amending the notes and re-tagging — the failure mode is a blocked release,
never a wrong one published. The comparison degrades safely on shallow clones
(equal timestamps pass); the release workflow now fetches full history so the
gate is real where it matters.

## Verification evidence

- `python3 scripts/validate_release_tag.py v0.2.1` after the notes amendment
  commit: passes. (Before the amendment was committed, it refused — observed,
  which is the gate doing its job on this very branch's stale notes.)
- `python3 -m unittest discover -s tests`: 81 tests pass, including the new
  `test_efficacy_shaped_numbers_need_a_results_contract_or_retired_status`.
- All four contract commands pass via `engineering verify`.

## Known limits and learning gaps

- The stale-notes refusal branch has no hermetic unit test: the validator
  resolves its repository root from its own location, so exercising the
  failure requires manipulating this repository's history. Observed manually
  instead (see verification). A test-only root override was rejected as a
  backdoor in a release-critical script.
- The widened gate covers README and `docs/validation/**`; release notes and
  change records may legitimately carry trigger-rate numbers backed by
  committed probe runs.

## References

- `scripts/validate_release_tag.py`
- `.github/workflows/release.yml`
- `tests/test_evals.py` (`PublishedResultCase`)
- `docs/engineering/decisions/arm-release-currency-gate.md`
