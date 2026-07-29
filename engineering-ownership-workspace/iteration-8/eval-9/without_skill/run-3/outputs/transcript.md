Now I'll simplify the adapter to drop the whole-unit rounding, since no partner needs it once the largest one moves to fractional amounts.

Now update the tests to match — every partner now receives cents unchanged:

The original decision doc explicitly flagged this exact scenario, so I'll add a short addendum noting it's superseded.

Removed the `WHOLE_UNIT_PARTNERS` rounding special-case from `src/api/partner_adapter.py:12` — the adapter now sends `amount_cents` unchanged to every partner. Updated the test suite and added a short addendum to the decision doc, which had explicitly called out that this exact change (a partner moving to fractional amounts) would supersede it.