# 2026-08-05 · Let a closed change still record that its owner understood it

Change ID: `reopen-understanding-review`
Created: `2026-08-05T23:41:00+09:00`
Status: Accepted

## Context

`change review` writes `understanding` -- the field recording whether the person
responsible retained an understanding of the change, and any gaps they found. It
is the artifact this project exists to keep.

`add-terminal-close-state` put `ensure_open` on that command, alongside `verify`
and `set-risk`. Its reasoning was that "review obligations end" when a change
closes. That is true of one half of what the command does and false of the
other. `--revisit-days` snoozes the `status --due` view, and a closed change
never becomes due; that half genuinely ends. Recording understanding does not.
An owner reviews their understanding of a change after it lands, which in this
workflow is after it closes.

The result: every closed record is frozen at whatever `understanding` held when
it closed, permanently. In this repository that is `not-reviewed` on all 32
records, with no command able to change any of them. The tool measured
everything except the thing it is for.

It was found when the owner asked for the review to be recorded and the first
invocation was refused.

## Options considered

**A. Leave it and record understanding some other way.** Edit the evidence JSON
directly, or add a second command that writes the field.

**B. Add a reopen verb.** `change reopen <id>` clears `closed`, the owner
reviews, then closes again.

**C. Drop `ensure_open` from `review` entirely.** Any closed record can be
reviewed, `--revisit-days` included.

**D. Split the gate along the seam that was conflated.** Reviewing is allowed on
a closed record; `--revisit-days` is refused there, because its only effect is a
due date on a record that never becomes due.

## Decision

**D.**

A is the shape this project rejects everywhere else. Writing the evidence file
by hand bypasses the schema, the redaction pass over gap text, and the digest
bookkeeping; a second command writing the same field means two writers, and one
of them will drift.

B was close, and was rejected on the terminal-close decision's own reasoning:
"There is no reopen: continuation is a new change record." Reopening to review
would make `closed` a soft state and would put a record back into `status`,
`handoff` and the session reminder as live work, which is what closing exists to
prevent. Reviewing understanding is not continuation of the work.

C removes the refusal but keeps a flag that quietly does nothing. A user passing
`--revisit-days 30` on a closed record would be told a review was recorded and
would reasonably believe a reminder was set. Accepting an argument whose effect
is nil is worse than refusing it.

D keeps `closed` terminal for everything that mutates the work -- verification,
risk, the diff they are bound to -- and reopens only the attestation, which is
not a mutation of the work at all.

## Consequences and reversal

`understanding` becomes writable for the life of a record. That is the intent: a
review can be revised when a later reader finds something, and the existing
`Corrected:` convention already covers saying so in prose.

`revisit_after` is still written for closed records. It is inert -- `--due`
skips closed records -- and the schema requires the field, so omitting it would
mean a schema change to remove data nothing reads.

A closed record can be re-reviewed repeatedly, each write replacing the last.
Nothing keeps a history of reviews; the file holds only the most recent. That is
unchanged from before rather than introduced here, and it is a real limit.

This changes shipped CLI behaviour, so an installed repository that relied on
`review` being refused after close will find it accepted. Nothing in this
project's own workflow depended on that refusal.

Reversal is restoring `ensure_open` on the command. The suite fails on exactly
that, and separately on removing the `--revisit-days` refusal.

## Implementation references

- `plugins/engineering-ownership/src/engineering_ownership/cli.py` --
  `command_change_review`
- `tests/test_cli.py` --
  `test_closed_change_rejects_mutation_but_stays_readable`

## Supersession

Supersedes: None
Superseded by: None
