# 2026-07-26 · Remove the write-only competency tag subsystem

Change ID: `remove-competency-tags`
Created: `2026-07-26T10:42:28+09:00`
## Assets and trust boundaries

The evidence records under `.engineering/evidence/` and the shipped plugin
package. No trust boundary moves: this change deletes a write-only field and
its plumbing; the CLI's write path, subprocess policy, and path-safety checks
are untouched.

## Attacker-controlled inputs

None new. One input surface is removed (`--competency` argument values), which
strictly shrinks the parser.

## Security invariants

- Existing evidence records — including those carrying a legacy
  `competencies` array — remain readable; removal cannot brick a repository's
  memory.
- The schema change is subtractive only (field no longer required or
  described); no record that validated before fails after.
- The release package shrinks; nothing new ships.

## Abuse and failure cases

The only meaningful failure is compatibility: rejecting legacy records would
make `status`, `handoff`, `refs check`, and `check` fail on every pre-existing
repository. Covered by a dedicated regression test and by hand-verification
against this repository's own 13 legacy-tagged records.

## Mitigations and residual risk

Mitigation is the compatibility test plus the full suite. Residual risk is
nil beyond ordinary revert cost; the field was never consumed, so no behavior
depended on it.
