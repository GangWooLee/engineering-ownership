Tracking is set up. I won't commit unless you'd like me to — just let me know.

Summary of what's in place for `settlement-currency` (R2):
- **Brief**: `docs/engineering/changes/settlement-currency.md` — problem, scope, and searched ownership (schema owns the column, adapter owns the payload), linking back to the proposal and plan, and noting it's a sibling to `partner-settlement-rounding`.
- **ADR**: `docs/engineering/decisions/settlement-currency.md` — records the "store on order, not a per-partner table" decision already agreed in the proposal.
- **Evidence**: bound to the current diff (`src/db/schema.py`), with the `unit` verification passing.

Per the plan, steps 1 (schema) and 3 (adapter payload) are in progress, and steps 2 (backfill), 4 (reporting read), 5 (remove hard-code) are not started — that's captured in the Brief's "Known limits" section. One gap worth flagging: I couldn't find a reporting module in `src/` yet, so I can't tell where the hard-coded currency for steps 4/5 actually lives — worth confirming before continuing.