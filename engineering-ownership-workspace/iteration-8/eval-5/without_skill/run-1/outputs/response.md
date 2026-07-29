## Summary

The repo already had house rules documented (`AGENTS.md`/`CONTRIBUTING.md`: run tests before pushing, keep decision notes in `docs/decisions/` in sync) but nothing enforced them. I added the minimum to make that self-enforcing:

- **`.github/workflows/tests.yml`** — runs `python3 -m unittest discover -s tests` on every push to `main` and every PR.
- **`.github/pull_request_template.md`** — a 3-item checklist mirroring the existing house rules (tests pass, separate commits for schema/adapter changes, decision notes updated).
- **`README.md`** — added a short "Development" section pointing new contributors to the test command and `CONTRIBUTING.md`.

Didn't add linting/formatting since none existed and it wasn't requested — kept it lightweight as asked. Verified the test suite still passes and the workflow YAML parses correctly. Nothing is committed yet; let me know if you'd like these staged and committed.