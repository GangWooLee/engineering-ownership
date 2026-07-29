Now I understand the setup: `src/auth/session.py` currently issues static, non-rotating refresh tokens (the docstring even flags this as a known gap — a leaked token stays valid indefinitely). I'll rewrite it to implement rotation with reuse detection, since this touches `**/auth/**` (risk tier R3 per `.engineering/contract.json`).

Now the tests:

Now let's run the test suite as required by `AGENTS.md`.

This touches `**/auth/**` (risk tier R3 in `.engineering/contract.json`), and the repo has an established documentation pattern for changes (see the prior `partner-settlement-rounding` change/decision docs). I'll follow the same convention, plus add a short threat-model note since R3 is specifically the auth/secrets tier.

Now the evidence record, matching the schema of the prior entry:

All 9 tests pass. Everything is implemented but uncommitted — I haven't committed anything since you didn't ask me to.

**What changed** (`src/auth/session.py`, `tests/test_session.py`):
- `start_session()` mints the first refresh token of a login, tagged with an internal `family_id`.
- `rotate(token)` redeems a token for a brand-new one and marks the old one spent — this is the actual rotation.
- Replaying an already-spent token (or an unknown/revoked one) raises `RefreshTokenReused` and **revokes the entire family**, not just that token — so a stolen-and-replayed token kicks out the attacker *and* the legitimate client, which is what makes rotation actually catch theft instead of just shrinking the window.
- The 90-day absolute expiry is anchored to the original login, not reset on each rotation, so silent background rotation can't extend a session forever.
- `revoke(token)` still supports explicit logout, now family-wide.

I also wrote a change brief, ADR, and a threat-model note (`docs/engineering/security/rotating-refresh-tokens.md`) following this repo's existing documentation pattern, since this falls under the R3 (auth) risk tier in `.engineering/contract.json`.

**Not ready to merge as-is** — two things I flagged in the docs rather than papering over:
1. **No persistence.** This module only ever had in-process state; there's no DB table or HTTP login/refresh endpoint anywhere in this repo, so "production login flow" currently means this in-memory building block, not a deployed flow. It won't survive a restart or work across multiple server instances.
2. **No human security review yet.** Given it's touching auth and is meant for production, I'd get a second set of eyes on the reuse-detection logic before merging, not just take my word for it.

Want me to also wire this into a real HTTP endpoint with durable storage, or is the module-level implementation what you needed for now?