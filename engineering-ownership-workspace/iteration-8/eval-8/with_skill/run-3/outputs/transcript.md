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


ARGUMENTS: Reviewing readiness of current changes (src/api/partner_adapter.py modified, new src/api/rate_limit.py and tests/test_rate_limit.py) before merge. Need to ensure the reasoning behind design decisions is captured so someone reading this in six months understands why it was built this way. Last commit message was "feat: partner settlement rounding in progress" suggesting possibly unfinished prior work.

All 4 tests pass, including the new rate limiter tests. Now I'll start a proper change record for this feature so the reasoning is preserved.

Now let's run verification and the readiness gate for this change record.

The rate limiting feature is now documented and gated for review. Here's what I found and did:

**Done for this feature (`partner-rate-limit`, R2):**
- Ran the tests — all 4 pass, including the 3 new `RateLimiterCase` tests.
- Created a Brief (`docs/engineering/changes/partner-rate-limit.md`) and ADR (`docs/engineering/decisions/partner-rate-limit.md`) explaining *why*: an in-process sliding-window limiter was chosen over relying on the partner's own throttling or building an external/shared limiter, because it needs no new infrastructure and is trivially testable with an injected clock.
- Recorded verification evidence tied to the current diff and ran the readiness gate — `engineering check` → **PASS**.

**Two real gaps I documented rather than papering over** (in the "Known limits" section, so they're visible to the next reader instead of hidden):
1. `BURST_LIMIT = 7` / `WINDOW_SECONDS = 1.0` aren't sourced from any documented partner rate limit in this repo — I didn't invent a justification for these specific numbers.
2. `may_submit_now()` is defined but **not called anywhere**. It has zero effect on real traffic until some submission path checks it — worth confirming that's intentional before this ships.

**One thing outside this feature's scope that you should know about:** the prior "partner settlement rounding" change record (from the `feat: partner settlement rounding in progress` commit) has an ADR stating a decision to "convert cents to whole units at the adapter boundary," but `to_partner_payload` in the actual code has no such conversion — it just passes `amount_cents` straight through. That record is now stale (`engineering status` flags it: no passing verification, digest mismatch). I left it untouched since it's unrelated to the rate limiter, but you may want to either implement the missing conversion or close/update that record so it doesn't mislead someone later.