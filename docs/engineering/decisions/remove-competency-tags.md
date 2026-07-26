# 2026-07-26 · Remove the write-only competency tag subsystem

Change ID: `remove-competency-tags`
Created: `2026-07-26T10:42:28+09:00`
Status: Accepted

## Context

The tags were introduced in v0.1 as "evidence tags without scores". Two days
and zero external users later, an executed audit found them written once and
read by nothing but two `print` calls, with a duplicated source of truth and a
reference doc implying aggregation that does not exist. A subsystem that
records data no consumer uses is not evidence; it is pretense, and it invites
exactly the person-scoring misreading the project disclaims.

## Options considered

1. **Build the missing consumer** (filters, aggregation in `status`). Rejected:
   no user has asked for it, and the audit's core misalignment finding was
   machinery built ahead of any demand.
2. **Keep the field but stop documenting it.** Rejected: dead plumbing with two
   unsynced copies keeps its carrying cost and its drift risk.
3. **Remove the subsystem; ignore the field on old records.** Chosen. Removal
   is total for the live surface; history is untouched.

## Decision

Option 3. Legacy compatibility is read-side only: `validate_evidence` no longer
inspects the field, the schema no longer requires or describes it, and nothing
rejects a record that carries it. If a tagging need returns with a real
consumer, it starts from a new decision — this one does not reserve the field.

## Consequences and reversal

New evidence records are smaller by one dead field. Old records and eval
fixture data keep theirs, unread. Reversal is a revert plus re-adding the flag;
no data migration in either direction because the field was never load-bearing.

## Implementation references

- `plugins/engineering-ownership/src/engineering_ownership/model.py`
- `plugins/engineering-ownership/src/engineering_ownership/evidence.py`
- `plugins/engineering-ownership/src/engineering_ownership/cli.py`

## Supersession

Supersedes: None
Superseded by: None
