# 2026-07-23 · Correct public Git attribution and release refs

Change ID: `correct-git-attribution`
Created: `2026-07-23T21:26:36+09:00`
## Signals and alerts

- Remote ref differs from the recorded lease.
- Rewritten commit count or semantic comparison differs.
- GitHub API author is not `GangWooLee`.
- CI, release build, checksum, or attestation verification fails.

## Safe diagnosis

Stop before pushing when any local comparison fails. After pushing, inspect
`main` and both tag object IDs, Actions runs, GitHub commit author resolution,
Release asset digests, and attestations. Do not delete backups during
diagnosis.

## Rollback or repair

Use the dated bundle or remote `backup/pre-attribution-rewrite-*` refs to
restore the previous `main` and release tags with explicit leases and an atomic
push. Rebuild and replace both Release assets from the restored tag state.
Verify old commit IDs, CI, checksums, and Release downloads before removing the
incident status.

The retained remote recovery refs for this operation are:

- `backup/pre-attribution-rewrite-main-20260723-212812`
- `backup/pre-attribution-rewrite-v0.1.0-20260723-212812`
- `backup/pre-attribution-rewrite-v0.2.0-20260723-212812`

## Escalation and data handling

Do not publish the full old or new noreply email, GitHub token, or local backup
path. If GitHub rejects atomic updates or release replacement, preserve all
backups and stop for user review rather than weakening leases or deleting
releases.
