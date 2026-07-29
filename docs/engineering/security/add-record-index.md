# 2026-07-29 · Give the engineering records an entry point

Change ID: `add-record-index`
Created: `2026-07-29T16:11:56+09:00`
## Assets and trust boundaries

| Asset | Boundary |
| --- | --- |
| Evidence records under `.engineering/evidence/` | Read-only here. `index` never writes them. |
| The generated index at `docs/engineering/README.md` | Written only through `write_repo_text`, which rejects path escape and symlinks. |
| Change ids and titles | **Newly public in aggregate.** They were always committed; the index collects them onto one page a reader will actually open. |

## Attacker-controlled inputs

Two, both pre-existing. The `--write` path is user-supplied and goes through
`write_repo_text` — the same guard every other writing command uses, so
absolute paths, `..` traversal, and symlinked destinations are rejected before
any write. Record titles and change ids come from the repository's own evidence
files and are emitted into markdown; a title containing a pipe or bracket can
distort the table but cannot escape the document, and those files are already
trusted input to `status`, `handoff`, and `explain`.

## Security invariants

- `index` reads evidence and the decisions directory, writes exactly one file
  and only when `--write` is given, and never outside the repository.
- No command output, environment value, secret, or home path enters the index.
  It renders change ids, titles, risk tiers, close timestamps, truncated
  revisions, and repository-relative document paths — nothing else.
- The index cannot change verification state or risk. It is a view.
- `engineering check` is untouched: nothing here participates in a gate.

## Abuse and failure cases

- **A misleading title.** Titles are author-written and now surface on the
  front page for records. Nothing validates that a title describes its change;
  the record remains the authority. Stated rather than guarded, because
  checking prose for accuracy is not something a test can do.
- **Information aggregation.** Everything in the index was already committed,
  but scattered. If a change id or title ever names something that should not
  be public, the index is where that becomes obvious — an argument for naming
  records carefully, and the reason this is written down.
- **Overwriting a hand-authored file.** `--write` overwrites unconditionally by
  design, because the target is a generated artifact. Pointing it at a written
  document would destroy that document; the runbook covers the repair.

## Mitigations and residual risk

The write path reuses the existing rejection of escapes and symlinks rather
than introducing a second one. The staleness test regenerates and compares, so
a committed index that disagrees with the records fails the suite.

Residual: an index can be current, valid, and still describe a change badly,
because the accuracy of a title is a human judgement. Every row links to the
records behind it for exactly that reason.
