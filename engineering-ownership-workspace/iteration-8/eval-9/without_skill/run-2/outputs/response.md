That's just a generic reference, no update needed there. Tests pass.

**Changes:**
- `src/api/partner_adapter.py`: removed `WHOLE_UNIT_PARTNERS` and the whole-unit rounding logic — `to_partner_payload` now always forwards the raw `amount_cents` value, so every partner gets fractional amounts.
- `tests/test_partner_adapter.py`: replaced the whole-unit-rounding tests with one confirming all partners (including the previously special-cased ones) get unrounded cents.
- Added `docs/decisions/2026-07-settlement-fractional-amounts.md` noting that the Feb 2026 whole-unit decision no longer applies, per its own stated expiry condition.