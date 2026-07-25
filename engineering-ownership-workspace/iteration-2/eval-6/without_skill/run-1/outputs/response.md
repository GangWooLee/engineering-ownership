I picked up the in-progress work on `partner-settlement-rounding` (docs/engineering/decisions & changes docs, `.engineering/contract.json`). Current uncommitted diff adds `WHOLE_UNIT_PARTNERS` truncation and a new `settlementCurrency` field/schema column. Tests still pass (1 test), but that test only checks `orderId` — it doesn't cover the new conversion logic at all.

Two things need your call before I continue, since they're money-handling decisions the team's own ADR explicitly flagged as unresolved:

1. **Truncation bug**: `amount // 100` for `WHOLE_UNIT_PARTNERS` silently drops the remainder whenever `amount_cents` isn't a multiple of 100 (e.g. 555 cents → 5, losing 55 cents). The `# TODO` in the code admits this. What's the intended rule — floor, round-half-up, ceiling, or reject/flag orders that don't divide evenly for manual review?

2. **Scope**: the accepted ADR (`docs/engineering/decisions/partner-settlement-rounding.md`) says conversion should happen "once inside the adapter boundary" and explicitly lists "changing how amounts are stored" as **not in scope**. The current diff adds a `settlement_currency` column to `src/db/schema.py`. Is that intentional new scope (multi-currency support), or should currency stay out of storage for now and just be a fixed adapter constant?

Once you confirm the rounding rule, I'll implement it, add test coverage for both the whole-unit and default paths, and update the change/decision docs to reflect the resolved gap.