# 2026-07-26 · Assert the tag validator's quoting concern without coupling it to notes currency

Change ID: `scope-currency-gate-to-tag-time`
Created: `2026-07-26T11:54:22+09:00`
Risk: R1

## Problem and intended outcome

The notes-currency refusal added in `arm-release-currency-gate` fired for the
first time today, correctly: the refs-exclusion change touched `plugins/**`
after `docs/releases/v0.3.0.md` was last amended. But it fired inside
`test_release_tag_validation_has_no_shell_quoting_dependency`, which asserted
a zero exit for the current tag. That test's stated concern is that the tag
argument survives without shell quoting; coupling it to notes currency means
**every** `plugins/**` commit fails the suite until the release notes are
amended.

That is the anti-pattern the refs-exclusion change had just named in its own
rationale: a gate that is red most of the time teaches people to ignore it.
Notes currency is a tag-time condition, not a per-commit one.

Intended outcome: the test asserts only its own concern; the validator keeps
refusing stale notes exactly as designed, where it is consulted at tag time.

## Success and non-goals

Success: the suite passes mid-development with stale notes, and still fails
if the tag/package mismatch regresses; `validate_release_tag.py v0.3.0`
passes once the notes actually cover the shipped content.

Non-goals: weakening the validator. No flag, no skip switch, no change to
`scripts/validate_release_tag.py` at all — the refusal stays unconditional
wherever the script is run, including the release workflow's first step.

## Existing responsibilities searched

The mismatch assertion for the invalid tag (`v9.9.9`) already covers the
quoting concern's negative case; only the positive case needed re-aiming.
No new test was added — the existing one was narrowed to its claim.

## System and data flow

Unchanged. The test now asserts the absence of the tag-mismatch message
rather than a zero exit, so a currency refusal — a different, legitimate
refusal — no longer registers as a quoting failure.

## Decisions and trade-offs

Considered adding a `--require-current-notes` flag so the check ran only in
CI. Rejected: `validate_release_tag.py` is an R3 path under the contract
adopted today, and adding surface to a release-critical script to make a
test pass is the wrong direction. Narrowing the test costs nothing and
leaves the gate at full strength.

Trade-off accepted: the currency branch has no automated coverage, which the
`arm-release-currency-gate` Brief already recorded as a known limit (the
script resolves its own repository root, so a hermetic test would need a
backdoor). It is covered in practice by the release workflow.

## Failure, security, and recovery

If the tag/package match regresses, the invalid-tag assertion still fails the
suite. If notes go stale, the release job fails at its first step — observed
today. No security surface.

## Verification evidence

- `python3 -m unittest discover -s tests`: 83 tests pass.
- `python3 scripts/validate_release_tag.py v0.3.0`: passes after the release
  notes and CHANGELOG were amended to cover `refs.exclude` — the content fix
  the gate was asking for, made rather than bypassed.

## Known limits and learning gaps

The gate's own failure path remains manually observed rather than tested
(twice now: on this branch's stale notes, and again today). If it fires a
third time without catching a real problem, revisit whether the comparison
is too coarse.

## References

- `tests/test_release.py`
- `docs/engineering/changes/arm-release-currency-gate.md` (the gate itself)
- `docs/engineering/decisions/exclude-illustrative-references.md` (the
  "permanently red gate" principle this applies)
