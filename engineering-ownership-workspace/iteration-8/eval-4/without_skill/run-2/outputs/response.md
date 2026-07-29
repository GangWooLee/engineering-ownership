I read through last week's shipped commit (two bundled changes: `partner-timeout-policy` and `partner-settlement-rounding`) — the docs, ADRs, evidence, and actual code — and wrote a handoff at `.engineering/handoffs/2026-07-26-partner-settlement-handoff.md`, following this repo's existing documentation convention.

**Key finding worth flagging directly:** the `partner-settlement-rounding` ADR/change-brief describe converting amounts from cents to whole units at the adapter boundary, but `src/api/partner_adapter.py` still passes `amount_cents` straight through unconverted — the doc itself marks this "in progress" and lists it as a known limit, so it's not a hidden regression, but a new session reading only the ADR could easily assume it's done. The handoff calls this out explicitly with the code snippet so no one builds on top of it by mistake.

**What's in the handoff:**
- Why each decision was made the way it was (fixed vs. adaptive timeout, manual vs. auto resubmission, adapter-boundary conversion vs. a second stored column) — preserved from the ADRs' trade-off reasoning, not just restated
- The gap between documented intent and shipped code for the rounding change
- A reading order for studying this later: `contract.json` → change briefs → ADRs → code (compared against the briefs) → evidence files (check `understanding.gaps`/`revisit_after` — both are at or past due as of today, 2026-07-26)
- Open questions to carry forward (partner idempotency-on-order-id, actual fractional rounding rule, missing test coverage on the `amount` field)

**Engineering maturity score: 3/5 — "process ahead of practice."**

| Dimension | Score | Note |
|---|---|---|
| Problem framing & non-goals | 4/5 | Clear intended outcomes and explicit non-goals in both change docs |
| Decision records (ADRs) | 4/5 | Real trade-offs, rejected options, reversal plans, supersession tracking |
| Failure/recovery planning | 4/5 | Rollback and manual-recovery paths spelled out |
| Verification machinery | 4/5 | `contract.json` ties risk tiers to required verification; evidence JSON records digest, exit code, timestamp |
| **Actual test coverage** | 1/5 | One test in the whole repo; doesn't touch `amount` at all despite that being the entire point of the rounding change |
| **Doc-to-code fidelity** | 1/5 | ADR describes a conversion that doesn't exist in the shipped function |
| Follow-through on staleness | 2/5 | `revisit_after` dates exist but both have lapsed with no re-review yet |

The team has genuinely good documentation discipline (ADRs, risk classification, structured evidence) — better than most repos this size. The score is dragged down by the two dimensions that matter most for trust: whether the code matches what's written, and whether tests actually exercise the risky behavior. Those are exactly the two things that let documentation quietly drift into fiction.