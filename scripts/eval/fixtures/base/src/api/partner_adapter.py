"""Adapter for the partner settlement API."""


def to_partner_payload(order: dict) -> dict:
    return {
        "orderId": order["id"],
        "partner": order["partner_id"],
        "amount": order["amount_cents"],
    }
