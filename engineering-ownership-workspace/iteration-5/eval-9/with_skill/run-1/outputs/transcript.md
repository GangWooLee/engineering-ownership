CONTRIBUTING.md is explicit: design notes must be updated in the same change when they no longer describe the code. I'll update the adapter, the tests, and the decision doc together.

Now update the design decision doc, since it explicitly said it would stop describing the code once this happened:

Now running the test suite as required by the repo's contribution guidelines:

Tests pass. Summary of changes:

- **`src/api/partner_adapter.py`**: removed `WHOLE_UNIT_PARTNERS` and `_to_whole_units`; `to_partner_payload` now always sends `amount_cents` unchanged, so every partner gets the fractional amount.
- **`tests/test_partner_adapter.py`**: replaced the whole-unit-rounding tests with one covering that all partners (including the former whole-unit ones) receive cents unchanged.
- **`docs/decisions/2026-02-settlement-amount-units.md`**: added a July 2026 update section per `CONTRIBUTING.md`'s requirement to keep design notes in sync, since the note itself said it would stop describing the code once a partner went fractional.