# Record quality, full corpus

Status: Current
Checked: 2026-08-05

Every change record in `docs/engineering/changes/` graded against the layer-2
dimensions in [record-quality-rubric.md](record-quality-rubric.md). Two blind
judges per record, `claude-opus-5`, 27 records, 54 passes, 216 cells. Judges saw
five extracted sections and nothing else: no filename, no date, no risk tier, no
commit message.

This measures the writing in this repository's records. It is not a measurement
of the plugin, and no number here is exported to the README or to release notes.

## Per record

`pass` and `fail` mean both judges agreed. `split` means they disagreed.
Ordered by cells passed, worst first. Cell counts are a within-row summary, not
a score to compare across dimensions -- the dimensions are not equally hard.

| Record | D1 | D2 | D3 | D4 | Cells |
| --- | --- | --- | --- | --- | --- |
| `documentation-first-workflow` | fail | fail | fail | fail | 0/8 |
| `v0-1-0-public-release` | fail | fail | fail | fail | 0/8 |
| `v0-2-immediate-workflow` | fail | fail | fail | fail | 0/8 |
| `complete-the-fixture-set` | fail | fail | fail | pass | 2/8 |
| `correct-git-attribution` | pass | fail | fail | fail | 2/8 |
| `fix-benchmark-postpass` | fail | pass | fail | fail | 2/8 |
| `rename-pending-release-030` | split | pass | fail | fail | 3/8 |
| `add-record-index` | fail | pass | fail | pass | 4/8 |
| `arm-release-currency-gate` | fail | pass | fail | pass | 4/8 |
| `define-record-quality-rubric` | fail | pass | fail | pass | 4/8 |
| `exclude-illustrative-references` | fail | pass | fail | pass | 4/8 |
| `separate-fixture-from-answer-key` | fail | pass | fail | pass | 4/8 |
| `declare-english-canonical` | fail | pass | split | pass | 5/8 |
| `add-terminal-close-state` | pass | pass | fail | pass | 6/8 |
| `cover-ship-critical-paths` | pass | pass | fail | pass | 6/8 |
| `describe-when-to-invoke` | pass | pass | fail | pass | 6/8 |
| `fix-blinding-redaction` | pass | pass | fail | pass | 6/8 |
| `guard-record-conventions` | pass | pass | fail | pass | 6/8 |
| `remove-competency-tags` | pass | pass | fail | pass | 6/8 |
| `revise-rubric-after-dry-run` | pass | pass | fail | pass | 6/8 |
| `rewrite-evaluation-expectations` | pass | pass | fail | pass | 6/8 |
| `scope-currency-gate-to-tag-time` | pass | pass | fail | pass | 6/8 |
| `tighten-rubric-with-control` | pass | pass | fail | pass | 6/8 |
| `validate-revised-rubric` | pass | pass | fail | pass | 6/8 |
| `withdraw-unsupported-evaluation-claim` | pass | pass | fail | pass | 6/8 |
| `defensible-skill-evaluation` | pass | pass | split | pass | 7/8 |
| `observable-run-evidence` | pass | pass | pass | pass | 8/8 |

`grade-the-record-corpus` is absent because it was still an unfilled template
when the run started. The grader skips records carrying the template marker
rather than scoring a skeleton.

## Per dimension

| | Cells passed | Records both-pass | Records both-fail | Split |
| --- | --- | --- | --- | --- |
| D1 Calibration | 31/54 | 15 | 11 | 1 |
| D2 Stated verification | 44/54 | 22 | 5 | 0 |
| D3 Load-bearing jargon | 4/54 | 1 | 24 | 2 |
| D4 Bounded takeaway | 42/54 | 21 | 6 | 0 |

Judges agreed on 105 of 108 record-dimension pairs (97%). All three
disagreements are on records that pass their neighbours' dimensions, so no
disagreement changes which records sit at the bottom.

## The three lowest

All three failed every cell. What each is missing, from the judges' quoted
evidence:

- **`documentation-first-workflow`** -- no check with a result anywhere in the
  five sections. A judge searched and reported the nearest candidates were
  ownership statements, not checks. Its central claim rests on `teach-back`,
  a term the record never defines.
- **`v0-1-0-public-release`** -- its only verification sentence is "Controls
  are documented in the repository threat model and exercised by tests," which
  is the pointer-at-another-document form D2 explicitly names as no check. Its
  success criteria are all properties the release was built to have.
- **`v0-2-immediate-workflow`** -- same pattern. Of its three takeaway
  candidates, one is a general property of plugin hosts and two are scope
  disclaimers; none carries an observation this change produced.

The common shape is a record covering a whole release rather than a change. All
three describe intent and architecture; none reports an outcome.

Two of the three -- `documentation-first-workflow` and `v0-1-0-public-release`
-- have no `Verification evidence` section at all. They were authored against an
older template that asked for a `Verification plan` instead, so their D2 failure
is a fact about what they contain and not an artifact of what was extracted.
That distinction matters because of the next section.

## The prediction the tightening carried

The three tightenings applied after the negative-control run were **predicted,
not measured**. Each judge named which records their edit would newly fail. The
stated prediction was that `v0-1-0-public-release`, previously failing D2 and
D3, would after tightening also fail D1 and D4.

It failed all four, both judges, zero cells. The prediction was met exactly.

## D3 is a near-constant, and it inverts against the control

D3 fails 24 of 27 records outright and passes one. By the rubric's own rule
against dimensions that never separate, that is a deletion candidate.

It should not be deleted yet, because of what the negative control did. The
control in `fixtures/negative-control-record.md` was written to game D1, D2 and
D4 and deliberately **not** to game D3 -- every identifier glossed where it
appears. It passed D3 while 24 real records fail it. A record documenting no
real work is more legible on its own vocabulary than almost the entire corpus.

Two readings, and this run cannot separate them:

1. The corpus genuinely writes for insiders. Counting the records in which a
   term appears in at least one judge's D3 failure evidence, the most-flagged
   are the risk tiers (10 of 27, `R2` alone in 7), "contract" in any form (8),
   "the skill" or "this skill" (6), and "ADR" in any form (5). Further down:
   "the audit" and "layer 2" (3 each), "layer-1", "threat model" and `R0` alone
   (2 each).

   The risk tiers are the sharpest case, because the shipped skill does not
   define them either. `operating-model.md` gives a table of what each tier
   *requires before completion*; `start.md` says only "classify the highest
   applicable risk". Neither states what places a change at R2 rather than R1.
   A judge asked to resolve `R2` from the record cannot, and a reader who leaves
   the record to look it up cannot either.
2. D3's bar is placed where only a short record can clear it, so it rewards
   thinness. The one record that passes, `observable-run-evidence`, is not the
   longest.

What would separate them: grade a record written deliberately for an outsider,
at normal length. If it passes D3, reading 1 holds and the corpus has a real
defect. If it fails, D3 is measuring length.

## What the judges said about the dimensions

All 54 passes used the critique channel. Counting which dimension each critique
opens on: D2 37, D1 11, D3 5, D4 1.

The convergence on D2 is the finding. D2 passes 22 of 27 records, the highest of
any dimension, and the judges say that number is soft. Their objection, in one
judge's words, is that D2 "is satisfied by any single check-with-outcome
anywhere in the graded sections, so a record can punt on the verification that
matters most and still pass on an incidental aside."

**The judges diagnosed a symptom whose cause was hidden from them.** The five
graded sections do not include `Verification evidence`. That section is excluded
because the template's instructions for it changed, and scoring a section that
moved would measure the template. The consequence was not thought through: D2
asks what the record says was checked and what the check produced, and the
section that answers that question is the one section withheld from the judge.
25 of the 27 records have it.

The demonstration is `add-record-index`. Both judges reported that its
verification defers entirely, quoting "See the linked threat model and runbook",
and passed it only on a count appearing elsewhere. Its actual
`Verification evidence` section reports four checks with outcomes -- a test
count before and after, a guard proved by breaking it, a link count, and the
contract commands. The judges never saw it. What they read as deferral is a
different section doing a different job.

So D2's 44 of 54 does not measure whether these records report their
verification. It measures whether a check with an outcome happens to surface
outside the section meant to carry it. The number should not be quoted as a
verification-reporting rate, and this document does not do so anywhere else.

The next step is therefore not a wording change. It is a decision about
extraction: grade `Verification evidence` and treat its absence as a D2 failure.
The reason it was excluded does not survive contact with the corpus -- the two
records authored against the older template do not have the section under any
name that would be extracted, so including it costs those two nothing and
returns the answer for the other 25.

## Limits

- **D2 was measured on text that excludes the answer.** The section extraction
  withholds `Verification evidence`, which 25 of the 27 records have. The D2
  column above is therefore a measurement of incidental mentions, not of
  verification reporting, and it should not be carried forward once extraction
  is fixed. D1, D3 and D4 do not depend on that section and are unaffected.
- The claims in this document were checked against the judge output by
  independent readers before it was committed. Nine statements were corrected as
  a result, four of them factually wrong -- including the previous version of
  the D2 conclusion above, which repeated the judges' diagnosis without noticing
  what had been withheld from them.
- Both judges are the same model family. 97% agreement measures how
  unambiguously the dimensions are written less well than cross-family
  agreement would.
- Records were graded at `HEAD`, not as first authored. Nine records have been
  edited after their first commit, so for those the grade describes the current
  text and not the writing at the time of the work.
- The rubric's author graded the rubric's corpus. Every record here was written
  in the same repository by the same process the rubric was designed around.
- One split on D1 and two on D3 are reported as splits rather than resolved. No
  tie-break rule exists, and inventing one after seeing the results would be
  choosing the answer.
- 216 cells is one run. Nothing here is a rate that would survive being quoted
  without this document attached.

## References

- [record-quality-rubric.md](record-quality-rubric.md) -- the standard and its
  three dry runs
- `scripts/grade_records.py` -- the run
- `engineering-ownership-workspace/record-quality/` -- per-record judge output
  with quoted evidence, committed so every cell in the table above can be
  checked against what the judge actually wrote
