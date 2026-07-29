**Continued and closed out the two open items in `orders-service`:**

1. **Fixed a real bug**: the whole-unit conversion for partners `p-1`/`p-7` used integer floor division (`amount_cents // 100`), which truncated rather than rounded — silently shorting the settled amount by up to 99 cents on any order with a remainder. Now uses `Decimal` with `ROUND_HALF_UP`.
2. **Added regression tests** for the rounding fix, the non-whole-unit passthrough, and the `settlementCurrency` field (default + pass-through).
3. **Committed in two commits** per `AGENTS.md`'s convention: schema change (`settlement_currency` column) separate from the adapter fix + tests + doc updates.
4. **Updated the change doc and evidence record** to reflect the fix and re-verification.

**Open item, left as-is rather than guessing**: `settlement_currency` now travels through the payload, but the adapter doesn't yet vary rounding precision by currency (e.g. 0-decimal JPY, 3-decimal KWD) — it assumes 2 decimals for all whole-unit partners. That's a business decision, not something I should invent silently for a money-handling path. It's flagged in the change doc and evidence file with `revisit_after: 2026-08-09` — let me know if you want to define that rule now.