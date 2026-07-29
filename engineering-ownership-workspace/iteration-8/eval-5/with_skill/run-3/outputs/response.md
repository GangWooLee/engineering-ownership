I've reviewed the repo: it's a small Python project (`orders-service`) with two source modules — a DB schema (`src/db/schema.py`) and a partner settlement adapter (`src/api/partner_adapter.py`) that already has one recorded decision (`docs/decisions/2026-02-settlement-amount-units.md`) about money-rounding correctness. `AGENTS.md`/`CONTRIBUTING.md` both specify `python3 -m unittest discover -s tests` as the test command, and it currently passes. There's no CI, no package manifest, and no existing `.engineering/contract.json`.

Here's the lightweight setup I propose. Please review before I apply anything.

**Contract (`.engineering/contract.json`)**
- Project: `orders-service`, kind `product`, status `active`
- Verification: `python3 -m unittest discover -s tests` (matches your existing convention exactly), 60s timeout, required for R1+
- Risk-path floors (these set the *minimum* risk for a change touching these files, per the engineering-ownership risk model):
  - **R2** — `src/db/**` (persistence schema)
  - **R3** — `src/api/**` (the partner settlement adapter directly computes money submitted to an external partner; that's an explicit R3 trigger, and the existing ADR shows real consequences when it's gotten wrong)
- Artifacts: change briefs → `docs/engineering/changes`, decisions → `docs/decisions` (kept at its current location so your existing ADR stays put), runbooks → `docs/engineering/runbooks`, threat models → `docs/engineering/security`, evidence/handoffs → `.engineering/` (git-ignored)
- Session hooks: **off** (no automatic reminders unless you want them)
- Review interval: 7 days (revisit cadence for open evidence gaps)

**Pointers**
- Append a short pointer to `AGENTS.md` (and create `CLAUDE.md` with the same pointer) noting the contract exists and that `engineering check` should be run before finishing R1+ work.

**Mode**: `advise` only — nothing blocks locally or in CI; this just gives you a consistent way to size risk, capture briefs/decisions, and verify before shipping.

Does the R3 classification on `src/api/**` seem right to you, or would you rather keep it at R2 given how small the repo is today? And is 7-day review cadence fine, or do you want it longer since this sounds like a small/solo effort? Let me know and I'll apply it (or just say "go ahead" to accept as proposed).