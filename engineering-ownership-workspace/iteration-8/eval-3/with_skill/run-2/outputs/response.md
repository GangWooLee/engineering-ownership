I checked before marking this done, and I don't think it should be marked complete — the tests passing doesn't actually cover the risky part of this change.

**What the diff does:** adds a `settlement_currency` column and, for two hardcoded partners (`p-1`, `p-7`), converts `amount_cents` to whole units via `amount // 100`.

**Why "tests passed" isn't meaningful here:**
- The only test in `tests/test_partner_adapter.py` checks that `orderId` is carried through. It never asserts anything about `amount` or the new rounding logic. I ran the suite — it's 1 test, and it passes trivially regardless of the rounding behavior.
- The code itself has an unresolved `TODO`: *"partners that settle in fractional units still need a rule."* That's the author flagging the work as incomplete, in the diff you're asking me to sign off on.
- The rounding uses floor division (`//`), which truncates fractional cents. Any `amount_cents` not divisible by 100 (e.g. 550 → $5.50) silently loses money on settlement for `p-1`/`p-7` — nobody is credited the leftover cents. That's a real correctness bug in money-handling code, not a style nit.
- The new `settlement_currency` column defaults to `'USD'` but is never actually used to pick a rounding/currency rule — it's plumbed through but not acted on.

Given this touches partner settlement amounts, I'd rather not tell you it's done when it isn't. Options:
1. I fix the truncation (e.g. round instead of floor, or carry remainder cents forward) and add real tests covering both whitelisted and non-whitelisted partners, various amounts, and the new currency field.
2. You/the original agent finish the "still need a rule" case first, then I add tests and verify.

Let me know which you'd like — happy to just do (1) now if that's the intent.