I'll use the engineering-ownership skill, which is built for exactly this situation — setting up process in a repo that has none.

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


ARGUMENTS: Set up a lightweight engineering process for this repository. The user has not worked in it before.

Now let me check the default contract template and the POINTER text to know exactly what will be generated.

I've inspected the repo. Before proposing setup, one thing stood out that you should know about regardless of what we do next:

**Finding:** `docs/decisions/2026-02-settlement-amount-units.md` documents a decision to convert order amounts from cents to whole units with half-up rounding *inside* `src/api/partner_adapter.py`. But the actual code in that file just passes `amount_cents` straight through unconverted — there's no rounding logic at all. The decision record and the code disagree. This is the only commit in the repo's history, so either the conversion was never implemented or was dropped. Worth resolving before anyone next touches that adapter, since the settlement payload sent to partners today would be rejected per the ADR's own description of the bug it was meant to fix.

Now, here's what I found for the repo itself:
- Small Python package (`orders-service`): order persistence schema + a partner settlement adapter.
- No CI, no package manifest. Tests run via `python3 -m unittest discover -s tests` (per `AGENTS.md`/`CONTRIBUTING.md`) — I ran it, it passes (1 test).
- `AGENTS.md` exists with 2 lines of instructions; no `CLAUDE.md` yet.
- No `.engineering/contract.json` yet.

**Proposed setup (nothing written yet — confirm and I'll apply it in one pass):**

1. **`.engineering/contract.json`** (new):
```json
{
  "version": 2,
  "project": { "name": "orders-service", "kind": "product", "status": "active" },
  "verification": [
    {
      "id": "unit",
      "argv": ["python3", "-m", "unittest", "discover", "-s", "tests"],
      "env": {},
      "timeout_seconds": 60,
      "required_for": ["R1", "R2", "R3"]
    }
  ],
  "risk_paths": {
    "R2": ["src/db/**"],
    "R3": ["src/api/**"]
  },
  "artifacts": {
    "changes": "docs/engineering/changes",
    "decisions": "docs/engineering/decisions",
    "runbooks": "docs/engineering/runbooks",
    "threat_models": "docs/engineering/security",
    "evidence": ".engineering/evidence",
    "handoffs": ".engineering/handoffs"
  },
  "automation": { "session_hooks": "off" },
  "review_interval_days": 7
}
```
   Note I customized `risk_paths` from the tool's generic defaults (`api/**`, `db/**`) to `src/api/**` / `src/db/**` since that's the real path prefix here, and put the adapter at **R3** rather than R2 — it's the only place money (settlement amounts) crosses into an external payload, which the risk model treats as R3 regardless of file size. `docs/decisions/**` already exists and doesn't need a pattern.

2. **`.engineering/handoffs/.gitignore`** (new) — `*` / `!.gitignore`, so future session handoffs stay untracked.

3. **`AGENTS.md`** — append a short pointer block (your existing 2 lines stay untouched).

4. **`CLAUDE.md`** — create new, containing only that same pointer block.

5. Session hooks default to **off** (no automatic reminders). I'd leave it there unless you want start/stop reminders — say so if you do.

Confirm this (or tell me what to adjust — e.g. different risk classification, `kind`/`status`, hook mode) and I'll apply it, then run `engineering doctor` to verify the setup landed cleanly.