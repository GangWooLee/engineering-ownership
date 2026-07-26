# Efficacy measurement — ABANDONED 2026-07-26

This iteration is dead as a measurement. Do not read any figure from it, and do
not resume the sweep with `--resume`: finishing it would produce a worse
artifact than leaving it incomplete.

## Why it was abandoned

Two independent reasons, either of which is sufficient.

**The skill changed mid-sweep.** Every run recorded here was produced on
2026-07-25 (21:46 KST onward). On 2026-07-26 the plugin changed materially:
the terminal close state (`2ec5d1d`), the removal of the competency tag
subsystem including the deletion of `references/competencies.md` (`a5cd820`),
and the version stamp (`3c17f43`). The runner passes `--plugin-dir` pointing
at the working tree, so any run added now would exercise a different skill
from the runs already here. One arm containing two skill versions is a
confound between conditions — the same class of defect the withdrawn
evaluation was retracted over.

**The sweep was cut off, not merely paused.** It was terminated during eval-8
while a stale process was still writing. Present: 14 of 27 `with_skill` runs
and 22 of 27 `without_skill` runs; eval-9 never ran at all. Eight `with_skill`
runs were separately quarantined because their action logs named the runner's
directory, which identifies the configuration to the judge — the defect fixed
in `fix-blinding-redaction`. Those eight were moved to a temporary directory
outside the repository; they are not needed for a rebuilt iteration and are
not preserved.

## What survives

The `without_skill` runs are unaffected by the plugin change — the baseline
runs with all plugins disabled and never loads the skill. They are kept here
as reference data only; they are not a result on their own, since a baseline
without its treatment measures nothing.

## What replaces it

A fresh iteration collected against a settled plugin, after
`withdraw-unsupported-evaluation-claim` (PR #1) merges. Measuring a plugin
whose pull request is still open spends money on a number that review can
invalidate.

This note is committed; the run data under it is not. The runs are kept on
local disk only, as the record of what was collected and why it was discarded,
never as an input to any claim.
