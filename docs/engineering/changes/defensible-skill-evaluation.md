# 2026-07-25 · Build a defensible skill evaluation harness

Change ID: `defensible-skill-evaluation`
Created: `2026-07-25T13:22:42+09:00`
Risk: R1
Status: In progress

## Problem and intended outcome

`withdraw-unsupported-evaluation-claim` removed a claim the project could not
defend. This change builds the machinery that can produce a defensible one, and
proves that machinery works before any number is measured.

The owner's stated focus shapes what is being measured. Most agent harnesses
optimise for producing a program; this project extends the same discipline to
maintaining one - resuming work with no conversation context, respecting a prior
accepted decision, handing over to whoever comes next. The pilot therefore ran
the most maintenance-shaped scenario in the suite rather than the simplest one.

## Success and non-goals

Success for this stage is a runner, a fixture, a blinded judge, and an
aggregator that work end to end, plus evidence that the two configurations
differ in the skill and nothing else.

Not in scope yet: rewriting the expectations, running enough repetitions to
report a mean, or publishing any number. Those follow, and the first requires
touching `evals.json`, which raises this to R2 and forces a version bump.

## Existing responsibilities searched

The `skill-creator` plugin already owns A/B evaluation of Agent Skills, and this
repository's `grading.json` and `benchmark.json` already matched its schema. Its
aggregator and judge prompt are vendored verbatim under
`scripts/eval/vendor/` with recorded digests rather than reimplemented; only the
runner is new, because `skill-creator` delegates execution to interactive
subagent spawns and this needed to be unattended and reproducible.

`tests/test_cli.py` already had a helper that builds a throwaway Git repository,
and `scripts/eval/build_fixture.py` follows the same shape.

The runner shells out to the same `claude` CLI the repository is developed with,
using the developer's existing session. Evaluation therefore needs no separate
API credential and is not a separately billed activity.

## System and data flow

`evals.json` -> runner (fixture + two configurations) -> per-run response,
transcript, metrics, timing -> blinded judge -> `grading.json` -> aggregator ->
`benchmark.json`.

Both configurations run with every user-scope plugin disabled and with
`CLAUDE_CODE_DISABLE_CLAUDE_MDS=1`. The treatment then gets the skill back
through `--plugin-dir` and nothing else, so plugin loading is the only variable.
The judge receives the response inline and is given no tools, so it cannot read
the directory name that encodes the configuration.

## Decisions and trade-offs

**Record what a run changed rather than discarding it.** Restricting the tool
set did not reliably prevent writes. Rather than fight that, a run that modifies
the fixture is recorded, not invalidated - and for a maintenance scenario the
edits are part of what is being observed. The trade-off is that this is no
longer purely a text comparison; the boundary move is stated rather than hidden.

**Detect skill use by the Skill tool alone.** Matching the skill's name against
tool inputs looked reasonable and was wrong: this repository's own directory
carries that name, so every absolute path the agent touched matched it and the
baseline was reported as having loaded the skill.

**Vendor rather than reference.** An in-place reference to a path under a
maintainer's home directory cannot be reproduced by an auditor, and that path
contains `unknown` as its version segment.

## Failure, security, and recovery

The runner invokes an agent with a relaxed permission mode. The mitigations are
a per-run throwaway fixture built outside this repository, a tool allowlist with
no network access, and a recorded diff of whatever the run changed. Responses
and transcripts are redacted before being written, because they are committed
and `AGENTS.md` forbids storing home paths.

Nothing here ships: `scripts/build_release.py` packages only
`plugins/engineering-ownership/**`. Rollback is `git revert`; the artifacts are
additive.

## Verification evidence

- `python3 -m unittest discover -s tests`: 54 tests pass.
- `validate_distribution.py`, `claude plugin validate --strict .`: pass.
- `build_release.py --version 0.2.0` still produces digest `8507a02d...`,
  unchanged, because `evals.json` was not touched.

Real-runtime evidence, recorded separately from the tests:

- `engineering-ownership-workspace/iteration-2/preflight.json` records that on
  the same fixture and model the baseline answered `NONE` when asked which
  engineering-ownership skills were available, and the treatment named the
  skill. This is the control the withdrawn evaluation never had.
- Runs now carry real measurements where the withdrawn evaluation carried
  hardcoded zeros: 22 and 6 tool calls, 37 and 11 turns, 312s and 104s,
  3,254,669 and 725,974 tokens.
- Four new guards were each deliberately broken, observed failing with a
  specific message, and restored - including the home-path scan, which was
  written after a real leak was found in a transcript.

## Known limits and learning gaps

**The pilot found five defects in its own harness.** That was its purpose, and
they are recorded because the fixes are only as trustworthy as the record of
what they fix.

| Defect | Consequence | Resolution |
| --- | --- | --- |
| `--allowedTools` pre-approves but does not restrict | The agent edited fixture files | `--tools` set; writes are now recorded rather than prevented |
| Only this plugin was disabled | Thirteen others stayed active, one of which rewrites the response format | All user-scope plugins disabled |
| Fixture had no ignore rule | Running tests dirtied the tree and looked like tampering | Ignore rule added to the fixture |
| Skill detection matched tool inputs | The baseline was reported as having loaded the skill, because the repository directory shares its name | Detect the Skill tool only |
| Home path written into a transcript | A committed artifact would have violated the repository's own rule | Redaction at write time, plus a test |

**The current expectations are not yet valid measurements.** The pilot graded
one run per configuration against the original expectations. The blinded judge
passed the baseline on all four and failed the treatment on one - because the
treatment resolved the staleness it was asked to identify and then reported the
resulting clean state, while the baseline stopped and asked, leaving the
staleness visible in its answer. As written, that expectation rewards not
fixing the problem. The judge's own critique flagged the same expectation as
conjunctive and weakly falsifiable, and flagged another as satisfiable by
accident. Rewriting them is the next step and is a precondition for any number.

**No efficacy claim is supported by this pilot.** One run per configuration
gives a standard deviation of zero by construction.

**Cost is now measured and is substantial**: the treatment used roughly four to
five times the tokens of the baseline on this scenario. Whether that buys
proportionate value is exactly what the rewritten expectations have to answer.

**The vendored aggregator needs a post-pass.** It mislabels the eval count and
reports a character count where tokens belong, because it reads a field this
runner populates differently. Not corrected upstream-in-place, by design.

**One eval is missing for the stated focus.** The skill requires an agent to
record whether a change follows, supersedes, or invalidates a prior decision,
and never to overwrite accepted rationale silently. No eval tests that, and it
is the most maintenance-specific behaviour the skill has. The pilot response
happened to demonstrate it - an ADR addendum "without rewriting the original
accepted decision" - which is exactly the kind of behaviour that should be
measured rather than noticed by luck.

## References

- Retraction this builds on: `docs/engineering/changes/withdraw-unsupported-evaluation-claim.md`
- Withdrawn claim and its defects: `docs/validation/skill-evaluation.md`
- Vendored harness and its provenance: `scripts/eval/vendor/PROVENANCE.md`
- Pilot artifacts: `engineering-ownership-workspace/iteration-2/`
