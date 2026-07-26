I'll start by exploring the repository to understand its structure, language, and tooling before setting up a process.

This is a tiny, dependency-free Python repo (stdlib `unittest`) that already has informal conventions (`CONTRIBUTING.md`, `AGENTS.md`, ADR-style notes in `docs/decisions/`) but nothing that enforces them. I'll turn those conventions into a minimal, low-maintenance process: CI that runs the existing test command, a PR checklist mirroring what `CONTRIBUTING.md` already asks for, and a template for the design-note pattern that's already in use — no new dependencies, linters, or frameworks.

Now updating `CONTRIBUTING.md` and `AGENTS.md` to point at the new template and CI check:

Let me verify everything's in order and the test suite still runs clean:

Set up. Here's what's in place:

- **`.github/workflows/ci.yml`** — runs `python3 -m unittest discover -s tests` on every push/PR to `main`. No new dependencies; it's the exact command `CONTRIBUTING.md`/`AGENTS.md` already ask contributors to run, just automated.
- **`.github/pull_request_template.md`** — a 3-item checklist mirroring the existing conventions (tests pass, decision note updated, schema/adapter commits kept separate).
- **`docs/decisions/TEMPLATE.md`** — a copyable skeleton matching the prose style of the existing `2026-02-settlement-amount-units.md` note (problem → options rejected → decision → boundary of when it stops applying).
- **`CONTRIBUTING.md` / `AGENTS.md`** — updated with one line each pointing to the new template and noting CI now enforces the test command.

I didn't add a linter, formatter, or dependency manifest — the project has zero third-party dependencies today, so introducing tooling for that felt like more process than the repo currently needs.

One thing worth flagging while I was in there: the [decision note](docs/decisions/2026-02-settlement-amount-units.md) describes converting `amount_cents` to whole units with half-up rounding before sending to the partner, but `src/api/partner_adapter.py` just passes `amount_cents` straight through as `amount`, and the one existing test only checks `orderId`. That gap wouldn't be caught by the CI I just added since there's no test for it — worth a look, but I left it alone since it's outside "set up the process."