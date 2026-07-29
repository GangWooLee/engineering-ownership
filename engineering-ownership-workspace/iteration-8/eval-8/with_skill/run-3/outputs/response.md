The rate limiting feature is now documented and gated for review. Here's what I found and did:

**Done for this feature (`partner-rate-limit`, R2):**
- Ran the tests — all 4 pass, including the 3 new `RateLimiterCase` tests.
- Created a Brief (`docs/engineering/changes/partner-rate-limit.md`) and ADR (`docs/engineering/decisions/partner-rate-limit.md`) explaining *why*: an in-process sliding-window limiter was chosen over relying on the partner's own throttling or building an external/shared limiter, because it needs no new infrastructure and is trivially testable with an injected clock.
- Recorded verification evidence tied to the current diff and ran the readiness gate — `engineering check` → **PASS**.

**Two real gaps I documented rather than papering over** (in the "Known limits" section, so they're visible to the next reader instead of hidden):
1. `BURST_LIMIT = 7` / `WINDOW_SECONDS = 1.0` aren't sourced from any documented partner rate limit in this repo — I didn't invent a justification for these specific numbers.
2. `may_submit_now()` is defined but **not called anywhere**. It has zero effect on real traffic until some submission path checks it — worth confirming that's intentional before this ships.

**One thing outside this feature's scope that you should know about:** the prior "partner settlement rounding" change record (from the `feat: partner settlement rounding in progress` commit) has an ADR stating a decision to "convert cents to whole units at the adapter boundary," but `to_partner_payload` in the actual code has no such conversion — it just passes `amount_cents` straight through. That record is now stale (`engineering status` flags it: no passing verification, digest mismatch). I left it untouched since it's unrelated to the rate limiter, but you may want to either implement the missing conversion or close/update that record so it doesn't mislead someone later.