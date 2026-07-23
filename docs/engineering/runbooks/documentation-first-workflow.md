# Runbook: documentation-first-workflow

## Signals and alerts

Treat any of the following as a workflow defect:

- `check --mode enforce` blocks only because understanding review is pending;
- R2/R3 passes with an unfilled required record or stale verification;
- status or handoff omits canonical document paths;
- a next session duplicates or overwrites an accepted ADR instead of linking or
  superseding it.

## Safe diagnosis

Reproduce in a disposable repository. Start an R2 change, fill its records, run
fresh verification, leave understanding as `not-reviewed`, and run enforce
mode. Inspect only repository-relative evidence and document paths.

## Rollback or repair

Revert the workflow change as one atomic commit if required-record or
current-diff gates regress. Do not reintroduce mandatory teach-back merely to
repair a display or migration bug. Restore the prior evidence schema only with
an explicit compatibility plan and re-run the complete CLI and distribution
suite.

## Escalation and data handling

Do not attach private project briefs, ADRs, or command output to public issues.
Reduce failures to a disposable repository and report security-sensitive
behavior through private vulnerability reporting.
