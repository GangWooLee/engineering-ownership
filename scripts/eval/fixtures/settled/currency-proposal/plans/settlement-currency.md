# Implementation plan: settlement currency

Derived from `docs/proposals/settlement-currency.md`.

1. Add `settlement_currency` to the orders schema, defaulting to USD.
2. Backfill existing rows to USD.
3. Include the currency in the adapter payload.
4. Read the currency from the row in the reporting path.
5. Remove the hard-coded currency from reporting once step 4 lands.

Steps 1 and 3 are in progress. Steps 2, 4, and 5 are not started.
