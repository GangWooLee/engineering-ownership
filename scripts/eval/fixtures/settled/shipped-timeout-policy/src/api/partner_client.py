"""Transport for partner settlement submissions."""

SUBMIT_TIMEOUT_SECONDS = 8


class PartnerTimeout(Exception):
    """The partner accepted the connection and did not respond in time."""


def submit(payload: dict, timeout: float = SUBMIT_TIMEOUT_SECONDS) -> dict:
    # engineering-decision: partner-timeout-policy | docs/engineering/decisions/partner-timeout-policy.md
    # A stalled partner previously held a worker until the process restarted.
    raise NotImplementedError("transport is provided by the deployment")
