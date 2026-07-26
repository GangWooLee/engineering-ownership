# 2026-07-16 · Partner request timeout policy

Change ID: `partner-timeout-policy`
Created: `2026-07-16T10:04:00+00:00`
Status: Accepted

## Context

Settlement submissions had no timeout, and a partner-side stall held workers
until the process was restarted.

## Options considered

1. No timeout, rely on partner availability.
2. Adaptive timeout derived from observed latency.
3. Fixed timeout with the submission left unsent.

## Decision

Choose option 3. The failure being guarded against is a stall rather than
slowness, and an adaptive bound needs latency history that is not collected.

## Consequences and reversal

A timed-out submission needs a human to decide on resubmission, because the
partner has not confirmed that it deduplicates on order id. Reversal is removing
the timeout argument.

## Implementation references

- `src/api/partner_client.py`

## Supersession

Supersedes: None
Superseded by: None
