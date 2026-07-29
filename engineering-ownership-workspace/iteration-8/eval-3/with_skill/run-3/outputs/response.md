I checked the actual diff, the test suite, and ran it — this isn't ready to mark complete:

**What "tests passed" actually covered:** The only test in `tests/test_partner_adapter.py` just checks that `orderId` is passed through. It exercises none of the new logic — not the rounding, not `settlement_currency`, not the schema change. A green test run here doesn't validate this change.

**The change itself is explicitly unfinished:**
- `src/api/partner_adapter.py:9` does `amount = amount // 100` for `WHOLE_UNIT_PARTNERS`, converting cents to whole units by floor division — this silently truncates fractional cents. In settlement code, that's a real money-loss bug (e.g. 1099 cents → 10, dropping 99 cents).
- There's a `# TODO: partners that settle in fractional units still need a rule.` left in the code — the author flagged the rounding rule as unresolved.
- The commit message itself is `feat: partner settlement rounding in progress` — "in progress," not done.

I'm not going to mark this complete or fix the rounding rule myself, since that's a business decision (round vs. truncate, who eats the remainder) I shouldn't guess at for money-handling code. Do you want me to:
1. Write tests that pin down the current (truncating) behavior and flag it as a known gap, or
2. Implement a specific rounding rule you specify, or
3. Just leave the TODO and schema change as a documented in-progress state?