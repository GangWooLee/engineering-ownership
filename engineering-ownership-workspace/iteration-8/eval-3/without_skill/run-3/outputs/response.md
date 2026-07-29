I looked at the diff before marking anything complete, and this isn't safe to sign off on:

- **The test suite doesn't actually cover the change.** `tests/test_partner_adapter.py` has one test, and it only asserts `orderId` is passed through. It never checks `amount` — even though the order it uses (`partner_id: "p-1"`, `amount_cents: 500`) hits the new rounding branch. "Tests passed" here means nothing about the rounding logic.
- **There's a live bug in the rounding.** `amount = amount // 100` for `WHOLE_UNIT_PARTNERS` truncates instead of rounding — e.g. `1099` cents → `10`, silently dropping 99 cents on every order for partners `p-1`/`p-7`. That's real money lost per transaction, not an edge case.
- **The code admits it's unfinished**: `# TODO: partners that settle in fractional units still need a rule.` — this is settlement/money logic shipped with a known-missing rule.

Given this touches partner settlement amounts and a schema migration (`settlement_currency` with `DEFAULT 'USD'`), I don't think this should be marked complete as-is.

Do you want me to:
1. Fix the truncation to proper rounding and add real test coverage for the amount/currency fields, or
2. Leave the TODO for now but flag it explicitly (not mark "complete") until someone defines the fractional-unit rule?