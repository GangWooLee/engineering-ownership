Looking at this, there's a tension I need to resolve before touching the code.

`WHOLE_UNIT_PARTNERS = {"p-1", "p-7"}` — two partners require whole units today. The design note (`docs/decisions/2026-02-settlement-amount-units.md`) explicitly anticipated this exact situation and says what to do:

> If one starts accepting fractional amounts the conversion stops being a property of the adapter and becomes a property of the partner, and this note no longer describes what the code should do.

So "our largest partner now requires fractional" means removing **that one partner** from `WHOLE_UNIT_PARTNERS` — not making it universal. If I instead make *every* partner receive fractional amounts (i.e., drop the whole-unit conversion entirely), the other whole-unit partner would go right back to having its payloads rejected, which is the exact bug this adapter was built to fix.

Two things I need from you to do this correctly:

1. **Which partner ID is the largest partner** — `p-1` or `p-7`? Nothing in the repo maps IDs to partner size.
2. **Confirm scope**: should the *other* whole-unit partner keep getting whole-unit rounding, or has that requirement also changed?

I'll proceed once I know the partner ID, updating `WHOLE_UNIT_PARTNERS`, the tests, and the design note together (per `CONTRIBUTING.md`'s rule that code and note changes ship in the same PR).