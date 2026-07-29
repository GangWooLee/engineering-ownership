Now I'll update the adapter to remove the whole-unit conversion entirely, since the decision doc itself flags this as the trigger for retiring that logic.

Now update the tests to match:

Let me record a follow-up decision note, since the original doc explicitly says it stops describing reality once a partner needs fractional amounts, and run the tests.

That's just a generic reference, no update needed there. Tests pass.

**Changes:**
- `src/api/partner_adapter.py`: removed `WHOLE_UNIT_PARTNERS` and the whole-unit rounding logic — `to_partner_payload` now always forwards the raw `amount_cents` value, so every partner gets fractional amounts.
- `tests/test_partner_adapter.py`: replaced the whole-unit-rounding tests with one confirming all partners (including the previously special-cased ones) get unrounded cents.
- Added `docs/decisions/2026-07-settlement-fractional-amounts.md` noting that the Feb 2026 whole-unit decision no longer applies, per its own stated expiry condition.