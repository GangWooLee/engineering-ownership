# Skill evaluation

Date: 2026-07-23

Four prompts were run once with the shared skill and once without it:

1. README-only typo;
2. production refresh-token rotation;
3. database plus partner API change with stale test claims;
4. post-release handoff, retained understanding, and a maturity-score request.

| Configuration | Passed expectations |
| --- | ---: |
| With skill | 16 / 16 |
| Without skill | 5 / 16 |

The skill added the clearest value at:

- explicit risk classification without overburdening R0;
- R3 threat, recovery, and no-AI teach-back requirements;
- current-diff evidence rather than test-file or old-run claims;
- refusing to convert evidence into a maturity score.

Both configurations performed well at lightweight README review and rejecting
an old test result. These assertions alone are not discriminating. Timing and
token metrics are omitted because the collaboration task surface did not expose
them; no synthetic values are reported.

The local evaluation workspace includes response files, assertion-level
grading, benchmark JSON, and a static review viewer. It is intentionally
excluded from the release package.

