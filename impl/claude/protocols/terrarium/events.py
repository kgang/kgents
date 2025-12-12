"""
Terrarium events for I-gent widget updates.

These events flow through the HolographicBuffer to observers,
providing real-time visibility into agent metabolism.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class EventType(str, Enum):
    """Types of events that flow through the Mirror."""

    # Agent lifecycle events
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    AGENT_STATE_CHANGED = "agent_state_changed"

    # Processing events
    RESULT = "result"
    ERROR = "error"

    # Metabolic events
    METABOLISM = "metabolism"
    FEVER = "fever"
    METRICS_DEGRADED = "metrics_degraded"

    # Purgatory/Semaphore events (Phase 5)
    SEMAPHORE_EJECTED = "semaphore_ejected"
    SEMAPHORE_RESOLVED = "semaphore_resolved"

    # System events
    PING = "ping"
    SNAPSHOT = "snapshot"


@dataclass
class TerriumEvent:
    """
    Event for I-gent widget updates.

    These events provide real-time visibility into agent metabolism,
    enabling the DensityField and other I-gent widgets.

    The Flux Topology metrics:
    - pressure: Queue depth (backlog) - 0-100 scale
    - flow: Throughput (events/second)
    - temperature: Metabolic heat (entropy consumption rate)
    """

    event_type: EventType
    agent_id: str
    data: dict[str, Any] = field(default_factory=dict)

    # Flux Topology metrics (optional)
    state: str | None = None
    pressure: float = 0.0
    flow: float = 0.0
    temperature: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        result: dict[str, Any] = {
            "type": self.event_type.value,
            "agent_id": self.agent_id,
        }

        if self.data:
            result["data"] = self.data

        if self.state is not None:
            result["state"] = self.state

        # Only include metrics if non-zero
        if self.pressure != 0.0:
            result["pressure"] = self.pressure
        if self.flow != 0.0:
            result["flow"] = self.flow
        if self.temperature != 0.0:
            result["temperature"] = self.temperature

        return result


@dataclass
class SemaphoreEvent:
    """
    Event emitted when a semaphore is ejected to Purgatory.

    Phase 5 integration: When FluxAgent detects a SemaphoreToken result,
    it emits this event through the mirror, making Purgatory observable.
    """

    token_id: str
    agent_id: str
    prompt: str
    options: list[str]
    severity: str = "info"
    context: dict[str, Any] = field(default_factory=dict)

    def as_terrium_event(self) -> TerriumEvent:
        """Convert to TerriumEvent for broadcasting."""
        return TerriumEvent(
            event_type=EventType.SEMAPHORE_EJECTED,
            agent_id=self.agent_id,
            data={
                "token_id": self.token_id,
                "prompt": self.prompt,
                "options": self.options,
                "severity": self.severity,
                "context": self.context,
            },
        )


def make_result_event(
    agent_id: str,
    result: Any,
    state: str | None = None,
    pressure: float = 0.0,
    flow: float = 0.0,
    temperature: float = 0.0,
) -> TerriumEvent:
    """Create a result event."""
    return TerriumEvent(
        event_type=EventType.RESULT,
        agent_id=agent_id,
        data={"result": result},
        state=state,
        pressure=pressure,
        flow=flow,
        temperature=temperature,
    )


def make_error_event(
    agent_id: str,
    error: str,
    error_type: str | None = None,
) -> TerriumEvent:
    """Create an error event."""
    data: dict[str, Any] = {"error": error}
    if error_type:
        data["error_type"] = error_type
    return TerriumEvent(
        event_type=EventType.ERROR,
        agent_id=agent_id,
        data=data,
    )


def make_metabolism_event(
    agent_id: str,
    pressure: float,
    flow: float,
    temperature: float,
    state: str,
) -> TerriumEvent:
    """Create a metabolism update event."""
    return TerriumEvent(
        event_type=EventType.METABOLISM,
        agent_id=agent_id,
        state=state,
        pressure=pressure,
        flow=flow,
        temperature=temperature,
    )
