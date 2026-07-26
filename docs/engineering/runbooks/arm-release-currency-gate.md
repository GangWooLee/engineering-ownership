# 2026-07-26 · Fail a tag whose release notes predate shipped content

Change ID: `arm-release-currency-gate`
Created: `2026-07-26T10:52:39+09:00`
## Signals and alerts

- Release job fails at "Verify tag matches package" with "shipped content
  changed after docs/releases/<tag>.md was last amended": the notes are stale.
- Same step, "release notes ... do not exist": the notes file was never
  created for this tag — the v0.2.0 failure shape.

## Safe diagnosis

Read-only, locally: `python3 scripts/validate_release_tag.py <tag>`, then
`git log -1 --format='%ci %h' -- plugins` versus
`git log -1 --format='%ci %h' -- docs/releases/<tag>.md` to see exactly which
shipped commit outran the notes.

## Rollback or repair

- Stale notes: amend `docs/releases/<tag>.md` and the CHANGELOG to cover the
  outrunning commits, commit, delete and re-push the tag. Never hand-publish
  around the gate — that is the exact path that produced the v0.2.0 release
  outside the workflow.
- Gate misbehaving: revert the validator commit; the release job falls back
  to the tag-match and notes-exist checks.

## Escalation and data handling

No secrets or external state; everything the gate reads is repository
history. If the gate blocks and the cause is unclear, the two `git log`
commands above are the whole diagnosis.
