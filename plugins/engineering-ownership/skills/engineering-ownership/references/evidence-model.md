# Evidence model

`.engineering/contract.json` is the repository-owned adapter. Version 2 stores
verification as argv arrays with bounded timeouts and literal, non-secret
environment values. The CLI never invokes a shell.

`.engineering/evidence/<change-id>.json` binds:

- risk and competency tags;
- repository-relative artifact paths;
- verification command IDs and outcomes;
- the exact current diff digest;
- teach-back state, learning gaps, and review date.

`docs/engineering/changes/<change-id>.md` remains the human-readable reasoning
record. Machine evidence does not prove understanding. A self-attested
teach-back does not prove production correctness. Both are visible so reviewers
can make their own decision.

Contract v1 remains readable by `audit` and `check`. Migration is preview-only
until `engineering contract migrate --write`; the original is preserved as
`.engineering/contract.v1.backup.json`.

