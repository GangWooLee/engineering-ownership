No memory yet — this is a fresh project. Let me explore the repo structure before proposing a process.

The repo already has a documented process — I'll summarize it and add the missing piece: automation to enforce it.

**What's already here:**
- `AGENTS.md` / `CONTRIBUTING.md`: run `python3 -m unittest discover -s tests` before pushing; keep schema and adapter changes in separate commits; update `docs/decisions/` notes in the same PR when a change alters what they describe.
- `docs/decisions/`: lightweight ADRs (one exists: `2026-02-settlement-amount-units.md`).
- No CI, no dependency manifest, no PR template — the rules are documented but not enforced.

One thing worth flagging: that decision doc describes converting cents to whole-unit amounts with half-up rounding in the adapter, but `src/api/partner_adapter.py` just passes `amount_cents` straight through — the doc and code have already drifted apart. I'll leave that as-is since it's not what you asked for, but it's a good example of why doc-sync enforcement is useful here.

I'll add CI to run the test suite automatically and a PR template that mirrors the two rules already in CONTRIBUTING.md, so they're surfaced instead of relied on from memory.

Set up for a repo that already had documented conventions but no enforcement:

- **`.github/workflows/tests.yml`** — runs `python3 -m unittest discover -s tests` on every push to `main` and every PR, so the existing "run tests before pushing" rule in `AGENTS.md`/`CONTRIBUTING.md` is actually checked rather than relied on memory.
- **`.github/pull_request_template.md`** — a 3-item checklist mirroring the two rules already documented: tests pass, schema/adapter changes split into separate commits, and `docs/decisions/` notes updated in the same PR if a change alters what they describe.

Nothing else needed changing — `AGENTS.md`, `CONTRIBUTING.md`, and `docs/decisions/` already form a reasonable lightweight process for a repo this size; these two files just make it enforced instead of memorized. Both files are new/untracked, nothing committed.

One thing to flag since you're new here: `docs/decisions/2026-02-settlement-amount-units.md` documents converting order amounts to whole units with half-up rounding inside the adapter, but `src/api/partner_adapter.py` currently just passes `amount_cents` through unconverted — the doc and code have already drifted. Let me know if you'd like me to look into that.