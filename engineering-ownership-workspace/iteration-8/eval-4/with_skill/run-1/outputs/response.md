## Handoff for `partner-settlement-rounding` (in progress)

**What I did:** re-ran verification, saved two handoff snapshots (`.engineering/handoffs/…partner-settlement-rounding.md` and `…partner-timeout-policy.md`, git-ignored), and confirmed refs/checks pass. Uncommitted right now: `.gitignore` (added `.engineering/handoffs/`, required before `--save` would work) and refreshed evidence timestamps — I didn't commit these; let me know if you want them in a commit.

### Why it was built this way

Two related decisions landed in `b70c0ca`:

1. **Partner timeout policy** (2026-07-16, *completed*) — a 14 July incident held four workers for 50 minutes when a partner connection accepted but never responded. Fix: a fixed 8s timeout in `partner_client.py`, kept separate from `partner_adapter.py` because timeout is a transport concern, not a payload concern. **Adaptive timeout was rejected** — no latency history exists to base it on, and the failure being guarded against is a stall, not slowness. Trade-off accepted: a timed-out submission is left unsent, requiring manual resubmission, because the partner has never confirmed it dedupes on order ID — that's an explicit open question, not an oversight.

2. **Partner settlement rounding** (2026-07-18, **in progress**) — orders are stored in cents; the partner API rejects non-whole-unit payloads. Decision: convert once at the adapter boundary (`partner_adapter.py`), not by adding a second stored column (rejected — needs backfill, can drift from the cents value) and not in every caller (rejected — conversion would live in N places).

### ⚠️ Gap you need to know about

**The conversion described in the decision doesn't exist yet.** `to_partner_payload` still forwards `amount_cents` raw:

```python
"amount": order["amount_cents"],   # src/api/partner_adapter.py:8
```

The Brief's own "Known limits" section flags this: *"Rounding behaviour for partners that settle in fractional units is unresolved."* The one test in `test_partner_adapter.py` only asserts `orderId` is carried — it does not exercise amount conversion at all, so there's no red test marking the missing behavior. **This is the actual next safe action**: write a failing test for the conversion, then implement it in the adapter, per the accepted decision.

### How to study this later

- `engineering explain partner-settlement-rounding` — walks the six standard review prompts (problem, data flow, why this design vs. alternatives, failure modes, evidence, rollback) against the canonical docs.
- Read in order: `docs/engineering/changes/partner-settlement-rounding.md` (Brief) → `docs/engineering/decisions/partner-settlement-rounding.md` (ADR) → `src/api/partner_adapter.py`.
- `engineering status --due` any time to see what's due for re-review (settlement-rounding was due 2026-07-25 — it's already overdue by a day).
- Once you've actually re-read it, record that with `engineering change review partner-settlement-rounding --status reviewed --revisit-days 30` (or `--gap "..."` if something's still unresolved) — this is what keeps `status` honest instead of silently stale.

### Engineering maturity score

This scores the *artifacts and process* around this change — not you or the author as an engineer. It's process maturity, not a competency grade.

| Dimension | Score (1–5) | Note |
|---|---|---|
| Problem framing & scope | 5 | Both Briefs state problem, success criteria, and explicit non-goals |
| Decision recording | 5 | Both ADRs list rejected alternatives and *why* — this is the strongest part of the setup |
| Risk classification | 4 | Correctly tagged R2, mapped to real `risk_paths` in the contract |
| Failure/rollback thinking | 4 | Both docs name the failure mode and reversal path clearly |
| Verification evidence | 2 | Tests pass, but coverage doesn't touch the behavior the ADR promises (rounding) — passing tests are currently a false signal of completeness |
| Implementation ↔ decision consistency | 1 | Code doesn't yet do what the accepted decision says it does |
| Enforcement/automation | 2 | `check` mode is `advise`-only, no CI gate; nothing currently blocks landing this half-finished |

**Overall: ~3.3 / 5 — good reasoning discipline, weak closure discipline.** The team is unusually good at writing down *why* before/while building (rare — most repos skip this entirely), but the loop isn't closed: "in progress" got committed to `main` with passing CI-shaped tests that don't test the actual promised behavior. If you fix one thing before the next session, make it the missing conversion test — everything else here is in good shape.