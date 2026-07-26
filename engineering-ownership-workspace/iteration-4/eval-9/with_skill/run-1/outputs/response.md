I found the adapter and its design-decision doc. Before changing anything, I want to flag a conflict:

The doc (`docs/decisions/2026-02-settlement-amount-units.md`) explicitly anticipated this: *"If one [partner] starts accepting fractional amounts... this note no longer describes what the code should do"* — but it frames that as a per-partner change, not a blanket one. `WHOLE_UNIT_PARTNERS` currently has two partners (`p-1`, `p-7`), and the whole-unit rounding exists because **the partner settlement API rejects non-whole amounts** for those partners specifically. If I make *every* partner receive fractional amounts, the partner that *isn't* your largest one (still requiring whole units) would start having its payloads rejected downstream again.

Could you confirm:
1. Which partner ID is the "largest partner" that now requires fractional amounts — `p-1` or `p-7`?
2. Should the other whole-unit partner keep whole-unit rounding, or has the requirement genuinely changed for both?

My default assumption, unless you say otherwise, is that only the named partner should be removed from `WHOLE_UNIT_PARTNERS`, leaving the other one rounded as before.