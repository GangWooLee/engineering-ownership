# 2026-08-05 · Close the arm-name leak the redaction pass and its guard both missed

Change ID: `close-arm-name-leak`
Created: `2026-08-05T22:03:46+09:00`
Risk: R2

## Problem and intended outcome

A pre-push review of 22 unpushed commits found that two graded runs in the
iteration-8 sweep reached their judge with `eval-7-without_skill-1` and
`eval-5-without-skill-1` sitting in the judge-visible action log. The judge was
shown which arm it was grading.

The sweep's own note published the opposite: "Blinding held — all 54 action logs
pass the leak check." Every clause of that sentence was true. The conclusion was
false, because the check could not see the thing it was being cited for.

Three failures had to line up, and did:

1. `run_skill_evals.py` names each fixture directory
   `{overlay}-{configuration}-{index}`, so the directory itself states the arm.
2. `action_target.relative` normalizes a token that *starts* with `/`, `~`, or
   `$`. A token of the form `D=/abs/path` starts with a letter, so it was
   returned whole, absolute path and all.
3. `BLINDING_TELLS` lists four strings and none of them is an arm name, so
   `blinding_leaks` returned `[]` for a log that says `without_skill` in plain
   text.

Intended outcome: a run cannot record the leaking form, the predicate can see
the class, and the six already-published instances are disclosed rather than
quietly cleaned.

## Success and non-goals

Success is that the three token shapes that leaked are normalized, that the
guard fails on any unpinned leak *and* on a pin that no longer leaks, and that
every place reporting the affected figures states the defect and its size. The
guard direction could have gone the other way: an exception list is the standard
way to turn a red suite green permanently, and a pin that is never re-checked is
exactly that.

Non-goals: re-collecting the sweep; changing any published figure; renaming the
fixture directories, which is the deepest cause and cannot be verified without a
live run.

## Existing responsibilities searched

`fix-blinding-redaction` already owns this exact surface -- it closed the
quoting evasions where `cat "~/…"` reached the judge. The normalization added
here extends that function rather than adding a second pass, and the arm names
join the tell list that change established rather than getting their own
predicate.

That record claims two independent nets: the grader's refusal at
`grade_skill_evals.py` and `JudgeBlindingCase`. Both call `blinding_leaks`. They
are one net wearing two hats, which is why a single gap in the predicate let six
logs through both. The claim is corrected in that record.

## System and data flow

`action_target.relative` gains a fallback: a token that is neither a
fixture-relative path nor an absolute one is scanned for a path *embedded* after
`=` or `:`, optionally quoted, and that substring is replaced. `D=/abs/x`,
`MEMFILE="~/x`, and `--out=/abs/x` all normalize; `python3 -m pytest tests/ -q`
and `src/api/adapter.py` pass through unchanged.

`BLINDING_TELLS` gains `with_skill`, `without_skill`, and their hyphenated
forms, so both the grader's refusal path and the suite can see the class.

`JudgeBlindingCase` changes in two ways. It enumerates action logs from
`git ls-files` instead of `rglob`, because the test's name says "committed" and
the filesystem is not the index -- an untracked directory was being scanned, and
after this change a directory removed from git but still on disk would have
failed a guard about what is published. And it carries `KNOWN_ARM_LEAKS`, six
run identifiers that leak and are published anyway, asserted in both directions.

## Decisions and trade-offs

The full decision is in
[`close-arm-name-leak`](../decisions/close-arm-name-leak.md). In short: the
artifacts are not rewritten, because editing a judge's recorded input to satisfy
a guard falsifies the evidence; the runs are not re-collected, because excluding
them moves the result by 0.005; and the figures are reported as collected with
the excluded-subset figure stated beside them, because an exclusion rule written
after seeing results is a degree of freedom.

## Failure, security, and recovery

The failure mode this introduces is a pin that becomes permanent suppression.
`KNOWN_ARM_LEAKS` is asserted in both directions to prevent it: an unpinned leak
fails, and a pinned run that no longer leaks also fails, so the list cannot
outlive its subject silently.

The second failure mode is over-broad normalization eating legitimate targets --
a judge that sees `(outside the repository)` where it should see a filename
loses information. The regex is anchored to `=` or `:` followed by `~`, `$`, or
`/`, and was checked against normal commands and file paths.

The security-relevant property here is the integrity of a published measurement,
not confidentiality. Recovery is reverting two functions and one frozenset; the
disclosures revert with them, since they would otherwise describe a state that
no longer holds.

Separately, this change adds the abandoned iteration-7 run's data to
`.gitignore`. 269 files of a run documented as "deliberately left uncommitted"
were swept into an unrelated commit by an over-broad `git add`, and were removed
from history before this push. The ignore rule stops that recurring.

## Verification evidence

| Check | Result |
| --- | --- |
| The three leaking token shapes | `D=/…/eval-7-without_skill-1 find …` → `D=(outside the repository) find "$D" -type f`; the `MEMFILE="~/…` and `--out=/…` forms likewise. No arm name survives |
| Normal targets unchanged | `python3 -m pytest tests/ -q`, `src/api/adapter.py`, `def handler` pass through verbatim |
| Guard proved by breaking it, unpinned leak | Removing `iteration-8/eval-7/without_skill/run-1` from `KNOWN_ARM_LEAKS` fails with `['without_skill'] != []` |
| Guard proved by breaking it, dead pin | Adding a clean run to `KNOWN_ARM_LEAKS` fails with "pinned as a known leak but no longer leaks" |
| Leak census over tracked artifacts | 6 runs: `iteration-3` ×1, `iteration-5` ×3, `iteration-8` ×2. All six pinned, none unpinned |
| Numeric impact, recomputed from `benchmark.json` | Baseline 0.5648 (n=27) → 0.5700 (n=25); difference 0.1512 → 0.1460 |
| `.gitignore` proved effective | `git check-ignore -v` resolves an iteration-7 data file to the new rule |
| Suite | 96 tests |
| Contract commands | Recorded via `engineering verify` |

## Known limits and learning gaps

- **The deepest cause is untouched.** The fixture directory still encodes the
  arm in its name, so the normalization is a scrub rather than a structural
  guarantee. Making it structural means changing the run layout, which cannot be
  verified without a live sweep. Named as the next change, not deferred silently.
- The two nets remain one net. Splitting them means a second predicate with a
  different derivation, which is more than this change should carry.
- The tell list is a substring match. It catches the arm names as spelled; a run
  layout that encodes the arm some other way would need a new tell.
- Six pinned leaks are six artifacts a reader must be told about, in three
  separate documents. Nothing enforces that the disclosures stay in sync with
  the pin list.
- The census covers tracked `actions.json` only. Whether other judge-visible
  files carry the same form was checked for these six runs, not proven for all.

## References

- [`close-arm-name-leak`](../decisions/close-arm-name-leak.md) -- the decision
- `docs/engineering/changes/fix-blinding-redaction.md` -- the earlier fix on
  this surface, and the "two independent nets" claim corrected there
- `engineering-ownership-workspace/iteration-8/PILOT.md` -- the corrected
  blinding paragraph and the numeric impact
- `scripts/eval/run_skill_evals.py`, `scripts/eval/grade_skill_evals.py`,
  `tests/test_evals.py`
