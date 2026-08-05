# 2026-08-05 · Let a closed change still record that its owner understood it

Change ID: `reopen-understanding-review`
Created: `2026-08-05T23:41:00+09:00`
## Assets and trust boundaries

The asset is the `understanding` object inside `.engineering/evidence/<id>.json`
in the repository where the plugin is installed: a status, a list of gap strings,
a timestamp, and `self_attested`. It is committed, so in a public repository it
is public.

The boundary this change moves is temporal, not one of privilege. Before, that
object was writable only while a change was open. Now it is writable for the
life of the record. Nobody gains access who did not already have it: writing
requires the ability to run the CLI in a checkout, which is the ability to edit
the file directly.

Everything else stays inside the repository. The command opens no socket, runs
no subprocess, reads no environment secret, and touches no path outside
`.engineering/`.

## Attacker-controlled inputs

- **`--gap <text>`** -- free text from the invoker, stored verbatim after
  `redact`. The only untrusted-shaped input in the command.
- **`<change_id>`** -- resolved through the same path handling as every other
  subcommand, which rejects traversal and symlink escapes.
- **`--status`** -- constrained by `argparse` to `reviewed` or `gaps`.
- **`--revisit-days`** -- bounded to 1-365, and now refused outright on a closed
  record.

The evidence file itself is also an input, since the command reads and rewrites
it. A malformed or hostile file is the schema validator's problem, and this
change does not weaken that: the record is validated on read and on save exactly
as before.

## Security invariants

1. A review can never raise or lower the record's risk tier, alter its
   verification results, or change its `closed` state. This change touches
   `understanding` and `updated_at` and nothing else.
2. `closed` remains terminal for `verify` and `set-risk`. Reviewing is not
   continuation of work and does not make the record live again -- it stays out
   of `status`, `handoff` and the session reminder.
3. Gap text passes through `redact` before it is written, so a home path or the
   repository's own absolute location is normalised out.
4. `self_attested` is always `true`. The tool never asserts that a review was
   independently confirmed.

## Abuse and failure cases

**A review that overwrites a real one.** Each write replaces the whole
`understanding` object and no history is kept, so a second review silently
discards the first. This is the sharpest consequence of making the field
writable for the life of the record. It is not new -- the same was true while a
change was open -- but the window is now unbounded. The mitigation is social:
the `Corrected:` convention already requires saying so in prose when a record's
content changes.

**A false attestation.** Someone can record `reviewed` without having reviewed
anything, and the file will say a person understood the change. This was already
true and is the honest limit of a self-attested field; `self_attested: true` is
stored precisely so no reader mistakes it for a signature.

**Secrets in gap text.** `redact` normalises paths, not credentials. A gap
saying "the token in config was wrong" would be committed as written.

**Confusion from an inert `revisit_after`.** A closed record carries a future
date that `--due` will never act on. Someone reading the JSON could take it as a
pending obligation. The refusal of `--revisit-days` on closed records removes
the path by which a user would deliberately set one and expect it to fire.

## Mitigations and residual risk

Mitigated: privilege is unchanged, the risk and verification fields are
untouched, closed stays terminal for work, gap text is redacted, and the
misleading flag is refused rather than silently accepted. Two guards pin the
behaviour and both were checked by breaking them.

Residual, and accepted: a review can be silently overwritten and the previous
one is not recoverable from the file; a `reviewed` status is a claim and not
evidence; and `redact` does not remove secrets a person chooses to type into a
gap. None of these are introduced here. The first is widened in time by this
change, and that is the price of a field that could not otherwise be written at
all.
