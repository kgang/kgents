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
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .events import EventType, TerriumEvent, make_metabolism_event
from .mirror import HolographicBuffer

if TYPE_CHECKING:
    from agents.flux import FluxAgent


# ─────────────────────────────────────────────────────────────
# Metric Calculations
# ─────────────────────────────────────────────────────────────


def calculate_pressure(flux_agent: "FluxAgent[Any, Any]") -> float:
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
        Pressure value from 0-100
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

        return min(output_pressure + perturbation_pressure, 100.0)
    except Exception:
        return 0.0


def calculate_flow(
    flux_agent: "FluxAgent[Any, Any]",
    previous_count: int,
    time_delta: float,
) -> float:
    """
    Calculate throughput (events/second).

    Flow = how fast is work moving through?

    Args:
        flux_agent: The FluxAgent to poll
        previous_count: Events processed at previous check
        time_delta: Time since previous check in seconds

    Returns:
        Events per second
    """
    if time_delta <= 0:
        return 0.0

    current_count = flux_agent.events_processed
    events_delta = current_count - previous_count

    return max(events_delta / time_delta, 0.0)


def calculate_temperature(flux_agent: "FluxAgent[Any, Any]") -> float:
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
        Temperature value from 0-1
    """
    try:
        # Check if metabolism is attached
        if flux_agent.metabolism is not None:
            # Use metabolic temperature directly
            return min(flux_agent.metabolism.temperature, 1.0)

        # Otherwise, derive from entropy consumption
        budget = flux_agent.config.entropy_budget
        remaining = flux_agent.entropy_remaining

        if budget <= 0:
            return 0.0

        # Temperature is how much entropy has been consumed
        consumed_ratio = (budget - remaining) / budget
        return min(max(consumed_ratio, 0.0), 1.0)
    except Exception:
        return 0.0


# ─────────────────────────────────────────────────────────────
# Metrics Loop
# ─────────────────────────────────────────────────────────────


async def emit_metrics_loop(
    agent_id: str,
    flux_agent: "FluxAgent[Any, Any]",
    buffer: HolographicBuffer,
    interval: float = 1.0,
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
    """
    previous_count = flux_agent.events_processed
    previous_time = time.monotonic()

    while flux_agent.is_running:
        current_time = time.monotonic()
        time_delta = current_time - previous_time

        # Calculate metrics
        pressure = calculate_pressure(flux_agent)
        flow = calculate_flow(flux_agent, previous_count, time_delta)
        temperature = calculate_temperature(flux_agent)

        # Create and emit event
        event = make_metabolism_event(
            agent_id=agent_id,
            pressure=pressure,
            flow=flow,
            temperature=temperature,
            state=flux_agent.state.value,
        )
        await buffer.reflect(event.as_dict())

        # Update tracking
        previous_count = flux_agent.events_processed
        previous_time = current_time

        await asyncio.sleep(interval)

    # Emit final stopped event
    final_event = TerriumEvent(
        event_type=EventType.AGENT_STOPPED,
        agent_id=agent_id,
        state=flux_agent.state.value,
        data={
            "total_events": flux_agent.events_processed,
            "entropy_remaining": flux_agent.entropy_remaining,
        },
    )
    await buffer.reflect(final_event.as_dict())


# ─────────────────────────────────────────────────────────────
# Metrics Manager
# ─────────────────────────────────────────────────────────────


@dataclass
class MetricsManager:
    """
    Manages metrics emission for registered agents.

    Thin manager that tracks metrics emission tasks per agent.
    Automatically cleans up when agents are unregistered.

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

        task = asyncio.create_task(
            emit_metrics_loop(agent_id, flux_agent, buffer, actual_interval),
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

        # Clean up cached metrics
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
        self._last_metrics.clear()

        return count

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
