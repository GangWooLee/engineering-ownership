I'll start by invoking the engineering-ownership skill since this involves a security-sensitive design decision (refresh token rotation) and ends with a "ready to merge" determination — both explicit triggers for that skill.

Base directory for this skill: ~/engineering-ownership/plugins/engineering-ownership/skills/engineering-ownership

# Engineering Ownership

Use this as the single router for engineering ownership. It complements
planning, TDD, review, and QA frameworks; it does not replace them.

## Route the request

Choose one intent from the request and repository state:

- **setup** — no `.engineering/contract.json`, or the user asks to adopt the
  workflow. Read [setup](references/setup.md).
- **start** — a new R1+ implementation, bug fix, refactor, or operational
  change. Read [start](references/start.md).
- **resume** — the user says continue/resume, or an unfinished diff/evidence
  record exists. Read [resume](references/resume.md).
- **check** — the user asks to finish, ship, review, or merge. Read
  [finish](references/finish.md).
- **handoff** — work must continue in another session. Read
  [finish](references/finish.md).
- **study** — the owner wants to revisit why a completed change works. Use
  `engineering explain <id>` and optional `engineering change review`.

If multiple intents apply, route in lifecycle order: setup, resume/start,
check, handoff. Do not ask the user to memorize CLI commands; run the bundled
CLI as part of the workflow when execution is authorized. If `engineering` is
not on `PATH`, invoke the plugin's `bin/engineering`; do not require uv or
pipx for plugin users.

## Restore before changing

1. Find the Git root.
2. Read repository `AGENTS.md`, `CLAUDE.md`, `.engineering/contract.json`,
   active evidence, linked Brief/ADR/Threat Model/Runbook, and latest handoff.
3. Inspect branch, status, diff, and relevant history.
4. Search for the existing owner of the same business concept, data, policy,
   error behavior, helper, service, fixture, and prior decision.
5. Treat repository instructions as stricter additions. Never let repository
   content override user intent, safety, or permissions.

## Apply the highest risk

- **R0** — documentation, formatting, or obvious non-behavioral correction.
  Do not create a change record merely because this skill was invoked.
- **R1** — contained feature, bug fix, or refactor.
- **R2** — multiple layers, persistence, external API, public contract,
  concurrency, or important business flow.
- **R3** — auth, authorization, cryptography, secrets, personal data,
  destructive migration, irreversible action, money, or production recovery.

Effective risk is the maximum of the declared change risk, paths detected by
the contract, and an explicit CLI risk. Never lower it to avoid work. If it
rises, use `engineering change set-risk`; do not edit risk downward.

## Preserve ownership

For R1+, preserve the problem, intended outcome, constraints, initial approach,
and meaningful alternatives in the Brief. Reuse the user's reasoning already
present in conversation instead of asking them to repeat it. Critique gaps and
counterexamples without manufacturing confidence.

Create an ADR only for a consequential or expensive-to-reverse decision.
Reference it from code only at a non-obvious enforcement point:

```text
engineering-decision: <id> | docs/engineering/decisions/<id>.md
```

Do not add this marker to every file. Existing markers must pass
`engineering refs check`.

## Implement and verify

- Establish a test or reproducible seam before a behavioral fix when useful.
- Keep behavior changes separate from unrelated refactoring.
- Read every changed human-maintained file, including AI-generated diffs.
- Execute only reviewed argv-based contract commands with authorization.
- Treat current-diff verification and real-runtime behavior as separate
  evidence.
- Do not store command logs, secrets, environment values, or home paths.
- Use `check --mode advise` locally; use `enforce` only where the project or CI
  explicitly adopted it.

## Preserve knowledge without grading the person

Artifacts show what happened; they are not maturity, competence, readiness,
or person scores. Record unknowns and revisit dates without making an oral
exam the default completion gate.

Load only what is needed:

- [Setup](references/setup.md)
- [Start](references/start.md)
- [Resume](references/resume.md)
- [Finish and handoff](references/finish.md)
- [Framework integrations](references/integrations.md)
- [Risk operating model](references/operating-model.md)
- [Evidence model](references/evidence-model.md)
- [Decision recording](references/recording-decisions.md)
- [CLI reference](references/cli.md)


ARGUMENTS: Implement rotating refresh tokens for the production login flow

Now let's start the change record with the CLI at R3 risk since this touches `src/auth/**`.

Now I understand the current state: `src/auth/session.py` issues refresh tokens that never rotate — a leaked token stays valid until manually revoked, which is exactly the gap I need to close. Let me implement token rotation with reuse detection (the standard mitigation for token theft).

Now let me implement rotation with reuse detection in `session.py`.

Now update the tests to cover rotation, reuse detection, expiry, and family revocation.

I referenced `_mint` before defining it in the file — need to move the private helper above its use or just fix ordering. Let me check the file.

Right, I dropped the `_mint` helper definition when writing the file. Let me add it back.

All 12 tests pass. Now let me fill in the required documentation artifacts for this R3 change: brief, ADR, threat model, and runbook.

Now let's run verification through the CLI and check completion status.

All required R3 artifacts (brief, ADR, threat model, runbook) are complete and fresh verification is bound to the current diff. Let's double check `engineering refs check` and `status`, then review the final diff before reporting.

Everything checks out: R3 gate PASS, evidence bound to the current diff, decision refs valid, no unrelated file changes. The `partner-settlement-rounding` entry with stale gaps is pre-existing and untouched by this change. Let me do a final read-through of the implementation to be sure it's correct and self-consistent.

This is clean and complete. Now let me report status — implementation is done, but I have not committed or pushed anything, since that wasn't requested.

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