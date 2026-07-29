Created the change-tracking artifacts for `settlement-currency`, following the same convention already used for `partner-settlement-rounding` (per `.engineering/contract.json`):

- `docs/engineering/changes/settlement-currency.md` — the change brief (Change ID, Risk R2, Status: In progress, problem/outcome, scope, decisions, verification, known gaps)
- `docs/engineering/decisions/settlement-currency.md` — the ADR, formalizing the proposal's rejected per-partner-table alternative
- `.engineering/evidence/settlement-currency.json` — evidence record with the current diff digest and a passing unit-test run

One thing worth flagging: the plan says steps 1 *and* 3 are "in progress," but I only found an uncommitted change for step 1 (`settlement_currency` column in `src/db/schema.py`) — `src/api/partner_adapter.py` doesn't include currency in the payload yet. I noted that discrepancy in both the brief and the evidence `understanding.gaps` rather than silently assuming step 3 was done.

These three files are untracked/unstaged — let me know if you'd like me to commit them (and whether alongside the schema.py change or separately, per the AGENTS.md guidance to keep schema and adapter changes in separate commits).