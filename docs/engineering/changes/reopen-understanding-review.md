# 2026-08-05 · Let a closed change still record that its owner understood it

Change ID: `reopen-understanding-review`
Created: `2026-08-05T23:41:00+09:00`
Risk: R3

## Problem and intended outcome

`change review` is the only command that writes `understanding`, the field
recording whether the person responsible retained an understanding of a change
and what gaps they found. It is the artifact this project exists to keep.

`add-terminal-close-state` gated it behind `ensure_open`, alongside `verify` and
`set-risk`. The consequence went unnoticed until the owner asked for a review to
be recorded and the first invocation was refused: **all 32 records in this
repository are closed, so the field was unwritable on every one of them, and had
been since the day closing shipped.** They all still read `not-reviewed`.

The tool measured risk, verification, artifacts, references and record quality.
The one thing it could not record was the human ownership it is named for.

Intended outcome: a closed record can still record that its owner reviewed it,
while everything that binds a change to a live diff stays closed.

## Success and non-goals

Success: `change review` succeeds on a closed record and writes the same
`understanding` shape; `verify` and `set-risk` are still refused there;
`--revisit-days` is refused on a closed record rather than accepted and ignored;
and reverting either half fails the suite. The last of those could plainly have
gone the other way — the case that pinned the old behaviour listed `review`
among the refused commands, so a change that only edited the code and left that
list alone would have passed nothing and looked green.

Non-goals: a reopen verb, which the terminal-close decision rules out; keeping a
history of reviews, which nothing did before; changing what `--due` shows;
verifying an attestation, which is not possible and is why `self_attested` is
stored.

## Existing responsibilities searched

`ensure_open` already owns "this record is terminal" and is used by `verify`,
`set-risk` and `close`. It stays on all three. Nothing new was written for the
closed check here: `command_change_review` reads the same `closed` key the
guard reads.

The `--due` filter already skips closed records — `add-terminal-close-state`
established that and it is unchanged. That is what makes `revisit_after` inert
on a closed record rather than a live obligation, and why this change does not
need to remove the field.

`redact` already owns gap text, and the schema validator already owns the shape
of `understanding`. Both are untouched.

## System and data flow

`command_change_review` no longer calls `ensure_open`. It reads the record,
notes whether `closed` is set, and refuses `--revisit-days` when it is, because
that flag's only effect is a `status --due` reminder and a closed record never
becomes due. Everything else is as before: gaps are redacted, `reviewed` with
gaps is still rejected, the day bound is still 1-365, and the whole
`understanding` object is replaced.

`revisit_after` is still written on closed records. It is inert and the schema
requires it, so omitting it would mean a schema change to remove data nothing
reads. The first draft did omit it and failed five tests; keeping it is the
smaller change.

The success line says `(closed)` when the record was closed, so the operator can
see which path they took.

## Decisions and trade-offs

The full decision is in
[`reopen-understanding-review`](../decisions/reopen-understanding-review.md).
The close alternative was a `reopen` verb, rejected on the terminal-close
decision's own reasoning: reopening would make `closed` soft and put the record
back into `status`, `handoff` and the session reminder as live work. Reviewing
understanding is not continuation of the work.

Dropping the gate entirely was rejected because it leaves `--revisit-days`
accepted and inert, which tells a user a reminder was set when none was.

## Failure, security, and recovery

The threat model is in
[`reopen-understanding-review`](../security/reopen-understanding-review.md) and
the operational note in
[the runbook](../runbooks/reopen-understanding-review.md).

The failure this widens: each review replaces the whole `understanding` object
and no history is kept, so a second review silently discards the first. That was
already true while a change was open; this change makes the window unbounded.
Nothing enforces the `Corrected:` convention on a re-review.

The failure this change could have introduced and did not: making `closed` soft.
`verify` and `set-risk` are still refused, and the pinned case asserts it in the
same test that asserts review now works, so the two cannot drift apart.

Recovery is restoring one line. No data is migrated and records written under
either behaviour validate under the same schema.

## Verification evidence

| Check | Result |
| --- | --- |
| Review on a closed record | `Recorded self-review: complete-the-fixture-set -> reviewed (closed)` |
| `--revisit-days` on a closed record | Refused: "a closed change never becomes due" |
| `verify` and `set-risk` on a closed record | Still refused with "start a new change" |
| Guard proved by breaking it, the gate | Restoring `ensure_open` fails `test_closed_change_rejects_mutation_but_stays_readable` with `2 != 0` |
| Guard proved by breaking it, the flag | Removing the `--revisit-days` refusal fails the same case with `0 != 2` |
| First draft, omitting `revisit_after` on closed | Failed five tests on the schema's required field; recorded rather than quietly reworked |
| Suite | 98 tests |
| Contract commands (R3: four) | Recorded via `engineering verify` |

## Known limits and learning gaps

- **No review history.** The file holds the most recent review only. A
  re-review that changes a verdict leaves no trace of the earlier one, and this
  change makes re-review possible indefinitely. Nothing enforces recording the
  change in prose.
- **`self_attested` is the whole assurance.** A `reviewed` status means someone
  ran a command. It is not evidence that they understood anything, and this
  change does not improve that — it only makes the claim recordable.
- The gate was wrong for a year of this repository's life and no test noticed,
  because the test that covered it asserted the wrong behaviour confidently.
  Nothing here prevents the same shape of error elsewhere; the only reason this
  one surfaced is that a person tried to use the command.
- Installed repositories that predate this change keep the old behaviour until
  they update, so their closed records remain unwritable.

## References

- [`reopen-understanding-review`](../decisions/reopen-understanding-review.md)
- [threat model](../security/reopen-understanding-review.md),
  [runbook](../runbooks/reopen-understanding-review.md)
- `docs/engineering/decisions/add-terminal-close-state.md` -- where the gate was
  decided, and the "review obligations end" reasoning this narrows
- `plugins/engineering-ownership/src/engineering_ownership/cli.py`,
  `tests/test_cli.py`
