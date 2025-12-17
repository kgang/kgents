"""
Metrics emission for I-gent widget visualization.

Provides real-time agent metabolism metrics through the HolographicBuffer,
enabling live dashboard visualization of running FluxAgents.

The Insight:
    TerriumEvent already carries pressure/flow/temperature.
    This module provides the loop that periodically polls FluxAgents
    and emits metrics to observers via the Mirror Protocol.

Metrics:
    - pressure: Queue depth (backlog) as 0-100 scale
    - flow: Throughput (events processed over time window)
    - temperature: Metabolic heat (entropy consumption rate)

Usage:
    >>> from protocols.terrarium.metrics import MetricsManager
    >>>
    >>> manager = MetricsManager()
    >>> manager.start_metrics(agent_id, flux_agent, buffer)
    >>>
    >>> # Later:
    >>> manager.stop_metrics(agent_id)
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from .events import EventType, TerriumEvent, make_metabolism_event
from .mirror import HolographicBuffer

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from agents.flux import FluxAgent


# ─────────────────────────────────────────────────────────────
# Circuit Breaker for Metrics Polling
# ─────────────────────────────────────────────────────────────


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation, metrics flowing
    OPEN = "open"  # Metrics failing, circuit tripped
    HALF_OPEN = "half_open"  # Testing if metrics recovered


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for metrics polling.

    When metrics collection repeatedly fails, the circuit opens
    to prevent cascading failures and alert operators.

    State transitions:
        CLOSED -> OPEN: failure_count >= failure_threshold
        OPEN -> HALF_OPEN: recovery_timeout elapsed
        HALF_OPEN -> CLOSED: successful metrics poll
        HALF_OPEN -> OPEN: another failure
    """

    failure_threshold: int = 5
    """Number of consecutive failures before opening circuit."""

    recovery_timeout: float = 30.0
    """Seconds to wait in OPEN state before trying HALF_OPEN."""

    degraded_threshold: int = 3
    """Failures before emitting degradation warning (< failure_threshold)."""

    # Internal state
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _last_failure_time: float = field(default=0.0, init=False)
    _total_failures: int = field(default=0, init=False)
    _degraded_since: float | None = field(default=None, init=False)

    @property
    def state(self) -> CircuitState:
        """Current circuit state."""
        # Check if we should transition from OPEN to HALF_OPEN
        if self._state == CircuitState.OPEN:
            time_since_failure = time.monotonic() - self._last_failure_time
            if time_since_failure >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker half-open: attempting recovery")
        return self._state

    @property
    def is_open(self) -> bool:
        """True if circuit is open (metrics failing)."""
        return self.state == CircuitState.OPEN

    @property
    def is_degraded(self) -> bool:
        """True if metrics are degraded but not yet failed."""
        return self._failure_count >= self.degraded_threshold

    def record_success(self) -> None:
        """Record successful metrics poll."""
        if self._state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker closed: metrics recovered")
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._degraded_since = None

    def record_failure(self, error: Exception | None = None) -> bool:
        """
        Record failed metrics poll.

        Args:
            error: Optional exception that caused the failure

        Returns:
            True if circuit just opened (threshold reached)
        """
        self._failure_count += 1
        self._total_failures += 1
        self._last_failure_time = time.monotonic()

        # Track degradation start
        if self._failure_count == self.degraded_threshold:
            self._degraded_since = time.monotonic()
            logger.warning(
                f"Metrics degraded: {self._failure_count} consecutive failures. "
                f"Error: {error}"
            )

        # Check threshold
        if self._failure_count >= self.failure_threshold:
            if self._state != CircuitState.OPEN:
                self._state = CircuitState.OPEN
                logger.error(
                    f"Circuit breaker OPEN: {self._failure_count} consecutive failures. "
                    f"Metrics polling suspended for {self.recovery_timeout}s"
                )
                return True

        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            logger.warning("Circuit breaker re-opened: recovery failed")

        return False

    def get_health(self) -> dict[str, Any]:
        """Get circuit breaker health status."""
        return {
            "state": self.state.value,
            "failure_count": self._failure_count,
            "total_failures": self._total_failures,
            "is_degraded": self.is_degraded,
            "degraded_since": self._degraded_since,
        }


# ─────────────────────────────────────────────────────────────
# Metric Calculations
# ─────────────────────────────────────────────────────────────


def calculate_pressure(
    flux_agent: "FluxAgent[Any, Any]",
) -> tuple[float, Exception | None]:
    """
    Calculate queue pressure (backlog) as 0-100 scale.

    Pressure = how backed up is the agent's input queue?

    Higher pressure means the agent has more work queued
    than it can process. This is calculated from:
    - Perturbation queue depth
    - Output queue fullness

    Args:
        flux_agent: The FluxAgent to poll

    Returns:
        Tuple of (pressure value 0-100, error if any)
    """
    try:
        # Get queue sizes
        perturbation_size = flux_agent._perturbation_queue.qsize()
        output_size = flux_agent._output_queue.qsize()
        buffer_size = flux_agent.config.buffer_size

        # Normalize: pressure is output queue fullness + perturbation backlog
        output_pressure = (output_size / buffer_size) * 50 if buffer_size > 0 else 0

        # Perturbations are high priority, so weight them more
        # Assume a reasonable max perturbation queue size of 10
        perturbation_pressure = min(perturbation_size / 10, 1.0) * 50

        return (min(output_pressure + perturbation_pressure, 100.0), None)
    except Exception as e:
        logger.debug("calculate_pressure failed (agent may be stopping): %s", e)
        return (0.0, e)


def calculate_flow(
    flux_agent: "FluxAgent[Any, Any]",
    previous_count: int,
    time_delta: float,
) -> tuple[float, int, Exception | None]:
    """
    Calculate throughput (events/second).

    Flow = how fast is work moving through?

    Args:
        flux_agent: The FluxAgent to poll
        previous_count: Events processed at previous check
        time_delta: Time since previous check in seconds

    Returns:
        Tuple of (events per second, current count, error if any)
    """
    if time_delta <= 0:
        return (0.0, previous_count, None)

    try:
        current_count = flux_agent.events_processed
        events_delta = current_count - previous_count
        return (max(events_delta / time_delta, 0.0), current_count, None)
    except Exception as e:
        logger.debug("calculate_flow failed: %s", e)
        return (0.0, previous_count, e)


def calculate_temperature(
    flux_agent: "FluxAgent[Any, Any]",
) -> tuple[float, Exception | None]:
    """
    Calculate metabolic heat (entropy consumption rate).

    Temperature = how hard is the agent working?
    High temperature = high entropy consumption, complex processing.

    This is derived from:
    - Entropy budget consumption rate
    - Metabolism temperature if attached

    Returns value from 0-1 scale (normalized heat).

    Args:
        flux_agent: The FluxAgent to poll

    Returns:
        Tuple of (temperature value 0-1, error if any)
    """
    try:
        # Check if metabolism is attached
        if flux_agent.metabolism is not None:
            # Use metabolic temperature directly
            return (min(flux_agent.metabolism.temperature, 1.0), None)

        # Otherwise, derive from entropy consumption
        budget = flux_agent.config.entropy_budget
        remaining = flux_agent.entropy_remaining

        if budget <= 0:
            return (0.0, None)

        # Temperature is how much entropy has been consumed
        consumed_ratio = (budget - remaining) / budget
        return (min(max(consumed_ratio, 0.0), 1.0), None)
    except Exception as e:
        logger.debug("calculate_temperature failed (agent may be stopping): %s", e)
        return (0.0, e)


# ─────────────────────────────────────────────────────────────
# Metrics Loop
# ─────────────────────────────────────────────────────────────


async def emit_metrics_loop(
    agent_id: str,
    flux_agent: "FluxAgent[Any, Any]",
    buffer: HolographicBuffer,
    interval: float = 1.0,
    circuit_breaker: CircuitBreaker | None = None,
) -> None:
    """
    Periodically emit metabolism metrics.

    Runs until the FluxAgent stops. Called when an agent is registered
    with the Terrarium if metrics emission is enabled.

    Args:
        agent_id: Unique identifier for the agent
        flux_agent: The FluxAgent to poll for metrics
        buffer: HolographicBuffer to emit events to
        interval: Polling interval in seconds
        circuit_breaker: Optional circuit breaker for failure handling
    """
    # Use provided circuit breaker or create default
    cb = circuit_breaker or CircuitBreaker()

    previous_count = flux_agent.events_processed
    previous_time = time.monotonic()

    while flux_agent.is_running:
        current_time = time.monotonic()
        time_delta = current_time - previous_time

        # Skip polling if circuit is open
        if cb.is_open:
            await asyncio.sleep(interval)
            continue

        # Calculate metrics with error tracking
        pressure, pressure_err = calculate_pressure(flux_agent)
        flow, previous_count, flow_err = calculate_flow(
            flux_agent, previous_count, time_delta
        )
        temperature, temp_err = calculate_temperature(flux_agent)

        # Check for errors
        first_error = pressure_err or flow_err or temp_err
        if first_error:
            circuit_opened = cb.record_failure(first_error)
            if circuit_opened:
                # Emit circuit open event
                alert_event = TerriumEvent(
                    event_type=EventType.METRICS_DEGRADED,
                    agent_id=agent_id,
                    state=flux_agent.state.value,
                    data={
                        "error": str(first_error),
                        "circuit_state": cb.state.value,
                        "failure_count": cb._failure_count,
                    },
                )
                await buffer.reflect(alert_event.as_dict())
        else:
            cb.record_success()

        # Create and emit event (with degraded flag if applicable)
        event = make_metabolism_event(
            agent_id=agent_id,
            pressure=pressure,
            flow=flow,
            temperature=temperature,
            state=flux_agent.state.value,
        )

        # Add circuit breaker health to event data
        event_dict = event.as_dict()
        if cb.is_degraded:
            event_dict["data"]["metrics_degraded"] = True
            event_dict["data"]["failure_count"] = cb._failure_count

        await buffer.reflect(event_dict)

        # Update tracking
        previous_time = current_time

        await asyncio.sleep(interval)

    # Emit final stopped event
    try:
        final_event = TerriumEvent(
            event_type=EventType.AGENT_STOPPED,
            agent_id=agent_id,
            state=flux_agent.state.value,
            data={
                "total_events": flux_agent.events_processed,
                "entropy_remaining": flux_agent.entropy_remaining,
                "metrics_total_failures": cb._total_failures,
            },
        )
        await buffer.reflect(final_event.as_dict())
    except Exception as e:
        logger.warning(f"Failed to emit final stopped event: {e}")


# ─────────────────────────────────────────────────────────────
# Metrics Manager
# ─────────────────────────────────────────────────────────────


@dataclass
class MetricsManager:
    """
    Manages metrics emission for registered agents.

    Thin manager that tracks metrics emission tasks per agent.
    Automatically cleans up when agents are unregistered.
    Includes circuit breakers for resilient metrics collection.

    Usage:
        >>> manager = MetricsManager()
        >>> manager.start_metrics("agent-1", flux_agent, buffer)
        >>> # ... later ...
        >>> manager.stop_metrics("agent-1")
        >>> # Or stop all:
        >>> manager.stop_all()
    """

    default_interval: float = 1.0
    """Default metrics emission interval in seconds."""

    _tasks: dict[str, asyncio.Task[None]] = field(default_factory=dict, init=False)
    """Active metrics emission tasks by agent_id."""

    _circuit_breakers: dict[str, CircuitBreaker] = field(
        default_factory=dict, init=False
    )
    """Circuit breakers per agent."""

    _last_metrics: dict[str, dict[str, float]] = field(default_factory=dict, init=False)
    """Cache of last emitted metrics per agent."""

    def start_metrics(
        self,
        agent_id: str,
        flux_agent: "FluxAgent[Any, Any]",
        buffer: HolographicBuffer,
        interval: float | None = None,
    ) -> bool:
        """
        Start emitting metrics for an agent.

        Args:
            agent_id: Unique identifier for the agent
            flux_agent: The FluxAgent to poll for metrics
            buffer: HolographicBuffer to emit events to
            interval: Polling interval (uses default if None)

        Returns:
            True if started, False if already running
        """
        if agent_id in self._tasks:
            return False  # Already running

        actual_interval = interval if interval is not None else self.default_interval

        # Create dedicated circuit breaker for this agent
        cb = CircuitBreaker()
        self._circuit_breakers[agent_id] = cb

        task = asyncio.create_task(
            emit_metrics_loop(agent_id, flux_agent, buffer, actual_interval, cb),
            name=f"metrics-{agent_id}",
        )
        self._tasks[agent_id] = task

        # Track initial metrics
        self._last_metrics[agent_id] = {
            "pressure": 0.0,
            "flow": 0.0,
            "temperature": 0.0,
        }

        return True

    def stop_metrics(self, agent_id: str) -> bool:
        """
        Stop emitting metrics for an agent.

        Args:
            agent_id: The agent to stop metrics for

        Returns:
            True if stopped, False if not found
        """
        if agent_id not in self._tasks:
            return False

        task = self._tasks.pop(agent_id)
        task.cancel()

        # Clean up circuit breaker and cached metrics
        self._circuit_breakers.pop(agent_id, None)
        self._last_metrics.pop(agent_id, None)

        return True

    def stop_all(self) -> int:
        """
        Stop all metrics emission.

        Returns:
            Number of tasks stopped
        """
        count = len(self._tasks)

        for task in self._tasks.values():
            task.cancel()

        self._tasks.clear()
        self._circuit_breakers.clear()
        self._last_metrics.clear()

        return count

    def get_circuit_breaker_health(self, agent_id: str) -> dict[str, Any] | None:
        """Get circuit breaker health for an agent."""
        cb = self._circuit_breakers.get(agent_id)
        return cb.get_health() if cb else None

    def get_all_circuit_breaker_health(self) -> dict[str, dict[str, Any]]:
        """Get circuit breaker health for all agents."""
        return {aid: cb.get_health() for aid, cb in self._circuit_breakers.items()}

    def is_emitting(self, agent_id: str) -> bool:
        """Check if metrics are being emitted for an agent."""
        return agent_id in self._tasks and not self._tasks[agent_id].done()

    @property
    def active_agents(self) -> list[str]:
        """List of agent IDs with active metrics emission."""
        return [aid for aid, task in self._tasks.items() if not task.done()]

    def get_last_metrics(self, agent_id: str) -> dict[str, float] | None:
        """
        Get the last cached metrics for an agent.

        This is a convenience method for REST endpoints that want
        current metrics without waiting for the next emission.

        Args:
            agent_id: The agent to get metrics for

        Returns:
            Dict with pressure/flow/temperature, or None if not found
        """
        return self._last_metrics.get(agent_id)

    def get_all_metrics(self) -> dict[str, dict[str, float]]:
        """
        Get all cached metrics.

        Returns:
            Dict mapping agent_id to metrics dict
        """
        return dict(self._last_metrics)


# ─────────────────────────────────────────────────────────────
# Fever Alert (Stretch Goal)
# ─────────────────────────────────────────────────────────────


async def emit_fever_alert(
    agent_id: str,
    buffer: HolographicBuffer,
    temperature: float,
    threshold: float = 0.8,
) -> bool:
    """
    Emit a fever event when temperature exceeds threshold.

    This is a helper for implementing fever alerts in I-gent widgets.

    Args:
        agent_id: The agent experiencing fever
        buffer: HolographicBuffer to emit to
        temperature: Current temperature
        threshold: Fever threshold (default 0.8)

    Returns:
        True if fever event was emitted
    """
    if temperature < threshold:
        return False

    event = TerriumEvent(
        event_type=EventType.FEVER,
        agent_id=agent_id,
        temperature=temperature,
        data={
            "threshold": threshold,
            "severity": "high" if temperature > 0.95 else "moderate",
        },
    )
    await buffer.reflect(event.as_dict())

    return True
