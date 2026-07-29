The rate-limiter feature is now documented and verified. Summary:

**Recorded for the new feature** (`partner-settlement-rate-limit`, risk R2):
- **Brief** (`docs/engineering/changes/partner-settlement-rate-limit.md`): the problem (unthrottled partner API calls), that `may_submit_now()` is advisory/opt-in rather than enforced inside `to_partner_payload`, and that nothing in the repo calls it yet.
- **ADR** (`docs/engineering/decisions/partner-settlement-rate-limit.md`): why a sliding-window log was chosen over a fixed window (avoids boundary double-bursting) or a token bucket (fewer parameters to justify).
- Code comments referencing the ADR at the two genuinely non-obvious points: the `BURST_LIMIT`/`WINDOW_SECONDS` constants, and the "advisory, not enforced" contract of `may_submit_now()`.
- Verified via `engineering verify` (unit tests pass) and `engineering check --mode advise` (PASS).

**One thing I deliberately didn't invent:** I don't know why `BURST_LIMIT = 7` and `WINDOW_SECONDS = 1.0` specifically — there's no partner API doc, incident, or prior conversation in this repo backing those numbers. Rather than writing a plausible-sounding justification into a permanent decision record, I recorded it as an open gap (`understanding=gaps`, revisit 2026-08-09) so a future reader sees it's unconfirmed instead of trusting a fabricated rationale. If you know the actual source, tell me and I'll update the ADR.

**Separate finding from restoring context:** the existing `partner-settlement-rounding` change (same file, unrelated to this feature) is still open, past its revisit date, and its Brief claims the adapter "converts amounts once, at the boundary" — but the current code still passes `amount_cents` straight through with no conversion. That looks like the implementation was never finished against its own documented intent. I didn't touch it since it's outside what you asked for, but it's worth knowing before this ships.