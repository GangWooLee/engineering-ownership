# Efficacy measurement — COLLECTING (started 2026-07-26)

Do not read a figure from this directory until this note says the sweep
finished and reports what was excluded. A partially collected sweep looks
exactly like a complete one from the outside, and the rate-limited stretch in
an earlier attempt showed that runs vanish in contiguous blocks rather than at
random — the shape most likely to bias a mean if it is read early.

## What this is measuring

Whether the skill helps, not whether it runs. Trigger rate was settled
separately (iteration-6, frozen probes, pre-registered bars); this asks what
difference consulting the skill makes to the work itself.

## Conditions

- Treatment loads the plugin exactly as published in `v0.3.0` (`main` at
  `0a4feed`); the baseline runs with every user-scope plugin disabled and no
  `--plugin-dir`.
- Preflight is **run, not skipped**. The previous attempt skipped it while
  resuming; this one starts fresh against a skill that changed materially
  (terminal close state, competency-tag removal), so the control that proves
  the two arms differ only in skill availability has to be re-established.
- Nine scenarios, three runs per configuration, 600 s timeout, 15 s pause
  between runs. The pause exists because eight runs were once lost to rate
  limiting three seconds apart.
- The judge sees an action log and what each run wrote, never the transcript,
  and a mechanical check refuses to grade evidence that identifies the
  configuration.

## Why the previous attempt does not carry over

`iteration-7` was abandoned: it was cut off mid-sweep and the plugin changed
the next morning, so completing it would have put two skill versions in one
arm. Nothing from it is reused here — this sweep starts from zero.

## Status

Collection in progress. This note will be replaced with the finished state,
including any runs excluded and why, before any figure here is read.
