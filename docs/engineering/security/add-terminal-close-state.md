# 2026-07-25 · Add a terminal close state to change records

Change ID: `add-terminal-close-state`
Created: `2026-07-25T23:55:33+09:00`
## Assets and trust boundaries

The evidence records under `.engineering/evidence/` are the asset: they are the
repository's memory of risk, verification, and rationale. The trust boundary is
unchanged — records are written only through the CLI's `save_evidence` path,
which already rejects path escape and symlinks. `close` adds one field through
the same path; it opens no new input surface, no network, no subprocess.

## Attacker-controlled inputs

The change id argument (existing surface, already pattern-validated on read)
and the repository's own git metadata (`head_revision`). A hostile repository
cannot use `close` to write outside `.engineering/evidence/` because the write
path is the existing `save_evidence`.

## Security invariants

- Closing never deletes or rewrites verification history; it adds a field.
- `engineering check` — the enforce/CI gate — is byte-identical before and
  after this change; a closed record can neither satisfy nor block a gate it
  previously did not.
- `refs check` continues to resolve decision references to closed changes, so
  closing cannot be used to orphan a decision marker silently.
- The revision recorded at close is taken from `git rev-parse HEAD` at close
  time, never from user input — no flag exists to backdate or forge it.

## Abuse and failure cases

- Closing someone else's live record to hide it from `status`: visible in git
  history (the evidence JSON is tracked) and recoverable — the record is
  intact, and `status --all` still lists it.
- Closing before the work landed: the gaps freeze in the record and the close
  command prints a non-blocking note naming them; `handoff --change <id>`
  still reports them.
- Accidental close: no reopen by design; recovery is a new change record
  linking the closed one, preserving rather than rewriting history.

## Mitigations and residual risk

Mitigations are the invariants above plus seven regression tests. Residual
risk: a habit of closing with open gaps would erode the record's meaning; the
non-blocking note is the only friction, chosen deliberately (evidence over
enforcement). Revisit if closed-with-gaps becomes the norm in practice.
