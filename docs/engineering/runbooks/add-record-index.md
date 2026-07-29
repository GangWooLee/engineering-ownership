# 2026-07-29 · Give the engineering records an entry point

Change ID: `add-record-index`
Created: `2026-07-29T16:11:56+09:00`
## Signals and alerts

- `tests/test_docs.py` fails with **"is stale; regenerate it"** — the records
  changed and the committed index did not. Expected after starting, closing, or
  renaming a change.
- **"exists but the index does not list it"** — a document was added under
  `docs/engineering/` that no evidence record claims. Usually an ADR written
  under an R1 record, which allocates no decision file.
- **"links to X, which does not resolve"** — a document moved or was deleted
  while the index still points at it.

## Safe diagnosis

All read-only:

```
engineering index                      # what the records say the table should be
git diff docs/engineering/README.md    # what the committed table says
engineering status --all               # per-record state, including closed
```

For a staleness failure, the first two disagreeing is the whole diagnosis.

## Rollback or repair

- **Stale index** — regenerate. This is the fix for the common case:
  ```
  engineering index --format md --write docs/engineering/README.md
  ```
- **Unclaimed document** — decide which it is. If it belongs to a record, the
  record's risk tier should have allocated it: raise the tier with
  `engineering change set-risk` rather than hand-placing the file. If it
  legitimately stands alone, regenerating lists it as `decision only`, which is
  the honest state.
- **Broken link** — restore the moved document, or if the deletion was
  intended, regenerate so the row disappears with it.
- **Rolling back the feature** — revert the commit. The command, the test file,
  and the generated document are the whole surface; no evidence record is
  modified by this change, so there is nothing to migrate in either direction.

## Escalation and data handling

Local repository data only — no network, no secrets, no home paths. If the
index disagrees with the records and regenerating does not settle it, the
evidence files under `.engineering/evidence/` are the authority and their git
history shows what changed.
