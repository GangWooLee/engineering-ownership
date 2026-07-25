# 2026-07-16 · Partner request timeout policy

Change ID: `partner-timeout-policy`
Created: `2026-07-16T10:04:00+00:00`
Risk: R2
Status: Completed

## Problem and intended outcome

Settlement submissions to the partner had no timeout. A partner-side stall held
a worker until the process was restarted, and during the incident on 14 July
four workers were held for fifty minutes before anyone noticed.

## Success and non-goals

Success is that a stalled partner cannot hold a worker indefinitely, and that a
timeout is distinguishable in the logs from a rejection.

Not in scope: retrying a timed-out submission. That needs an idempotency
guarantee the partner has not confirmed.

## Existing responsibilities searched

`src/api/partner_adapter.py` owns the payload; the transport concern is separate
and went into `src/api/partner_client.py` rather than widening the adapter.

## System and data flow

Worker -> partner_client.submit -> partner settlement API. The client raises on
timeout; the worker records the submission as unsent and moves on.

## Decisions and trade-offs

Fixed timeout rather than adaptive. Adaptive would need latency history we do
not collect, and the failure it guards against is a stall rather than slowness.

## Failure, security, and recovery

A submission that times out is left unsent and is visible in the unsent queue.
Recovery is manual resubmission, which is safe only for partners that treat the
order id as an idempotency key.

## Verification evidence

Unit tests cover the timeout path. The stall was reproduced against a local
socket that accepts and never responds.

## Known limits and learning gaps

Whether the partner deduplicates on order id is still unconfirmed. Until it is,
resubmission after a timeout is a manual decision rather than an automatic one,
and this is the open question a reader should carry forward.

## References

- ADR: `docs/engineering/decisions/partner-timeout-policy.md`
