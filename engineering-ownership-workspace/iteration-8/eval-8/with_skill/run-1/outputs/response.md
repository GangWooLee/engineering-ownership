I've mapped the repo state. Two things are entangled here that I want to make sure I handle correctly before writing anything down permanently:

**What's actually in the diff:**
- New: `src/api/rate_limit.py` (a sliding-window `RateLimiter`, burst=7/window=1.0s) + `tests/test_rate_limit.py` — fully tested, all 4 tests pass.
- Modified: `src/api/partner_adapter.py` wires in a module-level `_limiter` and exposes `may_submit_now()`.

**A pre-existing, unrelated gap I found on the same file:** there's already an R2 change record `partner-settlement-rounding` (started 2026-07-18) whose Brief/ADR describe converting order amounts to whole units at the adapter boundary — but `to_partner_payload` still passes `amount_cents` through unconverted. That change is also overdue for its understanding review (`revisit_after: 2026-07-25`, today is 2026-07-26). This isn't part of your rate-limit work, so I won't touch the rounding logic, but I don't want to write documentation implying it's done.

Since `src/api/**` is R2 under this repo's contract, and the point of this pass is to preserve the *actual* reasoning (not plausible-sounding invented reasoning), I need a few real answers before I write the Brief/ADR:

1. **Why burst=7 / window=1.0s specifically?** Is that the partner's documented rate limit, or a number you picked empirically?
2. **What's the intended caller behavior when `may_submit_now()` returns `False`?** Retry with backoff, queue, or just drop/log? Right now nothing calls it yet — is that wiring intentionally out of scope for this change?
3. Should I leave the stale `partner-settlement-rounding` record alone (just note it as a pre-existing gap), or do you want it flagged more prominently since it now overlaps this file?