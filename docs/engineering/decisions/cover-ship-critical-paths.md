# 2026-07-26 · Cover ship-critical paths in the risk contract

Change ID: `cover-ship-critical-paths`
Created: `2026-07-26T11:00:30+09:00`
Status: Accepted

## Context

The contract claimed to risk-tier the repository while matching none of
`scripts/**`, not `ci.yml`, and only four hand-picked `src` files. Meanwhile
84% of the branch's churn happened in the uncovered evaluation harness. Two
honest positions existed: widen coverage, or stop claiming it.

## Options considered

1. **Cover `scripts/**` wholesale at R2.** Rejected: it would attach Brief
   ceremony to every harness tweak — the audit's core over-built finding was
   precisely change-record ceremony on measurement work with no user-facing
   consequence.
2. **Drop the coverage claim (docs-only).** Rejected: it leaves `evidence.py`
   — the module that writes every evidence record — at R1, a real
   under-verification, not just a wording problem.
3. **Cover ship-critical only; exclude the harness deliberately.** Chosen,
   by owner decision. What ships or gates shipping is tiered by blast
   radius; what measures is not taxed.

## Decision

R3 gains `evidence.py`, `templates.py`, `resources/schemas/**` (they define
what every installer's records look like), plus `build_release.py`,
`validate_release_tag.py`, and `validate_distribution.py` (they decide what
ships and whether it may). R2 gains `ci.yml` (it gates every merge).
`scripts/eval/**` and `tests/**` stay uncovered **on purpose**: the harness is
repository tooling whose failures cannot reach an installer, and its integrity
is enforced by `tests/test_evals.py` guards rather than by change-record
ceremony. This exclusion is a decision, not an omission — the distinction the
audit demanded.

## Consequences and reversal

Future edits to the evidence writer, the templates, the schemas, or the
release scripts require the full R3 artifact set — which this branch's own
history shows is warranted (three of this session's five changes touched
those exact files). Reversal is a one-line glob removal per path.

## Implementation references

- `.engineering/contract.json`

## Supersession

Supersedes: None
Superseded by: None
