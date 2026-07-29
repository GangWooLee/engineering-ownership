I'll start by checking memory for relevant context and exploring the current auth implementation.

This repo has an engineering ownership contract flagging `**/auth/**` as risk tier R3 (production auth), so let me consult that process before touching the code.

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


ARGUMENTS: Implement rotating refresh tokens for production login flow in src/auth/session.py. This touches R3 (auth) risk path per .engineering/contract.json.

Now I'll design the rotation logic. Let me check the current test coverage and constant usage once more, then implement.

Now the tests:

I left a stray dead-code line in that last test — let me clean it up.

Now let's run the test suite as the contract requires:

All 10 tests pass. Now let me fill in the required R3 documentation artifacts: the brief, ADR, threat model, and runbook.

Now I'll fill each of these out.

Now let's run verification through the CLI to bind fresh evidence to this exact diff, then check the change's status.

Let me add the decision marker at the non-obvious enforcement point in the code, per the ADR-linking convention.

Tests still pass and the decision marker checks out. Let me re-verify against the now-updated diff and re-run the advisory check.

Everything is clean and current. Now let's look at the final diff for a sanity read-through before reporting status.

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