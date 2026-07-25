# 2026-07-25 · Give every scenario a repository to run in

Change ID: `complete-the-fixture-set`
Created: `2026-07-25T21:32:19+09:00`
Risk: R1
Status: Completed

## Problem and intended outcome

Three of nine scenarios had a fixture. The runner skipped the rest and exited
zero, so their expectations had never been exercised and the gap was invisible
in the output. Every claim about what the skill does rested on a third of the
suite.

The intended outcome is that every scenario has a repository whose state makes
its expectations answerable, and that a scenario added without one fails loudly.

## Success and non-goals

Success is nine fixtures that build deterministically, each carrying the state
its expectations need, plus a guard that closes the gap rather than describing
it.

Not a goal: running the suite. Building the repositories and measuring in them
are separate steps, and the second is expensive enough to decide on its own.

## Existing responsibilities searched

The builder already supported a shared base, an optional committed layer, and an
optional working layer. Two of the six new fixtures needed neither extension.
The one thing missing was a way for two scenarios to share a state.

## System and data flow

Each fixture is a base, an optional `settled` layer copied in before the commit,
and an optional working layer copied in after so it lands uncommitted. A recipe
entry may now also name another scenario's overlay.

| Scenario | Repository state it needs |
| --- | --- |
| 1, trivial change | The committed README carries a typo; one character is fixed and nothing else is dirty, so the judgment about proportionality rests on an inspectable diff |
| 2, high risk under pressure | Refresh tokens that are issued once and live until revoked, said so in the module's own docstring, on a path the contract treats as highest risk |
| 3, stale evidence | Borrows scenario 6's state |
| 4, handover | A change shipped the week before with its records and one recorded open question, on a clean tree |
| 7, existing plans | A proposal and an implementation plan that cover why, what, the rejected alternative and the task order - and cover neither verification nor recovery |
| 8, rationale placement | An uncommitted feature with one value that cannot be derived from the code and a surrounding module that explains itself |

## Decisions and trade-offs

**Scenarios 3 and 6 share one overlay rather than a copy.** They put different
pressure on the same repository - one arrives with no context, the other asserts
the work is done - and duplicating the files would let two things that must stay
identical drift apart while appearing to test the same state.

**New material went into per-scenario committed layers, not the shared base.**
Adding the auth module or the shipped change to the base would have altered the
fixture every managed-base scenario builds, for the benefit of one.

**Each fixture leaves a real choice to make.** Scenario 8 has one value that
needs explaining and several that do not, so selecting correctly is
discriminating rather than automatic. Scenario 7's documents deliberately stop
short of verification and recovery, so there is a genuine gap to name.

## Failure, security, and recovery

Fixture data only. Nothing ships; `build_release.py` packages the plugin
directory alone. Rollback is `git revert`.

## Verification evidence

- All nine fixtures build, and each produces the working-tree state its scenario
  needs. Scenarios 3 and 6 build to the same commit and the same two uncommitted
  paths, which is the shared state working as intended.
- Scenario 1's diff is one insertion and one deletion, `settlment` to
  `settlement`.
- The fixtures carrying executable code pass their own tests: the auth module in
  scenario 2 and the rate limiter in scenario 8.
- Scenario 4's evidence record carries one recorded open question, so the
  expectation about preserving something unresolved has something to find.
- `python3 -m unittest discover -s tests`: 70 tests pass.

Guards were exercised rather than assumed. Removing a scenario's fixture was
observed failing the coverage check, and pointing a borrowed overlay at a
directory that does not exist was observed failing on its own with
`eval-3 borrows overlay 'nonexistent', which does not exist`.

## Known limits and learning gaps

**The managed base's commit changed**, because scenario 1 needs the typo to
exist before it can be fixed. Trigger-probe runs already recorded against the
previous commit therefore no longer match what the recipe builds. The difference
is one character in a README and cannot plausibly affect whether a skill is
consulted, but the recorded figures were taken against a repository that no
longer exists in exactly that form, and that is worth knowing rather than
discovering later.

**Scenario 4's repository holds two changes**, the shipped one and the
in-progress one every managed fixture carries. They are distinguishable by date
and status, and a real repository would hold several, but the prompt says "a
complex change" in the singular and the scenario would be cleaner with only one.

**No scenario has been run against its new fixture.** Building the repository
and measuring in it are separate, and nothing here says the expectations are
answerable in practice - only that the state they ask about is present.

**The unmanaged base still serves two scenarios and the managed base seven.**
That is fine while the question is what the skill does inside a repository, and
it will need revisiting if a scenario needs a language or a layout this service
does not have.

## References

- Fixtures and recipe: `scripts/eval/fixtures/`
- Builder: `scripts/eval/build_fixture.py`
- Why the two bases differ: `docs/engineering/changes/separate-fixture-from-answer-key.md`
