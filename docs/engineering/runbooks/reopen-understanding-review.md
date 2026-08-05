# 2026-08-05 · Let a closed change still record that its owner understood it

Change ID: `reopen-understanding-review`
Created: `2026-08-05T23:41:00+09:00`
## Signals and alerts

There is no alert. This change has no runtime, no service and no schedule; it
alters what one CLI subcommand accepts. The signals are what a person notices.

- **`engineering change review <id>` is refused on a closed record**, with
  "start a new change to continue". The change has been reverted or the
  installed plugin predates it.
- **`engineering status --all` shows `understanding=not-reviewed` on records
  that were reviewed.** The review wrote to a different repository root, or
  `save_evidence` failed silently. Check the file's `updated_at`.
- **`--revisit-days` is accepted on a closed record.** The refusal has been
  removed; a user may believe a reminder is set that will never fire.
- **`engineering status --due` starts listing closed records.** Unrelated to
  this change, but it would mean the closed filter broke and the inert
  `revisit_after` this change leaves on closed records became live.

## Safe diagnosis

All read-only.

```text
engineering status --all                 # understanding= per record
engineering handoff --change <id>        # closed state and gaps together
engineering explain <id>                 # readable whether open or closed
```

To see what was actually stored, read `.engineering/evidence/<id>.json` and look
at `understanding`: `status`, `gaps`, `reviewed_at`, `revisit_after`,
`self_attested`. On a closed record `revisit_after` is present and inert by
design -- `--due` skips closed records -- so a future date there is not a
pending obligation.

To confirm the behaviour without touching a real record, run the pinned case:

```bash
python3 -m unittest tests.test_cli.CliCase.test_closed_change_rejects_mutation_but_stays_readable
```

It asserts both halves: review accepted on a closed record, `--revisit-days`
refused there, and `verify` and `set-risk` still refused.

## Rollback or repair

Rollback is restoring `ensure_open` in `command_change_review` and reverting the
test. No data migration is involved: nothing this change writes has a new shape,
and records reviewed while it was in effect stay valid under the schema either
way. They simply become unmodifiable again.

Repair for a review recorded against the wrong record is to re-run
`change review` on the right one and again on the wrong one with the state it
should have had. Each write replaces the whole `understanding` object, so there
is no partial state to clean up -- and no history: the previous review is gone.
If the earlier review mattered, record what it said in the change record's prose
before overwriting.

There is nothing to roll forward. A repository that never runs `change review`
is in the same state it was before.

## Escalation and data handling

`gaps` text is written by a person and passes through `redact` before it is
stored, the same pass used for handoff text. It is the one place in this command
where free text reaches a file, and the file is committed. A gap that would
name a credential, a customer, or a path outside the repository should not be
written; the redaction pass is a backstop, not a permission.

`self_attested: true` is stored on every review. It means the tool did not
verify the claim and no one else signed it. Do not read a `reviewed` status as
independent confirmation of anything.

Escalation, for a repository that installs this plugin: this command writes only
inside `.engineering/` in the current repository, sends nothing anywhere, and
runs no subprocess. A failure here cannot affect a service. Nothing needs to be
escalated beyond the person who owns the record.
