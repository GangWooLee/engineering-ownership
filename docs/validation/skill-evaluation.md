# Skill evaluation

## Documentation-first regression

After the owner clarified that retained decision records—not a mandatory oral
exam—are the intended default, the changed handoff/revisit scenario was run
against the revised local skill.

The first run correctly linked a change brief, ADR, and runbook and treated
review as optional, but still produced a provisional maturity score. The skill
was strengthened to prohibit translating artifacts, checks, review state, or
competency tags into a person score. A fresh run then:

- linked canonical records in the handoff;
- marked old verification as stale until refreshed;
- offered optional `explain` and review commands without blocking other work;
- recorded gaps and a revisit date;
- refused the requested maturity score and reported specific missing evidence.

This targeted live regression passed after one observed-and-fixed failure. It
does not reuse the earlier 16/16 result as proof of the revised wording.

## Initial paired comparison

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

This comparison predates the documentation-first correction. It remains useful
for risk proportionality and current-diff behavior, but its mandatory
teach-back expectation is superseded.

The initial skill added the clearest value at:

- explicit risk classification without overburdening R0;
- R3 threat and recovery requirements;
- current-diff evidence rather than test-file or old-run claims;
- refusing to convert evidence into a maturity score.

Both configurations performed well at lightweight README review and rejecting
an old test result. These assertions alone are not discriminating. Timing and
token metrics are omitted because the collaboration task surface did not expose
them; no synthetic values are reported.

The local evaluation workspace includes response files, assertion-level
grading, benchmark JSON, and a static review viewer. It is intentionally
excluded from the release package.
