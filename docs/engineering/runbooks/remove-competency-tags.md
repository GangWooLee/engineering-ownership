# 2026-07-26 · Remove the write-only competency tag subsystem

Change ID: `remove-competency-tags`
Created: `2026-07-26T10:42:28+09:00`
## Signals and alerts

- `engineering change start` rejects `--competency`: expected — the flag is
  gone. Remove it from any script or muscle memory.
- A validation error naming `competencies` on read would mean the
  compatibility guarantee regressed: file a change against
  `validate_evidence` immediately.

## Safe diagnosis

Read-only: `engineering status`, `explain <id>`, and
`python3 -m unittest tests.test_cli -k legacy_competencies` reproduce the
compatibility guarantee in isolation.

## Rollback or repair

Revert the single commit. Old records were never modified, so rollback
restores the previous behavior completely; records created during the
removal window simply lack the field, which the restored code treats as an
empty list.

## Escalation and data handling

Local repository data only. Historical records keep their tag arrays as
written; no cleanup pass should ever rewrite them.
