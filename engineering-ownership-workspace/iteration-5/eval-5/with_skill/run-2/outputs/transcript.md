I'll start by exploring the repository to understand its structure, stack, and current state before proposing a process.

This repo already has good bones — `AGENTS.md`, `CONTRIBUTING.md`, and a decision-record in `docs/decisions/`. I'll build on those rather than replace them: add CI to enforce the existing "run tests" rule, a PR template mirroring the existing checklist, a decision-doc template so future notes follow the same shape, and a `CLAUDE.md` so I (and other agents) pick up the conventions automatically.

Now I'll add small, additive notes to the existing docs to close the loop (CI existing, commit style, template pointer):

Let me verify everything still works and check the final state.

Tests pass and all new files are in place. I haven't committed anything — let me know if you'd like these staged/committed.

**What I set up, building on what was already here (`AGENTS.md`, `CONTRIBUTING.md`, `docs/decisions/`):**

- `.github/workflows/ci.yml` — runs `python3 -m unittest discover -s tests` on every push/PR, automating the rule your docs already state
- `.github/pull_request_template.md` — checklist mirroring `CONTRIBUTING.md` (tests pass, schema/adapter commits separated, decision note updated)
- `docs/decisions/TEMPLATE.md` — standardizes future decision notes on the shape of your existing `2026-02-settlement-amount-units.md`
- `CLAUDE.md` — points me (and future agent sessions) at `AGENTS.md`/`CONTRIBUTING.md` so the conventions get followed automatically
- Small additive notes in `AGENTS.md`/`CONTRIBUTING.md`: CI now runs the test command, commit subjects should be typed (`feat:`, etc., matching your existing commit), and pointers to the new template/PR checklist

I intentionally didn't add a linter/formatter or requirements file — the codebase is pure stdlib right now, and adding tooling config would be more ceremony than this repo needs today.

**One thing worth flagging, not fixed:** `docs/decisions/2026-02-settlement-amount-units.md` describes converting `amount_cents` to whole units with half-up rounding in `to_partner_payload`, but the actual code (`src/api/partner_adapter.py:8`) just passes `amount_cents` straight through — no conversion, no rounding — and the one existing test never checks the `amount` field. This is exactly the kind of drift the new PR checklist is meant to catch going forward, but it already exists in the current code. Want me to fix the adapter and add a test for it as a separate change?