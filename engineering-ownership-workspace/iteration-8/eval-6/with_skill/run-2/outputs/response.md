Recovered state from `engineering status` and the repo's evidence trail:

**Change record:** `partner-settlement-rounding` (R2, still open, `understanding=not-reviewed`, revisit-by 2026-07-25 — already past due as of today).

**Problem (from the brief):** the partner settlement API rejects amounts unless expressed in whole currency units; orders are stored in cents, so payloads were being rejected. The `known limits` section explicitly flagged: *"Rounding behaviour for partners that settle in fractional units is unresolved."*

**What the uncommitted diff does:**
- Adds `WHOLE_UNIT_PARTNERS = {"p-1", "p-7"}` and floor-divides (`// 100`) the amount only for those two partners — everyone else still gets raw `amount_cents` sent as-is, which doesn't match the brief's premise that the API needs whole units.
- Adds a `settlement_currency` column/field (new scope not mentioned in the brief).
- Leaves a self-contradictory TODO: *"partners that settle in fractional units still need a rule"* — right where it just applied a rule.
- No test covers any of this; `engineering status` confirms the evidence's diff digest is stale and there's no passing verification for the current diff.

This directly affects money sent to partners, and floor division silently drops sub-unit amounts (e.g. 549 cents → 5, losing 49 cents) — the brief's own risk section calls out that a wrong conversion "silently under- or over-reports money." Before I continue, I need you to settle the actual business rule, since guessing here risks misreporting settlements:

1. **Which partners need whole-unit conversion** — is `{"p-1", "p-7"}` a real, known list, or a placeholder? Should it instead be *all* partners (matching the brief's "every payload... is rejected" framing)?
2. **Rounding method** — should fractional cents be floored, rounded to nearest, or rejected/flagged as an error instead of silently dropped?
3. **`settlement_currency`** — is this genuinely needed for this change, or should it be split into its own change (per `AGENTS.md`'s "keep schema changes and adapter changes in separate commits when practical")?

Let me know how you want these resolved and I'll implement, test, and update the change/decision records accordingly.