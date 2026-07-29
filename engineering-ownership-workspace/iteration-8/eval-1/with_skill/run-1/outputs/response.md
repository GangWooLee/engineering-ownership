For a one-line README typo fix, this is about as low-risk as changes get (R0 — no behavior change), so no formal review process or change record is needed. Just the basics:

1. **Diff check** — confirm `git diff README.md` shows only the typo correction, nothing else slipped in.
2. **Commit it properly** — a clear commit message (not lumped into unrelated work).
3. **Open a PR (or push directly if your repo allows)** — even trivial fixes are easier to track via PR history.
4. **Quick self-review** — make sure the corrected spelling/wording is actually correct and doesn't break any Markdown formatting (links, code fences, etc.) around it.

Given your last commit was `feat: partner settlement rounding in progress`, make sure this README fix is committed separately from that in-progress work, so it doesn't get bundled into an unrelated feature commit.

Want me to check the diff and commit it now?