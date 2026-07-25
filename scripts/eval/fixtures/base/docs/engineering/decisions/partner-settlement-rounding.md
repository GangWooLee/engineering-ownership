# 2026-07-18 · Partner settlement rounding

Change ID: `partner-settlement-rounding`
Created: `2026-07-18T09:12:04+00:00`
Status: Accepted

## Context

Stored amounts are integer cents. The partner settlement API accepts whole
currency units only.

## Options considered

1. Store a second column in whole units.
2. Convert in every caller before building the payload.
3. Convert once inside the adapter boundary.

## Decision

Choose option 3. The adapter already owns the payload contract, so the
conversion has a single owner and cannot drift between callers.

## Consequences and reversal

Callers keep passing cents. Reversal is removing the conversion from the
adapter. The cost is that the adapter now encodes a partner-specific rule.

## Implementation references

- `src/api/partner_adapter.py`

## Supersession

Supersedes: None
Superseded by: None
