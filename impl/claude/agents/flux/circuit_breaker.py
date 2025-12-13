"""
Circuit Breaker for Synapse target operations.

Prevents cascade failures by opening the circuit when a target
(Qdrant, Redis) fails repeatedly. While open, calls fail fast
without attempting the operation.

State Machine:
    CLOSED -> OPEN: failure_count >= threshold
    OPEN -> HALF_OPEN: recovery_timeout elapsed
    HALF_OPEN -> CLOSED: successful call
    HALF_OPEN -> OPEN: another failure

Categorical Role: The circuit breaker is a natural transformation
that augments operations with failure-aware behavior.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitOpenError(Exception):
    """Raised when circuit is open and call is rejected."""

    def __init__(self, name: str, time_until_retry: float) -> None:
        self.name = name
        self.time_until_retry = time_until_retry
        super().__init__(f"Circuit '{name}' is open. Retry in {time_until_retry:.1f}s")


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""

    failure_threshold: int = 5  # Failures before opening
    recovery_timeout: float = 30.0  # Seconds before half-open
    success_threshold: int = 1  # Successes to close from half-open


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for protecting Synapse targets.

    When a target (Qdrant, embedding provider) fails repeatedly,
    the circuit opens to:
    1. Stop wasting resources on failing calls
    2. Allow the target to recover
    3. Queue events for later processing

    Usage:
        breaker = CircuitBreaker("qdrant")
        try:
            result = await breaker.call(qdrant.upsert, collection, id, vector)
        except CircuitOpenError:
            # Send to DLQ
            pass
    """

    name: str
    config: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _success_count: int = field(default=0, init=False)
    _last_failure_time: float = field(default=0.0, init=False)
    _last_state_change: float = field(default_factory=time.monotonic, init=False)

    @property
    def state(self) -> CircuitState:
        """Current circuit state."""
        return self._state

    @property
    def is_closed(self) -> bool:
        """True if circuit is closed (normal operation)."""
        return self._state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        """True if circuit is open (failing fast)."""
        return self._state == CircuitState.OPEN

    @property
    def is_half_open(self) -> bool:
        """True if circuit is half-open (testing recovery)."""
        return self._state == CircuitState.HALF_OPEN

    @property
    def time_in_state(self) -> float:
        """Seconds since last state change."""
        return time.monotonic() - self._last_state_change

    @property
    def time_until_retry(self) -> float:
        """Seconds until circuit will attempt half-open."""
        if self._state != CircuitState.OPEN:
            return 0.0
        elapsed = time.monotonic() - self._last_failure_time
        return max(0.0, self.config.recovery_timeout - elapsed)

    async def call(
        self,
        fn: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute function through circuit breaker.

        Raises CircuitOpenError if circuit is open and timeout not elapsed.
        """
        self._check_state_transition()

        if self._state == CircuitState.OPEN:
            raise CircuitOpenError(self.name, self.time_until_retry)

        try:
            result = await fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def call_sync(
        self,
        fn: Callable[..., T],
        *args: Any,
        **kwargs: Any,
    ) -> T:
        """Synchronous version of call."""
        self._check_state_transition()

        if self._state == CircuitState.OPEN:
            raise CircuitOpenError(self.name, self.time_until_retry)

        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _check_state_transition(self) -> None:
        """Check if state should transition based on time."""
        if self._state == CircuitState.OPEN:
            elapsed = time.monotonic() - self._last_failure_time
            if elapsed >= self.config.recovery_timeout:
                self._transition_to(CircuitState.HALF_OPEN)

    def _on_success(self) -> None:
        """Handle successful call."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)
        else:
            # Reset failure count on success in closed state
            self._failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed call."""
        self._failure_count += 1
        self._last_failure_time = time.monotonic()

        if self._state == CircuitState.HALF_OPEN:
            # Any failure in half-open reopens
            self._transition_to(CircuitState.OPEN)
        elif self._state == CircuitState.CLOSED:
            if self._failure_count >= self.config.failure_threshold:
                self._transition_to(CircuitState.OPEN)

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        self._state = new_state
        self._last_state_change = time.monotonic()

        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._success_count = 0

    def force_open(self) -> None:
        """Manually open the circuit (for testing/emergencies)."""
        self._transition_to(CircuitState.OPEN)
        self._last_failure_time = time.monotonic()

    def force_close(self) -> None:
        """Manually close the circuit (for testing/recovery)."""
        self._transition_to(CircuitState.CLOSED)

    def reset(self) -> None:
        """Reset to initial closed state."""
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._last_state_change = time.monotonic()

    def stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self._state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "time_in_state": self.time_in_state,
            "time_until_retry": self.time_until_retry,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold,
            },
        }


# ===========================================================================
# Factory for common circuit breakers
# ===========================================================================


def create_qdrant_breaker(
    failure_threshold: int = 5,
    recovery_timeout: float = 30.0,
) -> CircuitBreaker:
    """Create a circuit breaker for Qdrant operations."""
    return CircuitBreaker(
        name="qdrant",
        config=CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        ),
    )


def create_embedding_breaker(
    failure_threshold: int = 3,
    recovery_timeout: float = 60.0,
) -> CircuitBreaker:
    """Create a circuit breaker for embedding provider."""
    return CircuitBreaker(
        name="embedding",
        config=CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        ),
    )
