Let me look at the git history to understand this file's evolution, then update the adapter.

Now update the tests to match the new fractional-unit behavior for every partner.

All tests pass. Now let me keep this repo's engineering-contract paper trail consistent, since this change reverses the prior "Accepted" ADR for the same `src/api/**` (R2) path.

Final verification run and status check.

`src/api/partner_adapter.py` now converts every partner's amount to fractional currency units using `Decimal` (e.g. 549 cents → 5.49), replacing the old `WHOLE_UNIT_PARTNERS` special case that rounded p-1/p-7 to whole units and silently left everyone else in raw cents. Updated the test suite to match, and all 4 tests pass.

Since this reverses the prior "Accepted" ADR on the same `src/api/**` R2 path, I also marked that decision as Superseded and added a new decision/change/evidence record (`partner-settlement-fractional-units`) following this repo's existing engineering-contract pattern. Nothing has been committed — let me know if you'd like me to commit.