# 2026-07-26 · Cover ship-critical paths in the risk contract

Change ID: `cover-ship-critical-paths`
Created: `2026-07-26T11:00:30+09:00`
Risk: R2

## Problem and intended outcome

The audit found the contract did not govern the code the project works on:
zero globs matched `scripts/**`, `ci.yml` sat at R1 while `release.yml` was
R3, and the R3 list named four `src/` files literally — silently excluding
`evidence.py` (the module that writes every evidence record), `templates.py`,
and the published schemas. A change to `evidence.py` alone classified R1: no
ADR, no threat model, and the plugin/package verifications not required.

Intended outcome (owner's decision: cover ship-critical only): everything that
determines what installers receive or how it is verified carries the tier its
blast radius deserves, while the evaluation harness stays deliberately out of
scope so measurement work is not taxed with change-record ceremony — the
proportionality failure the audit called out.

## Success and non-goals

Success: `evidence.py`, `templates.py`, `resources/schemas/**`, the three
release/validation scripts, and `release.yml` classify R3; `ci.yml`
classifies R2; the full suite and all contract commands pass under the new
contract.

Non-goals: covering `scripts/eval/**` or `tests/**` — deliberate, recorded in
the ADR; changing verification commands or artifacts configuration.

## Existing responsibilities searched

The contract's own `risk_paths` mechanism is the single source of truth for
path-detected risk (`effective_risk`, model.py); this change edits data, not
mechanism.

## System and data flow

`classify_risk` matches changed paths against the globs with `fnmatch`, where
`*` crosses `/`. New R3 entries: the two `src` modules, the schema glob, and
the three scripts the release workflow executes. New R2 entry: `ci.yml`, the
file that gates every merge.

## Decisions and trade-offs

See `docs/engineering/decisions/cover-ship-critical-paths.md` for why the
evaluation harness is excluded on purpose.

## Failure, security, and recovery

Widening risk paths can only raise future obligations, never lower them
(`effective_risk` takes the maximum). Misclassification upward costs ceremony;
the previous misclassification downward cost silent under-verification of the
modules that write the evidence this tool exists to keep. Revert restores the
old globs with no data impact.

## Verification evidence

- `python3 -m unittest discover -s tests`: 81 tests pass under the new
  contract.
- All four contract commands pass via `engineering verify` for this change.
- Spot-check: `evidence.py` now matches an R3 entry; `ci.yml` matches R2;
  no glob matches `scripts/eval/**` (deliberate).

## Known limits and learning gaps

`tests/**` remains uncovered: a test edit alone still classifies R1. Accepted
for now — the unit suite is itself the verification layer, and taxing test
edits with R2 ceremony would discourage exactly the additions the audit asked
for. Revisit if a test change ever ships a behavior regression.

## References

- `.engineering/contract.json`
- `docs/engineering/decisions/cover-ship-critical-paths.md`
- Cold audit finding: UNDER-BUILT #7
