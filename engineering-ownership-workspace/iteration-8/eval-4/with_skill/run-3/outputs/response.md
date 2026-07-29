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