The memory directory is empty — no prior context there. Let me look at the project's own tracking docs to understand the in-progress work.

I have the full picture now: the previous session added a whole-unit rounding fix for partners `p-1`/`p-7` plus a new `settlement_currency` column/field, but left a TODO about fractional-unit rounding, and the conversion itself uses floor division (`// 100`), which truncates rather than rounds — silently dropping fractional cents rather than rounding to the nearest whole unit. That's a real money-correctness bug given the ADR's own stated risk ("wrong conversion silently under- or over-reports money"). I'll fix that, add regression tests, and follow `AGENTS.md`'s guidance to keep schema and adapter changes in separate commits.

The schema change (`settlement_currency` column) looks complete and correct on its own. The adapter has a real bug: `amount // 100` truncates toward zero instead of rounding, which for a whole-unit partner silently shorts them by up to 99 cents on every order. I'll fix that with explicit half-up rounding.

Now let me add regression tests covering the rounding fix, the passthrough case, and the currency field.

Tests pass. Now updating the tracked engineering docs to reflect the fix and the still-open item, and computing a real verification digest for the evidence file.

That's a 64-char sha256 digest: `9392c0f3e254796307521a623a03b9ef8841bbdf20658e8d568adf1963c0c4f1` — good.

Everything passes. Now committing in two commits per `AGENTS.md`'s guidance to keep schema and adapter changes separate.

**Continued and closed out the two open items in `orders-service`:**

1. **Fixed a real bug**: the whole-unit conversion for partners `p-1`/`p-7` used integer floor division (`amount_cents // 100`), which truncated rather than rounded — silently shorting the settled amount by up to 99 cents on any order with a remainder. Now uses `Decimal` with `ROUND_HALF_UP`.
2. **Added regression tests** for the rounding fix, the non-whole-unit passthrough, and the `settlementCurrency` field (default + pass-through).
3. **Committed in two commits** per `AGENTS.md`'s convention: schema change (`settlement_currency` column) separate from the adapter fix + tests + doc updates.
4. **Updated the change doc and evidence record** to reflect the fix and re-verification.

**Open item, left as-is rather than guessing**: `settlement_currency` now travels through the payload, but the adapter doesn't yet vary rounding precision by currency (e.g. 0-decimal JPY, 3-decimal KWD) — it assumes 2 decimals for all whole-unit partners. That's a business decision, not something I should invent silently for a money-handling path. It's flagged in the change doc and evidence file with `revisit_after: 2026-08-09` — let me know if you want to define that rule now.