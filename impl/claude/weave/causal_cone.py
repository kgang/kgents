"""
CausalCone - The Perspective Functor for Turn-gents.

The "killer feature" of Turn-gents: automatic context projection.

Instead of manually selecting context, CausalCone projects the Weave
onto an agent's **Causal Cone** (Light Cone / Past Cone):

    Classical LLMs: Feed entire chat log (noise).
    CausalCone:     Feed only causal ancestors (signal).

This implements Law 4 — Perspective as Functor:
    Context is computed via CausalCone.project_context(),
    not manually curated.

Mathematical Foundation:
- The Causal Cone is the transitive closure of dependencies
- If Agent A never read Agent B's message, B's turn is NOT in A's cone
- This mathematically eliminates context bloat

References:
- Lamport, "Happened-Before Relation" (1978)
- Turn-gents Plan: Phase 2 (Causal Cone Projection)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .dependency import DependencyGraph
from .event import Event
from .turn import Turn

if TYPE_CHECKING:
    from .weave import TheWeave


@dataclass
class CausalCone:
    """
    Implements the Past Light Cone projection.

    The Causal Cone computes the minimal context an agent needs
    for their next turn: only events that causally precede
    their current state.

    This is the categorical move: Weave → list[Event[T]]

    Properties:
    - **Minimal**: Only includes causal ancestors
    - **Sound**: Respects happened-before ordering
    - **Concurrent-safe**: Independent threads excluded

    Example:
        weave = TheWeave()
        cone = CausalCone(weave)

        # Get context for agent's next turn
        context = cone.project_context("agent-a")

        # Context contains only events agent-a can observe
        # (their own events + transitive dependencies)
    """

    weave: TheWeave
    _braid: DependencyGraph = field(init=False)

    def __post_init__(self) -> None:
        """Cache the braid (dependency graph) for efficient lookups."""
        self._braid = self.weave.braid()

    def refresh_braid(self) -> None:
        """Refresh the cached braid after weave modifications."""
        self._braid = self.weave.braid()

    def project_context(self, agent_id: str) -> list[Event[Any]]:
        """
        Return MINIMAL causal history for agent's next turn.

        If Agent A never read Agent B's message,
        Agent B's turn is NOT in A's cone.
        This mathematically eliminates context bloat.

        Args:
            agent_id: The agent whose perspective to compute

        Returns:
            List of events in valid topological order that
            the agent can "see" (causally precedes their state)

        Algorithm:
        1. Find agent's tip (most recent event)
        2. Compute transitive closure of dependencies
        3. Include all agent's own events
        4. Linearize (topological sort) for LLM consumption
        """
        # 1. Get agent's tip (most recent event)
        tip = self.weave.tip(agent_id)
        if tip is None:
            return []

        # 2. Compute causal history (transitive closure)
        causal_ids = self._braid.get_all_dependencies(tip.id)
        causal_ids.add(tip.id)  # Include tip itself

        # 3. Include all agent's own events (they can see their past)
        agent_events = self.weave.thread(agent_id)
        for event in agent_events:
            causal_ids.add(event.id)
            # Also include their transitive dependencies
            causal_ids.update(self._braid.get_all_dependencies(event.id))

        # 4. Linearize for LLM consumption
        return self.weave.monoid.linearize_subset(causal_ids)

    def project_context_from_events(self, event_ids: set[str]) -> list[Event[Any]]:
        """
        Compute causal cone for a set of events (not agent-based).

        Useful for:
        - Computing context for a specific turn
        - Debugging causal relationships
        - Knot context computation

        Args:
            event_ids: Set of event IDs to compute cone for

        Returns:
            Linearized causal history
        """
        if not event_ids:
            return []

        # Compute transitive closure
        causal_ids: set[str] = set()
        for eid in event_ids:
            causal_ids.add(eid)
            causal_ids.update(self._braid.get_all_dependencies(eid))

        return self.weave.monoid.linearize_subset(causal_ids)

    def are_causally_related(self, event_a: str, event_b: str) -> bool:
        """
        Check if two events are causally related (one depends on other).

        Args:
            event_a: First event ID
            event_b: Second event ID

        Returns:
            True if one happened-before the other, False if concurrent
        """
        return not self._braid.are_concurrent(event_a, event_b)

    def cone_size(self, agent_id: str) -> int:
        """
        Get the size of an agent's causal cone.

        Useful for:
        - Context budget estimation
        - Compression ratio metrics
        - Debugging

        Args:
            agent_id: The agent to measure

        Returns:
            Number of events in the cone
        """
        return len(self.project_context(agent_id))

    def compression_ratio(self, agent_id: str) -> float:
        """
        Calculate context compression ratio for an agent.

        Compression = 1 - (cone_size / total_weave_size)

        Higher is better (more context eliminated).

        Args:
            agent_id: The agent to measure

        Returns:
            Compression ratio in [0.0, 1.0]
        """
        total = len(self.weave)
        if total == 0:
            return 0.0

        cone = self.cone_size(agent_id)
        return 1.0 - (cone / total)


@dataclass
class CausalConeStats:
    """Statistics about a causal cone projection."""

    agent_id: str
    cone_size: int
    total_weave_size: int
    compression_ratio: float
    speech_turns: int
    action_turns: int
    thought_turns: int
    yield_turns: int
    silence_turns: int

    @classmethod
    def from_cone(
        cls,
        agent_id: str,
        context: list[Event[Any]],
        total_weave_size: int,
    ) -> CausalConeStats:
        """
        Compute statistics from a projected context.

        Args:
            agent_id: The agent this cone is for
            context: The projected context (list of events)
            total_weave_size: Total events in the weave

        Returns:
            Statistics about the cone
        """
        from .turn import TurnType

        cone_size = len(context)
        compression = 1.0 - (cone_size / total_weave_size) if total_weave_size > 0 else 0.0

        # Count turn types (only for Turn instances)
        speech = action = thought = yield_t = silence = 0
        for event in context:
            if isinstance(event, Turn):
                if event.turn_type == TurnType.SPEECH:
                    speech += 1
                elif event.turn_type == TurnType.ACTION:
                    action += 1
                elif event.turn_type == TurnType.THOUGHT:
                    thought += 1
                elif event.turn_type == TurnType.YIELD:
                    yield_t += 1
                elif event.turn_type == TurnType.SILENCE:
                    silence += 1

        return cls(
            agent_id=agent_id,
            cone_size=cone_size,
            total_weave_size=total_weave_size,
            compression_ratio=compression,
            speech_turns=speech,
            action_turns=action,
            thought_turns=thought,
            yield_turns=yield_t,
            silence_turns=silence,
        )


def compute_cone_stats(
    cone: CausalCone,
    agent_id: str,
) -> CausalConeStats:
    """
    Convenience function to compute cone statistics.

    Args:
        cone: The CausalCone instance
        agent_id: The agent to analyze

    Returns:
        Statistics about the agent's causal cone
    """
    context = cone.project_context(agent_id)
    return CausalConeStats.from_cone(
        agent_id=agent_id,
        context=context,
        total_weave_size=len(cone.weave),
    )
