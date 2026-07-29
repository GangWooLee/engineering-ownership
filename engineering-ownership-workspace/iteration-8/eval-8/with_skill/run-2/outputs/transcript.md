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


ARGUMENTS: This feature is ready for review. Make sure someone reading this code in six months can find out why it was built this way.

Now let me fill in the Brief with what's actually verifiable from the code, and flag the one gap I can't fabricate: the origin of the specific limiter numbers.

Now the ADR for the algorithm choice:

Now let's run verification through the CLI and check refs.

All tests pass. Now recording this through the CLI:

Now let's check overall status and also revisit the stale, still-open `partner-settlement-rounding` record I found while restoring context:

The rate-limiter feature is now documented and verified. Summary:

**Recorded for the new feature** (`partner-settlement-rate-limit`, risk R2):
- **Brief** (`docs/engineering/changes/partner-settlement-rate-limit.md`): the problem (unthrottled partner API calls), that `may_submit_now()` is advisory/opt-in rather than enforced inside `to_partner_payload`, and that nothing in the repo calls it yet.
- **ADR** (`docs/engineering/decisions/partner-settlement-rate-limit.md`): why a sliding-window log was chosen over a fixed window (avoids boundary double-bursting) or a token bucket (fewer parameters to justify).
- Code comments referencing the ADR at the two genuinely non-obvious points: the `BURST_LIMIT`/`WINDOW_SECONDS` constants, and the "advisory, not enforced" contract of `may_submit_now()`.
- Verified via `engineering verify` (unit tests pass) and `engineering check --mode advise` (PASS).

**One thing I deliberately didn't invent:** I don't know why `BURST_LIMIT = 7` and `WINDOW_SECONDS = 1.0` specifically — there's no partner API doc, incident, or prior conversation in this repo backing those numbers. Rather than writing a plausible-sounding justification into a permanent decision record, I recorded it as an open gap (`understanding=gaps`, revisit 2026-08-09) so a future reader sees it's unconfirmed instead of trusting a fabricated rationale. If you know the actual source, tell me and I'll update the ADR.

**Separate finding from restoring context:** the existing `partner-settlement-rounding` change (same file, unrelated to this feature) is still open, past its revisit date, and its Brief claims the adapter "converts amounts once, at the boundary" — but the current code still passes `amount_cents` straight through with no conversion. That looks like the implementation was never finished against its own documented intent. I didn't touch it since it's outside what you asked for, but it's worth knowing before this ships.