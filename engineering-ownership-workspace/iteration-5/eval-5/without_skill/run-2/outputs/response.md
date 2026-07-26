I set up:

- **`.github/workflows/tests.yml`** — runs `python3 -m unittest discover -s tests` on every push to `main` and every PR. Turns the existing "run tests before pushing" rule into an enforced one instead of an honor system.
- **`.github/pull_request_template.md`** — a 3-item checklist encoding the conventions already stated in `AGENTS.md`/`CONTRIBUTING.md`: tests pass, decision notes updated, schema/adapter changes in separate commits.
- **`CONTRIBUTING.md`** — one added line noting CI now runs the suite automatically.

No remote is configured on this repo, so the workflow will activate once you push to GitHub.

One thing worth your attention before your first PR here: `docs/decisions/2026-02-settlement-amount-units.md` documents that the adapter should convert `amount_cents` to whole units (round half-up) before sending to the partner, but `src/api/partner_adapter.py` doesn't do that conversion, and the only test doesn't check the `amount` field — so this is exactly the kind of drift the new checklist is meant to catch, but it already slipped through once. Want me to fix the adapter to match the decision note, or leave it for now?