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

---

## Correction, 2026-07-27 — two readings above are wrong

A follow-up investigation into the eval-3 and eval-9 engagement misses
overturned two claims made earlier in this note. They are corrected here rather
than edited away.

**Wrong: "Eval 9 went the wrong way."** The gap is not a scenario-level effect.
Exact two-sided permutation over the six runs gives **p = 0.600** — with
`{0.2, 0.4, 0.4}` against `{0.2, 0.6, 0.6}`, twelve of twenty splits are at
least as extreme. The entire −0.133 decomposes into **two boolean judge cells**
(5 of 15 expectation-cells passed against 7 of 15). Three further facts make
attribution to the skill untenable: expectation E4 (*"says why keeping the
earlier reasoning legible matters to someone reading this later"*) has passed
**0 of 8 times across every eval-9 run ever recorded, in both arms and two
rubric generations** — 20% of the denominator is a constant that cannot
discriminate; all six judges independently flagged E3 and E5 as unreachable for
a run that correctly pauses to ask; and the fixture is self-contradictory — its
decision note asserts every partner settles in whole units while the settled
code restricts conversion to `{p-1, p-7}`, so "our largest partner" has no
referent. Finally, dropping the one consulting run makes the treatment arm
*worse* (0.300), because that run was the arm's joint best — and it invoked the
skill as its **terminal** tool call, after deciding to stop, having read no
reference file. Consulting cannot cause a deficit it sits above. Eval-9 is a
**measurement** problem, not an efficacy one.

**Wrong: "The skill never consulted itself on stale evidence, so it changed
nothing."** The first clause is right and now stronger; the second does not
follow. Eval-3's engagement is **0 of 6 pooled across iterations 7 and 8** — the
`description` is byte-identical between them, and selection is a function of the
description alone, so the abandoned iteration's engagement data is still valid.
Against this arm's 20/27 rate that is p ≈ 3×10⁻⁴: not noise. But the expectation
eval-3 fails (E3, *"addresses how this change would be undone or repaired"*) has
**no owner anywhere on the routed path** — `resume.md`, `finish.md`, and
`start.md` contain zero rollback, revert, undo, or repair guidance (`resume.md`'s
only near-match is "the recovered problem", meaning context, not reversal).
Eval-6 runs on a byte-identical working tree, engaged **3/3**, scored **1.000**,
and still produced zero reversibility language. **The skill would have changed
nothing here even if it had fired.** That is a content gap wearing a triggering
gap's clothes, and it is worse than the original reading.

**New, and it qualifies the headline:** `skill_loaded` records that the Skill
tool was invoked — that the 109-line router page entered context — not that any
route was followed. **Nine of the twenty "consulting" runs read no reference
file at all**, including eval-9's only consulting run and two eval-6 runs that
scored 1.000. The +0.1512 is therefore substantially an effect of the router
page; the reference layer that carries the actual guidance is largely
**unmeasured**, not validated.

**Also corrected:** eval-1's 1/3 was described above as possibly "obedience
rather than failure". Its single consulting run is the only eval-1 run in either
arm to fail E1 — it spent its one action on a read outside the repository
instead of the diff — while its two non-consulting arm-mates scored 1.000 and
0.667. Whatever eval-1's misses are, principled restraint being rewarded is not
supported by this data.

---

## Re-grade outcome, 2026-07-29 — the prediction failed

The correction above proposed that a corrected rubric would show eval-9's
negative gap to be an artifact. The six stored responses were re-graded in
`iteration-8-eval9-regrade` under a rubric fixed **before** any re-graded score
existed (`db97464`): the never-passing expectation removed, the two
artifact-requiring expectations given a deferral branch. **The gap did not
disappear.**

| | with skill | without skill | difference | permutation p |
| --- | --- | --- | --- | --- |
| original rubric, 5 expectations | 0.3333 | 0.4667 | −0.1333 | 0.600 |
| corrected rubric, 4 expectations | 0.5833 | 0.7500 | **−0.1667** | **0.700** |

Both arms rose sharply, which confirms the rubric was broken: the dead
expectation and the missing deferral branch were suppressing every run in both
configurations. But the direction held, and the result became *less*
distinguishable from noise, not more.

Per run, before → after:

| run | with skill | without skill |
| --- | --- | --- |
| run-1 | 1/5 → 1/4 | 1/5 → 3/4 |
| run-2 | 2/5 → **4/4** | 3/5 → 3/4 |
| run-3 | 2/5 → 2/4 *(the only run that consulted the skill)* | 3/5 → 3/4 |

The honest reading is about variance, not means. The baseline is now perfectly
uniform — 3/4 in all three runs — while the treatment ranges from 1/4 to a clean
4/4. The treatment produced both the best run in the set and the worst. With
three runs per arm and p = 0.700, **these six runs cannot distinguish the two
configurations in either direction**, and that is the finding.

Two things this settles and one it does not:

- **Settled:** the rubric was genuinely defective, and the earlier claim that
  eval-9's gap was attributable to the skill remains unsupported — now on two
  independent rubrics rather than one.
- **Settled:** "the gap will disappear once the rubric is fixed" was a
  prediction made in this file, and it was wrong. It is recorded rather than
  quietly dropped.
- **Not settled:** whether the skill helps, hurts, or does nothing on this
  scenario. Answering it needs more runs per arm, not a better rubric — the
  variance in the treatment arm is larger than the gap between arms.

The corrected rubric is not back-ported to the shipped `evals.json`. Doing that
is a product change and belongs to its own decision, made in the open rather
than as a side effect of an investigation.
