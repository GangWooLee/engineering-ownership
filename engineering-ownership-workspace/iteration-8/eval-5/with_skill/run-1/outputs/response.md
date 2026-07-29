I've inspected the repo. Before proposing setup, one thing stood out that you should know about regardless of what we do next:

**Finding:** `docs/decisions/2026-02-settlement-amount-units.md` documents a decision to convert order amounts from cents to whole units with half-up rounding *inside* `src/api/partner_adapter.py`. But the actual code in that file just passes `amount_cents` straight through unconverted — there's no rounding logic at all. The decision record and the code disagree. This is the only commit in the repo's history, so either the conversion was never implemented or was dropped. Worth resolving before anyone next touches that adapter, since the settlement payload sent to partners today would be rejected per the ADR's own description of the bug it was meant to fix.

Now, here's what I found for the repo itself:
- Small Python package (`orders-service`): order persistence schema + a partner settlement adapter.
- No CI, no package manifest. Tests run via `python3 -m unittest discover -s tests` (per `AGENTS.md`/`CONTRIBUTING.md`) — I ran it, it passes (1 test).
- `AGENTS.md` exists with 2 lines of instructions; no `CLAUDE.md` yet.
- No `.engineering/contract.json` yet.

**Proposed setup (nothing written yet — confirm and I'll apply it in one pass):**

1. **`.engineering/contract.json`** (new):
```json
{
  "version": 2,
  "project": { "name": "orders-service", "kind": "product", "status": "active" },
  "verification": [
    {
      "id": "unit",
      "argv": ["python3", "-m", "unittest", "discover", "-s", "tests"],
      "env": {},
      "timeout_seconds": 60,
      "required_for": ["R1", "R2", "R3"]
    }
  ],
  "risk_paths": {
    "R2": ["src/db/**"],
    "R3": ["src/api/**"]
  },
  "artifacts": {
    "changes": "docs/engineering/changes",
    "decisions": "docs/engineering/decisions",
    "runbooks": "docs/engineering/runbooks",
    "threat_models": "docs/engineering/security",
    "evidence": ".engineering/evidence",
    "handoffs": ".engineering/handoffs"
  },
  "automation": { "session_hooks": "off" },
  "review_interval_days": 7
}
```
   Note I customized `risk_paths` from the tool's generic defaults (`api/**`, `db/**`) to `src/api/**` / `src/db/**` since that's the real path prefix here, and put the adapter at **R3** rather than R2 — it's the only place money (settlement amounts) crosses into an external payload, which the risk model treats as R3 regardless of file size. `docs/decisions/**` already exists and doesn't need a pattern.

2. **`.engineering/handoffs/.gitignore`** (new) — `*` / `!.gitignore`, so future session handoffs stay untracked.

3. **`AGENTS.md`** — append a short pointer block (your existing 2 lines stay untouched).

4. **`CLAUDE.md`** — create new, containing only that same pointer block.

5. Session hooks default to **off** (no automatic reminders). I'd leave it there unless you want start/stop reminders — say so if you do.

Confirm this (or tell me what to adjust — e.g. different risk classification, `kind`/`status`, hook mode) and I'll apply it, then run `engineering doctor` to verify the setup landed cleanly.