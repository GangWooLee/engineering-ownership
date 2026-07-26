# 2026-07-26 · Exclude illustrative decision references from refs check

Change ID: `exclude-illustrative-references`
Created: `2026-07-26T11:26:59+09:00`
## Assets and trust boundaries

The asset is the integrity of the `refs check` gate: its promise that every
`engineering-decision:` marker in scanned content is backed by live evidence.
The trust boundary is `.engineering/contract.json` — a reviewed, committed
file that already governs risk classification and verification commands;
`refs.exclude` adds gate *scope* to what that file controls.

## Attacker-controlled inputs

The `refs` block of the contract, and file paths matched against it. A
malicious or careless contract edit could exclude `**` and blind the scan
entirely, or attempt path escapes (`/…`, `..`) to probe files outside the
repository.

## Security invariants

- Patterns must be repository-relative: absolute paths and any `..` segment
  are rejected at contract validation, before any scan runs.
- A malformed `refs` block fails closed — the CLI exits 2 and no command
  proceeds with a partially-validated contract.
- Exclusion filters only marker *collection*; ADR implementation-reference
  checks and evidence validation are unaffected.
- An absent `refs` key scans everything, so existing contracts cannot lose
  coverage silently.

## Abuse and failure cases

Excluding a broad glob (e.g. `plugins/**`) would let real dangling markers
ship unflagged. This is a policy weakening, not a code execution or path
traversal vector: patterns are only ever compared against already-enumerated
repository-relative paths from `git ls-files`, never used to open files.

## Mitigations and residual risk

Weakening requires a contract diff, which `risk_paths` classifies as
reviewed territory and Git history attributes. Residual risk: a reviewer
approving an over-broad glob; mitigated by keeping this repository's list to
three narrowly illustrative path families, each justified in the ADR.
