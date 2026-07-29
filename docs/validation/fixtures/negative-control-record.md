# Negative control — not a real change record

This file is a fixture for validating `docs/validation/record-quality-rubric.md`.
It documents no real work. It exists to answer a question two independent judges
could previously only answer by speculation: **what would a clearly bad record
also pass?**

It is written to game three specific leniencies the judges named — a non-goals
list made entirely of features not built, a verification claim phrased as a
success criterion that was never run, and preferences with a `because` clause
carrying neither evidence nor a boundary. It deliberately does *not* game D3:
every identifier is glossed where it appears, so a D3 pass isolates the other
three dimensions rather than confounding them.

If a judge passes the sections below on D1, D2, or D4, that dimension is
confirmed lenient by demonstration rather than by argument.

---

## Success and non-goals

Success: the retry policy is applied consistently across the request layer, the
full suite passes, and the configuration remains backward compatible.

Non-goals: a circuit breaker, per-endpoint overrides, a metrics dashboard, and
migration of the legacy client. Those are deferred to a later change.

## Existing responsibilities searched

The request layer already had two places that retried: `HttpSender.send`, which
is the single function every outbound call passes through, and
`LegacyClient.post`, a older path kept for one integration. The new policy is
applied in `HttpSender.send` so that both eventually share it. `RetryPolicy` is
the small object holding the attempt count and the backoff base.

## System and data flow

A caller invokes `HttpSender.send`, which reads a `RetryPolicy` — the object
described above — from the injected configuration and applies it around the
transport call. On a retryable status the sender waits for the backoff interval
and repeats up to the configured attempt count. Nothing else in the path
changes: the transport, the serializer, and the caller's interface are all as
they were.

## Failure, security, and recovery

If the policy is misconfigured the sender falls back to a single attempt, which
is the previous behaviour. Rolling back is reverting this change; no data is
migrated in either direction, so there is nothing to undo beyond the code.

## Known limits and learning gaps

`LegacyClient.post` still has its own retry loop and is not covered here,
because unifying it would widen the change. Backoff is fixed rather than
jittered, because jitter adds a dependency we prefer to avoid. Attempt counts
are global rather than per-endpoint, because per-endpoint configuration is more
surface than this change needs.
