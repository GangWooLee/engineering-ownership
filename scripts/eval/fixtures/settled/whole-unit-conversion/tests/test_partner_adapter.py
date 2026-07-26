import unittest

from src.api.partner_adapter import to_partner_payload


def order(amount_cents: int, partner_id: str = "p-1") -> dict:
    return {
        "id": "o-1",
        "partner_id": partner_id,
        "amount_cents": amount_cents,
        "created_at": "2026-01-01",
    }


class PartnerAdapterCase(unittest.TestCase):
    def test_payload_carries_the_order_identifier(self):
        self.assertEqual(to_partner_payload(order(500))["orderId"], "o-1")

    def test_whole_unit_partners_receive_rounded_units(self):
        self.assertEqual(to_partner_payload(order(549))["amount"], 5)
        self.assertEqual(to_partner_payload(order(550))["amount"], 6)

    def test_other_partners_receive_cents_unchanged(self):
        self.assertEqual(to_partner_payload(order(549, "p-9"))["amount"], 549)
