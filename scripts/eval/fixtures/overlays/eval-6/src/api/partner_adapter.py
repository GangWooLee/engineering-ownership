"""Adapter for the partner settlement API."""

WHOLE_UNIT_PARTNERS = frozenset({"p-1", "p-7"})


def to_partner_payload(order: dict) -> dict:
    amount = order["amount_cents"]
    if order["partner_id"] in WHOLE_UNIT_PARTNERS:
        # TODO: partners that settle in fractional units still need a rule.
        amount = amount // 100
    return {
        "orderId": order["id"],
        "partner": order["partner_id"],
        "amount": amount,
        "settlementCurrency": order.get("settlement_currency", "USD"),
    }
