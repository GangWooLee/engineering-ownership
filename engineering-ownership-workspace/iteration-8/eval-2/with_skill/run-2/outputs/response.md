This looks solid. Here's the summary and merge readiness status:

## What I implemented

`src/auth/session.py` now does true token rotation instead of a single static refresh token:

- **`start_session()`** issues the first refresh token and creates a token *family* (a login session's lineage).
- **`rotate(token)`** exchanges the current token for a new one, marks the old one `ROTATED`, and keeps the family's original 90-day expiry absolute — rotating never extends the session.
- **Reuse detection**: presenting any non-current token (already rotated, or explicitly revoked) to `rotate()` raises `ReuseDetected` and kills the *entire family* — including the legitimate client's current token. That's a deliberate fail-closed trade-off (documented in the ADR), since the module can't tell a genuine attacker replay from a client double-submitting a request.
- **`revoke_family()`** for logout-everywhere / manual breach response.

I verified this with unit tests (12 passing, covering rotation, family-scoped expiry, reuse, single-token revoke, logout-everywhere) *and* by directly running the attack scenario end-to-end (login → legit rotation → stolen-token replay) to confirm `ReuseDetected` actually fires and the family actually dies — not just that the test asserts it.

Because this touches `**/auth/**`, it's an R3-risk change per this repo's `.engineering/contract.json`, so I also wrote the required Brief, ADR, threat model, and runbook (`docs/engineering/{changes,decisions,security,runbooks}/rotating-refresh-tokens.md`), and linked the ADR from the enforcement point in code.

## Ready to merge?

**Yes, for what's in this repo.** `engineering verify`, `refs check`, and `check --mode advise` all pass, and there's no existing caller of this module to break (nothing else in the repo imports it yet).

Two things worth knowing before it goes further:
- **Residual race**: if a stolen token and the legitimate client both try to rotate before either sees the other's result, whoever goes first "wins" and the loser is only caught on their *next* call — documented in the threat model, not fixed here (needs an atomic store, which doesn't exist yet).
- **No persistence or login endpoint**: tokens are still in-memory (matches the original module), and there's no HTTP/login handler in this repo to wire it into yet.

I haven't committed anything — changes are sitting in the working tree. Want me to commit this?