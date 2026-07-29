I looked at the uncommitted diff plus the change/decision artifacts under `docs/engineering/` and `.engineering/`, and found a real conflict before writing more code.

**State:** `src/api/partner_adapter.py` and `src/db/schema.py` have uncommitted changes from the "partner settlement rounding" work (commit `aba224f`). Tests still pass (1 test), but it doesn't cover the new logic.

**The conflict:**
- The accepted ADR (`docs/engineering/decisions/partner-settlement-rounding.md`) explicitly rejected "store a second column" and chose "convert once inside the adapter boundary" — a partner-ID-based rule (`WHOLE_UNIT_PARTNERS`), no schema change.
- The in-progress diff does the opposite of that: it adds a `settlement_currency` column to `schema.py`. That's a design shift the ADR doesn't document.
- The adapter still has an open `TODO`: "partners that settle in fractional units still need a rule."
- Separately, `amount // 100` for whole-unit partners *truncates* rather than rounds — e.g. 550 cents ($5.50) becomes `5`, silently dropping 50 cents. The decision doc itself flags this exact risk ("a wrong conversion silently under- or over-reports money"), so I don't want to guess.

Before I continue, I need you to pick the actual rule, since it changes both the schema and the ADR:

1. **Keep the ADR's original design** (partner-whitelist only, no currency column) — then I should drop `settlement_currency` from `schema.py`/the adapter and just fix the TODO by deciding what fractional-unit partners get (raw cents? rounded-to-nearest-cent whole value?).
2. **Supersede the ADR with a currency-driven rule** — convert based on each currency's minor-unit count (e.g. 2 decimals for USD/EUR, 0 for JPY, 3 for BHD/KWD) using the new `settlement_currency` column, replacing the partner-ID whitelist entirely. This is more correct long-term but means updating the ADR ("Superseded by") and the change brief.

Which direction do you want, and for whole-unit partners should truncation become rounding (round-half-up, presumably) instead of floor division?