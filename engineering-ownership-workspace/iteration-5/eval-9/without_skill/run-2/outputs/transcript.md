Now updating the tests to match the new fractional-for-everyone behavior:

Now let's run the tests, and also update the decision doc since the old rationale (rounding to whole units) no longer describes the code:

All tests pass. The decision doc explicitly predicted this change and said it would no longer describe the code, so I'm updating it to reflect the new state rather than leaving it stale:

`src/api/partner_adapter.py` now converts every partner's `amount_cents` to an exact fractional currency unit (`Decimal`, 2 decimal places) instead of rounding whole-unit partners and leaving others as raw cents. Removed `WHOLE_UNIT_PARTNERS`/rounding entirely, updated tests, and updated the decision doc to reflect the new contract. Tests pass.