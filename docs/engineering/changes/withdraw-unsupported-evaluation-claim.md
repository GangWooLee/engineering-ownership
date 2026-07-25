# 2026-07-25 · Withdraw the unsupported skill evaluation claim

Change ID: `withdraw-unsupported-evaluation-claim`
Created: `2026-07-25T12:41:41+09:00`
Risk: R1
Status: Completed

## Problem and intended outcome

`docs/validation/skill-evaluation.md` published "With skill 16 / 16, Without
skill 5 / 16" as the project's only efficacy claim. Six defects were confirmed
by inspection and execution, any one of which is sufficient to invalidate it.
The most serious is that the largest measured separation was credited to
"required R3 teach-back" — behavior this project deliberately removed in
`documentation-first-workflow`. The number therefore does not merely predate the
current design; it advertises a property the design rejects.

This project's stated premise is evidence over confidence, and `CONTRIBUTING.md`
requires contributors to supply paired skill/baseline evaluation evidence. A
maintainer publishing an indefensible number while asking that of others is the
specific failure this change removes.

The intended outcome is that the repository publishes **no** quantitative
efficacy claim until a defensible one exists, that the withdrawn claim and its
reasons stay on the record rather than being deleted, and that the drift which
produced it cannot recur silently.

## Success and non-goals

Success:

- No current document presents an efficacy number.
- The withdrawn number is quoted alongside the reasons it fails, so a reader can
  audit the retraction instead of trusting it.
- Automated checks fail if a number is published without a committed artifact
  behind it.
- The release ZIP digest is unchanged, so the published integrity claim in
  `correct-git-attribution` stays true.

Non-goals for this change:

- Producing a replacement measurement. That requires a new runner, fixtures, an
  independent judge, and paid runs; it is scoped separately and must not delay
  this retraction.
- Rewriting the eight evals' expectations. Those live under
  `plugins/engineering-ownership/skills/**`, which the contract classifies R2 and
  which ships in the release ZIP. Keeping them untouched is what holds this
  change at R1 and keeps the ZIP digest stable.

## Existing responsibilities searched

- `docs/validation/` had no status or supersession convention, while
  `docs/engineering/decisions/` already had one (`Status:`, `Supersedes:`,
  `Superseded by:`). Rather than invent a second scheme, this change mirrors the
  decision-record convention in a lighter two-line form, so
  `plugin-discovery.md` — stale since v0.2 host validation superseded it — now
  says so.
- `scripts/grade_skill_evals.py` was the only owner of eval grading. It was
  removed rather than repaired: it could not run (`WORKSPACE` pointed at a
  non-existent `iteration-2`), had assertions for four of eight evals and
  `raise ValueError` for the rest, and matched on the skill's own vocabulary.
  Keeping a non-functional grader that encodes the discredited method would
  leave a second source of truth for a claim that no longer stands.
- `tests/` had no coverage of the eval manifest at all, which is why the drift
  between `evals.json` and the grader went undetected. The new tests reuse the
  existing house pattern (`unittest.TestCase`, `ROOT = Path(__file__).parents[1]`,
  no third-party runner) and are picked up by the existing
  `unittest discover -s tests` step, so CI needed no change.

## System and data flow

A published number now has one path and one gate:

`evals.json` (manifest) → runner → committed workspace artifacts →
`benchmark.json` → the machine-readable block in `skill-evaluation.md`.

`tests/test_evals.py::PublishedResultCase` closes the loop: if the validation
document contains a results block, the cited iteration's `benchmark.json` must
exist and its means must match to four decimal places. If it contains no results
block, the document must be marked `Withdrawn` or `Superseded`. There is no
third state in which a number can appear without an artifact behind it.

## Decisions and trade-offs

**Withdraw before re-measuring, as a separate commit.** The retraction is cheap
and reversible; the rebuild is expensive and uncertain. Coupling them would keep
an indefensible number published for as long as the rebuild takes. The cost is
that the project temporarily has no efficacy evidence at all, which is the
honest state.

**Quote the withdrawn number instead of deleting it.** Deleting the record of a
retracted claim destroys the evidence that it was retracted, and this project's
own ADR convention exists to avoid rewriting accepted history. The cost is a
longer document that a careless reader could misread; the `Status: Withdrawn`
header and an explicit "no replacement number is published yet" mitigate that.

**Delete the grader rather than fix it.** Rejected alternative: retain its
deterministic checks as a pre-filter for a future judge. That would re-import
the vocabulary keying and word-boundary bugs at smaller blast radius. The
replacement design keeps deterministic checks only as validity gates (non-empty
response, language control, clean exit), never as assertion graders.

**Assert the absence of a pattern, not the presence of an implementation.** The
grader tests scan any `scripts/**eval*.py` for hardcoded eval names, the skill's
private vocabulary, and non-ASCII matching terms. This constrains a replacement
that does not exist yet without prescribing its shape.

## Failure, security, and recovery

This change is documentation, one deletion, and one test module. It adds no
runtime surface, no network call, and no new dependency; nothing here reaches
the shipped plugin.

The reversible failure mode is over-strict tests blocking legitimate future work
— for example if a replacement grader must legitimately mention an eval name.
Recovery is to narrow the assertion with a recorded reason rather than delete
it, since the test encodes a defect that actually occurred.

Rollback is `git revert` of this commit. Because `evals.json` is untouched, the
v0.2.0 release ZIP rebuilds to its published digest before and after.

## Verification evidence

Run against the current diff:

- `python3 -m unittest discover -s tests`: 50 tests pass (38 pre-existing, 12
  new).
- `python3 scripts/validate_distribution.py`: passed.
- `claude plugin validate --strict .`: passed.
- `python3 scripts/build_release.py --version 0.2.0`: digest `8507a02d…`,
  unchanged from the pre-change build, confirming the published ZIP-integrity
  claim still holds.

Real-runtime evidence, recorded separately from the test results because a
passing test that has never been observed failing is not evidence: each of four
guards was deliberately broken and confirmed to fail with a specific message,
then restored.

| Guard | Injected fault | Observed failure |
| --- | --- | --- |
| English-only manifest | Korean expectation added to eval 1 | `r0-readme-typo.expectations[0] is not ASCII` |
| Backed-number gate | Results block citing a non-existent iteration | `published results cite iteration-9 but no benchmark.json is committed` |
| No grader whitelist | Script branching on an eval name | `fake_eval_grader.py hardcodes eval 'r0-readme-typo'` |
| Validation status convention | Document with no `Status:` line | `temp-probe.md has no Status line` |

The full suite returned to green after each restoration.

## Known limits and learning gaps

- **No efficacy evidence exists right now.** This change removes an unsupported
  claim; it does not supply a supported one.
- The `PublishedResultCase` gate checks that a published mean matches a committed
  artifact. It cannot check that the artifact was produced by a sound method —
  that is what the evaluation-methodology decision record will have to carry.
- `scripts/**` still matches no `risk_paths` entry in `.engineering/contract.json`.
  The script that generates the project's public efficacy claims is therefore
  unclassified, which is part of how this defect survived. Deliberately left for
  the R2 rebuild, where the replacement runner lands and the classification can
  be decided with its evidence rather than in passing.
- `legacy-project-read-only.md` is marked `Current` but was checked with the v0.1
  CLI; a v0.2 re-check is unrecorded. Noted in the document, not resolved here.

## References

- Withdrawn claim and its six defects: `docs/validation/skill-evaluation.md`
- Convention and index: `docs/validation/README.md`
- Decision that superseded mandatory teach-back:
  `docs/engineering/decisions/documentation-first-workflow.md`
- Published ZIP-integrity claim this change preserves:
  `docs/engineering/changes/correct-git-attribution.md`
- Contributor requirement this change brings the maintainer into line with:
  `CONTRIBUTING.md`
