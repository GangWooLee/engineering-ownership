Tracking is set up. I won't commit since you didn't ask me to — let me know if you'd like these staged/committed.

**Summary:** Set up `.engineering` tracking for the `settlement-currency` change (R2, since it touches `src/db/**` and `src/api/**`), matching the pattern already used for `partner-settlement-rounding`:

- `docs/engineering/changes/settlement-currency.md` — Brief filled in from `docs/proposals/settlement-currency.md` and `plans/settlement-currency.md`, noting steps 1 & 3 in progress and 2/4/5 not started
- `docs/engineering/decisions/settlement-currency.md` — ADR recording the "store on the row vs. per-partner table" decision from the proposal
- `.engineering/evidence/settlement-currency.json` — created by `engineering change start`, now has a passing `unit` verification run against the current diff (`src/db/schema.py`)

`engineering status --all` shows `settlement-currency` tracked with `current_diff=yes` and passing verification; `engineering check --mode advise` passes. Note: the pre-existing `partner-settlement-rounding` record shows stale/failing gaps unrelated to this — left untouched since it wasn't part of this request.