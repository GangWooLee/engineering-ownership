I'll invoke the engineering-ownership skill since this involves starting tracked work based on an existing proposal/plan.

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


Good, the CLI is available. Now let's check current status before creating the change record.

This touches `src/db/**`, so it's risk R2 per the contract. Let me start tracking the change.

I'll populate the Brief and ADR with the reasoning already captured in the proposal and plan, rather than asking the user to repeat it.

Now let's check the status and run verification for the current diff.

The `settlement-currency` change is now tracked cleanly (R2, current diff verified, no gaps). The pre-existing `partner-settlement-rounding` record is unrelated and out of scope here.

Work is now tracked as change `settlement-currency` (risk R2, since it touches `src/db/**`):

- **Brief** (`docs/engineering/changes/settlement-currency.md`) — problem, intended outcome, and the 5-step plan carried over from `docs/proposals/settlement-currency.md` and `plans/settlement-currency.md`, with steps 1 and 3 marked in progress.
- **Decision record** (`docs/engineering/decisions/settlement-currency.md`) — the already-agreed rejection of a per-partner currency table, recorded as an ADR since it's the consequential, expensive-to-reverse choice.
- **Evidence** — unit tests verified passing against the current diff (`src/db/schema.py`).

Note: there's a pre-existing, unrelated tracked change `partner-settlement-rounding` with a stale/failing evidence gap — that's separate prior work, not something I touched.

Next per the plan: backfill existing rows to USD, then wire the currency through the adapter payload and reporting read path.