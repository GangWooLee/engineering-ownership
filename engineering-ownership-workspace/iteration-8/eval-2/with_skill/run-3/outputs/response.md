I've implemented rotating refresh tokens, but **it is not ready to merge as a production login flow yet** — here's the honest status:

**What's done and verified:**
- `src/auth/session.py` now rotates refresh tokens: every `rotate(token)` call retires the old token and mints a new one in the same session "family." Reusing an already-retired token raises `TokenReuseDetected` and revokes the *entire* family (standard practice — same mechanism Auth0/Google use), so a stolen token that gets used is caught on the very next legitimate rotation attempt.
- Family lifetime is still capped at 90 days from the original login, independent of how many times it rotates — rotation can't be used to extend a session forever.
- 10 unit tests pass, covering rotation, reuse detection, family-wide revocation, expiry, and the "rotation doesn't extend absolute lifetime" invariant.
- Since this repo touches `**/auth/**` (flagged R3 in `.engineering/contract.json`), I went through the full R3 process: brief, ADR, threat model, and runbook are filled in under `docs/engineering/`, and `engineering check` passes.

**Why it's not merge-ready for production yet** (documented in the brief's "Known limits" and the threat model):
1. **No persistence** — state is an in-memory dict, matching what was already there. A process restart or running more than one server process silently loses the retirement/family records, which reopens the exact leak-detection gap this change exists to close. This needs a shared store (Redis/DB) before it's real.
2. **No login/refresh HTTP endpoint exists in this repo** to call `rotate()` from — there's nothing wiring this into an actual request flow yet.
3. **No alerting** when `TokenReuseDetected` fires — right now it's just a raised exception with no operational signal.

So: the rotation *logic* is solid and tested, but calling this "production login flow" would be overstating it — there's no production flow here to plug it into yet, and the in-memory storage is a real gap for a multi-process deployment. Happy to build the persistence layer and endpoint next if you want to keep going, or if there's an existing service elsewhere this should integrate with, point me at it.

Unrelated: I noticed `partner-settlement-rounding` (R2) is sitting with stale/unverified evidence from before — not something I touched, flagging in case it's relevant to your merge queue.