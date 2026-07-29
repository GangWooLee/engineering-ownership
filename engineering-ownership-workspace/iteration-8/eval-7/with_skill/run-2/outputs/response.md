Work is now tracked as change `settlement-currency` (risk R2, since it touches `src/db/**`):

- **Brief** (`docs/engineering/changes/settlement-currency.md`) — problem, intended outcome, and the 5-step plan carried over from `docs/proposals/settlement-currency.md` and `plans/settlement-currency.md`, with steps 1 and 3 marked in progress.
- **Decision record** (`docs/engineering/decisions/settlement-currency.md`) — the already-agreed rejection of a per-partner currency table, recorded as an ADR since it's the consequential, expensive-to-reverse choice.
- **Evidence** — unit tests verified passing against the current diff (`src/db/schema.py`).

Note: there's a pre-existing, unrelated tracked change `partner-settlement-rounding` with a stale/failing evidence gap — that's separate prior work, not something I touched.

Next per the plan: backfill existing rows to USD, then wire the currency through the adapter payload and reporting read path.