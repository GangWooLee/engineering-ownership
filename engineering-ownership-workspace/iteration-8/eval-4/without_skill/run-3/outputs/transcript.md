I'll start by checking memory for relevant context, then look at the actual change to understand what was built.

That last block is just generic MCP boilerplate, not relevant here. Let me look at the actual code and the second bundled change.

Now I have the full picture. This "complex change last week" is actually two bundled changes to the partner settlement pipeline, and there's a meaningful gap between what was documented and what was actually implemented — worth surfacing clearly. Let me write the handoff.

Let me save a couple of memory notes so future sessions in this repo pick up where this leaves off.

## Handoff written

**`.engineering/handoffs/2026-07-26-partner-settlement.md`** — following this repo's own decision/change/evidence structure (`.engineering/contract.json`), since that's exactly where "why" already lives here.

The commit actually bundles two related changes to the partner settlement pipeline:

- **partner-timeout-policy** (2026-07-16, Completed) — fixed 8s timeout on partner submission, chosen over adaptive, because a 2026-07-14 incident stalled 4 workers for 50 minutes and the failure mode is a *stall*, not slowness (adaptive needs latency history that doesn't exist).
- **partner-settlement-rounding** (2026-07-18, In progress) — plan to convert cents→whole-units at the adapter boundary rather than a second DB column or per-caller conversion, so there's a single owner and no drift risk.

**The important thing for a fresh session to know**: the docs are ahead of the code.
- The rounding conversion the ADR marks "Accepted" **isn't implemented** — `to_partner_payload` still passes `amount_cents` straight through.
- The timeout path has **zero test coverage**, despite the change brief claiming otherwise — only one test exists, and it only checks `orderId`.
- The rounding change's review date (`revisit_after: 2026-07-25`) already lapsed as of today.

I verified all three by reading the code and running the test suite, not just the docs.

## How to study it later
Follow the handoff's reading order: `contract.json` → the two ADRs → the two change briefs → the two evidence JSONs → the code (`schema.py` → `partner_adapter.py` → `partner_client.py`, note the inline comment linking code to its ADR) → `git show b70c0ca` for the raw diff.

## Engineering maturity score: **6.5 / 10**

**Strong (pulls it up):** deliberate ADR-per-change with options-considered and explicit reversal cost; a machine-readable evidence file tying verification to a diff digest; a contract that defines risk paths and a review cadence; code that traces back to its decision doc inline. That's more rigor than most repos this size have.

**Weak (pulls it down):** the rigor is partly theater right now — an "Accepted" decision whose implementation doesn't exist, and a "tests cover this" claim with no corresponding test. Verification claims aren't being checked against reality, and the review cadence itself has already lapsed once. Mature process without enforcement is just paperwork.

If nothing else, the gap between claimed and actual state was the single most important thing to surface — it's now in the handoff and in memory for next time.