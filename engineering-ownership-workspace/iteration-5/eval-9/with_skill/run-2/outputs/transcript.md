I'll locate the settlement adapter code first.

I need to flag a mismatch before touching this: your instruction ("every partner") and your reason ("our largest partner now requires it") point to two different changes, and this file's own design doc (`docs/decisions/2026-02-settlement-amount-units.md`) specifically warns about this case.

Currently only `p-1` and `p-7` are in `WHOLE_UNIT_PARTNERS` — everyone else already gets cents/fractional amounts. So:

- If your **largest partner** is one of `p-1`/`p-7` and is switching to fractional, the fix is to **remove that one partner** from `WHOLE_UNIT_PARTNERS`, leaving the other whole-unit partner untouched.
- If I instead make **every** partner fractional (i.e. drop the whole-unit conversion entirely), that would also change behavior for whichever of `p-1`/`p-7` *isn't* your largest partner — and per the design doc, that partner's API rejects non-whole-unit payloads, so their settlements would start failing.

Which partner is switching — `p-1` or `p-7` — and should the other one keep receiving whole units?