Tracking is set up for the settlement-currency change, using this repo's `engineering-ownership` convention (same one `partner-settlement-rounding` uses):

- Started the record: `engineering change start settlement-currency --risk R2 --title "Carry settlement currency on the order"` (R2, since it touches `src/db/**`/`src/api/**` like the sibling change).
- Filled in the brief (`docs/engineering/changes/settlement-currency.md`) and ADR (`docs/engineering/decisions/settlement-currency.md`) from `docs/proposals/settlement-currency.md` and `plans/settlement-currency.md`.
- Ran the unit suite and bound it as verification evidence (`engineering verify settlement-currency --id unit` → passed), so `engineering check --change settlement-currency` now reports **PASS**.

One thing worth flagging: the plan document says steps 1 and 3 are "in progress," but I only found evidence of step 1 (the uncommitted `settlement_currency` column in `src/db/schema.py`) — `src/api/partner_adapter.py` has no currency field yet, and there's no reporting module in the repo. I noted this discrepancy in the brief's "Known limits" section rather than assuming step 3 is done.

Nothing is committed — these are new/modified working-tree files (`docs/engineering/changes/settlement-currency.md`, `docs/engineering/decisions/settlement-currency.md`, `.engineering/evidence/settlement-currency.json`, plus your existing `src/db/schema.py` edit). Let me know if you'd like these committed or if you want to proceed with the remaining implementation steps.