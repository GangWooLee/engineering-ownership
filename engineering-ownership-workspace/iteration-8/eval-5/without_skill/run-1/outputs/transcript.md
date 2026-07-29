Bash

This repo is tiny (one adapter, one schema module, one test) but already has the bones of a process: `AGENTS.md`/`CONTRIBUTING.md` say to run tests before pushing and to keep decision notes in `docs/decisions/` in sync, and there's already one such note. Nothing enforces those rules automatically yet — no CI, no PR template. I'll add just enough to make the existing rules self-enforcing without adding heavy tooling.

Now let me verify everything is consistent and the workflow YAML is valid.

YAML parses cleanly. Let me do a final review of everything added.

Everything looks good and tests still pass. Let me save a memory note about this repo's conventions since they're non-obvious and useful for future sessions.

## Summary

The repo already had house rules documented (`AGENTS.md`/`CONTRIBUTING.md`: run tests before pushing, keep decision notes in `docs/decisions/` in sync) but nothing enforced them. I added the minimum to make that self-enforcing:

- **`.github/workflows/tests.yml`** — runs `python3 -m unittest discover -s tests` on every push to `main` and every PR.
- **`.github/pull_request_template.md`** — a 3-item checklist mirroring the existing house rules (tests pass, separate commits for schema/adapter changes, decision notes updated).
- **`README.md`** — added a short "Development" section pointing new contributors to the test command and `CONTRIBUTING.md`.

Didn't add linting/formatting since none existed and it wasn't requested — kept it lightweight as asked. Verified the test suite still passes and the workflow YAML parses correctly. Nothing is committed yet; let me know if you'd like these staged and committed.