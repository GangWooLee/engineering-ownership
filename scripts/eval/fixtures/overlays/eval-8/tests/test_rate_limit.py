import unittest

from src.api.rate_limit import BURST_LIMIT, RateLimiter


class RateLimiterCase(unittest.TestCase):
    def test_allows_up_to_the_burst(self):
        limiter = RateLimiter()
        self.assertTrue(all(limiter.allow(now=0.0) for _ in range(BURST_LIMIT)))

    def test_refuses_beyond_the_burst(self):
        limiter = RateLimiter()
        for _ in range(BURST_LIMIT):
            limiter.allow(now=0.0)
        self.assertFalse(limiter.allow(now=0.5))

    def test_recovers_after_the_window(self):
        limiter = RateLimiter()
        for _ in range(BURST_LIMIT):
            limiter.allow(now=0.0)
        self.assertTrue(limiter.allow(now=1.1))
