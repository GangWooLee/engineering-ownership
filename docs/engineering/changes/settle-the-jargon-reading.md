# 2026-08-05 · Settle which of D3's two readings the corpus supports

Change ID: `settle-the-jargon-reading`
Created: `2026-08-05T22:51:35+09:00`
Risk: R1

## Problem and intended outcome

Two full-corpus runs left D3 -- the dimension asking which undefined terms a
record's argument rests on -- failing 23 of 29 records, and left two readings of
that number standing. Either the corpus is written for readers who already know
this project, or the dimension's bar is somewhere a record cannot reach for
reasons unrelated to how legible it is. A third possibility appeared in the
rerun: D3's cell count barely moved while five records changed verdict and the
identity of its one passing record swapped, which is what a dimension too noisy
to measure anything looks like.

The published document named the experiment that separates them and did not run
it. Intended outcome: run it, twice, and write down which reading survives --
including if it is the one that makes the dimension look bad.

## Success and non-goals

Success is a verdict that is not a coin flip: the same fixture graded in two
independent runs, agreeing with itself, with the other three dimensions holding
where the original sat so any movement is attributable. It could plainly have
gone the other way -- a fixture that failed D3, or that passed once and failed
once, would have been a finding about the dimension rather than about the
corpus, and either was a live outcome when the runs started.

Non-goals: changing D3's wording; re-grading the corpus; producing a second
fixture to control length, which is named as the remaining gap rather than done.

## Existing responsibilities searched

`docs/validation/fixtures/` already holds a negative control -- a record written
to fail the rubric on purpose -- so the directory, its exclusion from every
record guard and index, and the practice of grading a fixture blind among the
corpus all exist. This adds a second fixture to that directory rather than a new
mechanism.

`scripts/grade_records.py` already had `--only`. It could not grade a file
outside the record directory, which is why the negative control was graded by an
ad-hoc script that was never kept. `--path` closes that, so the next fixture
does not need a throwaway runner either.

## System and data flow

The fixture is a **matched rewrite**, not a new record. Writing a fresh
outsider-facing record would have changed subject, structure and vocabulary at
once, and a D3 pass would not say which of those did it.

`add-record-index` was chosen because it fails D3 outright in both runs and all
four judges failed it on the same terms: the risk tiers R1 and R2, on which its
central argument rests -- "an ADR written under an R1 record has nowhere to live
in that record's artifact map, because `artifact_paths` allocates a decision
document only from R2 up" -- and `artifact_paths` itself.

The rewrite keeps the same facts, decisions, counts and verification, and
changes only the glossing: what the tiers are, what each allocates, what
`artifact_paths` does, what `.engineering/contract.json` is. It was deliberately
not shortened, because a prior run found the rubric over-penalizes legible
thinness and a thin pass would have proved nothing.

`grade_records.py` gains `--path`, which grades a named file wherever it lives,
and `--only` now filters the combined candidate set so a fixture can be graded
alone.

## Decisions and trade-offs

Two runs rather than one, because the rerun had already shown four D1 verdicts
moving on byte-identical input. A single pass would have been indistinguishable
from a re-roll, which is the specific failure this experiment existed to avoid.

The first draft came out at 1.85x the original's graded length, near the corpus
maximum, which would have let any reader attribute a D3 pass to length. It was
tightened to 1.62x -- inside the corpus range -- by compressing wording rather
than removing content, so the comparison stays about glossing. Length is still
not controlled, and that is recorded rather than argued away.

## Failure, security, and recovery

The failure mode a fixture introduces is being mistaken for a record of real
work. Three things prevent it, the same three that protect the negative control:
it lives outside every directory the record guards and indexes walk, its own
first paragraph states it documents no new work, and that paragraph sits above
the first `##` heading, so the extraction that feeds the judge never sees it --
verified by extracting the file and searching the result for the disclaimer.

Recovery is deleting the file; nothing depends on it.

## Verification evidence

Prediction fixed before the runs: if the corpus-writes-for-insiders reading is
right, the rewrite passes D3 in both runs while D1, D2 and D4 stay where the
original sat.

| Check | Result |
| --- | --- |
| D3, run A | pass, both judges |
| D3, run B | pass, both judges |
| D3, original, both corpus runs | fail, all four judges |
| D2 and D4 | pass in all four rewrite passes, as in the original |
| D1 | one pass, three fail; the original failed D1 in both runs |
| Judges' stated reason | "the argument turns on the tier system, which is defined in place"; "both are defined in place" -- the glossing, unprompted |
| Extraction | Six sections, 5,226 characters; disclaimer absent from the extract |
| Length against the corpus | Fixture 5,226 characters. Across the 32 change records at this commit: range 1,718-7,987, median 3,235. The rewritten record is 3,218 |
| Suite | 98 tests |

The prediction held. D3's bar is clearable, at a length inside the corpus range,
by the same content once its vocabulary is resolved.

## Known limits and learning gaps

- **Length is not controlled.** 1.62x the original is inside the corpus range
  and above its median. A glossed rewrite at or below the original's length
  would separate glossing from volume, and has not been written.
- One record, one subject. `add-record-index` argues from the risk tiers; a
  record whose load-bearing terms are of a different kind might behave
  differently.
- The fixture was written by the author of the rubric, knowing all four
  dimensions. That is the same conflict already disclosed for the two 8/8
  records, and it is why the result is reported as "the bar is clearable" rather
  than "the corpus could easily clear it".
- D1 failed three of four passes here, as it did in the original. Nothing was
  done about it and nothing here explains it.
- The result says the corpus writes for insiders. It does not say that is worth
  fixing across 23 records, and no such work is proposed.

## References

- `docs/validation/record-quality-2026-08-rerun.md` -- where the experiment was
  named and where its result is now recorded
- `docs/validation/fixtures/outsider-rewrite-record.md`
- `docs/engineering/changes/add-record-index.md` -- the record rewritten
- `scripts/grade_records.py`
