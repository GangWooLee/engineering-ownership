# 2026-07-25 · Add a terminal close state to change records

Change ID: `add-terminal-close-state`
Created: `2026-07-25T23:55:33+09:00`
Risk: R3
Corrected: 2026-08-05 — `change review` was gated on the change being open, on
the reasoning that "review obligations end at close". That holds for the `--due`
snooze and not for recording the owner's understanding, which happens after work
lands. The gate left `understanding` frozen at `not-reviewed` on every closed
record. Narrowed in `reopen-understanding-review`.

## Problem and intended outcome

The evidence-record lifecycle has no terminal state. Executed evidence from the
cold audit of this repository: plain `engineering status` lists all 11 records
with 47 permanently false gap lines (every historical record's digest can never
match the current tree again); the bare `engineering handoff` dumps every record
into every handoff; the opt-in session hook's "Stale passing verification
records: N" grows monotonically. The documented resume flow's first step
(`references/resume.md`) is plain `status` — the exact surface that buries the
live record under every completed one, linearly with completed work. Eight
Briefs hand-write `Status: Completed`, a line no code writes or reads; the Brief
template hardcodes `Status: In progress`. There is no retirement path at all:
no CLI verb, `change review --revisit-days` is a bounded snooze on `--due`
only, and hand-deleting an evidence JSON breaks `refs check`.

Intended outcome (owner's decision, recorded in conversation): an explicit
`engineering change close <id>` that records the closing timestamp and HEAD
revision, consumed by `status`, the bare `handoff`, and the session hook — so
the surfaces documented for resuming show open work only, while closed records
stay on disk, readable, and referenced.

## Success and non-goals

Success: a closed record leaves plain `status` (still listed by `status
--all`), leaves the bare `handoff`, and leaves the hook's stale count;
`refs check` still passes with references to closed changes; `engineering
check` behavior is byte-identical; all 11 existing evidence records remain
readable with no data rewrite; the full suite passes with seven new tests.

Non-goals: a reopen verb (continuation is a new change record, per
`references/resume.md`); a completion gate on close (evidence over enforcement
— closing with open gaps prints a non-blocking note instead); deriving closure
from commit state (rejected: it cannot distinguish completed from abandoned
work, the most expensive confusion for a successor).

## Existing responsibilities searched

`change review` was examined as a possible completion mechanism: it snoozes the
`--due` view for at most 365 days and suppresses nothing else — a review
cadence, not a lifecycle. The hand-written `Status:` Brief convention was
examined: no parser exists except `decision_is_superseded`, which reads ADRs
only. `list_evidence`/`evidence_gaps` stay untouched as the shared pure layer;
filtering happens in the presentation callers (`command_status`,
`handoff_text`, the hook) because `reference_gaps` and `command_check` build on
the same record list and must keep seeing closed records.

## System and data flow

`change close <id>` → `ensure_open` → set `closed = {closed_at, revision}`
(full HEAD SHA; displayed truncated to 12, matching the handoff's revision
display) → `save_evidence`. Consumers: `command_status` skips closed records
unless `--all`; `--due` never matches a closed record (the *scheduling* half of
review ends at close — see the correction below); `handoff_text` without
`--change` lists open records only, and with
`--change` reports the close line for audit; `ownership_hook` excludes closed
records from both the current-change list and the stale count. Mutating verbs
(`verify`, `change set-risk`, `change review`, second `close`) reject closed
records; read verbs (`explain`, `check --change`, `refs check`, `handoff
--change`) keep working.

(Corrected 2026-08-05: `change review` should not have been in that list, and
"review obligations end at close" was true of only half of what it does. The
command both snoozes the `--due` view and records whether the owner understood
the change; the first ends at close, the second is what an owner does after the
work lands. Gating both froze `understanding` at `not-reviewed` on every closed
record — all 32 in this repository — with no command able to change any of them,
from the day this shipped until it was found. Narrowed in
[`reopen-understanding-review`](reopen-understanding-review.md): reviewing is
allowed on a closed record, `--revisit-days` is refused there, and `verify` and
`set-risk` stay closed.)

## Decisions and trade-offs

See `docs/engineering/decisions/add-terminal-close-state.md` — explicit close
versus derived closure, and no-gate versus gated close. This change replaces
the hand-written `Status:` markdown convention; it does not add a second one
(the Brief template's `Status: In progress` line is removed).

## Failure, security, and recovery

See the linked threat model. The single failure that matters: a record closed
by mistake cannot be reopened — the documented continuation is a new change
record linking the old one, which preserves history instead of rewriting it.

## Verification evidence

- `python3 -m unittest discover -s tests`: 79 tests pass (72 pre-existing,
  7 new: 6 in `test_cli.py`, 1 in `test_hooks.py`).
- All four contract commands pass for this change via `engineering verify`;
  `engineering check --mode advise --change add-terminal-close-state`: PASS.
- `engineering refs check --change add-terminal-close-state`: PASS. The new
  regression test proves references to closed changes keep resolving in a
  clean repository.
- Migration executed with the new verb: the 10 finished records closed; plain
  `status` now reports open records only.

## Known limits and learning gaps

- `audit_payload` still counts all evidence records without an open/closed
  split; deferred deliberately to keep the R3 diff minimal.
- `closed_at` records when the terminal state was recorded, not when work
  finished — finish timing already lives in `updated_at`, `verified_at`, and
  git history; a backdating flag was rejected because it would let records
  claim states that were never observed.
- Discovered while verifying: repository-wide `engineering refs check --all`
  was already BLOCKED before this change by ~10 pre-existing dangling
  references (test literals, tutorial examples, committed eval artifacts,
  and an eval fixture). Out of scope here; flagged as separate work. This
  change's new test composes its marker at runtime so it adds no new gap.

## References

- `plugins/engineering-ownership/src/engineering_ownership/cli.py`
- `plugins/engineering-ownership/src/engineering_ownership/evidence.py`
- `plugins/engineering-ownership/src/engineering_ownership/resources/schemas/evidence-v1.schema.json`
- `plugins/engineering-ownership/hooks/ownership_hook.py`
- `docs/engineering/decisions/add-terminal-close-state.md`
