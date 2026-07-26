# 2026-07-26 · Exclude illustrative decision references from refs check

Change ID: `exclude-illustrative-references`
Created: `2026-07-26T11:26:59+09:00`
Status: Accepted

## Context

`refs check --all` scans every text file in the repository for
`engineering-decision:` markers and demands live evidence for each one. On
this repository the scan reported ten gaps, none of which was a real dangling
decision: four test literals in `tests/test_cli.py`, two tutorial code blocks
in `docs/tutorials/`, one deliberate marker inside an eval fixture that
*simulates* a repository with a decision, and three eval output records that
quote that fixture. The scanner cannot distinguish a claim about this
repository from content that merely depicts a marker.

## Options considered

1. **Neutralize every illustrative marker in place.** Rejected: tutorials
   would lose their copy-paste worked example, eval fixtures exist precisely
   to contain real-looking markers, and rewriting committed eval grading
   records would falsify historical measurement data.
2. **Hard-code exclusions for this repository's paths in the CLI.** Rejected:
   the CLI ships to other repositories; their docs and fixture layouts
   differ. Repository-specific paths do not belong in shared code.
3. **Contract-declared exclusion globs (`refs.exclude`).** Chosen. The
   contract already owns repository-specific path policy (`risk_paths`), the
   same `fnmatch` semantics apply, and each repository decides — visibly, in
   a reviewed file — which paths are illustrative. Test literals are *not*
   excluded: `tests/**` stays scanned, and test files compose markers at
   runtime instead (the pre-existing `decision_marker` pattern).

## Decision

`validate_contract` accepts an optional `refs.exclude` array of
repository-relative globs; `refs check` and the `check` gate filter scanned
paths through those globs before collecting markers. This repository excludes
`docs/tutorials/**` (worked examples), `scripts/eval/fixtures/**` (synthetic
repositories whose markers are the eval subject), and
`engineering-ownership-workspace/**` (historical eval output that quotes
those fixtures). This extends `cover-ship-critical-paths`: the measurement
harness is deliberately outside the ceremony, and now also outside the
reference scan — a decision, not an omission.

## Consequences and reversal

A marker accidentally added under an excluded path will not be flagged;
acceptable because those paths never carry real enforcement points, and the
exclusion list itself sits in the contract where every change is reviewed.
ADR implementation-reference checks are unaffected — exclusion filters only
the marker scan. Reversal is deleting the `refs` block from the contract;
the CLI treats an absent key as "scan everything", so old contracts keep
their exact prior behavior.

## Implementation references

- `plugins/engineering-ownership/src/engineering_ownership/cli.py`
- `plugins/engineering-ownership/src/engineering_ownership/model.py`
- `.engineering/contract.json`

## Supersession

Supersedes: None
Superseded by: None
