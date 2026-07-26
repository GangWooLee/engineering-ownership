# 2026-07-26 · Exclude illustrative decision references from refs check

Change ID: `exclude-illustrative-references`
Created: `2026-07-26T11:26:59+09:00`
Risk: R3

## Problem and intended outcome

`refs check --all` reported BLOCKED on this repository with ten gaps, all
false positives: the tool that gates other repositories' reference hygiene
failed its own repository because it cannot tell a real decision marker from
content that depicts one (test literals, tutorial code blocks, eval fixtures,
and eval output quoting those fixtures).

Intended outcome: `refs check --all` passes on this repository, with each
false-positive class resolved by the mechanism appropriate to it rather than
one blanket exception — and the one behavioral change (contract-declared
exclusions) recorded as a decision.

## Success and non-goals

Success: `refs check --all` exits 0; the four test literals compose markers
at runtime; tutorials keep their concrete worked example; eval fixtures and
committed eval records are untouched; the full suite passes with new
coverage for exclusion behavior and contract validation.

Non-goals: an inline "example" pragma in the scanner (second mechanism for
the same problem); excluding `tests/**` (test files can and do compose
markers at runtime, so they stay scanned); editing historical eval artifacts.

## Existing responsibilities searched

- Runtime marker composition already existed in
  `test_refs_check_passes_when_referenced_change_is_closed`; promoted to a
  shared `decision_marker` helper and applied to all five sites instead of
  inventing a new pattern.
- Repository-specific path policy already lives in the contract
  (`risk_paths`, matched with `fnmatch`); `refs.exclude` reuses that exact
  shape and matching semantics rather than adding a new config surface.
- The deliberate-exclusion precedent is `cover-ship-critical-paths` (the
  harness is not taxed with ceremony); this change extends the same recorded
  stance to the reference scan.

## System and data flow

`read_contract` → `validate_contract` now validates an optional `refs`
object (`exclude`: non-empty repository-relative glob strings, no absolute
paths, no `..`). `reference_scan_paths` filters `text_paths` output through
the globs; `reference_gaps` (used by both `refs check` and the `check` gate)
and the scanned-file count consume the filtered list. The contract JSON
schema documents the key. Absent key → empty exclusion list → prior behavior.

## Decisions and trade-offs

See `docs/engineering/decisions/exclude-illustrative-references.md` for why
exclusion is contract-declared rather than in-place neutralization or
hard-coded paths, and why `tests/**` deliberately stays scanned.

## Failure, security, and recovery

A malformed `refs` block fails contract validation loudly (exit 2) rather
than silently scanning nothing. Patterns cannot escape the repository
(absolute and `..` rejected). The worst misuse — excluding a path that later
gains a real marker — is visible in the reviewed contract diff and reversible
by deleting one glob. See the threat model for the gate-weakening analysis.

## Verification evidence

- `python3 -m unittest discover -s tests`: 83 tests pass, including new
  `test_refs_check_skips_contract_excluded_paths` (BLOCKED without the glob,
  PASS with it) and `test_contract_rejects_escaping_refs_exclude_pattern`.
- `refs check --all` on this repository: 152 files scanned, RESULT: PASS.
- All four R3 contract commands recorded via `engineering verify`.

## Known limits and learning gaps

`fnmatch` treats `*` and `**` identically (both cross `/`), so `refs.exclude`
globs are broader than gitignore semantics — same caveat as `risk_paths`,
acceptable because both err toward matching more. Excluded paths are not
reported per-file; only the scanned-file count reveals the effect. Revisit if
an excluded path ever needs a real enforcement marker.

## References

- `docs/engineering/decisions/exclude-illustrative-references.md`
- `docs/engineering/decisions/cover-ship-critical-paths.md` (precedent)
- `plugins/engineering-ownership/src/engineering_ownership/resources/schemas/contract-v2.schema.json`
