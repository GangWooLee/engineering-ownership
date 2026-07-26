# Efficacy measurement — complete (2026-07-27)

Collection, grading, aggregation, and correction are all finished. Nothing was
excluded: 54 of 54 runs completed, all 54 were graded, and the judge refused
none of them. The pre-registration below was committed in `e3c3ebf`, before any
pass rate existed.

## Conditions

| | |
| --- | --- |
| Runs | 54 of 54 — no errors, no timeouts, none excluded |
| Arms | 27 `with_skill`, 27 `without_skill`, nine scenarios, three runs each |
| Executor | `claude-sonnet-5` |
| Judge | `claude-opus-5` — pinned, deliberately not the executor |
| Plugin under test | as published in `v0.3.0` (`main` at `0a4feed`) |

Preflight passed before the sweep: the baseline answered `NONE`, the treatment
named the skill. Blinding held — all 54 action logs pass the leak check, no
`without_skill` run loaded the skill, and no run was refused for identifying
its configuration.

## Result, in the pre-registered order

**1. All 27 treatment runs (intention-to-treat).** This is the conservative
figure and it leads.

| | pass rate |
| --- | --- |
| with skill | 0.7160 |
| without skill | 0.5648 |
| difference | **+0.1512** |

**2. The 20 runs that consulted the skill (per-protocol).** 0.7533 against the
same 0.5648 baseline. The seven runs that had the plugin but did not consult it
scored 0.6095 — between the two, not at baseline.

**3. Engagement.** The treatment consulted the skill in 20 of 27 runs. The
misses cluster: eval-1 1/3, eval-3 0/3, eval-9 1/3; the other six scenarios
engaged 3/3.

## Uncertainty, and how it was computed

Runs are not independent — three runs share a scenario, a prompt, and a
fixture — so treating 27 runs as 27 observations overstates precision. The
defensible unit is the scenario, paired across arms (n = 9):

mean difference **+0.1512**, SD 0.1644, SE 0.0548,
95% interval **[+0.025, +0.278]** (t, df = 8).

The interval excludes zero, but it is wide: the data are consistent with an
effect anywhere from about 2 to 28 percentage points.

**Declared honestly:** the analysis *populations* were pre-registered; this
interval method was not. It was chosen after seeing the data, because
scenario-level clustering was the obvious correct treatment once the
three-runs-per-scenario structure was in front of us. A reader should discount
it accordingly, and a future iteration should pre-register the test as well as
the population.

## Per-scenario, and the finding that cuts against the project

| Eval | with | without | diff | Scenario |
| --- | --- | --- | --- | --- |
| 4 | 1.000 | 0.583 | +0.417 | handover-without-grading-the-person |
| 5 | 1.000 | 0.667 | +0.333 | propose-before-changing-an-unfamiliar-repository |
| 1 | 0.778 | 0.556 | +0.222 | proportionate-effort-on-a-trivial-change |
| 2 | 1.000 | 0.833 | +0.167 | high-risk-change-under-time-pressure |
| 6 | 1.000 | 0.867 | +0.133 | resume-work-without-conversation-history |
| 7 | 0.333 | 0.222 | +0.111 | reuse-existing-planning-documents |
| 8 | 0.333 | 0.222 | +0.111 | leave-rationale-where-it-is-not-obvious |
| 3 | 0.667 | 0.667 | **0.000** | stale-evidence-offered-as-proof |
| 9 | 0.333 | 0.467 | **−0.133** | change-that-contradicts-an-accepted-decision |

Three scenarios deserve to be read before the headline number is:

- **Eval 9 went the wrong way.** A change that contradicts an accepted decision
  is the behaviour this project points to when it calls maintenance its
  differentiator, and the skill scored *below* the baseline on it — while
  engaging in only one of three runs. One negative scenario out of nine is
  within noise at this sample size, but it is the worst possible scenario to be
  negative on, and it should not be averaged away.
- **Eval 3 is exactly zero, with zero engagement.** The skill never consulted
  itself on stale evidence offered as proof, so it changed nothing. That is a
  triggering failure on a scenario squarely inside the skill's stated domain,
  and it is invisible in the aggregate.
- **Evals 7 and 8 are low in both arms** (0.333 vs 0.222). The gap is positive
  but both configurations mostly fail. Whatever those expectations ask for, the
  skill is not delivering it either.

Eval-1's 1/3 engagement is the one miss that may be correct: the skill's own R0
rule says not to create a change record merely because the skill was invoked,
so declining to consult it on a trivial change may be obedience rather than
failure. It still scored +0.222.

## Measurements

Corrected with `scripts/eval/fix_benchmark.py`, which replaces the vendored
aggregator's character-count-labelled-as-tokens with the real figures from each
run's `timing.json`:

| | with skill | without skill |
| --- | --- | --- |
| tokens (mean) | 1,638,349 | 1,406,880 |
| wall time (mean) | 137 s | 151 s |

Before correction the same file reported 2,037 and 1,356 "tokens" — the
character counts, off by roughly three orders of magnitude. That defect is the
reason the post-pass exists.

## Status of the claim

**Nothing here is published.** `docs/validation/skill-evaluation.md` remains
`Status: Withdrawn`, and this project still makes no quantitative efficacy
claim. Publishing would require a deliberate decision, the machine-readable
results block that `PublishedResultCase` checks, and a resolution of one
mismatch: that gate's denominator formula assumes a constant number of
expectations per eval, and this manifest has 3, 4, 3, 4, 3, 5, 3, 3, 5.

What a reader may take from this directory today: on nine scenarios with three
runs each, against a baseline that never loaded the skill, the skill scored
higher overall, engaged in 20 of 27 runs, and was neutral or worse on the two
scenarios closest to its stated differentiator.
