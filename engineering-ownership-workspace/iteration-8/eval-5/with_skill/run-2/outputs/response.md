I've reviewed the repo: it's a small Python service (`orders-service`) with no CI, no package manifest, tests run via `python3 -m unittest discover -s tests`, and an existing ADR convention in `docs/decisions/`. One thing worth flagging separately: the ADR at `docs/decisions/2026-02-settlement-amount-units.md` says the adapter should convert cents to whole units before sending to the partner API, but `src/api/partner_adapter.py` currently just passes `amount_cents` through unconverted — the code doesn't match the documented decision. I'll leave that alone for now since you asked for process setup, not a fix, but flag it in case it's news to you.

Here's the setup I'd like to apply (nothing is written yet):

**Contract** (`.engineering/contract.json`)
- kind: `product`, status: `active`
- Verification: `python3 -m unittest discover -s tests` (matches AGENTS.md/CONTRIBUTING.md)
- R2 paths: `src/db/**` (schema/persistence changes)
- R3 paths: `src/api/**` (partner settlement integration — handles money, matches your existing ADR's own reasoning)
- Hooks: `off` (no session-start/stop reminders unless you want them)

**Pointers**
- Add a short pointer in `AGENTS.md` noting the contract and that R1+ changes should go through `engineering change start`
- No `CLAUDE.md` exists yet — I'll leave it out unless you want one added too

**Handoff ignore file**: add the plugin's handoff directory to `.gitignore` so local handoffs never get committed.

Want me to proceed with this, or adjust the risk paths / hook setting first?