# 2026-07-25 · Rewrite the evaluation expectations to be passable on merit

Change ID: `rewrite-evaluation-expectations`
Created: `2026-07-25T14:28:50+09:00`
Risk: R2
Status: Completed

## Problem and intended outcome

The pilot in `defensible-skill-evaluation` proved the harness works and then
showed the expectations do not. The blinded judge scored the baseline 4/4 and
the skill 3/4, and the reason was not judgment quality: the skill run resolved
the stale verification it was asked to identify and reported the resulting clean
state, while the baseline stopped and asked, leaving the staleness visible in
its answer. That expectation rewards leaving the problem unfixed.

An audit of all 32 expectations found the problem was general, not local. Three
were sound. The intended outcome is a manifest whose expectations a competent
engineer unfamiliar with this skill could pass on merit, that still
discriminates, and that cannot drift back.

## Success and non-goals

Success is that every expectation satisfies four stated rules, that the rules
are enforced by tests rather than by review, and that the maintenance behaviour
the owner identified as this project's distinguishing focus is actually covered.

Not in scope: running the rewritten manifest at a sample size that would support
a published number. Two harness changes have to land first, and they are named
under known limits.

## Existing responsibilities searched

`tests/test_cli.py` and `tests/test_distribution.py` already assert
deterministically much of what the old manifest asked a judge to re-derive:
risk-tier detection, diff-digest staleness gating, handoff contents,
non-blocking review, the decision-marker format, the four `refs check` failure
modes, non-destructive init, and hooks being off by default. Those expectations
were removed rather than reworded. Spot-checked: `test_r0_passes_without_brief`
asserts `Risk: R0` on a documentation-only change, which is exactly what the old
eval 1 asked a judge to confirm.

The ninth scenario reuses the existing fixture base rather than adding one. Its
accepted decision - convert amounts at the adapter boundary - is already there,
and the new prompt contradicts it.

## System and data flow

`evals.json` is read by the runner, which pairs each prompt with a fixture and
runs it twice; the responses are graded by a blinded judge against the
expectation list carried in `eval_metadata.json`; the aggregator turns the
gradings into a benchmark. Changing the manifest therefore changes what is
measured but nothing about how.

Fixture construction gained one concept: an overlay may name a `settled` state
that is copied in **before** the commit, so a scenario can present a decision
that is already implemented rather than only planned. Overlay directories are
now optional, which is what lets a scenario start from a clean tree.

## Decisions and trade-offs

The four admissibility rules and the alternatives rejected are recorded in
`docs/engineering/decisions/rewrite-evaluation-expectations.md`.

Two trade-offs are worth stating here.

**Prompts changed, not only expectations.** Several named this project or its
concepts, so no baseline could answer them however the expectations were
worded. Changing a prompt changes what the scenario measures, which breaks
continuity with the withdrawn results - but those results are withdrawn, so
there is nothing to preserve continuity with.

**The ninth scenario was added now rather than later.** It expands the change.
It was added anyway because `evals.json` ships in the release package, so any
edit forces a version bump; deferring would pay that cost twice.

## Failure, security, and recovery

No runtime surface changes: the CLI, router, and hooks are untouched, and
`evals.json` is data read by a developer tool.

The real hazard was procedural. `.engineering/contract.json` and
`tests/test_release.py` both invoked `build_release.py --version 0.2.0`, and
that script overwrites both the archive and its `.sha256` sidecar from whatever
the working tree holds. Running verification after editing `evals.json` but
before bumping those pins would have produced a file labelled `0.2.0` whose
digest was not the published one, silently falsifying the integrity claim in
`correct-git-attribution`. `dist/` is untracked, so version control held no
copy.

Handled by bumping those two pins first, before any content edit, and by
recording the published digest into `docs/releases/v0.2.0.md`, where it now
survives independently of the build directory. Recovery, had it gone wrong, was
`gh release download v0.2.0`; the remote assets were confirmed byte-identical
beforehand.

## Verification evidence

- `python3 -m unittest discover -s tests`: 58 tests pass.
- `python3 scripts/validate_distribution.py`: passed.
- `claude plugin validate --strict .`: passed.
- `python3 scripts/build_release.py --version 0.2.1`: produced the new archive.
- `dist/engineering-ownership-v0.2.0.zip.sha256` still reads `8507a02d…`,
  confirming the published integrity claim survived the version bump.

Real-runtime evidence, recorded separately because a guard nobody has seen fail
is not evidence. Each new guard was given a violating expectation and observed
rejecting it, then restored:

| Injected | Observed |
| --- | --- |
| `"...classifies the change as R2..."` | requires a risk-tier label |
| `"Requires a runbook before..."` | requires 'runbook' |
| `"Does not require a change brief for a small edit."` | phrased as bare restraint |
| Same, with `"and says why that level of process is unnecessary"` | accepted, as intended |

The last row matters as much as the others: the guard distinguishes restraint
that is shown from restraint that is merely absent, rather than banning negation
outright.

Fixtures were rebuilt and inspected: the ninth scenario produces a clean tree
with the decision implemented and its tests passing, and the resume scenario
still produces the same two uncommitted paths as before.

## Known limits and learning gaps

**Eight expectations are not yet gradable.** They concern what the run leaves
behind, or acts of inspection. Two harness changes are required and neither has
landed:

1. **Runs must be allowed to write, symmetrically.** Restricting the tool set
   did not prevent writes in the pilot, and durable records cannot be observed
   without them. The capability must be identical in both configurations; giving
   the treatment a tool the baseline lacks would kill the comparison the way the
   language confound killed the first one.
2. **The judge must see what the run did, without learning which run it was.**
   It currently receives only the response. Handing it the transcript is the
   obvious fix and the wrong one: the treatment's transcript names this skill
   four times and the baseline's never does, and `metrics.json` carries a
   `Skill` key on one side only. What it should receive is a machine-derived,
   ordered action log with skill entries dropped, plus the content of what the
   run changed.

Until both land, any run of this manifest must report those expectations as
ungradable rather than failed.

**Only two of nine scenarios have fixtures.** The runner skips the rest, so
seven scenarios and most expectations remain unexercised. A guard now rejects an
orphaned fixture; the reverse gap is reported in each iteration rather than
enforced, because enforcing it would make the suite red for a gap that is
already known and recorded.

**The rules are a proxy, not a proof.** "Not satisfiable by silence" is checked
syntactically - leading negation without a clause requiring the response to show
its reasoning. That would have caught every instance of the actual regression,
and will not catch a carefully worded future one. The empirical version is to
grade a deliberately vacuous response and require it to score zero; that belongs
with an iteration, not with the unit tests.

**Response-side leakage remains.** A response may itself name a risk tier or
cite this project's directories, which no amount of input control removes. The
judge is never told two configurations exist and is instructed not to pass on
vocabulary, but this is a residual, not a solved problem.

## References

- Decision record: `docs/engineering/decisions/rewrite-evaluation-expectations.md`
- The pilot that exposed the defect: `docs/engineering/changes/defensible-skill-evaluation.md`
- The withdrawn claim: `docs/validation/skill-evaluation.md`
- Release notes: `docs/releases/v0.2.1.md`
