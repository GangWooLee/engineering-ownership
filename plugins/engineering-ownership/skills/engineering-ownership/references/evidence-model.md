# Evidence model

`.engineering/contract.json` is the repository-owned adapter. Version 2 stores
verification as argv arrays with bounded timeouts and literal, non-secret
environment values. The CLI never invokes a shell.

`.engineering/evidence/<change-id>.json` binds:

- risk and competency tags;
- repository-relative artifact paths;
- verification command IDs and outcomes;
- the exact current diff digest;
- optional understanding state, learning gaps, and revisit date.

`docs/engineering/changes/<change-id>.md` remains the human-readable reasoning
record. Significant decisions live in append-only ADRs and operational recovery
lives in runbooks. Machine evidence does not prove understanding, and an
understanding review does not prove production correctness. Both are visible
without turning the review into a default completion gate.

Contract v1 remains readable by `audit` and `check`. Migration is preview-only
until `engineering contract migrate --write`; the original is preserved as
`.engineering/contract.v1.backup.json`.
