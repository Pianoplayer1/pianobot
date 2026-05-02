"""Exception hierarchy for `WynncraftClient` failures."""


class WynncraftError(Exception):
    """Base error for the Wynncraft API client."""


class NotFoundError(WynncraftError):
    """404 from the Wynncraft API."""


class RateLimitedError(WynncraftError):
    """429 from the Wynncraft API after retries exhausted."""

    def __init__(self, retry_after: float) -> None:
        """Record `retry_after` seconds from the response header."""
        super().__init__(f"Rate limited; retry after {retry_after:.1f}s")
        self.retry_after = retry_after
