# 2026-07-26 · Rename the unreleased 0.2.1 to 0.3.0

Change ID: `rename-pending-release-030`
Created: `2026-07-26T11:26:58+09:00`
Status: Accepted

## Context

Work staged under the `0.2.1` label grew from "rewrite the eval manifest" to
include a removed CLI flag (`--competency`), a new verb (`change close`), and
changed default output in `status`, `handoff`, and the session hook. The label
was chosen when the content was a manifest edit and never revisited. Nothing
was ever tagged or published as `0.2.1`.

## Options considered

1. **Keep `0.2.1`.** The repository's earlier decision record permits editing
   shipped content under an unreleased label ("that cost is charged once").
   Rejected: that decision licenses *editing* under an unreleased label, not
   *mislabelling* the result. A user reading `0.2.0 → 0.2.1` would expect to
   upgrade without reading anything, and would lose a CLI flag.
2. **Go to `1.0.0`.** Rejected: a two-day-old project with zero external users
   has no stable interface to promise.
3. **Rename to `0.3.0`.** Chosen. Pre-1.0 convention puts breaking changes in
   the minor position, and an unreleased label costs nothing to move.

## Decision

`0.3.0`. The rename is mechanical and complete only if
`validate_distribution.py` passes, since it compares every manifest against
`pyproject.toml` — that check is the acceptance criterion, not a separate
inspection. Historical documents keep `0.2.1` where they describe what the
work was called at the time.

## Consequences and reversal

The next tag is `v0.3.0`, and `docs/releases/v0.3.0.md` is what the release
workflow will publish — now guarded by the notes-currency check added earlier
today. Reversal is the inverse substitution; nothing is published.

## Implementation references

- `pyproject.toml`
- `.engineering/contract.json`

## Supersession

Supersedes: None
Superseded by: None
