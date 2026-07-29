I'll check the current state of these changes before marking anything complete — the last commit message says "in progress," which is worth verifying against.

I wouldn't mark this complete — I looked at the actual diff and test coverage, and there's a real gap:

**What the diff does:**
- `schema.py`: adds a `settlement_currency` column (defaults to `'USD'`)
- `partner_adapter.py`: for two hardcoded partners (`p-1`, `p-7`), divides `amount_cents` by 100 to settle in whole units; everyone else still gets raw cents

**The problem:** there's a `# TODO: partners that settle in fractional units still need a rule.` left directly in the code — the author flagged the rounding logic as incomplete, and the commit message itself says "in progress." Any partner that isn't `p-1`/`p-7` but also doesn't settle in raw cents (e.g. anyone using the new `settlement_currency` field for a non-USD, fractional-unit currency) gets silently wrong amounts sent to the partner API — that's a financial correctness bug, not a nice-to-have.

**The "tests passed" claim is misleading:** the only test in `tests/test_partner_adapter.py` checks that `orderId` is copied through. Nothing exercises `WHOLE_UNIT_PARTNERS`, the new `amount` rounding, or `settlementCurrency`. A green suite here just means the untouched assertion still passes — it says nothing about the new logic.

I'd hold off on marking this done. Options:
1. Have the agent (or I) finish the fractional-unit rounding rule and add tests for both branches before calling it complete.
2. If `p-1`/`p-7` are the only partners in production today, land it as explicitly partial with a tracked follow-up ticket — but don't represent it as finished.

Want me to implement the missing rounding rule and tests, or would you rather scope that separately?