# Evaluation workspace

Committed so that anyone can audit the responses and the grading rather than
trusting a summary. `CONTRIBUTING.md` asks contributors for paired
skill/baseline evaluation evidence; keeping the maintainer's own evidence out of
the repository would exempt the maintainer from that.

`review.html` and `feedback.json` stay untracked. They are regenerated from the
committed JSON, and a second copy of the same numbers is a second thing that can
disagree.

| Iteration | Status | What it is |
| --- | --- | --- |
| `iteration-1` | Withdrawn | The evidence behind the retracted "16 / 16 versus 5 / 16" claim. Kept so the six defects listed in `docs/validation/skill-evaluation.md` can be checked rather than taken on faith. Its responses are in mixed languages, which is one of those defects. |
| `iteration-2` | Pilot | A two-run harness shakedown on one maintenance scenario. **Not an evaluation result and not a published claim.** It exists to show the runner, the fixture, the blinded judge, and the aggregator working end to end, and to record the harness defects it exposed. |
| `iteration-3` | Harness validation | One scenario, one run per configuration, exercising write-enabled runs and the action-log judge bundle. **Not an evaluation result.** Recorded because it is what showed the changed harness working, and because the judge's critique of an expectation here is why that expectation was split. |
| `iteration-4` | Fixture check | The ninth scenario repeated on a repository carrying ordinary engineering conventions instead of this skill's artifacts. **Not an evaluation result.** It was built to size a fixture confound and instead recorded that the skill did not engage at all on that repository. |
| `iteration-5` | Trigger rate | Two scenarios on the unmanaged base, three runs per configuration, run to settle whether `iteration-4`'s single non-engagement was a sample of one. **Not an evaluation result and not an efficacy claim**: it measures only how often the skill engages, never how well a run went. The treatment engaged in none of six runs. |
| `iteration-6` | Trigger probes | Whether the skill is consulted, measured against a frozen probe set with a positive and a negative class, before and after its description was rewritten. **Not an evaluation result**: it says whether the skill runs, never whether running it helps. Runs are filed by a digest of the description they measured. |

No quantitative efficacy claim is published from any iteration here.
`iteration-5` publishes a trigger rate, which is a claim about whether the skill
runs at all and not about what difference it makes. See
`docs/validation/skill-evaluation.md`.
