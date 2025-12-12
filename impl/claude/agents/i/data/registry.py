"""
Agent Registry - Connect I-gent to Real Agents.

The registry provides a unified interface to discover and observe
running agents in the kgents ecosystem.

The registry is designed to be pluggable:
- MemoryRegistry: In-memory registry for testing/demo
- (Future) K8sRegistry: Discover agents via Kubernetes API
- (Future) ProcessRegistry: Discover local agent processes
"""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Protocol, runtime_checkable

from .types import Phase


class AgentStatus(Enum):
    """Status of an agent in the registry."""

    UNKNOWN = "UNKNOWN"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


@runtime_checkable
class AgentObservable(Protocol):
    """
    Protocol for observable agents.

    Any agent that can be observed by I-gent must implement this protocol.
    This matches the spec from plans/self/interface.md.
    """

    @property
    def id(self) -> str:
        """Unique identifier for the agent."""
        ...

    @property
    def name(self) -> str:
        """Human-readable name."""
        ...

    @property
    def phase(self) -> Phase:
        """Current lifecycle phase."""
        ...

    @property
    def children(self) -> list[str]:
        """IDs of child agents."""
        ...

    def summary(self) -> str:
        """Brief status summary."""
        ...

    async def metrics(self) -> dict[str, Any]:
        """Get detailed metrics for WIRE mode."""
        ...

    async def activity_level(self) -> float:
        """Get current activity level (0.0-1.0)."""
        ...


@dataclass
class RegisteredAgent:
    """
    An agent registered with the registry.

    Contains both static metadata and a reference to the observable.
    """

    id: str
    name: str
    agent_type: str  # e.g., "g-gent", "robin", "summarizer"
    status: AgentStatus = AgentStatus.UNKNOWN
    observable: AgentObservable | None = None

    # Grid position (optional, for persistence)
    grid_x: int = 0
    grid_y: int = 0

    # Timestamps
    registered_at: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)

    # Connections to other agents (id -> connection type)
    connections: dict[str, str] = field(default_factory=dict)

    # Cached values (updated by polling)
    cached_phase: Phase = Phase.DORMANT
    cached_activity: float = 0.0
    cached_summary: str = ""


# Event types for registry changes
class RegistryEventType(Enum):
    """Types of registry events."""

    AGENT_REGISTERED = "AGENT_REGISTERED"
    AGENT_UNREGISTERED = "AGENT_UNREGISTERED"
    AGENT_UPDATED = "AGENT_UPDATED"
    AGENT_STATUS_CHANGED = "AGENT_STATUS_CHANGED"


@dataclass
class RegistryEvent:
    """Event emitted when registry changes."""

    event_type: RegistryEventType
    agent_id: str
    agent: RegisteredAgent | None = None
    old_status: AgentStatus | None = None
    new_status: AgentStatus | None = None
    timestamp: datetime = field(default_factory=datetime.now)


# Callback type for registry events
RegistryCallback = Callable[[RegistryEvent], None]


class AgentRegistry(ABC):
    """
    Abstract base for agent registries.

    Provides discovery and observation capabilities for agents.
    """

    def __init__(self) -> None:
        self._callbacks: list[RegistryCallback] = []

    @abstractmethod
    async def discover(self) -> list[RegisteredAgent]:
        """
        Discover all available agents.

        Returns a list of currently discoverable agents.
        """
        ...

    @abstractmethod
    async def get_agent(self, agent_id: str) -> RegisteredAgent | None:
        """Get a specific agent by ID."""
        ...

    @abstractmethod
    async def register(self, agent: RegisteredAgent) -> None:
        """Register an agent with the registry."""
        ...

    @abstractmethod
    async def unregister(self, agent_id: str) -> None:
        """Remove an agent from the registry."""
        ...

    @abstractmethod
    async def update_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update an agent's status."""
        ...

    def subscribe(self, callback: RegistryCallback) -> None:
        """Subscribe to registry events."""
        self._callbacks.append(callback)

    def unsubscribe(self, callback: RegistryCallback) -> None:
        """Unsubscribe from registry events."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _emit(self, event: RegistryEvent) -> None:
        """Emit an event to all subscribers."""
        for callback in self._callbacks:
            try:
                callback(event)
            except Exception:
                pass  # Don't let one callback break others


class MemoryRegistry(AgentRegistry):
    """
    In-memory agent registry.

    Useful for testing and demo mode.
    """

    def __init__(self) -> None:
        super().__init__()
        self._agents: dict[str, RegisteredAgent] = {}

    async def discover(self) -> list[RegisteredAgent]:
        """Return all registered agents."""
        return list(self._agents.values())

    async def get_agent(self, agent_id: str) -> RegisteredAgent | None:
        """Get a specific agent by ID."""
        return self._agents.get(agent_id)

    async def register(self, agent: RegisteredAgent) -> None:
        """Register an agent."""
        self._agents[agent.id] = agent
        self._emit(
            RegistryEvent(
                event_type=RegistryEventType.AGENT_REGISTERED,
                agent_id=agent.id,
                agent=agent,
            )
        )

    async def unregister(self, agent_id: str) -> None:
        """Remove an agent."""
        agent = self._agents.pop(agent_id, None)
        if agent:
            self._emit(
                RegistryEvent(
                    event_type=RegistryEventType.AGENT_UNREGISTERED,
                    agent_id=agent_id,
                    agent=agent,
                )
            )

    async def update_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update an agent's status."""
        agent = self._agents.get(agent_id)
        if agent:
            old_status = agent.status
            agent.status = status
            agent.last_seen = datetime.now()
            self._emit(
                RegistryEvent(
                    event_type=RegistryEventType.AGENT_STATUS_CHANGED,
                    agent_id=agent_id,
                    agent=agent,
                    old_status=old_status,
                    new_status=status,
                )
            )

    async def update_cached_values(
        self,
        agent_id: str,
        *,
        phase: Phase | None = None,
        activity: float | None = None,
        summary: str | None = None,
    ) -> None:
        """Update cached observation values for an agent."""
        agent = self._agents.get(agent_id)
        if agent:
            if phase is not None:
                agent.cached_phase = phase
            if activity is not None:
                agent.cached_activity = activity
            if summary is not None:
                agent.cached_summary = summary
            agent.last_seen = datetime.now()
            self._emit(
                RegistryEvent(
                    event_type=RegistryEventType.AGENT_UPDATED,
                    agent_id=agent_id,
                    agent=agent,
                )
            )


class MockObservable:
    """
    Mock implementation of AgentObservable for testing.
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        phase: Phase = Phase.DORMANT,
        activity: float = 0.0,
    ) -> None:
        self._id = agent_id
        self._name = name
        self._phase = phase
        self._activity = activity
        self._children: list[str] = []
        self._summary = f"{name} is {phase.value.lower()}"

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def children(self) -> list[str]:
        return self._children

    def summary(self) -> str:
        return self._summary

    async def metrics(self) -> dict[str, Any]:
        return {
            "id": self._id,
            "name": self._name,
            "phase": self._phase.value,
            "activity": self._activity,
        }

    async def activity_level(self) -> float:
        return self._activity

    def set_activity(self, activity: float) -> None:
        """Set activity level (for testing)."""
        self._activity = max(0.0, min(1.0, activity))

    def set_phase(self, phase: Phase) -> None:
        """Set phase (for testing)."""
        self._phase = phase
        self._summary = f"{self._name} is {phase.value.lower()}"


def create_demo_registry() -> MemoryRegistry:
    """
    Create a demo registry with sample agents.

    Matches the demo data from create_demo_flux_state().
    """
    registry = MemoryRegistry()

    # Create demo agents that match the flux demo state
    demo_agents = [
        RegisteredAgent(
            id="g-gent",
            name="Grammar",
            agent_type="grammar",
            status=AgentStatus.RUNNING,
            cached_phase=Phase.ACTIVE,
            cached_activity=0.7,
            grid_x=0,
            grid_y=0,
            cached_summary="Parsing morphisms",
            connections={"robin": "high"},
        ),
        RegisteredAgent(
            id="robin",
            name="Robin",
            agent_type="robin",
            status=AgentStatus.RUNNING,
            cached_phase=Phase.ACTIVE,
            cached_activity=0.9,
            grid_x=2,
            grid_y=1,
            cached_summary="Hypothesis synthesis",
            connections={"summarizer": "medium", "j-gent": "low"},
        ),
        RegisteredAgent(
            id="j-gent",
            name="J-gent",
            agent_type="lazy",
            status=AgentStatus.RUNNING,
            cached_phase=Phase.WAKING,
            cached_activity=0.3,
            grid_x=4,
            grid_y=0,
            cached_summary="Lazy evaluation",
            connections={},
        ),
        RegisteredAgent(
            id="summarizer",
            name="Summarizer",
            agent_type="summarizer",
            status=AgentStatus.RUNNING,
            cached_phase=Phase.DORMANT,
            cached_activity=0.1,
            grid_x=4,
            grid_y=2,
            cached_summary="Waiting for input",
            connections={},
        ),
        RegisteredAgent(
            id="o-gent",
            name="Observer",
            agent_type="observer",
            status=AgentStatus.RUNNING,
            cached_phase=Phase.ACTIVE,
            cached_activity=0.5,
            grid_x=0,
            grid_y=2,
            cached_summary="Monitoring XYZ",
            connections={"robin": "medium", "g-gent": "low"},
        ),
        RegisteredAgent(
            id="psi-gent",
            name="Psychopomp",
            agent_type="psi",
            status=AgentStatus.RUNNING,
            cached_phase=Phase.WANING,
            cached_activity=0.2,
            grid_x=2,
            grid_y=3,
            cached_summary="Metaphor engine idle",
            connections={},
        ),
    ]

    # Register all agents synchronously for convenience
    for agent in demo_agents:
        # Use direct dict access instead of async
        registry._agents[agent.id] = agent

    return registry


async def create_demo_registry_async() -> MemoryRegistry:
    """Async version of create_demo_registry."""
    registry = create_demo_registry()
    return registry
