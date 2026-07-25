import unittest

from src.api.partner_adapter import to_partner_payload


class PartnerAdapterCase(unittest.TestCase):
    def test_payload_carries_the_order_identifier(self):
        payload = to_partner_payload(
            {"id": "o-1", "partner_id": "p-1", "amount_cents": 500, "created_at": "2026-01-01"}
        )
        self.assertEqual(payload["orderId"], "o-1")
