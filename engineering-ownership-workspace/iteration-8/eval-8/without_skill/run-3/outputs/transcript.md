I'll look at the current changes to understand what was built before ensuring the reasoning is documented.

This repo has an existing documentation convention: change logs under `docs/engineering/changes/` and ADRs under `docs/engineering/decisions/`. Let me look at the existing pair for the sibling settlement-rounding feature to match the pattern.

Before I write the "why" documentation, I need to check one thing with you: the code sets `BURST_LIMIT = 7` and `WINDOW_SECONDS = 1.0` in `src/api/rate_limit.py`, but nothing in the repo records where those numbers came from.

Since the whole point of this task is making the reasoning traceable, I don't want to invent a justification for those specific values. Can you tell me: is 7 req/sec the partner's documented rate limit (or a safety margin below it), or based on an incident/support conversation? A one-line source is enough — I'll fold it into the docs and code comment.