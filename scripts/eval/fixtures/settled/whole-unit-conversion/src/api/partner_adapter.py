"""Adapter for the partner settlement API."""

WHOLE_UNIT_PARTNERS = frozenset({"p-1", "p-7"})


def _to_whole_units(amount_cents: int) -> int:
    # Round half up. Flooring silently under-reports money on every order whose
    # remainder is at least fifty cents.
    return (amount_cents + 50) // 100


def to_partner_payload(order: dict) -> dict:
    amount = order["amount_cents"]
    if order["partner_id"] in WHOLE_UNIT_PARTNERS:
        amount = _to_whole_units(amount)
    return {
        "orderId": order["id"],
        "partner": order["partner_id"],
        "amount": amount,
    }
