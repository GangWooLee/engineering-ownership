I've reviewed the repo. It's a tiny Python service (`orders-service`) with existing conventions but no automation enforcing them:

- **AGENTS.md / CONTRIBUTING.md**: run `python3 -m unittest discover -s tests` before pushing; keep schema vs. adapter changes in separate commits; update `docs/decisions/` notes in the same PR if a change alters what they describe.
- **docs/decisions/**: one ADR-style note so far (`2026-02-settlement-amount-units.md`).
- No CI, no PR template, no lint config — these rules currently rely entirely on people remembering them.

One thing worth flagging before I go further: the decision note says the adapter should convert cents to whole units with half-up rounding, but `src/api/partner_adapter.py` just passes `amount_cents` straight through with no conversion — and the only existing test doesn't check the `amount` field at all, so nothing catches this. That's a real doc/code mismatch, not something I'll fix silently since it changes settlement math. I'll leave it for you to confirm, but I'll make sure the process I set up would have caught it going forward.

For the "process" itself, given the repo's size, I'll keep it minimal:
1. A GitHub Actions workflow that runs the test suite on every push/PR (turns the "run tests before pushing" rule from a memory into an enforced check).
2. A PR template checklist mirroring the two rules already in CONTRIBUTING.md (tests pass, commits split, decision notes updated).

Let me set those up.

Now let me verify the workflow YAML is valid and check the final state.

Everything's in place and no other files were touched. Here's the state:

**Added:**
- `.github/workflows/tests.yml` — runs `unittest discover` on every push/PR to `main`
- `.github/pull_request_template.md` — checklist for the two rules already in AGENTS.md/CONTRIBUTING.md
- Small `CONTRIBUTING.md` update pointing at both

I haven't committed anything — let me know if you'd like these committed, and separately, whether you want me to look at fixing the `partner_adapter.py` / settlement-note mismatch (undocumented right now, and not covered by the existing test).