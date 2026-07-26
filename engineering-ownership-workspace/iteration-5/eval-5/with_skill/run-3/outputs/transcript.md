I'll start by exploring the repository to understand its structure, tech stack, and current state.

I now understand the repo: a tiny Python (stdlib-only) service with one adapter, one schema module, one test, and a decision-log convention (`docs/decisions/`) already referenced by `AGENTS.md`/`CONTRIBUTING.md`. Two things stand out before I set up process:

1. **No CI** — tests only run if someone remembers to run them locally.
2. **Live process gap**: `docs/decisions/2026-02-settlement-amount-units.md` says the adapter converts cents to whole units with half-up rounding before sending to the partner, but `src/api/partner_adapter.py` just passes `amount_cents` straight through — no conversion exists, and the single test only checks `orderId`, not `amount`. This is exactly the kind of doc/code drift the CONTRIBUTING.md rule is meant to prevent, and it's already present. I'm not fixing it (out of scope for "set up process"), but flagging it as the first thing to triage.

I'll add lightweight process scaffolding: CI to run tests automatically, and a PR template that encodes the two rules already written down in `AGENTS.md`/`CONTRIBUTING.md` (tests pass; decision notes updated alongside behavior changes) so they're enforced instead of just documented.

Now let me wire these into the existing docs with minimal edits, rather than duplicating rules.

Let me verify the CI workflow syntax and that tests still pass.

Everything's in place and verified. I haven't committed — let me know if you'd like these staged/committed, since you said you're new to the repo and may want to review first.

## What's set up

- **CI** (`.github/workflows/ci.yml`): runs the unittest suite on every push/PR to `main`.
- **PR template** (`.github/pull_request_template.md`): checklist for the two rules already documented in `AGENTS.md`/`CONTRIBUTING.md` (tests pass, decision notes updated alongside behavior changes).
- **`Makefile`**: `make test` as a shorthand for the unittest command.
- Small edits to `AGENTS.md`/`CONTRIBUTING.md` to point at CI and the PR checklist, and to make the existing `docs/decisions/` convention explicit in `AGENTS.md` (it was only mentioned in `CONTRIBUTING.md` before).

I kept this minimal on purpose — no linter/formatter added, since none was already in use and introducing one is a real decision (which tool, what config) rather than a "lightweight" default.

## Worth knowing before you start

`docs/decisions/2026-02-settlement-amount-units.md` documents that the partner adapter converts cents to whole-unit amounts with half-up rounding — but `src/api/partner_adapter.py` doesn't do this conversion at all, and the one existing test doesn't check the `amount` field. This is a live doc/code mismatch, not something I introduced or fixed. I'd treat it as the first item to triage under the new process, since it's a good test of whether the PR checklist actually catches this class of drift.