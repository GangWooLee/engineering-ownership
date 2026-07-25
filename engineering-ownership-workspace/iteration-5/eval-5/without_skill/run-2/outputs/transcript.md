I'll start by exploring the repository to understand its structure, language, and existing tooling before proposing a process.

Found the key thing worth knowing before you start: this repo already has *documented* conventions (`AGENTS.md`, `CONTRIBUTING.md`) — run tests before pushing, keep decision notes in sync — but they're enforced by hand only. And they're currently not being followed: `docs/decisions/2026-02-settlement-amount-units.md` documents that the adapter should convert cents to whole units (round half-up) before sending to the partner API, but `src/api/partner_adapter.py` just passes `amount_cents` straight through, and the one test doesn't check `amount` at all. That's a live discrepancy between the design note and the code — exactly the kind of thing manual review missed.

I'll set up a lightweight process that closes that gap: CI that runs the test suite automatically (turning the documented "run before pushing" rule into an enforced one), and a PR template that encodes the "update the decision note" and "separate commits" conventions already in `CONTRIBUTING.md`/`AGENTS.md` so they're not just tribal knowledge.

Now a one-line pointer in `CONTRIBUTING.md` so the automation is discoverable from the doc that already states the rule:

YAML is valid, and I already confirmed the test command itself runs clean (`OK`, 1 test).

I set up:

- **`.github/workflows/tests.yml`** — runs `python3 -m unittest discover -s tests` on every push to `main` and every PR. Turns the existing "run tests before pushing" rule into an enforced one instead of an honor system.
- **`.github/pull_request_template.md`** — a 3-item checklist encoding the conventions already stated in `AGENTS.md`/`CONTRIBUTING.md`: tests pass, decision notes updated, schema/adapter changes in separate commits.
- **`CONTRIBUTING.md`** — one added line noting CI now runs the suite automatically.

No remote is configured on this repo, so the workflow will activate once you push to GitHub.

One thing worth your attention before your first PR here: `docs/decisions/2026-02-settlement-amount-units.md` documents that the adapter should convert `amount_cents` to whole units (round half-up) before sending to the partner, but `src/api/partner_adapter.py` doesn't do that conversion, and the only test doesn't check the `amount` field — so this is exactly the kind of drift the new checklist is meant to catch, but it already slipped through once. Want me to fix the adapter to match the decision note, or leave it for now?