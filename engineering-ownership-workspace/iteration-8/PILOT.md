# Efficacy measurement — collection finished, grading pending (2026-07-27)

Collection is complete. Grading has not run yet. **This note is written before
any pass rate exists**, so the analysis population below is a pre-registration
and not a choice made after seeing which framing flatters the result.

## Collection

| | |
| --- | --- |
| Runs | 54 of 54, no errors, no timeouts |
| Arms | 27 `with_skill`, 27 `without_skill` |
| Scenarios | all 9, three runs per configuration |
| Executor | `claude-sonnet-5` |
| Judge | `claude-opus-5` — pinned, and deliberately not the executor |
| Plugin under test | as published in `v0.3.0` (`main` at `0a4feed`) |

Preflight passed before the sweep: the baseline answered `NONE` when asked
which engineering-ownership skills were available, and the treatment named the
skill. Blinding holds: all 54 action logs pass the leak check, and no
`without_skill` run loaded the skill (0 of 27).

## The finding that has to be declared before grading

The treatment arm had the plugin available in all 27 runs, but **consulted the
skill in only 20**. The seven non-consulting runs are not spread evenly — they
cluster in three scenarios:

| Eval | Consulted | Scenario |
| --- | --- | --- |
| 1 | 1 / 3 | `proportionate-effort-on-a-trivial-change` |
| 3 | **0 / 3** | `stale-evidence-offered-as-proof` |
| 9 | 1 / 3 | `change-that-contradicts-an-accepted-decision` |
| 2, 4, 5, 6, 7, 8 | 3 / 3 each | — |

Two readings are possible and they are not the same:

- **Eval 1 may be correct non-engagement.** The skill's own R0 rule says not to
  create a change record merely because the skill was invoked. A model that
  declines to consult it on a trivial change may be honoring that rule, not
  failing to trigger. This cannot be settled by the counter — it needs the run
  read.
- **Evals 3 and 9 are the uncomfortable ones.** Recognizing stale evidence and
  handling a change that contradicts an accepted decision are the two
  behaviours this project points to when it calls maintenance its
  differentiator. They have the worst engagement in the set.

Note also that this population differs from `iteration-6`, which measured
triggering against short frozen probes. These are full scenario prompts, so
engagement here is a different — and more realistic — measurement.

## Pre-registered analysis

Both populations get reported. Neither is the headline on its own:

1. **All 27 treatment runs** — answers "does installing the plugin help?"
   This is the conservative figure and the one that must appear first in any
   summary.
2. **The 20 runs that consulted the skill** — answers "does consulting the
   skill help?" Reporting this alone would silently exclude the runs where the
   skill failed to engage, which is itself a property of the product.

The engagement rate (20/27, with the per-scenario breakdown above) is reported
alongside both, never omitted. Per-scenario means are reported for all nine
scenarios; the three-run sample per configuration is too small for any
scenario-level claim, and no scenario-level claim will be made from it.

## What would make this publishable

A number leaves this directory only if `docs/validation/skill-evaluation.md`
carries the machine-readable results block that `PublishedResultCase` checks,
with means matching the committed `benchmark.json` to four places and a
denominator that is the product of its own factors. Until then this remains
collection, not a claim.
