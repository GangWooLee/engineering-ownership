Before making this change, I want to flag a conflict with the existing design.

`src/api/partner_adapter.py` only marks two partners as whole-unit: `WHOLE_UNIT_PARTNERS = {"p-1", "p-7"}`. All other partners already receive the raw cents value unrounded. The decision record (`docs/decisions/2026-02-settlement-amount-units.md`) explicitly anticipated this exact scenario:

> "This holds only while every partner settles in whole units. If one starts accepting fractional amounts the conversion stops being a property of the adapter and becomes a property of the partner..."

In other words, the documented fix for "a partner now requires fractional amounts" is to **remove that specific partner from `WHOLE_UNIT_PARTNERS`**, not to strip rounding for every partner. If I make it global and your largest partner is only one of `p-1`/`p-7`, the *other* whole-unit partner would start getting rejected payloads again — the exact manual-retry problem this adapter was built to fix.

Which partner ID is your largest partner — `p-1` or `p-7`? And should the remaining whole-unit partner keep the rounding, or do both now require fractional amounts?