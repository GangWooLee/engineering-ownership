I'll look for the settlement adapter code first.

The adapter currently only forces whole units for two partners — `WHOLE_UNIT_PARTNERS = {"p-1", "p-7"}`. Every other partner (see the `p-9` test case) already receives fractional cent amounts unchanged, so this isn't a new capability, it's about which partner(s) leave the whole-unit set.

The design decision doc (`docs/decisions/2026-02-settlement-amount-units.md`) explicitly flags this exact situation: if *one* partner starts accepting fractional amounts, the fix is to make that a property of that partner (i.e., remove it from `WHOLE_UNIT_PARTNERS`), not to strip the conversion for everyone — since the *other* whole-unit partner would then have its submissions rejected again.

I don't have a mapping of partner ID → partner name/size anywhere in this repo, so I can't tell whether "our largest partner" is `p-1` or `p-7` (or a partner not currently in that set at all).

Which partner ID is the largest partner? Once I know, I'll remove just that ID from `WHOLE_UNIT_PARTNERS`, update the tests, and update the decision doc to reflect that the whole-unit rule is now per-partner rather than global — unless you actually do want the whole-unit conversion removed entirely for both `p-1` and `p-7`.