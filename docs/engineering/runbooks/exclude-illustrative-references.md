# 2026-07-26 · Exclude illustrative decision references from refs check

Change ID: `exclude-illustrative-references`
Created: `2026-07-26T11:26:59+09:00`
## Signals and alerts

- `refs check --all` suddenly reports far fewer "Decision references
  checked" files than expected → an over-broad `refs.exclude` glob is
  swallowing real source paths.
- `engineering: refs.exclude patterns must be repository-relative globs` or
  `Contract 'refs' must be an object` on any command → malformed contract;
  no command runs until fixed.
- A known dangling marker stops being flagged → check whether its path now
  matches an exclusion glob.

## Safe diagnosis

Read the `refs` block of `.engineering/contract.json`, then compare
`refs check --all` scanned-file counts with and without the block (delete it
in a scratch working copy, never in place). `git log -p
.engineering/contract.json` attributes any exclusion change. All diagnosis
is local file reading; no state is mutated.

## Rollback or repair

Delete the `refs` block (or the offending glob) from
`.engineering/contract.json` and rerun `refs check --all`. Absent key means
full scan — rollback needs no code change and no migration. If validation
itself regressed, revert the `validate_contract` hunk in `model.py` and the
`reference_scan_paths` hunk in `cli.py` together; they are independent of
all other contract handling.

## Escalation and data handling

Single-maintainer repository: escalation is opening an issue on
`GangWooLee/engineering-ownership`. The feature touches no secrets, no
personal data, and no network; contract contents and scan results are the
only data involved, both already committed to the repository.
