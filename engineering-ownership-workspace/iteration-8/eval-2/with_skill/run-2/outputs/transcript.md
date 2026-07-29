I'll start by checking my memory for relevant context and looking at the current repo structure.

This repo already has an `.engineering/contract.json` set up, which is a direct trigger for the engineering-ownership skill given this is a production auth change. Let me load it before touching any code.

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


ARGUMENTS: Implement rotating refresh tokens for production login flow. User wants to know when it's ready to merge.

This is R3 (auth path change, matches `**/auth/**` risk rule) — production login token handling touches security, so I'll follow the full ownership workflow rather than just patching the file. Let me start the change record.

Now I understand the workflow. Let me implement the rotation logic itself first.

Now the tests covering rotation, reuse detection, and family revocation:

Now let me exercise the actual breach-detection path end-to-end (not just unit tests) as evidence for the R3 gate.

Good — confirmed behavior: on reuse detection, the *entire* family is revoked, including the legitimate client's current token (fail-closed, forces re-login). That's the key trade-off to document. Now filling in the required artifacts.

Now the ADR:

Now the threat model:

Now the runbook:

Now let's run the reviewed verification and bind it to the diff, then check the gate.

Let me add the decision marker in code at the actual enforcement point, since that's the non-obvious trade-off the ADR documents.

Format confirmed: `engineering-decision: <id> | <path>`. Adding it at the reuse-detection branch in `rotate()`.

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