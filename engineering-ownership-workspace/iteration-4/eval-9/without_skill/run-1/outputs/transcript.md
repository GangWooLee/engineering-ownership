Now updating the tests to match the new fractional behavior:

Now recording the decision reversal, since the existing note explicitly says it stops applying once any partner needs fractional amounts:

Running the test suite to confirm the change works:

Done. Changes to `src/api/partner_adapter.py`:

- Removed the `WHOLE_UNIT_PARTNERS` special-casing entirely — every partner now gets `amount_cents / 100` as a `Decimal` (e.g. `549` → `Decimal('5.49')`), avoiding float rounding error on money.
- Updated `tests/test_partner_adapter.py` to assert fractional amounts for both a former whole-unit partner and a regular one; all tests pass.
- Added `docs/decisions/2026-02-settlement-amount-units.md`'s successor note (`2026-07-settlement-fractional-amounts.md`) since that doc explicitly said it "no longer describes what the code should do" once any partner needed fractional amounts.

One assumption worth flagging: I treated fractional-with-`.00` as a strict superset of whole units, so `p-7` (the other partner previously in `WHOLE_UNIT_PARTNERS`) now also gets fractional amounts even though only "our largest partner" was mentioned as requiring the change. If `p-7`'s API actually rejects amounts with a decimal point (rather than just requiring whole values), that partner will need to go back into a whole-units exception list — let me know if that's the case.