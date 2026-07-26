import unittest
from datetime import datetime, timedelta, timezone

from src.auth.session import is_refresh_valid, issue_refresh_token, revoke


class SessionCase(unittest.TestCase):
    def test_a_fresh_token_is_valid(self):
        issued = datetime.now(timezone.utc)
        self.assertTrue(is_refresh_valid(issue_refresh_token(), issued))

    def test_an_expired_token_is_rejected(self):
        issued = datetime.now(timezone.utc) - timedelta(days=91)
        self.assertFalse(is_refresh_valid(issue_refresh_token(), issued))

    def test_a_revoked_token_is_rejected(self):
        token = issue_refresh_token()
        revoke(token)
        self.assertFalse(is_refresh_valid(token, datetime.now(timezone.utc)))
