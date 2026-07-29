The mention of making this ready for review and documenting the reasoning for future readers matches the engineering-ownership skill's use case. Let me invoke it.

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


ARGUMENTS: Feature ready for review: rate limiting (src/api/rate_limit.py, tests/test_rate_limit.py) plus in-progress changes to src/api/partner_adapter.py. Ensure the reasoning behind design decisions is captured so someone reading this in six months can understand why it was built this way.

I've mapped the repo state. Two things are entangled here that I want to make sure I handle correctly before writing anything down permanently:

**What's actually in the diff:**
- New: `src/api/rate_limit.py` (a sliding-window `RateLimiter`, burst=7/window=1.0s) + `tests/test_rate_limit.py` — fully tested, all 4 tests pass.
- Modified: `src/api/partner_adapter.py` wires in a module-level `_limiter` and exposes `may_submit_now()`.

**A pre-existing, unrelated gap I found on the same file:** there's already an R2 change record `partner-settlement-rounding` (started 2026-07-18) whose Brief/ADR describe converting order amounts to whole units at the adapter boundary — but `to_partner_payload` still passes `amount_cents` through unconverted. That change is also overdue for its understanding review (`revisit_after: 2026-07-25`, today is 2026-07-26). This isn't part of your rate-limit work, so I won't touch the rounding logic, but I don't want to write documentation implying it's done.

Since `src/api/**` is R2 under this repo's contract, and the point of this pass is to preserve the *actual* reasoning (not plausible-sounding invented reasoning), I need a few real answers before I write the Brief/ADR:

1. **Why burst=7 / window=1.0s specifically?** Is that the partner's documented rate limit, or a number you picked empirically?
2. **What's the intended caller behavior when `may_submit_now()` returns `False`?** Retry with backoff, queue, or just drop/log? Right now nothing calls it yet — is that wiring intentionally out of scope for this change?
3. Should I leave the stale `partner-settlement-rounding` record alone (just note it as a pre-existing gap), or do you want it flagged more prominently since it now overlaps this file?