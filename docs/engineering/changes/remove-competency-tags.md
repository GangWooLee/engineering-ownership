# 2026-07-26 · Remove the write-only competency tag subsystem

Change ID: `remove-competency-tags`
Created: `2026-07-26T10:42:28+09:00`
Risk: R3

## Problem and intended outcome

The cold audit verified exhaustively that the eight competency tags were
write-only: recorded once via `change start --competency`, read nowhere except
two verbatim `print` calls in `status` and `handoff`. Two hand-maintained
copies of the list (`model.py` and `resources/competencies/catalog.json`) had
no sync test; the reference doc implied `status` aggregates them, and nothing
did. The subsystem shipped to every installer and did nothing for them, while
standing as an open invitation to misread the tags as the maturity score the
project explicitly disclaims.

Intended outcome: the subsystem is gone — set, CLI flag, catalog, echo sites,
schema requirement, reference doc, count check — while every existing evidence
record that carries a `competencies` array remains fully readable.

## Success and non-goals

Success: full suite passes; the release ZIP no longer contains the catalog;
`grep` finds no live tag plumbing outside historical records and eval fixture
data; a regression test proves legacy records with the field stay readable.

Non-goals: rewriting historical evidence records, change records, release
notes, or CHANGELOG entries (history is not edited); touching the eval fixture
evidence JSONs that legitimately model pre-existing repositories.

## Existing responsibilities searched

The audit's refutation pass already confirmed no consumer exists: no gate,
filter, aggregation, or hook reads the field. The only compatibility surface is
`validate_evidence`, which now ignores the field instead of validating it
against a vocabulary that no longer exists.

## System and data flow

Removed: `COMPETENCIES` (model.py), the `--competency` argparse option and its
pass-through in `command_change_start`, the echo lines in `command_status` and
`handoff_text`, the catalog resource and its count check in
`validate_distribution.py`, the `competencies` requirement and property in
`evidence-v1.schema.json`, `references/competencies.md` and its SKILL.md link,
the README "eight tags" paragraph, and the CLI reference mention. New records
are written without the field; old records keep it, unread.

## Decisions and trade-offs

See `docs/engineering/decisions/remove-competency-tags.md`.

## Failure, security, and recovery

The risky failure would be rejecting old records. Covered by
`test_evidence_with_legacy_competencies_field_stays_readable` and by the
schema keeping the field merely unlisted (no `additionalProperties: false`
anywhere). No security surface changes; the CLI's write path is untouched.

## Verification evidence

- `python3 -m unittest discover -s tests`: 80 tests pass (one test reworked to
  drop the tag echo assertion, one added for legacy-field compatibility).
- `python3 scripts/validate_distribution.py`: passed after removing the
  catalog count check.
- Release ZIP rebuilt: zero entries matching the catalog or tag resources.
- All four contract commands pass via `engineering verify`; scoped
  `refs check --change remove-competency-tags`: PASS.

## Known limits and learning gaps

Historical texts (v0.1.0 release notes, CHANGELOG 0.1.0, closed change
records, one validation observation) still mention the tags as facts about the
past; deliberately untouched. Eval fixture evidence files carry the field as
realistic legacy data — also deliberately untouched.

## References

- `docs/engineering/decisions/remove-competency-tags.md`
- Cold audit finding: OVER-BUILT #1, "delete exactly one thing"
