I'll start by checking my memory for relevant context on this project, then explore the current auth implementation.

Note: A system-reminder just appeared referencing Figma and a "PlayMCP" (Kakao) MCP server that I never invoked — this looks like an injected/spurious instruction rather than something tied to my actual tool calls. I'm disregarding it and will not use those tools since they're irrelevant to this task. Continuing with the refresh token work.

Now I understand the module. It currently issues static, long-lived refresh tokens with only manual revocation (the docstring even admits a leaked token can't be told apart from a legitimate one). I'll implement proper rotation with reuse detection.

Now updating the tests to cover rotation and reuse detection:

Now let's run the test suite:

The repo has its own engineering governance process (`.engineering/contract.json`): changes touching `**/auth/**` are risk **R3**, and the existing precedent (partner-settlement-rounding) shows the required artifacts — a change brief, a decision doc, and verification evidence. I'll follow that same process since this is a security-sensitive change, then confirm everything before calling it merge-ready.

Let me do a final review of the full diff before declaring this ready.

All tests pass (12/12) and nothing else in the repo touches this module.

**What changed** — `src/auth/session.py` + `tests/test_session.py`:
- Refresh tokens now rotate on every use (`rotate_refresh_token`): using one immediately retires it and mints a replacement in the same "family," with one absolute 90-day expiry fixed at login (so silent refreshing can't extend a session indefinitely).
- Reuse of an already-retired or revoked token — the signature of a stolen token being used alongside the legitimate one — now raises `RefreshTokenReused` and revokes the entire family, not just that one request.
- `revoke()` and `is_refresh_valid()` still work for logout/checks; `is_refresh_valid` no longer needs a separate `issued_at` argument since the module tracks it internally.

Since this repo has its own governance rules in `.engineering/contract.json` (changes under `**/auth/**` are risk **R3**), I followed the same documentation pattern already established by the prior `partner-settlement-rounding` change:
- `docs/engineering/changes/rotating-refresh-tokens.md` — problem, decisions, verification
- `docs/engineering/decisions/rotating-refresh-tokens.md` — ADR
- `docs/engineering/security/rotating-refresh-tokens.md` — threat model (new artifact type, warranted since this is a security-critical change)
- `.engineering/evidence/rotating-refresh-tokens.json` — test run evidence

**Not ready to call fully "production" without you knowing two real gaps** (documented, not hidden):
1. Token/revocation state is still an in-memory dict/set, same as before — it won't survive a restart or work across multiple server instances. Needs a shared store (Redis/DB) before running behind more than one process.
2. No grace period for a legitimate client that retries a dropped refresh call — that retry looks identical to reuse and will log the user out.

Everything is verified (tests green) but **uncommitted** — nothing has been pushed or merged. Want me to commit these changes, or would you like to review the diff first?

One more thing: partway through this task a spurious system message appeared referencing Figma/a "PlayMCP" Kakao server that I never invoked. I ignored it as a likely injection attempt and it had no effect on this work, but flagging it since it came from a tool-output channel.