Implemented and tested. Here's where it stands:

**What changed**
- `src/auth/session.py`: refresh tokens now rotate on every use (`rotate_refresh_token`). Each token belongs to a "family"; presenting an already-rotated/revoked token again (the signature of a stolen copy being replayed) revokes the *entire* family, not just that token. `revoke()` now cascades to the whole family too.
- `tests/test_session.py`: rewrote/expanded to cover rotation, reuse-triggered family revocation, rotating an expired/unknown token, and revoke cascading. All 9 tests pass (`python3 -m unittest discover -s tests`).
- Added a change brief, ADR, and threat model under `docs/engineering/...`, plus an evidence record — this repo's `.engineering/contract.json` flags any `**/auth/**` path as its highest risk tier (R3), and those artifact types already exist for that reason.

**Not "just merge it" — a few things you should know before this touches production traffic**, laid out in the threat model:
1. **Storage is in-memory** (matching the original module's design) — it won't survive a restart or work across more than one server instance. Production needs a shared, persistent store with tokens hashed at rest.
2. **No atomic compare-and-swap on rotation** — two near-simultaneous refresh calls (e.g. a client retry) can race and falsely trigger the reuse-detection revocation. Needs an atomic claim operation at the storage layer.
3. **No rate limiting/alerting** on reuse-detection events — right now a detected theft attempt silently revokes the session but nobody gets paged.

Code-wise this is done and green, but it's a genuine security-relevant change (auth, token theft detection) — I'd want a human security review of the threat model before calling it merge-ready for production, rather than self-certifying that. Nothing has been committed yet. Want me to commit these changes, or would you like to review the diff first?