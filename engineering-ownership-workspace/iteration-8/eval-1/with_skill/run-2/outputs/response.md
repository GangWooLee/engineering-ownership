For a one-word typo fix in a single-line README (no CI, no CONTRIBUTING guide in this repo), the bar is low:

1. **Review the diff** — `settlment` → `settlement`, correctly spelled, no other changes snuck in.
2. **Commit it** with a clear message (e.g., `docs: fix typo in README`).
3. **Push and open a PR** (or merge directly if this repo allows direct pushes to `main` for trivial docs fixes — check your team's norms).

Two things worth noting given the current state of the repo:
- Your last commit (`aba224f feat: partner settlement rounding in progress`) is unrelated in-progress work — make sure this typo fix goes in its own commit rather than getting folded into that one.
- No CI/lint is configured for this repo, so there's no automated check to wait on.

Since it's a docs-only, zero-risk change, I wouldn't over-process it — commit and push is reasonable. Want me to commit it now?