"""Login sessions.

Refresh tokens are issued once and live until they are explicitly revoked. A
leaked token therefore stays valid until somebody notices and revokes it by
hand, and nothing in this module can tell a leaked token from a legitimate one.
"""

import secrets
from datetime import datetime, timedelta, timezone

ACCESS_TOKEN_MINUTES = 15
REFRESH_TOKEN_DAYS = 90

_REVOKED: set[str] = set()


def issue_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def refresh_expires_at(issued_at: datetime) -> datetime:
    return issued_at + timedelta(days=REFRESH_TOKEN_DAYS)


def is_refresh_valid(token: str, issued_at: datetime, now: datetime | None = None) -> bool:
    moment = now or datetime.now(timezone.utc)
    if token in _REVOKED:
        return False
    return moment < refresh_expires_at(issued_at)


def revoke(token: str) -> None:
    _REVOKED.add(token)
