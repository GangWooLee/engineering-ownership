I've restored context on this change using the repo's engineering-ownership records rather than guessing from the diff alone.

**Recovered state**
- Open change: `partner-settlement-rounding` (started 2026-07-18). Brief and ADR say: orders are stored in cents; some partners' settlement API rejects non-whole-unit amounts; the adapter should convert once at the boundary. The brief's own "Known limits" section already flagged: *"Rounding behaviour for partners that settle in fractional units is unresolved."*
- Current uncommitted diff adds `WHOLE_UNIT_PARTNERS = {"p-1", "p-7"}`, truncates their amount via `amount // 100`, and adds a `settlement_currency` column/field (default `"USD"`).
- Tests still pass, but the one existing test only checks `orderId` — nothing exercises the new conversion or currency field.
- This is money-handling touching persistence + an external payload contract, so I raised it from R2 to R3 (`engineering change set-risk`), which scaffolded a runbook and threat-model stub that still need content.

**Two real gaps, not just style nits**

1. **Truncation looks like the exact bug the brief warns about.** `amount // 100` floors — e.g. 501 cents → 5, silently dropping 1 cent every time the amount isn't a clean multiple of 100. The brief explicitly calls this failure mode out ("silently under- or over-reports money"), so I don't want to assume floor-division is intentional without confirming: are amounts for `p-1`/`p-7` guaranteed to already be whole dollars, or can they carry cents that get lost?
2. **The actual TODO is still unimplemented.** `settlement_currency` was added but nothing branches on it yet — the code still only distinguishes "whole-unit partners" vs. everyone else (unchanged, raw cents). There's no rule yet for partners that need fractional/decimal formatting, and no list of which partners those are.

Both are business decisions about how money gets reported to partners, so I'd rather confirm than guess:

- For `p-1`/`p-7`, should leftover cents be rounded (and if so, half-up or banker's rounding) rather than truncated — or is truncation-to-whole-dollars actually the agreed partner contract?
- What does "fractional units" partner mean concretely here — decimal string amount (e.g. `"5.01"`), and do you have the partner IDs/currencies for that category, or should I just record this as an open gap for now and land only the currency-plumbing part?

Let me know how you'd like to resolve the rounding rule, and I'll finish the implementation, add test coverage, and update the evidence/runbook/threat-model records accordingly.