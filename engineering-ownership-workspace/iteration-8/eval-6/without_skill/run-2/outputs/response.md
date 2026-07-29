Fixed a real bug and closed the test gap in the WIP partner-settlement work:

- **Fixed**: whole-unit conversion (`p-1`, `p-7`) was truncating with `//`, silently dropping leftover cents (e.g. $12.50 → 12). Now uses `Decimal` + `ROUND_HALF_UP` to round properly.
- **Added**: 5 new tests covering whole-unit rounding, non-whole-unit passthrough, and `settlementCurrency` default/passthrough — the new logic had zero coverage before. All 6 tests pass.
- **Updated** the change brief with what's resolved and what's genuinely still open.

One thing I didn't touch, and want your call on: `settlement_currency` was added to the schema/payload but isn't used yet — non-whole-unit partners still get raw `amount_cents` regardless of currency. That's fine for 2-decimal currencies (USD, EUR), but wrong for currencies like JPY (0 decimals) or BHD (3 decimals). The brief's "known limits" section already flagged this as unresolved before I picked it up — it needs a business decision on which partners/currencies need it, so I left it as an explicit open item rather than guessing. Let me know if you want to tackle that next.

I haven't committed anything — changes are still in the working tree if you want to review or split them per `AGENTS.md`'s "keep schema and adapter changes separate" guidance before committing.