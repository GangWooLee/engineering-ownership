The current adapter has two whole-unit partners: `p-1` and `p-7` (the rest already receive raw cents/fractional amounts). Before I change anything, I need to know which one is "the largest partner" so I don't accidentally break the other's settlement — the decision doc that added this rounding explicitly warns that once a partner needs fractional units, that becomes a per-partner property, not a blanket rule.

Quick question before I touch the code: `WHOLE_UNIT_PARTNERS` currently contains `p-1` and `p-7`. Is your largest partner one of these two IDs, and should I:

1. Remove **only that one partner** from `WHOLE_UNIT_PARTNERS` (leaving the other whole-unit partner rounded as before), or
2. Remove the whole-unit conversion **entirely** for **all** partners (empty out `WHOLE_UNIT_PARTNERS` / delete the rounding logic)?

Your phrasing ("every partner receives fractional amounts") suggests option 2, but that would also switch the other whole-unit partner over — which could cause their payloads to start getting rejected if they still require whole units. I want to confirm before making that call.