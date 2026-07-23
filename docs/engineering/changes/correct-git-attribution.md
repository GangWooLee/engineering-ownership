# 2026-07-23 · Correct public Git attribution and release refs

Change ID: `correct-git-attribution`
Created: `2026-07-23T21:26:36+09:00`
Risk: R3
Status: In progress

## Problem and intended outcome

All eight public commits use a GitHub noreply address attributed to another
account even though the repository and authenticated GitHub CLI account belong
to `GangWooLee`. Rewrite author and committer identity to the authenticated
account without changing source trees, messages, timestamps, topology, version
names, or release contents.

## Success and non-goals

- Every rewritten commit resolves to `GangWooLee` through the GitHub API.
- `main`, `v0.1.0`, and `v0.2.0` move together from expected old object IDs.
- Commit count, parent topology, source trees, messages, and dates remain
  equivalent after mapping old commits to new commits.
- Release ZIPs are rebuilt from the rewritten tags, checksums match, and fresh
  provenance exists for each released ZIP.
- A local bundle and remote backup refs make the old history recoverable.
- Do not modify product behavior, versions, release notes, or unrelated Git
  configuration.

## Existing responsibilities searched

Reuse Git refs as the source of truth, the repository release builder for ZIP
creation, GitHub Releases for assets, and the existing release workflow for
provenance. No application code owns commit attribution.

## System and data flow

Authenticated GitHub account ID and login determine the correct noreply
address. A mirror clone rewrites commit identity and annotated tags. Verified
refs are pushed atomically with explicit leases. GitHub Actions rebuilds and
attests the release ZIPs; release assets are then replaced with those exact
builds.

## Decisions and trade-offs

See `docs/engineering/decisions/correct-git-attribution.md`. The user explicitly
requested historical correction after future attribution was fixed. Leaving
history unchanged is safest but does not meet that outcome; rewriting directly
in the working clone was rejected in favor of an isolated mirror and backups.

## Failure, security, and recovery

See the threat model and runbook. Never print the full commit email or tokens.
Abort on ref drift, tree/message/date mismatch, non-atomic push failure, CI
failure, or release digest mismatch.

## Verification evidence

Pending isolated rewrite comparison, atomic ref update, GitHub author
resolution, CI, release checksum, and provenance verification.

## Known limits and learning gaps

Existing downstream clones keep the old history until users rebase or clone
again. GitHub contribution rendering may take up to 24 hours after attribution
is corrected.

## References

- `docs/engineering/decisions/correct-git-attribution.md`
- `docs/engineering/security/correct-git-attribution.md`
- `docs/engineering/runbooks/correct-git-attribution.md`
