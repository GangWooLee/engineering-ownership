Everything's in place and verified. I haven't committed — let me know if you'd like these staged/committed, since you said you're new to the repo and may want to review first.

## What's set up

- **CI** (`.github/workflows/ci.yml`): runs the unittest suite on every push/PR to `main`.
- **PR template** (`.github/pull_request_template.md`): checklist for the two rules already documented in `AGENTS.md`/`CONTRIBUTING.md` (tests pass, decision notes updated alongside behavior changes).
- **`Makefile`**: `make test` as a shorthand for the unittest command.
- Small edits to `AGENTS.md`/`CONTRIBUTING.md` to point at CI and the PR checklist, and to make the existing `docs/decisions/` convention explicit in `AGENTS.md` (it was only mentioned in `CONTRIBUTING.md` before).

I kept this minimal on purpose — no linter/formatter added, since none was already in use and introducing one is a real decision (which tool, what config) rather than a "lightweight" default.

## Worth knowing before you start

`docs/decisions/2026-02-settlement-amount-units.md` documents that the partner adapter converts cents to whole-unit amounts with half-up rounding — but `src/api/partner_adapter.py` doesn't do this conversion at all, and the one existing test doesn't check the `amount` field. This is a live doc/code mismatch, not something I introduced or fixed. I'd treat it as the first item to triage under the new process, since it's a good test of whether the PR checklist actually catches this class of drift.