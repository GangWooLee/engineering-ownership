That's fine (standard two blank lines before module-level code). Everything is in order.

## Rotating refresh tokens — implemented, ready for your review before merge

**What changed** (`src/auth/session.py`, `tests/test_session.py`):
- Refresh tokens now rotate on every redemption — `rotate(token)` consumes the old token and returns a new one in the same token family, invalidating the old one immediately instead of leaving it valid until manual revocation.
- **Reuse detection**: redeeming a token that was already rotated away can only mean it leaked (both the legit client and an attacker held a copy). That now raises `RefreshTokenReused` and revokes the *entire* family, forcing re-login — not just the one reused token.
- `revoke_family(family_id)` is the operational lever for logout / incident response.
- 12 tests pass (3 pre-existing + 9 new), covering rotation, reuse after 1 and after several further rotations, expiry, unknown tokens, and family isolation.

**Full R3 paper trail** (this repo's contract flags anything under `**/auth/**` as R3 — auth/crypto/secrets — requiring more than just code):
- Brief: `docs/engineering/changes/rotating-refresh-tokens.md`
- ADR (why full-family revocation over single-token revocation): `docs/engineering/decisions/rotating-refresh-tokens.md`
- Threat model: `docs/engineering/security/rotating-refresh-tokens.md`
- Runbook: `docs/engineering/runbooks/rotating-refresh-tokens.md`
- `engineering check --mode advise` → **PASS**, evidence bound to the current diff.

**Before you merge, know the real gap:** there is no login/refresh HTTP endpoint in this repo — `session.py` is a standalone module, so this is verified at the unit/state-machine level only, not end-to-end. Also flagged in the docs: storage is in-memory (drops on restart, not shared across replicas) and there's no alert emitted when reuse fires yet. None of that blocks merging *this* module, but it does mean it isn't production-safe behind a real multi-instance login endpoint until storage moves to a shared backend and reuse events are wired to alerting.

Nothing has been committed — working tree is dirty on purpose so you can review the diff. Want me to commit this, or do you want to look it over first?