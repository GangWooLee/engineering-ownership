# 2026-07-23 · Documentation-first engineering workflow

Change ID: `documentation-first-workflow`
Created: `2026-07-23T10:37:55+00:00`

Risk: R3

## User reasoning

The workflow should not turn every change into an oral examination that blocks
the next task. Its primary value is to preserve the work's context, decision
process, rationale, alternatives, verification, and limitations while those
facts are fresh.

Those records should let a less-experienced owner revisit an unfamiliar change
in a separate study session and let a future AI session modify the system
without silently contradicting an earlier constraint. The owner may not yet be
able to answer broad engineering questions from memory; that is a learning gap,
not a reason for AI to invent a passing grade.

## Success and non-goals

Success means R2 and R3 completion depends on durable reasoning artifacts and
fresh verification, not a mandatory no-AI teach-back. `explain` remains an
optional review aid, understanding gaps remain visible, and handoff points the
next reader to the canonical records.

This change does not remove human review, verification gates, risk
classification, or the ability for a repository to adopt a stricter policy.
It does not require documentation for R0 changes.

## Existing responsibilities searched

The existing brief, ADR, runbook, threat-model, evidence, status, explain, and
handoff responsibilities are retained. The completion gate in
`evidence_gaps`, the `teach_back` field, skill wording, templates, schemas,
tests, and release documentation are the owners that must change together.

## System and data flow

`change start` creates risk-proportional Markdown records and machine evidence.
The owner and AI keep the brief current; architecturally significant R2/R3
decisions receive an ADR. `verify` binds command outcomes to the current diff.
`check` gates required records and fresh verification. `status`, `explain`, and
`handoff` expose artifact paths, unresolved understanding gaps, and a suggested
revisit date without blocking completion by default.

## Alternatives and trade-offs

Keeping mandatory teach-back would test recall but would interrupt product work
and disadvantage a learner who needs the very records the project is meant to
create. Removing review state entirely would lose useful learning signals.
The selected design keeps optional review state and prompts while separating
them from default completion.

Putting all rationale in commit messages was rejected because long-lived
architectural decisions need stable, searchable records and commits are
implementation-history units. Duplicating full rationale across ADRs, commits,
PRs, and comments was rejected because copies drift.

## Failure, security, and recovery

The main risk is replacing a meaningful gate with documentation theater.
Templates therefore require concrete context and rationale, and current-diff
verification remains enforceable. Another risk is stale decisions; ADRs use
status and supersession links instead of rewriting accepted history.

The change is reversible by restoring the prior evidence field and gate, but a
repository that needs mandatory teach-back should add that as an explicit local
policy rather than relying on the public default.

## Verification plan

Update unit tests so R2 can pass with complete decision records and fresh
verification even when understanding review is pending, while stale
verification and unfilled records still block. Validate both plugin manifests,
distribution contents, release ZIP, status, explain, and handoff output.

## Known limits and learning gaps

The CLI checks that required records are present and filled; it cannot judge
whether their reasoning is good. Human or team review remains necessary.
Commit and PR practices are guidance because the CLI intentionally installs no
hooks and makes no network calls.
