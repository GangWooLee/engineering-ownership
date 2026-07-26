I'll start by exploring the repository to understand its structure, tech stack, and current state.

This is a small, clean Python repo (order records + a partner settlement adapter) with no CI, no hooks, and no PR template yet — but it already has good bones: `AGENTS.md`/`CONTRIBUTING.md` state a test command and an ADR convention (`docs/decisions/`). I found one important issue worth flagging separately below. Now let me set up a lightweight process that formalizes what's already implied.

Now making the hook executable, and adding an ADR template so the existing `docs/decisions/` convention is easy to follow consistently:

Now updating `CONTRIBUTING.md` to tie these pieces together:

Let's verify everything works end to end, and clean up the `__pycache__` noise from running tests earlier:

Everything runs cleanly, and no stray `__pycache__` files got picked up by git status. Let me review the final diff before handing off:

I've set up the process (not yet committed — let me know if you'd like these committed). Here's what's in place:

- **CI** (`.github/workflows/ci.yml`): runs the existing test command on every push/PR to `main`.
- **Pre-push hook** (`.githooks/pre-push`): runs tests locally before push; opt in with `git config core.hooksPath .githooks` (documented in `CONTRIBUTING.md`).
- **PR template** (`.github/PULL_REQUEST_TEMPLATE.md`): checklist mirroring the rules already stated in `AGENTS.md`/`CONTRIBUTING.md` (tests pass, schema/adapter commits separated, decision notes updated).
- **ADR template** (`docs/decisions/TEMPLATE.md`): so future design notes follow the same shape as the existing one.
- **`CONTRIBUTING.md`**: now points to all of the above.

I kept it minimal — no linter/formatter added, since none existed and the repo is small; adding opinionated tooling wasn't asked for.

**One important thing I found while reading the code, separate from the process setup:** `docs/decisions/2026-02-settlement-amount-units.md` documents that the adapter should convert `amount_cents` to whole units with half-up rounding before sending to the partner API — but `src/api/partner_adapter.py` just passes `amount_cents` straight through, unconverted. Both were added in the same commit (`5e6706c`), and the one existing test only checks `orderId`, so nothing currently catches this. If the doc is right, this is a real bug affecting partner payment amounts. Want me to fix the adapter and add a regression test for it?