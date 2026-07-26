# Proposal: carry settlement currency on the order

Author: platform team. Status: agreed in review, 2026-07-20.

## Why

Two partners onboarding this quarter settle in currencies other than USD. Today
the currency is implied by the partner and hard-coded at the reporting layer,
which is already wrong for one existing partner and is being worked around by
hand each month.

## What we agreed

Store the settlement currency on the order rather than deriving it. The adapter
sends it with the payload; reporting reads it from the row instead of a lookup
table.

## What we considered and rejected

A per-partner currency table was rejected: currency is a property of the
agreement in force when the order was placed, not of the partner today, and a
table loses that once an agreement changes.

## Scope

Order storage, the settlement payload, and the reporting read path. Historic
rows are backfilled to USD, which is correct for every order placed so far.
