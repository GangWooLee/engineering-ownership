I'll start by reviewing the recent change and checking memory for relevant context, then use the appropriate skill for post-ship documentation.

Both changes trace back to the same commit and share risk area, but the code tells a different story than the docs claim. Let me verify a few more details before writing the handoff, then create it.

I saved the handoff at `.engineering/handoffs/2026-07-26-partner-settlement-and-timeout.md`, following the path your repo's own `.engineering/contract.json` already designates for handoffs.

**What I found:** the two changes shipped together — settlement rounding and a partner request timeout — share a call path (`partner_adapter` → `partner_client`), so I wrote one handoff covering both.

**Why it was built that way:** rounding converts once at the adapter boundary (single owner of the payload contract, no drift between callers) instead of a second DB column or per-caller conversion. The timeout is fixed at 8s rather than adaptive, because the failure it guards against is a stall, not slowness, and no latency history is collected. Full trade-off reasoning is in the doc, sourced from the existing ADRs.

**The important part — code doesn't match the docs in three places:**
1. `partner_adapter.py:8` never actually converts cents → whole units; the core rounding problem is unsolved despite being the title of the commit.
2. `partner_client.py:13` — `submit()` is a `NotImplementedError` stub, yet its change brief says `Status: Completed`.
3. The one existing test only checks `orderId`, so the "passed" verification evidence doesn't actually cover either behavior.

**How to study it later:** the doc lays out a specific reading order (brief → ADR → evidence → source → tests) and an exercise — write the test that would've caught gap #1 before checking if one exists, to internalize *why* the boundary-conversion design was chosen rather than just what was chosen.

**Engineering maturity: 5.5/10** — decision documentation (briefs, ADRs, rollback plans) is genuinely strong, but the loop isn't closing: a status label went stale ("Completed" on unimplemented code) and a scheduled review (`revisit_after: 2026-07-25`) already lapsed unreviewed, which is exactly the failure that mechanism exists to catch. Full per-dimension breakdown is in the file.