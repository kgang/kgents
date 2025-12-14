"""
Categorical Routing: Task → Agent via Pheromone Gradients.

The adjunction insight: deposit ⊣ route.
Depositing creates gradients; routing follows them.

This module extends the basic CategoricalRouter from substrate.py
with richer Task types and the naturality property:

    route(f(task)) = f(route(task))

For any task morphism f, the routing respects task transformations.

Key Types:
- Task: A unit of work with concept affinity
- RoutingDecision: The chosen agent + reasoning
- GradientMap: Snapshot of pheromone gradients
- RouteTrace: Audit trail for routing decisions

The categorical insight: routing is a functor from Task to Agent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Generic, Protocol, TypeVar

if TYPE_CHECKING:
    from .stigmergy import PheromoneField, SenseResult
    from .substrate import AgentId

T = TypeVar("T")


# =============================================================================
# Task Type
# =============================================================================


@dataclass
class Task:
    """
    A unit of work to be routed to an agent.

    Categorical insight: Tasks form a category where morphisms are
    transformations that preserve routing relevance.

    Example:
        task = Task(
            concept="python_debugging",
            content="Fix the type error in module X",
            priority=0.8,
        )
    """

    concept: str  # Primary concept for routing
    content: str = ""  # Task content/description
    priority: float = 0.5  # Urgency (0 to 1)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    # Secondary concepts for multi-gradient routing
    related_concepts: list[str] = field(default_factory=list)

    def map(self, f: "TaskMorphism") -> "Task":
        """
        Apply morphism to this task.

        Naturality: route(f(task)) = f(route(task))
        """
        return f(self)


@dataclass
class TaskMorphism:
    """
    A transformation between tasks that preserves routing structure.

    For naturality to hold, morphisms must preserve the concept
    structure in a way that routing respects.
    """

    name: str
    transform_concept: bool = False  # Does this change the concept?
    new_concept: str | None = None  # If transform_concept, the new concept

    def __call__(self, task: Task) -> Task:
        """Apply the morphism."""
        if self.transform_concept and self.new_concept:
            return Task(
                concept=self.new_concept,
                content=task.content,
                priority=task.priority,
                metadata={**task.metadata, "morphism_applied": self.name},
                related_concepts=[task.concept] + task.related_concepts,
            )
        return Task(
            concept=task.concept,
            content=task.content,
            priority=task.priority,
            metadata={**task.metadata, "morphism_applied": self.name},
            related_concepts=task.related_concepts,
        )


# =============================================================================
# Routing Decision
# =============================================================================


@dataclass
class RoutingDecision:
    """
    Result of routing a task.

    Includes the decision and reasoning for auditability.
    """

    task: Task
    agent_id: str
    confidence: float  # How confident in this routing (0 to 1)
    gradient_strength: float  # Strength of the pheromone gradient
    reasoning: str  # Why this agent was chosen
    alternatives: list[tuple[str, float]] = field(
        default_factory=list
    )  # (agent_id, score)
    decided_at: datetime = field(default_factory=datetime.now)


# =============================================================================
# Gradient Map
# =============================================================================


@dataclass
class GradientMap:
    """
    Snapshot of pheromone gradients at a concept.

    Useful for debugging and visualizing routing decisions.
    """

    concept: str
    gradients: dict[str, float]  # agent_id → intensity
    sensed_at: datetime = field(default_factory=datetime.now)
    total_intensity: float = 0.0

    def strongest(self) -> tuple[str, float] | None:
        """Get the strongest gradient."""
        if not self.gradients:
            return None
        agent_id = max(self.gradients.keys(), key=lambda k: self.gradients[k])
        return (agent_id, self.gradients[agent_id])

    def top_k(self, k: int = 3) -> list[tuple[str, float]]:
        """Get top k gradients."""
        sorted_gradients = sorted(
            self.gradients.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        return sorted_gradients[:k]


# =============================================================================
# Route Trace
# =============================================================================


@dataclass
class RouteTrace:
    """
    Audit trail for a routing decision.

    The trace records:
    1. The task that was routed
    2. The gradients that were sensed
    3. The decision that was made
    4. Whether the routing was successful

    This supports debugging and improving routing over time.
    """

    task: Task
    gradient_map: GradientMap
    decision: RoutingDecision
    successful: bool | None = None  # Set after task completion
    feedback: str = ""  # Optional feedback on routing quality


# =============================================================================
# Enhanced Categorical Router
# =============================================================================


class CategoricalRouter:
    """
    Route tasks to agents via pheromone gradients.

    This is a functor: Task → Agent

    The categorical insight: instead of explicit routing tables,
    we follow the gradient in the pheromone field. This is
    adjoint to the deposit operation:

        deposit ⊣ route

    Depositing creates gradients; routing follows them.
    This adjunction ensures routes are "natural" (follow actual usage).

    Key Properties:
    1. Naturality: route(f(task)) = f(route(task))
    2. Adjunction: deposit ⊣ route
    3. Functoriality: route preserves task composition

    Example:
        field = PheromoneField()
        router = CategoricalRouter(field)

        task = Task(concept="python", content="Fix type error")
        decision = await router.route(task)
        print(f"Route to: {decision.agent_id}")
    """

    def __init__(
        self,
        field: "PheromoneField",
        default_agent: str = "default",
        confidence_threshold: float = 0.3,
        exploration_rate: float = 0.1,
    ) -> None:
        """
        Initialize categorical router.

        Args:
            field: The pheromone field to navigate
            default_agent: Fallback agent when no gradient
            confidence_threshold: Minimum confidence to route (else default)
            exploration_rate: Probability of exploring non-optimal route
        """
        self._field = field
        self._default_agent = default_agent
        self._confidence_threshold = confidence_threshold
        self._exploration_rate = exploration_rate
        self._traces: list[RouteTrace] = []
        self._route_count = 0

    @property
    def field(self) -> "PheromoneField":
        """The underlying pheromone field."""
        return self._field

    @property
    def traces(self) -> list[RouteTrace]:
        """Routing audit trail."""
        return self._traces.copy()

    async def route(self, task: Task) -> RoutingDecision:
        """
        Route a task to an agent by following gradients.

        Naturality: route(f(task)) = f(route(task)) for any morphism f

        Args:
            task: The task to route

        Returns:
            RoutingDecision with chosen agent and reasoning
        """
        # Sense gradients at task concept
        gradient_map = await self.sense_gradients(task.concept)

        # Also sense related concepts and combine
        for related in task.related_concepts:
            related_map = await self.sense_gradients(related)
            for agent_id, intensity in related_map.gradients.items():
                current = gradient_map.gradients.get(agent_id, 0.0)
                # Related concepts contribute at 50% weight
                gradient_map.gradients[agent_id] = current + intensity * 0.5

        # Make decision
        decision = self._decide(task, gradient_map)

        # Record trace
        trace = RouteTrace(
            task=task,
            gradient_map=gradient_map,
            decision=decision,
        )
        self._traces.append(trace)
        self._route_count += 1

        return decision

    async def route_batch(self, tasks: list[Task]) -> list[RoutingDecision]:
        """
        Route multiple tasks.

        Args:
            tasks: Tasks to route

        Returns:
            List of routing decisions
        """
        return [await self.route(task) for task in tasks]

    async def sense_gradients(self, concept: str) -> GradientMap:
        """
        Sense pheromone gradients at a concept.

        Args:
            concept: The concept to sense

        Returns:
            GradientMap with agent intensities
        """
        results: list["SenseResult"] = await self._field.sense(concept)

        gradients: dict[str, float] = {}
        total = 0.0

        for result in results:
            if result.dominant_depositor:
                gradients[result.dominant_depositor] = result.total_intensity
                total += result.total_intensity

        return GradientMap(
            concept=concept,
            gradients=gradients,
            total_intensity=total,
        )

    def _decide(self, task: Task, gradient_map: GradientMap) -> RoutingDecision:
        """
        Make routing decision based on gradients.

        Includes exploration (bushwhacking) for discovering new routes.
        """
        import random

        # Exploration: sometimes pick non-optimal
        if random.random() < self._exploration_rate and gradient_map.gradients:
            agents = list(gradient_map.gradients.keys())
            chosen = random.choice(agents)
            return RoutingDecision(
                task=task,
                agent_id=chosen,
                confidence=0.5,  # Low confidence for exploration
                gradient_strength=gradient_map.gradients[chosen],
                reasoning=f"Exploration: randomly chose {chosen}",
                alternatives=gradient_map.top_k(3),
            )

        # Get strongest gradient
        strongest = gradient_map.strongest()

        if strongest is None:
            # No gradient - use default
            return RoutingDecision(
                task=task,
                agent_id=self._default_agent,
                confidence=0.0,
                gradient_strength=0.0,
                reasoning=f"No gradient for '{task.concept}', using default",
                alternatives=[],
            )

        agent_id, intensity = strongest

        # Compute confidence from relative gradient strength
        total = gradient_map.total_intensity
        confidence = intensity / total if total > 0 else 0.0

        if confidence < self._confidence_threshold:
            # Low confidence - use default but record alternatives
            return RoutingDecision(
                task=task,
                agent_id=self._default_agent,
                confidence=confidence,
                gradient_strength=intensity,
                reasoning=f"Low confidence ({confidence:.2f} < {self._confidence_threshold}), using default",
                alternatives=gradient_map.top_k(3),
            )

        # High confidence - route to strongest
        return RoutingDecision(
            task=task,
            agent_id=agent_id,
            confidence=confidence,
            gradient_strength=intensity,
            reasoning=f"Following gradient: {agent_id} has {intensity:.2f} intensity ({confidence:.0%} of total)",
            alternatives=gradient_map.top_k(3),
        )

    async def record_outcome(
        self,
        decision: RoutingDecision,
        successful: bool,
        feedback: str = "",
    ) -> None:
        """
        Record the outcome of a routing decision.

        This feedback can be used to improve future routing.

        Args:
            decision: The decision to update
            successful: Whether the routing was successful
            feedback: Optional feedback
        """
        # Find and update the trace
        for trace in reversed(self._traces):
            if trace.decision is decision:
                trace.successful = successful
                trace.feedback = feedback
                break

        # If successful, reinforce the gradient
        if successful:
            await self._field.reinforce(decision.task.concept, factor=1.2)

    def stats(self) -> dict[str, Any]:
        """Get router statistics."""
        successful = sum(1 for t in self._traces if t.successful is True)
        failed = sum(1 for t in self._traces if t.successful is False)
        pending = sum(1 for t in self._traces if t.successful is None)

        return {
            "route_count": self._route_count,
            "trace_count": len(self._traces),
            "successful": successful,
            "failed": failed,
            "pending": pending,
            "success_rate": successful / max(successful + failed, 1),
            "exploration_rate": self._exploration_rate,
            "confidence_threshold": self._confidence_threshold,
        }


# =============================================================================
# Adjunction Verification
# =============================================================================


async def verify_adjunction(
    field: "PheromoneField",
    router: CategoricalRouter,
    concepts: list[str],
    depositor: str = "test_agent",
) -> dict[str, Any]:
    """
    Verify the deposit ⊣ route adjunction.

    For the adjunction to hold:
    - Every deposit creates a gradient
    - Every route follows an existing gradient

    Args:
        field: The pheromone field
        router: The router
        concepts: Concepts to test
        depositor: Agent name to use for deposits

    Returns:
        Dict with verification results
    """
    results: dict[str, Any] = {
        "deposits": 0,
        "routes_following_deposits": 0,
        "routes_to_depositor": 0,
        "adjunction_holds": False,
    }

    # Deposit at each concept
    for concept in concepts:
        await field.deposit(concept, intensity=1.0, depositor=depositor)
        results["deposits"] += 1

    # Route tasks and check if they follow deposits
    for concept in concepts:
        task = Task(concept=concept)
        decision = await router.route(task)

        if decision.gradient_strength > 0:
            results["routes_following_deposits"] += 1

        if decision.agent_id == depositor:
            results["routes_to_depositor"] += 1

    # Adjunction holds if all deposits create followable routes
    results["adjunction_holds"] = results["routes_to_depositor"] == results["deposits"]

    return results


# =============================================================================
# Factory Functions
# =============================================================================


def create_router(
    field: "PheromoneField",
    default_agent: str = "default",
    confidence_threshold: float = 0.3,
    exploration_rate: float = 0.1,
) -> CategoricalRouter:
    """
    Factory function to create a CategoricalRouter.

    Args:
        field: The pheromone field
        default_agent: Fallback agent
        confidence_threshold: Minimum confidence to route
        exploration_rate: Exploration probability

    Returns:
        Configured CategoricalRouter
    """
    return CategoricalRouter(
        field=field,
        default_agent=default_agent,
        confidence_threshold=confidence_threshold,
        exploration_rate=exploration_rate,
    )


def create_task(
    concept: str,
    content: str = "",
    priority: float = 0.5,
    related: list[str] | None = None,
) -> Task:
    """
    Factory function to create a Task.

    Args:
        concept: Primary concept
        content: Task content
        priority: Urgency
        related: Related concepts

    Returns:
        Configured Task
    """
    return Task(
        concept=concept,
        content=content,
        priority=priority,
        related_concepts=related or [],
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core types
    "Task",
    "TaskMorphism",
    "RoutingDecision",
    "GradientMap",
    "RouteTrace",
    # Router
    "CategoricalRouter",
    # Verification
    "verify_adjunction",
    # Factory functions
    "create_router",
    "create_task",
]
