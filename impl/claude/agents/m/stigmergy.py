"""
Stigmergic Memory: Coordination via Pheromone Fields.

Stigmergy is indirect coordination through the environment. Instead of
agents communicating directly, they deposit traces (pheromones) that
influence future behavior. This implements the Four Pillars insight:
memory is environmental, not individual.

Key Concepts:
- Trace: A pheromone deposit at a concept
- PheromoneField: The environmental substrate
- StigmergicAgent: Agent that follows gradients
- Natural decay: Traces evaporate over time (Ebbinghaus integration)

The act of depositing IS the tithe—paying forward for future agents
who will follow these trails.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Generic, Protocol, TypeVar

T = TypeVar("T")


@dataclass
class Trace:
    """A pheromone trace in the field.

    Traces represent past agent activity at a concept. They decay
    naturally over time (Ebbinghaus forgetting curve integration).
    """

    concept: str
    intensity: float
    deposited_at: datetime = field(default_factory=datetime.now)
    depositor: str = "anonymous"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def age(self) -> timedelta:
        """Time since deposit."""
        return datetime.now() - self.deposited_at

    @property
    def age_hours(self) -> float:
        """Age in hours."""
        return self.age.total_seconds() / 3600


@dataclass
class SenseResult:
    """Result of sensing pheromones from a position."""

    concept: str
    total_intensity: float
    trace_count: int
    dominant_depositor: str | None = None


class PheromoneField:
    """
    Environmental memory via pheromone traces.

    Agents deposit traces; other agents sense gradients.
    Natural decay integrates Ebbinghaus forgetting.

    The key insight: no central authority is needed. Consensus
    emerges from accumulated traces. This is collective memory
    without shared state.

    Example:
        field = PheromoneField(decay_rate=0.1)

        # Agent deposits a trace
        await field.deposit("python", intensity=1.0, depositor="agent_a")

        # Later, another agent senses the gradient
        gradients = await field.sense("programming")
        # → [("python", 0.9), ("javascript", 0.7), ...]

        # Natural decay happens automatically
        await field.decay(elapsed=timedelta(hours=1))
    """

    def __init__(
        self,
        decay_rate: float = 0.1,
        evaporation_threshold: float = 0.01,
    ) -> None:
        """Initialize pheromone field.

        Args:
            decay_rate: Decay per hour (0.1 = 10% per hour)
            evaporation_threshold: Below this, traces evaporate completely
        """
        self._decay_rate = decay_rate
        self._evaporation_threshold = evaporation_threshold

        # Map from concept -> list of traces
        self._traces: dict[str, list[Trace]] = {}

        # Statistics
        self._deposit_count = 0
        self._evaporation_count = 0

    @property
    def decay_rate(self) -> float:
        """Current decay rate per hour."""
        return self._decay_rate

    @property
    def concepts(self) -> set[str]:
        """All concepts with active traces."""
        return set(self._traces.keys())

    async def deposit(
        self,
        concept: str,
        intensity: float,
        depositor: str = "anonymous",
        metadata: dict[str, Any] | None = None,
    ) -> Trace:
        """
        Leave a trace at a concept (void.tithe integration).

        The act of depositing IS the tithe—paying forward
        for future agents who will follow these trails.

        Args:
            concept: The concept to mark
            intensity: Trace strength (higher = more influential)
            depositor: Agent leaving the trace
            metadata: Optional additional data

        Returns:
            The created Trace
        """
        trace = Trace(
            concept=concept,
            intensity=max(0.0, intensity),  # Clamp to positive
            depositor=depositor,
            metadata=metadata or {},
        )

        if concept not in self._traces:
            self._traces[concept] = []
        self._traces[concept].append(trace)

        self._deposit_count += 1

        return trace

    async def sense(self, position: str | None = None) -> list[SenseResult]:
        """
        Perceive gradients from current position.

        Returns concepts sorted by total trace intensity.
        If position is provided, concepts are filtered/weighted
        by proximity (future: semantic similarity).

        Args:
            position: Current position (concept) for context

        Returns:
            List of SenseResult sorted by intensity
        """
        # First, apply decay to get current intensities
        await self._apply_decay()

        results: list[SenseResult] = []

        for concept, traces in self._traces.items():
            if not traces:
                continue

            # Sum intensities
            total = sum(t.intensity for t in traces)

            # Find dominant depositor
            depositor_counts: dict[str, float] = {}
            for t in traces:
                depositor_counts[t.depositor] = (
                    depositor_counts.get(t.depositor, 0) + t.intensity
                )
            dominant = max(depositor_counts.keys(), key=lambda k: depositor_counts[k])

            if total > self._evaporation_threshold:
                results.append(
                    SenseResult(
                        concept=concept,
                        total_intensity=total,
                        trace_count=len(traces),
                        dominant_depositor=dominant,
                    )
                )

        # Sort by intensity (descending)
        results.sort(key=lambda r: r.total_intensity, reverse=True)

        return results

    async def gradient_toward(self, concept: str) -> float:
        """Get gradient strength toward a specific concept.

        Args:
            concept: The target concept

        Returns:
            Total trace intensity at that concept
        """
        if concept not in self._traces:
            return 0.0

        await self._apply_decay()

        if concept not in self._traces:  # May have evaporated
            return 0.0

        return sum(t.intensity for t in self._traces[concept])

    async def decay(self, elapsed: timedelta) -> int:
        """Explicitly apply decay for a time period.

        Args:
            elapsed: Time elapsed

        Returns:
            Number of traces evaporated
        """
        return await self._apply_decay(elapsed)

    async def _apply_decay(self, elapsed: timedelta | None = None) -> int:
        """Apply natural decay to all traces.

        If elapsed is not provided, calculates decay based on
        each trace's age since last decay application.

        Returns:
            Number of traces evaporated
        """
        evaporated = 0

        for concept in list(self._traces.keys()):
            surviving_traces: list[Trace] = []

            for trace in self._traces[concept]:
                # Calculate decay factor
                if elapsed:
                    hours = elapsed.total_seconds() / 3600
                else:
                    hours = trace.age_hours

                # Exponential decay: I(t) = I(0) * (1 - r)^t
                decay_factor = math.pow(1 - self._decay_rate, hours)
                decayed_intensity = trace.intensity * decay_factor

                if decayed_intensity > self._evaporation_threshold:
                    # Update trace intensity (mutate in place)
                    trace.intensity = decayed_intensity
                    surviving_traces.append(trace)
                else:
                    evaporated += 1
                    self._evaporation_count += 1

            if surviving_traces:
                self._traces[concept] = surviving_traces
            else:
                del self._traces[concept]

        return evaporated

    async def reinforce(self, concept: str, factor: float = 1.5) -> int:
        """Reinforce all traces at a concept.

        This is the opposite of decay—it strengthens traces,
        simulating repeated exposure or importance.

        Args:
            concept: Concept to reinforce
            factor: Reinforcement multiplier

        Returns:
            Number of traces reinforced
        """
        if concept not in self._traces:
            return 0

        count = 0
        for trace in self._traces[concept]:
            trace.intensity *= factor
            count += 1

        return count

    async def clear_concept(self, concept: str) -> int:
        """Remove all traces at a concept.

        Args:
            concept: Concept to clear

        Returns:
            Number of traces removed
        """
        if concept not in self._traces:
            return 0

        count = len(self._traces[concept])
        del self._traces[concept]
        return count

    def stats(self) -> dict[str, Any]:
        """Get field statistics."""
        all_traces = [t for traces in self._traces.values() for t in traces]
        intensities = [t.intensity for t in all_traces]

        return {
            "concept_count": len(self._traces),
            "trace_count": len(all_traces),
            "deposit_count": self._deposit_count,
            "evaporation_count": self._evaporation_count,
            "avg_intensity": sum(intensities) / max(len(intensities), 1),
            "max_intensity": max(intensities) if intensities else 0.0,
            "decay_rate": self._decay_rate,
        }


class StigmergicAgent:
    """
    Agent that navigates via pheromone gradients.

    Instead of explicit planning, follows environmental traces
    left by previous agents. Includes exploration for discovering
    new territory.

    The bushwhacking insight: sometimes you must leave the trail
    to find new paths.
    """

    def __init__(
        self,
        field: PheromoneField,
        exploration_rate: float = 0.1,
        deposit_intensity: float = 1.0,
    ) -> None:
        """Initialize stigmergic agent.

        Args:
            field: The pheromone field to navigate
            exploration_rate: Probability of random exploration (0.0 to 1.0)
            deposit_intensity: Default intensity for deposits
        """
        self._field = field
        self._exploration_rate = exploration_rate
        self._deposit_intensity = deposit_intensity
        self._current_position: str | None = None
        self._path_history: list[str] = []

    @property
    def current_position(self) -> str | None:
        """Current concept position."""
        return self._current_position

    @property
    def path_history(self) -> list[str]:
        """History of visited concepts."""
        return self._path_history.copy()

    async def follow_gradient(self) -> str | None:
        """
        Move toward strongest trace or explore.

        Returns:
            The concept moved to, or None if nowhere to go
        """
        # Random exploration (bushwhacking)
        if random.random() < self._exploration_rate:
            return await self._explore()

        # Sense gradients
        gradients = await self._field.sense(self._current_position)

        if not gradients:
            return await self._explore()

        # Probabilistic selection biased by intensity
        selected = self._weighted_select(gradients)

        if selected:
            await self._move_to(selected)

        return selected

    async def move_to(self, concept: str) -> None:
        """Explicitly move to a concept.

        Args:
            concept: Concept to move to
        """
        await self._move_to(concept)

    async def deposit(
        self,
        intensity: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Trace | None:
        """Deposit a trace at current position.

        Args:
            intensity: Trace intensity (uses default if not specified)
            metadata: Optional metadata

        Returns:
            The created Trace, or None if no current position
        """
        if self._current_position is None:
            return None

        return await self._field.deposit(
            concept=self._current_position,
            intensity=intensity or self._deposit_intensity,
            depositor=f"stigmergic_agent_{id(self)}",
            metadata=metadata,
        )

    async def _move_to(self, concept: str) -> None:
        """Internal move implementation."""
        self._current_position = concept
        self._path_history.append(concept)

    async def _explore(self) -> str | None:
        """Random exploration when no gradient or during exploration phase.

        In a real implementation, this would sample from a concept space.
        Here we just return None to indicate no known target.
        """
        # For now, return None to indicate exploration needed
        # Real implementation would have access to concept vocabulary
        return None

    def _weighted_select(self, gradients: list[SenseResult]) -> str | None:
        """Probabilistically select based on intensities."""
        if not gradients:
            return None

        # Build cumulative distribution
        total = sum(r.total_intensity for r in gradients)
        if total == 0:
            return None

        r = random.random() * total
        cumulative = 0.0

        for result in gradients:
            cumulative += result.total_intensity
            if r <= cumulative:
                return result.concept

        # Fallback to first
        return gradients[0].concept


class ConceptSpace(Protocol):
    """Protocol for providing a vocabulary of concepts."""

    async def sample(self) -> str:
        """Sample a random concept."""
        ...

    async def neighbors(self, concept: str) -> list[str]:
        """Get neighboring concepts."""
        ...


@dataclass
class SimpleConceptSpace:
    """Simple concept space with predefined vocabulary."""

    vocabulary: list[str] = field(default_factory=list)
    neighbors_map: dict[str, list[str]] = field(default_factory=dict)

    async def sample(self) -> str:
        """Sample a random concept from vocabulary."""
        if not self.vocabulary:
            raise ValueError("Empty vocabulary")
        return random.choice(self.vocabulary)

    async def neighbors(self, concept: str) -> list[str]:
        """Get neighbors of a concept."""
        return self.neighbors_map.get(concept, [])


class EnhancedStigmergicAgent(StigmergicAgent):
    """
    Enhanced stigmergic agent with concept space awareness.

    Can actually explore by sampling from a concept vocabulary,
    rather than returning None.
    """

    def __init__(
        self,
        field: PheromoneField,
        concept_space: SimpleConceptSpace,
        exploration_rate: float = 0.1,
        deposit_intensity: float = 1.0,
    ) -> None:
        """Initialize enhanced agent.

        Args:
            field: The pheromone field
            concept_space: The vocabulary of concepts
            exploration_rate: Probability of exploration
            deposit_intensity: Default deposit intensity
        """
        super().__init__(field, exploration_rate, deposit_intensity)
        self._concept_space = concept_space

    async def _explore(self) -> str | None:
        """Explore by sampling from concept space."""
        try:
            concept = await self._concept_space.sample()
            await self._move_to(concept)
            return concept
        except ValueError:
            return None

    async def follow_neighbors(self) -> str | None:
        """Move to a neighbor of current position.

        Uses pheromone gradients among neighbors only.
        """
        if self._current_position is None:
            return await self._explore()

        neighbors = await self._concept_space.neighbors(self._current_position)
        if not neighbors:
            return await self._explore()

        # Get gradients for neighbors only
        neighbor_gradients: list[SenseResult] = []
        for neighbor in neighbors:
            intensity = await self._field.gradient_toward(neighbor)
            if intensity > 0:
                neighbor_gradients.append(
                    SenseResult(
                        concept=neighbor,
                        total_intensity=intensity,
                        trace_count=1,
                    )
                )

        if not neighbor_gradients:
            # No pheromones, pick random neighbor
            concept = random.choice(neighbors)
            await self._move_to(concept)
            return concept

        # Weighted selection among neighbors
        selected = self._weighted_select(neighbor_gradients)
        if selected:
            await self._move_to(selected)
        return selected


async def create_ant_colony_optimization(
    field: PheromoneField,
    concept_space: SimpleConceptSpace,
    ant_count: int = 10,
    iterations: int = 100,
    evaporation_interval: timedelta = timedelta(hours=1),
) -> dict[str, float]:
    """
    Run ant colony optimization on a pheromone field.

    This is a simple ACO implementation for demonstration.
    Ants follow gradients and deposit traces, building
    consensus on important concepts.

    Args:
        field: The pheromone field
        concept_space: Available concepts
        ant_count: Number of ants
        iterations: Number of iterations
        evaporation_interval: Time between evaporation steps

    Returns:
        Final pheromone distribution
    """
    # Create ants
    ants = [
        EnhancedStigmergicAgent(
            field=field,
            concept_space=concept_space,
            exploration_rate=0.2,
        )
        for _ in range(ant_count)
    ]

    # Run iterations
    for _ in range(iterations):
        # Each ant makes a move and deposits
        for ant in ants:
            await ant.follow_gradient()
            await ant.deposit(intensity=1.0)

        # Apply decay
        await field.decay(evaporation_interval)

    # Collect final distribution
    gradients = await field.sense()
    return {r.concept: r.total_intensity for r in gradients}
