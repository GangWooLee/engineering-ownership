"""Outbound rate limiting for partner settlement submissions."""

import time
from collections import deque

BURST_LIMIT = 7
WINDOW_SECONDS = 1.0


class RateLimiter:
    def __init__(self, burst: int = BURST_LIMIT, window: float = WINDOW_SECONDS) -> None:
        self._burst = burst
        self._window = window
        self._sent: deque[float] = deque()

    def _drop_expired(self, now: float) -> None:
        while self._sent and now - self._sent[0] >= self._window:
            self._sent.popleft()

    def allow(self, now: float | None = None) -> bool:
        moment = time.monotonic() if now is None else now
        self._drop_expired(moment)
        if len(self._sent) >= self._burst:
            return False
        self._sent.append(moment)
        return True

    def wait_time(self, now: float | None = None) -> float:
        moment = time.monotonic() if now is None else now
        self._drop_expired(moment)
        if len(self._sent) < self._burst:
            return 0.0
        return self._window - (moment - self._sent[0])
