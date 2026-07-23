# 2026-07-23 · Correct public Git attribution and release refs

Change ID: `correct-git-attribution`
Created: `2026-07-23T21:26:36+09:00`
Status: Accepted

## Context

Public commits were pushed with repository-local Git identity belonging to a
different GitHub account. Correcting only future commits leaves the existing
public history attributed incorrectly.

## Options considered

1. Keep published history and correct future identity only.
2. Ask GitHub to associate the other account's noreply address.
3. Rewrite public commit and tag objects after creating recoverable backups.

## Decision

Use option 3 because the user explicitly requested historical correction and
the foreign noreply address cannot safely be reassigned. Rewrite in an isolated
mirror, preserve semantic history, and update `main` plus both release tags in
one atomic force-with-lease push. Rebuild release assets and provenance from
the rewritten tags.

## Consequences and reversal

Commit and tag object IDs change, so downstream clones must reconcile history.
Old IDs remain recoverable from a dated local bundle and temporary remote
backup refs. Rollback uses another atomic force-with-lease push of those refs,
followed by restoration of release assets from the backup bundle/tag builds.

## Implementation references

This is an operational Git history decision and is not enforced in product
code.

## Supersession

Supersedes: None
Superseded by: None
