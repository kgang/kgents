"""
RetryPolicy: Exponential backoff with jitter.

Configures retry behavior for stream reconnection:
- Base delay with exponential backoff
- Maximum delay cap
- Jitter to prevent thundering herd
- Retry conditions per error type

Example:
    policy = RetryPolicy(
        max_retries=5,
        base_delay_ms=1000,
        backoff_multiplier=2.0,
    )
    delay = policy.compute_delay(attempt=2)  # ~4000ms + jitter
"""

from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    """
    Exponential backoff retry configuration.

    Formula:
        delay = min(max_delay, base_delay * (backoff ^ attempt) + jitter)

    Attributes:
        max_retries: Maximum retry attempts
        base_delay_ms: Initial delay in milliseconds
        max_delay_ms: Maximum delay cap
        backoff_multiplier: Exponential multiplier (typically 2.0)
        jitter_ratio: Randomization range (+/- this ratio)
        retry_on_timeout: Retry timeout errors
        retry_on_network_error: Retry network errors
        retry_on_server_error: Retry 5xx errors
        retry_on_client_error: Retry 4xx errors (usually False)
    """

    max_retries: int = 5
    base_delay_ms: float = 1000.0  # 1 second
    max_delay_ms: float = 30000.0  # 30 seconds
    backoff_multiplier: float = 2.0
    jitter_ratio: float = 0.2  # +/- 20%

    # Retry conditions
    retry_on_timeout: bool = True
    retry_on_network_error: bool = True
    retry_on_server_error: bool = True
    retry_on_client_error: bool = False

    def compute_delay(self, attempt: int) -> float:
        """
        Compute delay for given attempt number.

        Args:
            attempt: Zero-indexed attempt number

        Returns:
            Delay in milliseconds with jitter applied
        """
        if attempt < 0:
            attempt = 0

        # Base exponential delay
        base = self.base_delay_ms * (self.backoff_multiplier**attempt)

        # Cap at maximum
        capped = min(base, self.max_delay_ms)

        # Add jitter
        jitter_range = capped * self.jitter_ratio
        jitter = random.uniform(-jitter_range, jitter_range)

        return max(0, capped + jitter)

    def compute_delay_seconds(self, attempt: int) -> float:
        """Compute delay in seconds."""
        return self.compute_delay(attempt) / 1000.0

    def should_retry(
        self,
        attempt: int,
        error_category: str | None = None,
    ) -> bool:
        """
        Determine if retry should be attempted.

        Args:
            attempt: Current attempt number (0-indexed)
            error_category: Error category from ErrorInfo

        Returns:
            True if retry should be attempted
        """
        # Check attempt count
        if attempt >= self.max_retries:
            return False

        # Check error category if provided
        if error_category:
            match error_category:
                case "timeout":
                    return self.retry_on_timeout
                case "network":
                    return self.retry_on_network_error
                case "permission" | "notFound" | "validation":
                    return self.retry_on_client_error
                case "unknown":
                    return self.retry_on_server_error
                case _:
                    return False

        return True

    def get_retry_schedule(self) -> list[float]:
        """
        Get full retry schedule in milliseconds.

        Returns list of delays for each retry attempt.
        Useful for displaying retry countdown.
        """
        return [self.compute_delay(i) for i in range(self.max_retries)]


# Preset policies
AGGRESSIVE_RETRY = RetryPolicy(
    max_retries=10,
    base_delay_ms=500,
    max_delay_ms=10000,
    backoff_multiplier=1.5,
)

CONSERVATIVE_RETRY = RetryPolicy(
    max_retries=3,
    base_delay_ms=2000,
    max_delay_ms=60000,
    backoff_multiplier=3.0,
)

NO_RETRY = RetryPolicy(max_retries=0)


__all__ = [
    "RetryPolicy",
    "AGGRESSIVE_RETRY",
    "CONSERVATIVE_RETRY",
    "NO_RETRY",
]
