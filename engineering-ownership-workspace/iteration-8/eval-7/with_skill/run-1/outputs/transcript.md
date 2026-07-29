This looks like a task for the engineering-ownership workflow — there's already a proposal, plan, and even an in-progress diff. Let me load that skill and the relevant docs.

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


`engineering` CLI is on PATH. I'll check current status, then start tracking the settlement-currency change at R2 (it touches `src/db/**` and will touch `src/api/**`, matching the contract's risk paths and the precedent set by the sibling `partner-settlement-rounding` change).

Now let me fill in the Brief and ADR templates using the content already agreed in the proposal and plan, plus the responsibility search for the existing code owners.

Now let's run verification and check the current state of the change record.

Let's do a final check with `engineering check` to confirm nothing else is missing.

Verification passed and is bound to the current diff. Let me record that in the brief.

Tracking is set up for the `settlement-currency` change:

- **Started** `engineering change start settlement-currency --risk R2` (R2: touches `src/db/**` and will touch `src/api/**` per the contract's risk paths, consistent with the sibling `partner-settlement-rounding` change).
- **Brief** (`docs/engineering/changes/settlement-currency.md`) filled from the proposal/plan: problem, success criteria, responsibility search (schema owns the table, `partner_adapter.to_partner_payload` owns the payload), decision link, failure/rollback, and known gaps.
- **ADR** (`docs/engineering/decisions/settlement-currency.md`) records the accepted decision (currency on the order row, not a per-partner table) and why the alternative was rejected.
- **Verified**: `unit` tests pass against the current diff (`engineering verify` bound it).
- `engineering check --mode advise` → **PASS**.

One gap worth flagging: the plan's step 4/5 (reporting read path) references a reporting module that isn't in this repo checkout — I noted that as an unresolved learning gap rather than guessing at its location. Also, unrelated to this: `partner-settlement-rounding`'s revisit date (2026-07-25) is already overdue — let me know if you want that looked at too.