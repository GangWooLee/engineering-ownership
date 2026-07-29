I'll use the engineering-ownership skill for this handoff, and check memory for any prior context on this change first.

This repo already has an `.engineering/contract.json` and decision records — exactly the setup the engineering-ownership skill expects. Let me load it to produce the handoff properly rather than freehanding it.

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


ARGUMENTS: Create a handoff for a new session for the complex change shipped last week (partner settlement rounding). Preserve why it was built that way, tell the user how to study it later, and give an engineering maturity score.

There are two change records from last week. Let me look at both evidence files and change/decision docs to see which is "the complex change" and gather full context.

The settlement-rounding change is unfinished — the docs describe converting cents to whole units at the adapter boundary, but the actual code just passes `amount_cents` straight through with no conversion. That's the real story here. Let me run the engineering CLI to check status and generate a proper saved handoff.

The handoffs directory isn't gitignored yet — the CLI requires that before it will save. Let me fix that first.

## Handoff: partner settlement rounding (`partner-settlement-rounding`, R2)

**Status: shipped as "in progress" — the code does not yet do what the docs say it does.**

### What was built and why (preserved from the ADR/brief)

**Problem:** the partner settlement API rejects payloads with amounts in cents; orders are stored in cents; every non-whole-unit partner payload was getting rejected and retried by hand.

**Decision:** convert cents → whole units once, inside `src/api/partner_adapter.py`, rather than (a) adding a second "whole units" column to the orders table, or (b) converting in every caller.
- **Why not a second column:** would need a backfill and could drift from the cents value that remains the source of truth.
- **Why not per-caller conversion:** the adapter already owns the payload contract, so keeping the conversion there gives it a single owner instead of scattering the rule across call sites.
- **Explicitly out of scope:** changing the storage representation, and the retry mechanism.
- **Rollback plan:** revert the adapter change; no data migration involved.
- **Known limit, called out at the time:** rounding behavior for partners that settle in *fractional* units was left unresolved.

### The gap the next session needs to know about first

I checked the actual code against the docs:

```python
# src/api/partner_adapter.py
def to_partner_payload(order: dict) -> dict:
    return {
        "orderId": order["id"],
        "partner": order["partner_id"],
        "amount": order["amount_cents"],   # <- raw cents, no conversion
    }
```

The unit-to-whole-units conversion described in the brief and ADR **was never implemented**. The one test in `tests/test_partner_adapter.py` only asserts `orderId` propagation — it never asserts anything about `amount`. So "verification: unit tests passed" in the evidence record is true but doesn't actually cover the behavior the change claims to deliver.

`engineering refs check` also shows the decision-to-code marker (`engineering-decision: partner-settlement-rounding | ...`) is missing from `partner_adapter.py`, even though the ADR itself says "the adapter now encodes a partner-specific rule" — exactly the non-obvious spot the marker convention exists for. (Its sibling change, `partner-timeout-policy`, does this correctly in `partner_client.py`.)

Net effect: whole-unit partners are still getting cents-denominated payloads today, this simply hasn't been rejected/noticed yet.

### Adjacent context from the same week

`partner-timeout-policy` (2026-07-16, R2, completed) added a fixed 8s timeout to `partner_client.submit`, driven by a real incident (4 workers stuck for 50 minutes on 2026-07-14 due to a partner stall). Fixed over adaptive because there's no latency history to size an adaptive timeout against. **Open gap it left behind:** whether the partner deduplicates on order id is unconfirmed, so a timed-out submission requires manual resubmission rather than automatic retry. Revisit is due 2026-07-30.

### How to study this later

```bash
export PATH="$HOME/.local/bin:$PATH"
engineering status --all                              # see both changes' review/staleness state
engineering explain partner-settlement-rounding        # canonical brief/ADR + reasoning prompts
engineering refs check --all                           # confirms decision-marker coverage
engineering change review partner-settlement-rounding --status gaps \
  --gap "amount conversion described in the ADR is not implemented in the adapter" \
  --revisit-days 3
```

Read, in order: `docs/engineering/changes/partner-settlement-rounding.md` → `docs/engineering/decisions/partner-settlement-rounding.md` → the same pair for `partner-timeout-policy` → `.engineering/evidence/*.json` for the raw verification trail. A saved session handoff is now on disk at `.engineering/handoffs/20260726T214813+0900-partner-settlement-rounding.md` (git-ignored, so it survives locally but isn't tracked).

One housekeeping fix I made along the way: `.engineering/handoffs/` wasn't gitignored yet, so `engineering handoff --save` refused to write. I added it to `.gitignore` (uncommitted — let me know if you want that committed).

### Engineering maturity score

Scoring the *process artifacts around this change*, not anyone's competence:

| Dimension | Score /5 | Note |
|---|---|---|
| Problem framing & non-goals | 5 | Clear problem, success criteria, explicit non-goals |
| Decision record (ADR) quality | 5 | Options, trade-offs, reversal path, supersession all present |
| Risk classification | 5 | Correctly auto-flagged R2 via `src/api/**` contract path |
| Decision→code traceability | 2 | Marker present for timeout-policy, **missing** for settlement-rounding |
| Verification fidelity | 1 | Passing test doesn't cover the claimed behavior at all |
| Review hygiene / freshness | 2 | `current_diff=no` (stale evidence); revisit date (2026-07-25) already passed |
| Repo scaffolding | 4 | Contract well-formed; only ding is AGENTS.md doesn't point at it (`engineering doctor` flag) |

**Overall: ~2.9 / 5 — "documentation-mature, implementation-incomplete."** The reasoning discipline (why) is genuinely strong; the gap is that the artifacts describe a change that shipped without its core behavior, and nothing in the verification pipeline caught it. That's the one thing worth fixing before this goes further: add an `amount` assertion to the adapter test and either implement the conversion or correct the docs to say it's still pending.