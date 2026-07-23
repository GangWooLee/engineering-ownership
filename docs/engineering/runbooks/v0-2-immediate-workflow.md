# 2026-07-23 · Engineering Ownership v0.2 immediate workflow

Change ID: `v0-2-immediate-workflow`
Created: `2026-07-23T11:43:43+00:00`

## Signals and alerts

- `doctor` reports an invalid/missing contract, plugin not detected, or missing
  verification executable.
- `verify` reports that detected risk exceeds recorded risk.
- `refs check` reports missing, noncanonical, escaped, or superseded references.
- Host debug output reports a hook error or reminder output exceeds 20 lines.

## Safe diagnosis

Run unit and distribution tests from a trusted checkout. Inspect only normalized
doctor output, the validated contract, current diff, and hook source. Do not
paste credential-rich child command logs into evidence or issues.

## Rollback or repair

Disable reminders by setting `automation.session_hooks` to `off` or decline
host hook trust. The core skill and CLI remain usable. Repair a stale or raised
risk record with `change set-risk`, refill required operational records, and
rerun current-diff verification. Repair broken decision markers to the
canonical ADR or remove unnecessary markers.

## Escalation and data handling

Treat path escape, secret disclosure, automatic verification, host blocking, or
release-asset compromise as security incidents. Stop release, preserve minimal
non-secret reproduction data, use private vulnerability reporting, and revoke
or replace compromised assets before publishing.
