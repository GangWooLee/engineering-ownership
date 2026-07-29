Added the missing "why" documentation for the new rate-limiting feature, following this repo's existing change/decision/evidence convention (the same one used for the prior settlement-rounding work):

- `docs/engineering/changes/partner-outbound-rate-limit.md` — problem, design decisions (sliding window vs. token bucket, shared per-process limiter, in-memory state), and known gaps
- `docs/engineering/decisions/partner-outbound-rate-limit.md` — ADR with options considered and why option 3 (in-process limiter) won
- `.engineering/evidence/partner-outbound-rate-limit.json` — verification record matching the schema used previously
- Short comments in `rate_limit.py` and `partner_adapter.py` pointing back to those docs, plus flagging that `BURST_LIMIT=7`/`WINDOW_SECONDS=1.0` aren't sourced from a documented partner limit — that's an open gap worth confirming, not something I invented a rationale for.

All 4 tests still pass. I didn't commit — let me know if you'd like me to.