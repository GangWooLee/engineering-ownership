# Settlement amount units

February 2026, agreed in the platform sync.

Orders are stored as integer cents. The partner settlement API rejects any
payload whose amount is not a whole currency unit, so every submission for a
whole-unit partner was being rejected downstream and retried by hand.

We looked at three ways out. Storing a second column in whole units was
rejected because it needs backfilling and can drift from the cents value.
Converting in each caller was rejected because the rule then has no single
owner. We chose to convert once inside the adapter, which already owns the
payload contract.

Rounding is half-up. Flooring silently under-reports money on any order whose
remainder is at least fifty cents, and that money is real.

This holds only while every partner settles in whole units. If one starts
accepting fractional amounts the conversion stops being a property of the
adapter and becomes a property of the partner, and this note no longer
describes what the code should do.
