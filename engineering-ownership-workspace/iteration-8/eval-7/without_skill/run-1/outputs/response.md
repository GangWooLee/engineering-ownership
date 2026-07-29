Tracking is now set up using this repo's engineering-ownership workflow (the same one used for the earlier `partner-settlement-rounding` change):

- Started change record `settlement-currency` (risk R2) via `engineering change start`
- Filled in the **Brief** (`docs/engineering/changes/settlement-currency.md`) with the problem, success criteria, the rejected per-partner-table alternative, and the 5-step status from `plans/settlement-currency.md` (steps 1 & 3 in progress, 2/4/5 not started — flagging that step 4/5's reporting path doesn't exist yet in this repo)
- Filled in the **ADR** (`docs/engineering/decisions/settlement-currency.md`) recording the accepted decision and rejected alternative from the proposal
- Ran the unit tests and bound a passing verification to the current diff via `engineering verify settlement-currency`
- `engineering check --mode advise --change settlement-currency` → **PASS**

These three new files plus the already-modified `src/db/schema.py` are staged in the working tree but not committed — let me know if you'd like me to commit them.