I've recovered the state of this in-progress change. Here's where things stand:

**Change record:** `partner-settlement-rounding` (R2, opened 2026-07-18, review was due 2026-07-25 — one day overdue). Original ADR decision: convert cents → whole units once inside `to_partner_payload`, keep the DB stored in cents (`docs/engineering/decisions/partner-settlement-rounding.md`).

**Uncommitted diff on top of that (from the prior session):**
- Adds `WHOLE_UNIT_PARTNERS = {"p-1", "p-7"}` and floor-divides `amount_cents // 100` for those partners.
- Adds a `settlementCurrency` field to the payload and a matching `settlement_currency` column in `orders` (default `'USD'`).
- Leaves the exact TODO the Brief already flagged as unresolved: *"partners that settle in fractional units still need a rule."*

**Two things I found that block safely continuing this (both are money-correctness decisions, not implementation details):**

1. **Silent truncation bug in the new code.** `amount // 100` floors instead of rounds — e.g. 501 cents → `5`, quietly dropping $0.01. The ADR itself names "wrong conversion silently under/over-reports money" as the top risk here, so I don't want to leave floor division in place without confirming that's intentional.
2. **The TODO is a real gap, not just a comment.** Non-`WHOLE_UNIT_PARTNERS` currently still get raw `amount_cents` (e.g. `501`) sent as `amount`, unchanged. If "fractional units" means those partners expect a decimal currency amount (e.g. `5.01`), that conversion doesn't exist yet — and no test covers either path.

Before I write code: what's the rule for these two cases?
- **Rounding for whole-unit partners:** round to nearest whole unit (e.g. round-half-up) instead of truncating, or should fractional cents be an error condition?
- **Fractional-unit partners:** should they receive `amount_cents / 100` as a decimal (e.g. `5.01`), and to how many decimal places?

If you'd rather I just make the call, my default would be: round-half-up to nearest whole unit for `WHOLE_UNIT_PARTNERS`, and send `amount_cents / 100` as a 2-decimal value for everyone else — let me know if that's fine or if the partner API has different requirements.