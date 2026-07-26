# 2026-07-25 · Add a terminal close state to change records

Change ID: `add-terminal-close-state`
Created: `2026-07-25T23:55:33+09:00`
Status: Accepted

## Context

Records accumulate so a later human or agent can pick the work up — that is
this tool's stated purpose. Without a terminal state, accumulation is the
failure mode: every completed change permanently pollutes the exact surfaces
documented for resuming (`status`, the bare `handoff`), and the noise grows
linearly with completed work. Eight Briefs already hand-write
`Status: Completed`, which nothing parses: the lifecycle exists as a human
convention the machine model does not own.

## Options considered

1. **Explicit close verb** — `engineering change close <id>` records the
   closing timestamp and HEAD revision. Distinguishes completed from abandoned
   work. Adds one CLI verb, but replaces the hand-written `Status:` convention
   rather than adding alongside it. **Chosen.**
2. **Derived closure** — treat a record as closed once its digest corresponds
   to a committed revision. No new verb, but it cannot distinguish "done" from
   "walked away", and committing alone would silence unfinished work in
   `status`. Rejected: mistaking abandoned work for completed work is the most
   expensive failure for a successor.
3. **Gated close** — require a green `check` before closing. Rejected: the
   tool's ethos is evidence, not enforcement; a gate forces ceremony exactly
   where proportionality is the rule. Closing with open gaps instead prints a
   non-blocking note, and the gaps stay frozen in the record.

## Decision

Option 1, with option 3's non-blocking honesty note. `closed` is an optional
object `{closed_at, revision}` on the v1 evidence schema (additive; no version
bump; existing records validate unchanged). Closed records are filtered in the
presentation callers only — `command_status`, `handoff_text`,
`ownership_hook` — never in `list_evidence` or `evidence_gaps`, because
`refs check` and `engineering check` build on the same shared layer and must
keep seeing closed records. There is no reopen: continuation is a new change
record, as the resume reference already documents.

## Consequences and reversal

Plain `status` and the bare `handoff` become open-work views; audit access to
closed records moves to `status --all`, `handoff --change <id>`, and `explain`.
A record closed by mistake stays closed; the recovery is a new change record
linking the old one. Reversal of this whole change is a single revert: prior
code ignores unknown keys, so records carrying `closed` remain fully readable
under reverted code and simply reappear in `status` — the exact pre-change
behavior.

## Implementation references

- `plugins/engineering-ownership/src/engineering_ownership/cli.py`
- `plugins/engineering-ownership/src/engineering_ownership/evidence.py`
- `plugins/engineering-ownership/hooks/ownership_hook.py`

## Supersession

Supersedes: None
Superseded by: None
