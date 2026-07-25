# 2026-07-18 · Partner settlement rounding

Change ID: `partner-settlement-rounding`
Created: `2026-07-18T09:12:04+00:00`
Risk: R2
Status: In progress

## Problem and intended outcome

The partner settlement API rejects payloads whose amount is not expressed in
whole currency units. Orders are stored in cents, so every payload we send for a
partner that settles in whole units is rejected downstream and retried by hand.

The intended outcome is that the adapter converts amounts once, at the boundary,
and that the stored representation stays in cents.

## Success and non-goals

Success is that no settlement payload is rejected for amount formatting, and
that the conversion is visible in one place rather than spread across callers.

Not in scope: changing how amounts are stored, or the retry mechanism.

## Existing responsibilities searched

`src/api/partner_adapter.py` already owns the payload shape, so the conversion
belongs there rather than in a new helper. `src/db/schema.py` owns the stored
representation and keeps cents.

## System and data flow

Order row (cents) -> `to_partner_payload` -> partner settlement API.

## Decisions and trade-offs

Convert at the adapter boundary rather than storing a second column. A second
column would need backfilling and could drift from the cents value.

## Failure, security, and recovery

A wrong conversion silently under- or over-reports money. Rollback is reverting
the adapter; no data migration is involved.

## Verification evidence

Unit tests passed on 2026-07-18 against the adapter change alone.

## Known limits and learning gaps

Rounding behaviour for partners that settle in fractional units is unresolved.

## References

- ADR: `docs/engineering/decisions/partner-settlement-rounding.md`
