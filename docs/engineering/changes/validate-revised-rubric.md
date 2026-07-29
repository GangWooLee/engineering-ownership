# 2026-07-29 · Validate the revised rubric on identical inputs

Change ID: `validate-revised-rubric`
Created: `2026-07-29T19:43:37+09:00`
Risk: R1

## Problem and intended outcome

The rubric's layer 2 failed its first dry run and was rewritten. The rewrite was
untested, and the rubric's own rule forbids automating a standard that has not
been tried. Grading twenty-two records against an unvalidated rubric would spend
judge calls on an instrument that might measure nothing, which is the mistake
this whole exercise exists to avoid.

Intended outcome: a decision on whether the revised dimensions may be used for a
full pass, with the criteria fixed before the result was visible.

## Success and non-goals

Success criteria, fixed before the run: no dimension may be all-pass or
all-fail; inter-rater agreement should hold near the first run's 22/24; D3 must
be satisfiable by at least one record, having been unsatisfiable by construction.

Non-goals: grading the full corpus; changing any record; adjusting the
dimensions again in response to this run — a rubric edited after every
observation is not a standard.

## Existing responsibilities searched

The same procedure as the first run, deliberately: same six records, same
extraction of the five sections whose template instructions never changed, same
output contract. Nothing new was built.

## System and data flow

Extracts regenerated from HEAD and compared by SHA-256 against the first run's:
**6 of 6 byte-identical**. Four of the six records had their headers edited in
the interim by the layer-1 fixes, and the extracts contain only body sections,
so the inputs were provably unchanged. Any difference in results is therefore
attributable to the rubric and not to the corpus.

Two fresh judges, each blind to the other and to the records' identity, dates,
and titles.

## Decisions and trade-offs

The dimensions were **not** adjusted after this run. Two judges proposed
specific tightenings — requiring an outcome that could have been otherwise,
distinguishing evidential scope from feature scope — and both are recorded in
the rubric as known leniencies rather than applied. A standard rewritten after
every observation converges on the last sample rather than on the thing it
measures. The tightenings are candidates for the next round, tested against a
negative control.

## Failure, security, and recovery

The failure this guards against is automating a rubric that separates nothing.
It is caught by the mandatory all-pass/all-fail check, which caught the first
version and cleared this one. No security surface: documentation only.

## Verification evidence

| | First run | Second run |
| --- | --- | --- |
| Inter-rater agreement | 22 / 24 (92%) | **24 / 24 (100%)** |
| Constant dimensions | 1 (D3 at 0/12) | **none** |
| Pass counts D1 / D2 / D3 / D4 | 11 / 2 / 0 / 11 | 10 / 10 / 8 / 10 |

All three pre-registered criteria met.

The honest qualification, reached independently by both judges: **the instrument
resolves two bands, not six.** One record fails all four dimensions, one other
fails only D3, and the remaining four pass everything. One judge wrote that the
run "mostly measured one outlier and told me little about the other five."

## Known limits and learning gaps

- **Two bands is not six.** Whether that means the rubric is lenient or the
  corpus is uniform cannot be settled by six real records. The next validation
  needs a **negative control** — a record written deliberately to fail — because
  both judges could only answer "what would a clearly bad document also pass?"
  speculatively, never having been shown one.
- D1 currently detects the presence of a non-goals section. Both judges failed
  the outlier by distinguishing features-not-built from limits-on-the-evidence,
  and one stated plainly that the distinction was theirs and not the rubric's.
- D2 cannot separate a reported outcome from a definition of done: "the full
  suite passes" in a success clause has the same form either way.
- D4 collapses toward "did you give a reason".
- A judge noted a correlation the rubric does not guard: D2 and D4 reward
  records that include a findings section, and short records omit those more
  often. Verdicts here were checked against length and did not track it, but the
  mechanism is unguarded.
- 100% agreement between two judges of the same model family measures rubric
  clarity less well than agreement across families would.

## References

- `docs/validation/record-quality-rubric.md` — both runs and what each changed
- `docs/engineering/changes/revise-rubric-after-dry-run.md` — the revision this
  validates
