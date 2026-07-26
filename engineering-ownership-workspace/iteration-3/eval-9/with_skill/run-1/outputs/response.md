Done. Summary of the change:

**`src/api/partner_adapter.py`**: removed the `WHOLE_UNIT_PARTNERS` allowlist and its half-up rounding to whole units. Every partner (including the largest, formerly whitelisted for whole units) now gets an exact fractional currency amount via `Decimal(amount_cents) / 100`, computed with `Decimal` rather than float to avoid binary rounding error on money.

**Tests** (`tests/test_partner_adapter.py`): updated to assert `Decimal("5.49")`-style fractional amounts across partners instead of the old rounded-int / raw-cents split.

Since this reverses the prior `partner-settlement-rounding` decision rather than just extending it, I recorded it as a new tracked change (`partner-settlement-fractional-amounts`) with its own brief and ADR, and marked the old ADR `Superseded` with a link forward — preserving the original rationale instead of rewriting it. Fresh unit-test verification, refs check, and the risk gate all pass (`engineering check --mode advise`).