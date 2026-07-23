# 2026-07-23 · Correct public Git attribution and release refs

Change ID: `correct-git-attribution`
Created: `2026-07-23T21:26:36+09:00`
## Assets and trust boundaries

Protected assets are public source history, release tags, GitHub Release
artifacts, checksums, provenance attestations, credentials, and the recovery
bundle. Trust boundaries are the local working repository, isolated mirror,
GitHub refs, Actions, and Releases.

## Attacker-controlled inputs

Remote refs may change concurrently. Commit metadata and tag objects are
untrusted until compared with the expected eight-commit graph. Tokens and
emails must not be copied into logs or committed artifacts.

## Security invariants

- Only author, committer, and tagger identity may change during rewrite.
- Push only when old remote object IDs match recorded leases.
- Never expose tokens or full email addresses.
- Release files must match their published SHA-256 files and attestations.
- Recovery refs and bundle must exist before destructive remote changes.

## Abuse and failure cases

- Concurrent push is overwritten.
- A tree, message, timestamp, or parent relation changes unexpectedly.
- Only one of the branch or tags is updated.
- Release assets still represent the old tag objects.
- A stale clone later force-pushes the old history.

## Mitigations and residual risk

Use an isolated mirror, old-to-new commit map validation, atomic
force-with-lease, local and remote backups, CI, checksum comparison, GitHub API
author checks, and provenance verification. Residual risk is disruption to
unknown downstream clones; public history consumers cannot be enumerated
completely.
