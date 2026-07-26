# 2026-07-25 · Add a terminal close state to change records

Change ID: `add-terminal-close-state`
Created: `2026-07-25T23:55:33+09:00`
## Signals and alerts

- `engineering status` suddenly shows no records: check whether everything was
  closed — run `engineering status --all` to see closed records with their
  close dates.
- A record expected to be open rejects `verify`/`review` with "was closed":
  someone closed it; `explain <id>` and git history of
  `.engineering/evidence/<id>.json` show when and at which revision.

## Safe diagnosis

All read-only: `engineering status --all`, `engineering explain <id>`,
`engineering handoff --change <id>` (without `--save`), and
`git log -- .engineering/evidence/<id>.json`. None of these mutate records.

## Rollback or repair

- Wrong record closed: do not edit the JSON by hand. Start a new change record
  that references the closed one and continue there — the closed record stays
  as history.
- Rolling back this feature: revert the single commit. Prior code ignores the
  `closed` key, so records carrying it remain fully readable and simply
  reappear in plain `status`/`handoff` — the pre-change behavior. Optionally
  strip `closed` keys in the revert commit to restore byte-identical output.

## Escalation and data handling

Local repository data only; no secrets, no network, no telemetry. If a closed
record's contents are disputed, the tracked evidence JSON's git history is the
authority.
