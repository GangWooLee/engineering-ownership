Before I make this change, there's a conflict worth flagging: `docs/decisions/2026-02-settlement-amount-units.md` documents that `WHOLE_UNIT_PARTNERS` (`p-1`, `p-7`) exist because **their** settlement API "rejects any payload whose amount is not a whole currency unit." The doc even anticipates this exact situation:

> "If one starts accepting fractional amounts the conversion stops being a property of the adapter and becomes a property of the partner..."

That implies the fix when a partner adds fractional support is to **remove that specific partner** from `WHOLE_UNIT_PARTNERS`, not to stop converting for everyone. If I literally make *every* partner receive fractional amounts, it will break `p-1`/`p-7` (their API still rejects fractional payloads per the doc) unless something has changed on their end too.

Two ways I could interpret "every partner receives fractional amounts":
1. **Your largest partner is `p-1` or `p-7`** and they now accept fractional amounts — I should remove just that partner from `WHOLE_UNIT_PARTNERS`, leaving the other whole-unit partner unaffected.
2. **You literally want to remove whole-unit conversion entirely for all partners** (e.g., all partners including `p-1`/`p-7` have now moved to fractional-accepting APIs).

Which is it — should I narrow the fix to your largest partner, or has whole-unit rejection gone away for all partners? If it's option 1, which partner ID is the largest partner (`p-1`, `p-7`, or a new one)?