I'll look at the repo to find the proposal and implementation plan first.

Found the docs. Let me read the proposal, plan, and recent change/decision notes to understand full scope.

There's a `.engineering/` contract/evidence system too. Let me check that before creating tracking docs.

The `engineering` CLI is available. Let's check the `change` subcommand's options before starting the record.

Now I'll start tracking the settlement-currency change with the CLI, matching the risk tier used for the other order/schema change.

Now let's fill in the scaffolded brief and ADR with the actual content from the proposal and plan.

Now let's verify the contract's `check` command is satisfied for this fill-required content, and confirm status.

The record is created but verification hasn't been bound to the current diff yet. Let's run the test suite and bind evidence.

The `settlement-currency` change is now fully tracked and passing. Let me check what's staged/untracked before summarizing, since I created new files.

Tracking is set up for the settlement-currency change, using this repo's `engineering-ownership` convention (same one `partner-settlement-rounding` uses):

- Started the record: `engineering change start settlement-currency --risk R2 --title "Carry settlement currency on the order"` (R2, since it touches `src/db/**`/`src/api/**` like the sibling change).
- Filled in the brief (`docs/engineering/changes/settlement-currency.md`) and ADR (`docs/engineering/decisions/settlement-currency.md`) from `docs/proposals/settlement-currency.md` and `plans/settlement-currency.md`.
- Ran the unit suite and bound it as verification evidence (`engineering verify settlement-currency --id unit` → passed), so `engineering check --change settlement-currency` now reports **PASS**.

One thing worth flagging: the plan document says steps 1 and 3 are "in progress," but I only found evidence of step 1 (the uncommitted `settlement_currency` column in `src/db/schema.py`) — `src/api/partner_adapter.py` has no currency field yet, and there's no reporting module in the repo. I noted this discrepancy in the brief's "Known limits" section rather than assuming step 3 is done.

Nothing is committed — these are new/modified working-tree files (`docs/engineering/changes/settlement-currency.md`, `docs/engineering/decisions/settlement-currency.md`, `.engineering/evidence/settlement-currency.json`, plus your existing `src/db/schema.py` edit). Let me know if you'd like these committed or if you want to proceed with the remaining implementation steps.