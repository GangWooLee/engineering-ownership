All verification passes and the evidence record is current. Summary of what changed in this session:

**Fixed a real correctness bug**: the adapter was truncating (floor-dividing) cents to whole units for `WHOLE_UNIT_PARTNERS` (`p-1`, `p-7`), which silently under-reports money whenever the fractional part is ≥50¢ (e.g. $5.50 → $5) — directly the failure mode this change's own ADR warned about. Replaced it with round-half-up in `_round_half_up_to_whole_unit`.

**Added test coverage** (`tests/test_partner_adapter.py`) for: whole-unit conversion, the `.49`/`.50`/`.51` rounding boundary, passthrough for non-whole-unit partners, and `settlementCurrency` default/passthrough — none of this new behavior had tests before.

**Updated the reasoning trail**: change brief and an ADR addendum documenting the round-half-up decision, without rewriting the original accepted decision.

**Left open, on purpose**: the wire format for partners outside `WHOLE_UNIT_PARTNERS` that settle in fractional units. Currently they get raw `amount_cents` passed through unchanged, which is an assumption, not a confirmed contract — closing it needs a partner integration spec I don't have, so I recorded it as an explicit understanding gap (revisit by 2026-08-08) instead of guessing at a format.

Everything currently sits as uncommitted working-tree changes (`src/api/partner_adapter.py`, `src/db/schema.py`, `tests/test_partner_adapter.py`, the change/ADR docs, and the evidence file). Per `AGENTS.md`'s "keep schema and adapter changes in separate commits" convention, I'd split this into two commits (schema, then adapter+tests+docs+evidence) — let me know if you'd like me to go ahead and commit.