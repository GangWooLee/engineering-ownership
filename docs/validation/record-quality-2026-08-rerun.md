# Record quality, full corpus, verification section included

Status: Current
Checked: 2026-08-05

Every change record graded against the layer-2 dimensions in
[record-quality-rubric.md](record-quality-rubric.md), after the extraction
defect found in the first run was fixed. Two blind judges per record,
`claude-opus-5`, 29 records, 58 passes, 232 cells, zero grading refusals.

The first run is [record-quality-2026-08.md](record-quality-2026-08.md). It
graded 27 records without the `Verification evidence` section, which is the
section D2 asks about. This run includes it. The two runs therefore measure
different inputs, and the comparison below is read as *what changed when the
judge could see more*, not as improvement.

Nothing here is exported to the README or to release notes.

## Per record

`pass` and `fail` mean both judges agreed; `split` means they did not. Ordered
by cells passed, worst first. Cell counts summarise a row and are not
comparable across dimensions, which are not equally hard.

Records marked `*` were written by the author of the rubric during the work
that produced these runs. See *The two perfect scores are not results* below.

| Record | D1 | D2 | D3 | D4 | Cells |
| --- | --- | --- | --- | --- | --- |
| `documentation-first-workflow` | fail | fail | fail | fail | 0/8 |
| `v0-1-0-public-release` | fail | fail | fail | fail | 0/8 |
| `v0-2-immediate-workflow` | split | fail | fail | fail | 1/8 |
| `add-record-index` | fail | pass | fail | pass | 4/8 |
| `complete-the-fixture-set` | fail | pass | fail | pass | 4/8 |
| `declare-english-canonical` | fail | pass | fail | pass | 4/8 |
| `define-record-quality-rubric` | fail | pass | fail | pass | 4/8 |
| `exclude-illustrative-references` | fail | pass | fail | pass | 4/8 |
| `rename-pending-release-030` | fail | pass | fail | pass | 4/8 |
| `rewrite-evaluation-expectations` | fail | pass | fail | pass | 4/8 |
| `separate-fixture-from-answer-key` | fail | pass | fail | pass | 4/8 |
| `arm-release-currency-gate` | split | pass | fail | pass | 5/8 |
| `correct-git-attribution` | pass | pass | split | fail | 5/8 |
| `fix-benchmark-postpass` | fail | pass | pass | split | 5/8 |
| `remove-competency-tags` | pass | pass | fail | split | 5/8 |
| `add-terminal-close-state` | pass | pass | fail | pass | 6/8 |
| `cover-ship-critical-paths` | pass | pass | fail | pass | 6/8 |
| `fix-blinding-redaction` | pass | pass | fail | pass | 6/8 |
| `guard-record-conventions` | pass | pass | fail | pass | 6/8 |
| `observable-run-evidence` | pass | pass | fail | pass | 6/8 |
| `revise-rubric-after-dry-run` | pass | pass | fail | pass | 6/8 |
| `scope-currency-gate-to-tag-time` | pass | pass | fail | pass | 6/8 |
| `tighten-rubric-with-control` | pass | pass | fail | pass | 6/8 |
| `validate-revised-rubric` | pass | pass | fail | pass | 6/8 |
| `withdraw-unsupported-evaluation-claim` | pass | pass | fail | pass | 6/8 |
| `defensible-skill-evaluation` | pass | pass | split | pass | 7/8 |
| `describe-when-to-invoke` | pass | pass | split | pass | 7/8 |
| `grade-the-record-corpus` * | pass | pass | pass | pass | 8/8 |
| `grade-verification-sections` * | pass | pass | pass | pass | 8/8 |

## Per dimension

| | Cells passed | Records both-pass | Records both-fail | Split |
| --- | --- | --- | --- | --- |
| D1 Calibration | 34/58 | 16 | 11 | 2 |
| D2 Stated verification | 52/58 | 26 | 3 | 0 |
| D3 Load-bearing jargon | 9/58 | 3 | 23 | 3 |
| D4 Bounded takeaway | 48/58 | 23 | 4 | 2 |

Judges agreed on 109 of 116 record-dimension pairs (94%), down from 97% in the
first run.

## What the fix bought, on the 27 records both runs graded

| | Run 1 cells | Run 2 cells | Records whose verdict moved |
| --- | --- | --- | --- |
| D1 | 31/54 | 30/54 | 4 |
| D2 | 44/54 | 48/54 | 2 |
| D3 | 4/54 | 5/54 | 5 |
| D4 | 42/54 | 44/54 | 3 |

D2 is the only dimension whose movement is directional and explicable. Two
records went from both-fail to both-pass -- `complete-the-fixture-set` and
`correct-git-attribution` -- and both have a `Verification evidence` section
that the first run withheld. `add-record-index`, the record the defect was
diagnosed on, passed D2 in both runs, but on entirely different text: in run 1
both judges quoted an audit count from the data-flow section, the only
check-with-outcome they could see; in run 2 both quote the section that reports
checks. The verdict was right for the wrong reason and is now right.

## The instrument moves when its input does not

D1 tells the judge to read **only the opening section**. The extraction change
added a section further down and touched nothing before it, so D1's designated
input is byte-identical across the two runs. Four of 27 D1 verdicts moved
anyway, in both directions: two records lost a pass, one lost a split, one
gained a split.

That is a measurement of run-to-run instability with the input held fixed, and
it sets a floor. A difference of fewer than roughly four records in a
27-record column is not distinguishable from the instrument re-rolling.

D3 shows the same thing more starkly. Its cell count barely moved, 4/54 to
5/54, but five records changed verdict and **the identity of the single
D3-passing record changed completely**: `observable-run-evidence`, the one
record that passed all four dimensions in run 1, lost D3; `fix-benchmark-postpass`
gained it. A dimension whose one success swaps records between runs is not
measuring a property of records yet.

## The two perfect scores are not results

The only 8/8 records in this corpus are `grade-the-record-corpus` and
`grade-verification-sections` -- the two records written for the work that
built and fixed this grader, by the author of the rubric, with all four
dimensions in view while writing.

Both scored 8/8 from both judges. No record written without that knowledge did.

Read this as a conflict of interest, not an achievement. It is the negative
control's question asked from the other side: the control showed a record built
to *fail* the dimensions can be constructed, and these show a record built to
*pass* them can be too. Neither says anything about whether the dimensions
track quality for an author who is not thinking about them.

The honest use of these two rows is as an upper bound on gameability. They
should be excluded from any future summary of the corpus, and this document
excludes them from every comparison in the section above.

## D3 remains near-constant

23 of 29 records fail D3 outright and three pass, two of those being the
author's own. Among the 27 independent records, exactly one passes -- and it is
a different record than the one that passed in run 1.

The two readings named in the first run still stand and this run does not
separate them: either the corpus writes for insiders, or D3's bar sits where
only certain records clear it for reasons unrelated to legibility. The
instability above adds a third possibility that must now be ruled out first --
that D3 is too noisy to be measuring anything. The experiment named in the
first run, grading a record written deliberately for an outsider at normal
length, should be run **twice** so its result can be told apart from a re-roll.

## Limits

- **One rerun is not a reliability study.** Four D1 moves on fixed input give a
  rough floor, not a variance estimate. Two graders and two runs cannot
  separate judge disagreement from run-to-run drift.
- Both judges are the same model family in both runs.
- The rubric's author graded the rubric's corpus, and wrote two of its records.
- Seven verdicts are reported as splits with no tie-break. No rule exists, and
  inventing one after seeing results would be choosing the answer.
- 232 cells is one run. No number here survives being quoted without this
  document attached.

## References

- [record-quality-rubric.md](record-quality-rubric.md) -- the standard, its
  three trial runs, and the corrected *What is graded*
- [record-quality-2026-08.md](record-quality-2026-08.md) -- the first run, kept
  as the record of what was measured before the fix
- `scripts/grade_records.py`
- `engineering-ownership-workspace/record-quality-2/` -- per-record judge output
  with quoted evidence, committed so every cell above can be checked
- `engineering-ownership-workspace/record-quality-verify/` -- the three-record
  probe taken before the full rerun
