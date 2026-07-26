I've set up a lightweight process built directly on the norms this repo already had:

**Added:**
- `.github/workflows/ci.yml` — runs `python3 -m unittest discover -s tests` on every push to `main` and every PR. This turns the "run tests before pushing" rule in `AGENTS.md`/`CONTRIBUTING.md` from an honor-system note into something enforced. (Note: there's no git remote configured yet, so this won't actually execute until the repo is pushed to GitHub.)
- `.github/pull_request_template.md` — a 3-item checklist mirroring the exact rules already in `CONTRIBUTING.md`/`AGENTS.md`: tests pass, decision notes stay in sync, schema/adapter changes stay in separate commits.
- Small edit to `CONTRIBUTING.md` — mentions CI now runs the test command, and pulled the "separate commits" rule from `AGENTS.md` into the human-facing doc too, so it's not agent-only.

I deliberately didn't add a linter/formatter or restructure anything — nothing in the repo currently establishes one, and the codebase is two small stdlib-only files, so imposing a tool choice felt like overreach for "lightweight."

**Flagging a real issue I found while reading the code, not part of this task's scope:** `docs/decisions/2026-02-settlement-amount-units.md` documents that the adapter should convert `amount_cents` to whole units with half-up rounding before sending to partners. `src/api/partner_adapter.py` doesn't do that — it passes `amount_cents` straight through, and the only test doesn't check `amount`, so it's not caught. This is exactly the kind of drift the new PR checklist item is meant to prevent going forward, but the existing drift is still there. Want me to fix it, or leave it for you to look at first?

Nothing is committed yet — let me know if you'd like these committed, or if you want to make edits first.