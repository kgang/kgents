"""
TheWeave - High-level API for Weave operations.

TheWeave provides the AGENTESE-integrated interface to the
underlying TraceMonoid implementation.

AGENTESE Integration:
- self.weave.braid  -> View dependency structure
- self.weave.knot   -> Create synchronization point
- self.weave.thread -> Get single agent's perspective
- self.weave.tip    -> Current growth position
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .dependency import DependencyGraph
from .event import Event, generate_id
from .trace_monoid import TraceMonoid


@dataclass
class TheWeave:
    """
    High-level interface to the Weave system.

    The Weave is concurrent history—unlike linear ContextWindow,
    it captures the braided structure of multi-agent interaction.

    Key Operations:
    - record(): Add an event
    - synchronize(): Create a knot (sync point)
    - thread(): Get single agent's view
    - braid(): Get dependency structure

    Usage:
        weave = TheWeave()

        # Record events
        id_a = await weave.record({"msg": "hello"}, source="agent_a")
        id_b = await weave.record({"msg": "world"}, source="agent_b")

        # Check concurrency
        braid = weave.braid()
        assert braid.are_concurrent(id_a, id_b)

        # Create sync point
        sync_id = await weave.synchronize({"agent_a", "agent_b"})
    """

    monoid: TraceMonoid[Any] = field(default_factory=lambda: TraceMonoid())

    async def record(
        self,
        content: Any,
        source: str,
        depends_on: set[str] | None = None,
        event_id: str | None = None,
    ) -> str:
        """
        Record an event in the Weave.

        Args:
            content: Event payload
            source: Agent that emitted this event
            depends_on: IDs of events this depends on
            event_id: Optional explicit ID

        Returns:
            The event ID
        """
        event: Event[Any] = Event.create(
            content=content,
            source=source,
            event_id=event_id or generate_id(),
            timestamp=time.time(),
        )
        self.monoid.append_mut(event, depends_on)
        return event.id

    async def synchronize(self, agents: set[str]) -> str:
        """
        Create a synchronization point for multiple agents.

        All agents must reach this point before any can proceed.
        This is a "knot" in the Weave.

        Args:
            agents: Agent IDs that must synchronize

        Returns:
            The knot event ID
        """
        # Find latest event from each agent
        latest_events: set[str] = set()
        for agent in agents:
            latest = self.monoid.get_latest_event(source=agent)
            if latest is not None:
                latest_events.add(latest.id)

        if not latest_events:
            # No events yet, create empty knot
            knot = self.monoid.knot(set())
        else:
            knot = self.monoid.knot(latest_events)

        self.monoid.append_mut(knot, latest_events or None)
        return knot.id

    def braid(self) -> DependencyGraph:
        """
        Get the dependency structure (braid) of the Weave.

        Returns a graph showing which events depend on which.
        Concurrent events have no dependency path between them.
        """
        return self.monoid.braid()

    def thread(self, agent: str) -> list[Event[Any]]:
        """
        Get a single agent's thread (perspective).

        Projects the Weave to show only events visible
        to the specified agent.

        Args:
            agent: Agent ID

        Returns:
            Events from that agent's perspective
        """
        return self.monoid.project(agent)

    def tip(self, agent: str | None = None) -> Event[Any] | None:
        """
        Get the current growth point (tip).

        If agent is specified, returns that agent's latest event.
        Otherwise returns the globally latest event.

        Args:
            agent: Optional agent ID

        Returns:
            The latest event, or None if empty
        """
        return self.monoid.get_latest_event(source=agent)

    def linearize(self) -> list[Event[Any]]:
        """
        Get a valid linear ordering of events.

        Note: Multiple valid orderings exist. This returns one.
        """
        return self.monoid.linearize()

    def get_event(self, event_id: str) -> Event[Any] | None:
        """Get an event by ID."""
        return self.monoid.get_event(event_id)

    def __len__(self) -> int:
        """Number of events in the Weave."""
        return len(self.monoid)

    def __contains__(self, event_id: str) -> bool:
        """Check if event is in the Weave."""
        return event_id in self.monoid
