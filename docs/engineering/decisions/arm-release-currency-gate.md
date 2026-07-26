# 2026-07-26 · Fail a tag whose release notes predate shipped content

Change ID: `arm-release-currency-gate`
Created: `2026-07-26T10:52:39+09:00`
Status: Accepted

## Context

`gh release create --notes-file` publishes whatever the notes file says at tag
time. A notes file is written once, mid-branch, and every later shipped-content
commit silently ages it. This repository hit both failure shapes within three
days: v0.2.0's run died on a missing notes path and was hand-published, and
v0.2.1's staged notes claimed "no runtime behaviour changes" while the branch
went on to change the CLI surface twice.

## Options considered

1. **Process rule** ("always amend notes before tagging"). Rejected: the rule
   already implicitly existed and was not followed by the author under time
   pressure; unenforced process is how the trap got armed.
2. **New CI job or script.** Rejected: the repository's remediation principle
   is that additions must replace something; a second gate script would sit
   beside the existing one.
3. **Extend the existing first step of the release job**,
   `validate_release_tag.py`, with a notes-exist check and a last-commit-time
   comparison between `plugins/**` and the notes file. Chosen.

## Decision

Option 3, plus `fetch-depth: 0` on the release checkout so the comparison is
real in CI (a shallow clone makes both timestamps the HEAD commit's and passes
trivially — degrade-safe, never degrade-wrong). Separately, the republication
gate in `PublishedResultCase` is widened from JSON-block-only to any README or
validation surface pairing a with/without-skill comparison with score-shaped
numbers — the withdrawn claim's original markdown-table form.

## Consequences and reversal

Cutting a tag now requires the notes to be the last thing touched after
shipped content — which is the honest order anyway. A legitimate notes-only
release (no plugins change) is unaffected. Reversal is a revert of the
validator and workflow lines; the gate has no state.

## Implementation references

- `scripts/validate_release_tag.py`
- `.github/workflows/release.yml`

## Supersession

Supersedes: None
Superseded by: None
