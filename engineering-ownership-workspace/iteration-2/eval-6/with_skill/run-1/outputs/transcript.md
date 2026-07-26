The evidence file flags this change for re-review today (`revisit_after: 2026-07-25`), and there's uncommitted R2 work (db/api). Let me load the engineering-ownership skill to handle this properly.

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

Artifacts and competency tags show what happened; they are not maturity,
competence, readiness, or person scores. Record unknowns and revisit dates
without making an oral exam the default completion gate.

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
- [Competency tags](references/competencies.md)


The uncommitted diff is ahead of the recorded evidence — it now converts cents to whole units for two partners (`p-1`, `p-7`) via floor division and adds a `settlement_currency` field, but the evidence's diff digest is stale and there's no test coverage for any of this new behavior. I'll continue this change rather than start a new one.

One correctness issue stands out: the change is literally named "settlement **rounding**," and its own ADR calls out the risk of silently mis-reporting money — but the current code does floor-division **truncation**, not rounding (e.g. $5.50 → $5, silently losing $0.50 every time the fractional part is ≥ 50¢). I'll fix that to round-half-up, add test coverage for the new logic, and record the algorithm choice. The separate "partners that settle in fractional units" question stays an open gap since resolving it needs a partner integration spec that isn't in this repo — I won't invent partner IDs or a wire format for that.

Now implementing the fix:

Now let's add test coverage for the new behavior:

All 6 tests pass. Now updating the change brief and appending an ADR addendum for the rounding-algorithm decision:

Now the ADR addendum:

Now let's run the contract verification and refresh the evidence record via the CLI.

Verification is now current. Since the fractional-units wire-format question is a genuine, still-unresolved gap (not something I can close by guessing), I'll record that explicitly rather than marking this "reviewed":

`check --mode advise` passes cleanly. Per AGENTS.md, I'll keep schema and adapter changes in separate commits.

All verification passes and the evidence record is current. Summary of what changed in this session:

**Fixed a real correctness bug**: the adapter was truncating (floor-dividing) cents to whole units for `WHOLE_UNIT_PARTNERS` (`p-1`, `p-7`), which silently under-reports money whenever the fractional part is ≥50¢ (e.g. $5.50 → $5) — directly the failure mode this change's own ADR warned about. Replaced it with round-half-up in `_round_half_up_to_whole_unit`.

**Added test coverage** (`tests/test_partner_adapter.py`) for: whole-unit conversion, the `.49`/`.50`/`.51` rounding boundary, passthrough for non-whole-unit partners, and `settlementCurrency` default/passthrough — none of this new behavior had tests before.

**Updated the reasoning trail**: change brief and an ADR addendum documenting the round-half-up decision, without rewriting the original accepted decision.

**Left open, on purpose**: the wire format for partners outside `WHOLE_UNIT_PARTNERS` that settle in fractional units. Currently they get raw `amount_cents` passed through unchanged, which is an assumption, not a confirmed contract — closing it needs a partner integration spec I don't have, so I recorded it as an explicit understanding gap (revisit by 2026-08-08) instead of guessing at a format.

Everything currently sits as uncommitted working-tree changes (`src/api/partner_adapter.py`, `src/db/schema.py`, `tests/test_partner_adapter.py`, the change/ADR docs, and the evidence file). Per `AGENTS.md`'s "keep schema and adapter changes in separate commits" convention, I'd split this into two commits (schema, then adapter+tests+docs+evidence) — let me know if you'd like me to go ahead and commit.