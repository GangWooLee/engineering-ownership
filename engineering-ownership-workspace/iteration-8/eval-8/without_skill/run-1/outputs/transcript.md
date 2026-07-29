I'll look at the current changes to understand what's been built.

There's an existing documentation pattern in this repo. Let me check it out.

Now I'll write the change doc, decision doc, and evidence record following this repo's established convention, plus tighten a couple of code comments so the "why" is visible without needing to go dig up the docs.

Now let me add a small comment to the code pointing back at the docs, since a reader in the source file shouldn't have to already know the docs exist to find them.

Let me verify tests still pass and review the final diff before you commit.

Added the missing "why" documentation for the new rate-limiting feature, following this repo's existing change/decision/evidence convention (the same one used for the prior settlement-rounding work):

- `docs/engineering/changes/partner-outbound-rate-limit.md` — problem, design decisions (sliding window vs. token bucket, shared per-process limiter, in-memory state), and known gaps
- `docs/engineering/decisions/partner-outbound-rate-limit.md` — ADR with options considered and why option 3 (in-process limiter) won
- `.engineering/evidence/partner-outbound-rate-limit.json` — verification record matching the schema used previously
- Short comments in `rate_limit.py` and `partner_adapter.py` pointing back to those docs, plus flagging that `BURST_LIMIT=7`/`WINDOW_SECONDS=1.0` aren't sourced from a documented partner limit — that's an open gap worth confirming, not something I invented a rationale for.

All 4 tests still pass. I didn't commit — let me know if you'd like me to.