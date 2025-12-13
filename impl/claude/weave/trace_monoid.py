"""
TraceMonoid - Mathematical Foundation for Concurrent History.

A Trace Monoid (Mazurkiewicz trace) captures concurrent history where:
- Independent events can be reordered: ab = ba if (a,b) independent
- Dependent events maintain order: ab != ba if (a,b) dependent

This is the mathematical foundation for The Weave.

Mathematical Definition:
- Σ: Alphabet of event types
- I ⊆ Σ × Σ: Independence relation (symmetric, irreflexive)
- Σ*/≈: Trace monoid (equivalence classes of strings)
- ab ≈ ba iff (a,b) ∈ I

References:
- Mazurkiewicz, "Trace Theory" (1977)
- Diekert & Rozenberg, "The Book of Traces" (1995)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, Iterator, TypeVar

from .dependency import DependencyGraph
from .event import Event, KnotEvent

T = TypeVar("T")


@dataclass
class TraceMonoid(Generic[T]):
    """
    A Trace Monoid for concurrent history.

    Unlike a linear list, a Trace Monoid captures:
    - Independent (commutative) events that can be reordered
    - Dependent events that must maintain order

    The independence relation I ⊆ Σ × Σ defines which
    events commute. Events (a, b) ∈ I can be swapped
    without changing meaning.

    Example:
    - Agent A talks to Agent B (event ab)
    - Agent C talks to Agent D (event cd)
    - These are independent: ab·cd = cd·ab

    But:
    - Agent A talks to Agent B (event ab)
    - Agent B talks to Agent C (event bc)
    - These are dependent: ab must precede bc
    """

    # List of events in observed order
    events: list[Event[T]] = field(default_factory=list)

    # Independence relation: frozenset of (source_a, source_b) pairs
    # Events from independent sources can commute
    independence: frozenset[tuple[str, str]] = field(default_factory=frozenset)

    # Dependency graph (DAG structure)
    _dependency_graph: DependencyGraph = field(default_factory=DependencyGraph)

    def append(
        self,
        event: Event[T],
        depends_on: set[str] | None = None,
    ) -> "TraceMonoid[T]":
        """
        Add an event to the Weave.

        Args:
            event: The event to add
            depends_on: IDs of events this one depends on

        Returns:
            New TraceMonoid with event added (immutable pattern)
        """
        new_events = list(self.events) + [event]

        new_graph = DependencyGraph(
            _dependencies=dict(self._dependency_graph._dependencies)
        )
        new_graph.add_node(event.id, depends_on)

        return TraceMonoid(
            events=new_events,
            independence=self.independence,
            _dependency_graph=new_graph,
        )

    def append_mut(
        self,
        event: Event[T],
        depends_on: set[str] | None = None,
    ) -> None:
        """
        Add an event to the Weave (mutating version).

        Args:
            event: The event to add
            depends_on: IDs of events this one depends on
        """
        self.events.append(event)
        self._dependency_graph.add_node(event.id, depends_on)

    def braid(self) -> DependencyGraph:
        """
        Return the dependency structure as a graph.

        This shows which events can be reordered (concurrent)
        and which must maintain order (sequential).
        """
        return self._dependency_graph

    def knot(self, event_ids: set[str]) -> KnotEvent:
        """
        Create a synchronization point (knot) in the Weave.

        A knot is where multiple concurrent threads must
        synchronize before proceeding. It's a consensus point.

        Args:
            event_ids: Events that must all complete before knot

        Returns:
            A new KnotEvent representing the synchronization
        """
        # Find maximum timestamp among specified events
        max_timestamp = 0.0
        for event in self.events:
            if event.id in event_ids:
                max_timestamp = max(max_timestamp, event.timestamp)

        return KnotEvent.create_knot(
            event_ids=frozenset(event_ids),
            timestamp=max_timestamp,
        )

    def linearize(self) -> list[Event[T]]:
        """
        Produce a valid linear ordering (topological sort).

        Note: Multiple valid orderings may exist due to
        concurrency. This returns ONE valid ordering.

        Returns:
            List of events in valid execution order
        """
        ordered_ids = self._dependency_graph.topological_sort()
        id_to_event = {e.id: e for e in self.events}
        return [id_to_event[eid] for eid in ordered_ids if eid in id_to_event]

    def linearize_subset(self, event_ids: set[str]) -> list[Event[T]]:
        """
        Linearize only the specified events (respecting dependencies).

        This is the key operation for CausalCone projection:
        given a set of event IDs (typically the causal past),
        return them in valid topological order.

        Args:
            event_ids: Set of event IDs to linearize

        Returns:
            List of events in valid execution order

        Example:
            # Get causal history for an agent's tip
            causal_history = braid.get_all_dependencies(tip_id)
            causal_history.add(tip_id)  # Include tip itself
            linear_context = monoid.linearize_subset(causal_history)
        """
        if not event_ids:
            return []

        # Build subgraph of only the specified events
        subgraph_deps: dict[str, set[str]] = {}
        for eid in event_ids:
            if eid in self._dependency_graph:
                # Only include dependencies that are also in our subset
                deps = self._dependency_graph.get_dependencies(eid)
                subgraph_deps[eid] = deps & event_ids
            else:
                subgraph_deps[eid] = set()

        # Topological sort on subgraph (Kahn's algorithm)
        in_degree = {eid: len(deps) for eid, deps in subgraph_deps.items()}

        # Build reverse mapping (who depends on whom)
        dependents: dict[str, set[str]] = {eid: set() for eid in event_ids}
        for eid, deps in subgraph_deps.items():
            for dep in deps:
                if dep in dependents:
                    dependents[dep].add(eid)

        # Start with events that have no dependencies (in subset)
        from collections import deque

        queue = deque([eid for eid, deg in in_degree.items() if deg == 0])
        ordered_ids: list[str] = []

        while queue:
            current = queue.popleft()
            ordered_ids.append(current)

            for dependent in dependents.get(current, set()):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Map IDs to events
        id_to_event = {e.id: e for e in self.events}
        return [id_to_event[eid] for eid in ordered_ids if eid in id_to_event]

    def project(self, agent: str) -> list[Event[T]]:
        """
        Project the Weave to a single agent's perspective.

        Returns only events visible to the specified agent,
        in their subjective order.

        Args:
            agent: Agent ID to project for

        Returns:
            Events from that agent's perspective
        """
        # Agent sees: their own events + events they depend on
        visible: list[Event[T]] = []
        agent_event_ids = {e.id for e in self.events if e.source == agent}

        for event in self.events:
            if event.source == agent:
                visible.append(event)
            elif self._is_visible_to(event, agent_event_ids):
                visible.append(event)

        return visible

    def _is_visible_to(self, event: Event[T], agent_event_ids: set[str]) -> bool:
        """Check if event is visible to an agent (they depend on it)."""
        # An event is visible if any of the agent's events depend on it
        for agent_eid in agent_event_ids:
            deps = self._dependency_graph.get_all_dependencies(agent_eid)
            if event.id in deps:
                return True
        return False

    def are_concurrent(self, event_a: str, event_b: str) -> bool:
        """
        Check if two events are concurrent (can be reordered).

        Args:
            event_a: First event ID
            event_b: Second event ID

        Returns:
            True if events are concurrent (independent)
        """
        return self._dependency_graph.are_concurrent(event_a, event_b)

    def get_event(self, event_id: str) -> Event[T] | None:
        """Get an event by ID."""
        for event in self.events:
            if event.id == event_id:
                return event
        return None

    def get_events_by_source(self, source: str) -> list[Event[T]]:
        """Get all events from a specific source."""
        return [e for e in self.events if e.source == source]

    def get_latest_event(self, source: str | None = None) -> Event[T] | None:
        """Get the latest event, optionally filtered by source."""
        candidates = (
            self.events if source is None else self.get_events_by_source(source)
        )
        if not candidates:
            return None
        return max(candidates, key=lambda e: e.timestamp)

    def filter_by_time(
        self,
        start: float | None = None,
        end: float | None = None,
    ) -> list[Event[T]]:
        """Get events within a time range."""
        result: list[Event[T]] = []
        for event in self.events:
            if start is not None and event.timestamp < start:
                continue
            if end is not None and event.timestamp > end:
                continue
            result.append(event)
        return result

    def __len__(self) -> int:
        """Number of events in the monoid."""
        return len(self.events)

    def __iter__(self) -> Iterator[Event[T]]:
        """Iterate over events in observed order."""
        return iter(self.events)

    def __contains__(self, event_id: str) -> bool:
        """Check if event is in the monoid."""
        return any(e.id == event_id for e in self.events)


# Independence relations for common patterns


def agents_independent(agent_a: str, agent_b: str) -> frozenset[tuple[str, str]]:
    """Create independence relation for two agents."""
    return frozenset({(agent_a, agent_b), (agent_b, agent_a)})


def all_agents_independent(agents: list[str]) -> frozenset[tuple[str, str]]:
    """Create independence relation where all agents are independent."""
    pairs: set[tuple[str, str]] = set()
    for i, a in enumerate(agents):
        for b in agents[i + 1 :]:
            pairs.add((a, b))
            pairs.add((b, a))
    return frozenset(pairs)
