For this change specifically, not much — it's a one-line README typo fix with no code impact. Concretely:

1. **Tests** — `AGENTS.md` requires running `python3 -m unittest discover -s tests` before pushing. I ran it: passes (1 test, OK).
2. **Commit & push** — stage `README.md`, commit with a plain message (e.g. `docs: fix typo in README`), then push and open a PR.

One thing worth flagging: the only commit currently on `main` is `aba224f feat: partner settlement rounding in progress`, which adds partner-settlement adapter/schema code labeled "in progress" along with `.engineering` evidence/decision docs. That's unrelated to your typo fix, but it means `main` already has WIP-labeled work on it — worth confirming with your team that's intentional before you add more commits on top, rather than something about to be reverted or rebased.

Want me to commit and push the README fix now?