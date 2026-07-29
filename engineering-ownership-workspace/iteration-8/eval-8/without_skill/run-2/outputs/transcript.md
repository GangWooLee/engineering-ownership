I'll start by examining the current state of the repository to understand what's changed and why.

I looked at the working tree and found this repo has an explicit governance convention for exactly this purpose: R2-risk changes (anything under `src/api/**`) get a change brief in `docs/engineering/changes/`, a decision record in `docs/engineering/decisions/`, and an evidence entry in `.engineering/evidence/`, as `.engineering/contract.json` specifies and as the sibling `partner-settlement-rounding` feature demonstrates.

The uncommitted rate-limiting feature (`src/api/rate_limit.py`, wiring in `partner_adapter.py`, `tests/test_rate_limit.py`) touches `src/api/**`, so it needs the same treatment before it's genuinely "ready for review." Tests pass (4/4).

One thing I can't infer from the code or repo: **why `BURST_LIMIT = 7` and `WINDOW_SECONDS = 1.0`**. There's no partner API spec, config, or prior doc anywhere in the repo that justifies those specific numbers — they're currently unexplained magic constants. I don't want to write an ADR that invents a plausible-sounding justification (e.g., "the partner's published limit is 7 req/s") if that's not actually true, since that would defeat the point of leaving a trustworthy trail for future readers.

Could you tell me the actual reasoning — e.g., is this the partner's documented rate limit, a conservative internal default, sized to match a worker pool, etc.? Once I have that, I'll write the ADR + change brief + evidence file in the established format and make sure the code comments reflect it.