Tracking is set up for the `settlement-currency` change:

- **Started** `engineering change start settlement-currency --risk R2` (R2: touches `src/db/**` and will touch `src/api/**` per the contract's risk paths, consistent with the sibling `partner-settlement-rounding` change).
- **Brief** (`docs/engineering/changes/settlement-currency.md`) filled from the proposal/plan: problem, success criteria, responsibility search (schema owns the table, `partner_adapter.to_partner_payload` owns the payload), decision link, failure/rollback, and known gaps.
- **ADR** (`docs/engineering/decisions/settlement-currency.md`) records the accepted decision (currency on the order row, not a per-partner table) and why the alternative was rejected.
- **Verified**: `unit` tests pass against the current diff (`engineering verify` bound it).
- `engineering check --mode advise` → **PASS**.

One gap worth flagging: the plan's step 4/5 (reporting read path) references a reporting module that isn't in this repo checkout — I noted that as an unresolved learning gap rather than guessing at its location. Also, unrelated to this: `partner-settlement-rounding`'s revisit date (2026-07-25) is already overdue — let me know if you want that looked at too.