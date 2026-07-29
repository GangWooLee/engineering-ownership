I can't mark this complete — the changes have real gaps that "tests passed" doesn't cover, since the only existing test (`test_partner_adapter.py`) checks just `orderId` and never touches the new rounding/currency logic. Concretely:

1. **Truncation bug, not rounding**: for partners `p-1`/`p-7`, `amount // 100` truncates cents to whole units instead of rounding — e.g. `550` cents ($5.50) becomes `5`, silently dropping $0.50 on every such order. In settlement code this is a real money-losing bug.
2. **Admittedly incomplete**: the code has `# TODO: partners that settle in fractional units still need a rule`, and the last commit is literally titled "partner settlement rounding **in progress**." This isn't finished work.
3. **Hardcoded partner list**: `WHOLE_UNIT_PARTNERS = frozenset({"p-1", "p-7"})` has no explanation for why exactly these two IDs are special-cased, which is fragile if a new partner needs the same treatment.
4. **Zero new test coverage**: nothing tests the rounding/truncation path or the new `settlement_currency` field/column.

Since this touches money and a DB schema, I'd rather not rubber-stamp it. Want me to: (a) fix the truncation to proper rounding, (b) resolve the TODO for fractional-unit partners, and (c) add tests covering both — before calling it done?