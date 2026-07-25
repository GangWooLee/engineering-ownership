"""Adapter for the partner settlement API."""

from src.api.rate_limit import RateLimiter

_limiter = RateLimiter()


def to_partner_payload(order: dict) -> dict:
    return {
        "orderId": order["id"],
        "partner": order["partner_id"],
        "amount": order["amount_cents"],
    }


def may_submit_now() -> bool:
    return _limiter.allow()
