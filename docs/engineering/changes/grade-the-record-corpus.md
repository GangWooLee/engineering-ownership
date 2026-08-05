# 2026-08-05 · Grade the whole record corpus against the tightened rubric

Change ID: `grade-the-record-corpus`
Created: `2026-08-05T17:05:30+09:00`
Risk: R1

## Problem and intended outcome

The record-quality rubric -- the document in `docs/validation/` that states how
a change record in this repository is judged -- reached its current wording
through three trial runs on six records. The last of those runs ended by
tightening three of its four dimensions, and each tightening was applied on a
**prediction**: the judge who proposed the wording named which records it would
newly fail, and that naming was accepted as sufficient reason to apply the edit
without a further round.

So three of four dimensions ship with predicted verdicts and no measured ones,
and no dimension has been run against more than six of the twenty-seven records.

Intended outcome: every change record graded under the shipped wording, the
predictions checked against what actually happened, and the result written down
whether or not it flatters the rubric.

## Success and non-goals

Success is not "the records score well." It is that the run can distinguish a
rubric that measures writing from one that measures nothing: the named
prediction either holds or it does not, and at least one dimension's behaviour
across twenty-seven records is different from its behaviour across six. Both
could have resolved the other way -- a rubric whose dimensions all pass at a
uniform rate would have been the failure case, and the same instrument produced
that outcome in its first trial run.

Non-goals: changing the dimensions inside this change; grading the other record
types (decision, runbook, threat model); producing any number that leaves this
repository.

The rubric document itself *is* edited here, in two places: a denominator that
was written as 56 with no commit pinned, and a retro-edit count that was 6 when
written and is 9 now. Both are corrections of measurements the document reported
about itself, carrying the header marker the convention requires. Neither
touches a dimension, so no record's grade depends on them.

## Existing responsibilities searched

The evaluation harness in `scripts/` already owns blinded judging: a judge that
receives extracted text with author, date and filename stripped. Its output
contract was reused verbatim -- quoted evidence required, no partial credit, a
critique channel where the judge attacks the criteria rather than the subject,
and an arity check that rejects a pass returning the wrong number of verdicts.

Three of its parts were deliberately **not** reused, each because it encodes an
assumption that is false here. Its leak detector is a substring test for four
fixed strings, one of which is this repository's own name, so it would mark
every record as leaked. Its evidence-section reader assumes a section shape this
corpus does not have. Its prompt instructs the judge to read files that a judge
running without tools cannot open.

`tests/test_evals.py` already owns the guard that stops a grader from
hard-coding what it should read at run time. It was widened rather than
duplicated.

## System and data flow

`scripts/grade_records.py` reads the rubric's layer-2 section -- the four
dimensions and their expectations -- out of the document at run time and hands
it to the judge whole. The criteria are not parsed. The document holds five
other tables, one of which still lists dimension names that were measured and
rejected, so a parser keyed on a table or on row labels can select the
superseded set and grade against it without any error appearing.

One parse remains: the dimension identifiers are read out of the layer-2 table
so a judge returning the wrong number of verdicts is rejected. It runs on the
already-extracted section, which is what keeps it away from the superseded
table, and it is the same regex shape as the hazard it sits next to.

For each record it extracts the five sections whose template instructions have
never changed, so the grade describes the writing rather than a template
revision, and sends that extract to two independent judges. A record still
carrying the template's unfilled marker is skipped, not scored.

Output is one JSON file per record holding both judges' verdicts and their
quoted evidence. The script performs no aggregation: the rubric forbids a
headline mean, and a script that computes one invites its use.

## Decisions and trade-offs

Records were graded at `HEAD` rather than as first authored. The alternative --
extracting each record at the commit that added it -- was tried and abandoned
when it returned a 252-character template skeleton for a real record: the
workflow creates the record before the work, so the add commit predates the
writing. The cost is that nine records that were edited after their first commit
are graded on their current text.

The results document is a validation record rather than a section in the rubric.
The rubric states how records are measured; a score written into it would make
the standard and its results move together, and the standard is supposed to
outlive any one run.

## Failure, security, and recovery

The failure mode that occurred was operational, not analytical. The run was
launched twice: a first launch was wrongly diagnosed as dead, because the
process match used to check for it returned unrelated matches and the absence of
the expected line was read as absence of the process. Its log file had also been
truncated by the second launch's `tee`, which was read as further confirmation.
Both processes then ran for roughly fifty minutes, interleaving into one log
file, which produced a fragment that read as a grading failure for a record that
had in fact been graded correctly.

No result was corrupted: each output file is written whole by one process, so
every file is one process's complete verdict. What was lost is judge calls.

Recovery was killing the duplicate and reading the output files rather than the
log. The general form: when a run writes both a log and artifacts, the artifacts
are the evidence and the log is a narrative.

## Verification evidence

Run: 27 records, 2 judges each, 54 passes, 216 cells, model `claude-opus-5`,
zero grading refusals. The 28th record is this one, skipped by design because it
was an unfilled template when the run started.

| Check | Result |
| --- | --- |
| Prediction under test: `v0-1-0-public-release` fails all four dimensions | Held. 0 of 8 cells, both judges |
| Judge agreement across record-dimension pairs | 105 / 108 (97%) |
| Dimension behaviour differs from the six-record trial | Yes. D3 passes 4 of 54 cells, against 24 records failing outright |
| Critique channel used | 54 of 54 passes; 37 open on the same dimension, D2 |
| Test suite after the guard widening | 92 tests, all passing |
| Guard widening proved by breaking it | A forbidden literal added to the new script failed `test_no_grader_matches_on_the_skill_private_vocabulary`, then was removed |

Two findings the run was not designed to produce. The deliberately bad record in
`docs/validation/fixtures/` passes the jargon dimension that 24 real records
fail: a document written to game the rubric, describing no real work, is more
legible on its own vocabulary than nearly the whole corpus. And D2 was measured
without the section that answers it -- see the limits below.

The claims in both documents were then checked against the judge output by six
independent readers, each given one claim cluster and instructed to refute. 23
objections were raised and 9 survived a second reader trying to refute them in
turn. All 9 were applied. Four were factually wrong, not merely loose: a
statement that this change does not edit the rubric when it does, a statement
that the rubric is never parsed when the dimension identifiers are, a table
count off by one, and a description of the eval harness's leak detector that
did not match its four-string implementation. The D2 finding above came out of
that pass; the first version of the results document repeated the judges'
diagnosis without noticing what had been withheld from them.

Full per-record results: `docs/validation/record-quality-2026-08.md`.

## Known limits and learning gaps

- **The D3 result has two readings this run cannot separate.** Either the corpus
  writes for insiders, or the dimension's bar is placed where only a short
  record clears it. The test that would separate them is grading a record
  written deliberately for an outsider at normal length; until that runs, D3
  should not be deleted and should not be trusted as a defect count.
- **D2's result is not usable, and the cause is in this change's own code.**
  The five graded sections exclude `Verification evidence`, which 25 of the 27
  records have. D2 asks what was checked and what the check produced, and the
  section holding that answer is the one withheld. Both judges reported
  `add-record-index` as deferring its verification; its actual
  `Verification evidence` section reports four checks with outcomes. The
  exclusion was inherited from the rubric without asking what it does to a
  dimension about verification. Fixing it is an extraction change -- grade that
  section, treat its absence as a D2 failure -- and the two records authored
  against the older template do not have the section under any extractable name,
  so nothing is lost by including it.
- Both judges are the same model family, so 97% agreement measures how
  unambiguously the dimensions are written less well than cross-family agreement
  would.
- The rubric's author graded the rubric's own corpus.
- Three verdicts are reported as splits with no tie-break. Inventing one after
  seeing the results would be choosing the answer.

## References

- `docs/validation/record-quality-2026-08.md` -- the results
- `docs/validation/record-quality-rubric.md` -- the standard and its three
  trial runs
- `scripts/grade_records.py`
- `docs/engineering/changes/tighten-rubric-with-control.md` -- where the
  predictions tested here were made
