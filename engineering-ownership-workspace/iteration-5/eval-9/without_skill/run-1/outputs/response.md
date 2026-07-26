Tests pass. Summary of changes:

- **`src/api/partner_adapter.py`**: Removed the `WHOLE_UNIT_PARTNERS` special case and half-up rounding. Every partner now gets `amount_cents / 100` as a `Decimal` fractional amount (e.g., `549` cents → `Decimal("5.49")`), avoiding float precision issues.
- **`tests/test_partner_adapter.py`**: Updated to verify fractional conversion applies uniformly across partners, including the former whole-unit ones (`p-1`, `p-7`).
- **`docs/decisions/2026-07-settlement-fractional-amounts.md`**: Added a new ADR superseding the February one, since that doc explicitly said it would stop describing the code once any partner required fractional amounts.