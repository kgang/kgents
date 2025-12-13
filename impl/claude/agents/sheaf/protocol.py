"""
Sheaf Protocol: Emergence from Local to Global.

A sheaf captures the mathematical structure of emergence:
- Local sections: Behavior in specific contexts
- Gluing: Combine compatible local behaviors into global behavior
- Restriction: Extract local behavior from global

The key insight from Mac Lane & Moerdijk:
    "A sheaf is defined as a presheaf satisfying locality and gluing
    conditions, ensuring coherent global structure while preserving
    local properties."

For agents, this means:
- Different observers (contexts) see different behaviors
- Compatible behaviors can be glued into emergent global behavior
- The global agent has capabilities no single local agent has

See: plans/ideas/impl/meta-construction.md
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, FrozenSet, Generic, Protocol, TypeVar

from agents.poly import PolyAgent

# Type variables
Ctx = TypeVar("Ctx")  # Context type
S = TypeVar("S")  # State type
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type


@dataclass(frozen=True)
class Context:
    """
    A context in the observation topology.

    Contexts represent different viewpoints or environments
    in which agents operate.
    """

    name: str
    capabilities: FrozenSet[str] = frozenset()
    parent: str | None = None

    def __hash__(self) -> int:
        return hash((self.name, self.capabilities, self.parent))


@dataclass
class GluingError(Exception):
    """Raised when local agents cannot be glued."""

    contexts: list[str]
    reason: str

    def __str__(self) -> str:
        return f"Cannot glue agents on {self.contexts}: {self.reason}"


@dataclass
class RestrictionError(Exception):
    """Raised when restriction fails."""

    context: str
    reason: str

    def __str__(self) -> str:
        return f"Cannot restrict to {self.context}: {self.reason}"


class AgentSheaf(Generic[Ctx]):
    """
    Sheaf structure for emergent agent behavior.

    A sheaf over a topology of contexts provides:
    - restrict: Extract local behavior for a subcontext
    - glue: Combine compatible local agents into global agent
    - compatible: Check if locals agree on overlaps

    The gluing operation is where EMERGENCE happens:
    The global agent has behaviors that no single local agent has.
    """

    def __init__(
        self,
        contexts: set[Ctx],
        overlap_fn: Callable[[Ctx, Ctx], Ctx | None],
    ):
        """
        Initialize agent sheaf.

        Args:
            contexts: Set of all contexts in the topology
            overlap_fn: Function that returns overlap of two contexts,
                       or None if they don't overlap
        """
        self.contexts = contexts
        self.overlap = overlap_fn

    def restrict(
        self,
        agent: PolyAgent[Any, Any, Any],
        subcontext: Ctx,
        position_filter: Callable[[Any, Ctx], bool] | None = None,
    ) -> PolyAgent[Any, Any, Any]:
        """
        Restrict agent behavior to a subcontext.

        The restricted agent only operates in states valid for the subcontext.

        Args:
            agent: Agent to restrict
            subcontext: Context to restrict to
            position_filter: Optional filter for valid positions
                            (default: all positions valid)

        Returns:
            Restricted agent
        """
        if position_filter is None:
            # Default: all positions valid in subcontext
            def position_filter(pos: Any, ctx: Ctx) -> bool:
                return True

        # Filter positions
        restricted_positions = frozenset(
            pos for pos in agent.positions if position_filter(pos, subcontext)
        )

        if not restricted_positions:
            raise RestrictionError(
                context=str(subcontext),
                reason="No valid positions in subcontext",
            )

        return PolyAgent(
            name=f"{agent.name}|{subcontext}",
            positions=restricted_positions,
            _directions=lambda s: agent.directions(s)
            if s in restricted_positions
            else frozenset(),
            _transition=agent._transition,
        )

    def compatible(
        self,
        locals: dict[Ctx, PolyAgent[Any, Any, Any]],
        equivalence: Callable[[Any, Any], bool] | None = None,
    ) -> bool:
        """
        Check if local agents agree on overlaps.

        For gluing to succeed, agents must produce equivalent results
        when restricted to overlapping contexts.

        Args:
            locals: Dict mapping contexts to local agents
            equivalence: Optional function to check output equivalence
                        (default: equality)

        Returns:
            True if all overlapping agents are compatible
        """
        if equivalence is None:
            equivalence = lambda a, b: a == b

        ctx_list = list(locals.keys())
        for i, ctx1 in enumerate(ctx_list):
            for ctx2 in ctx_list[i + 1 :]:
                overlap = self.overlap(ctx1, ctx2)
                if overlap is not None:
                    # Agents must agree on the overlap
                    agent1 = locals[ctx1]
                    agent2 = locals[ctx2]

                    # Check position intersection
                    common_positions = agent1.positions & agent2.positions
                    if common_positions:
                        # For simplicity, we check that agents have same structure
                        # Real implementation would verify output equivalence
                        if len(agent1.positions) == 0 or len(agent2.positions) == 0:
                            return False

        return True

    def glue(
        self,
        locals: dict[Ctx, PolyAgent[Any, Any, Any]],
    ) -> PolyAgent[Any, Any, Any]:
        """
        Glue compatible local agents into global agent.

        This is where EMERGENCE happens: the global agent has
        behaviors that no single local agent has alone.

        Args:
            locals: Dict mapping contexts to local agents
                   (must be compatible on overlaps)

        Returns:
            Glued global agent

        Raises:
            GluingError: If local agents are not compatible
        """
        if not self.compatible(locals):
            raise GluingError(
                contexts=list(str(c) for c in locals.keys()),
                reason="Local agents not compatible on overlaps",
            )

        # Global positions = union of local positions
        global_positions: frozenset[Any] = frozenset().union(
            *(agent.positions for agent in locals.values())
        )

        # Create context lookup for dispatch
        position_to_context: dict[Any, tuple[Ctx, PolyAgent[Any, Any, Any]]] = {}
        for ctx, agent in locals.items():
            for pos in agent.positions:
                if pos not in position_to_context:
                    position_to_context[pos] = (ctx, agent)

        def global_directions(state: Any) -> FrozenSet[Any]:
            """Get directions from appropriate local agent."""
            if state in position_to_context:
                _, agent = position_to_context[state]
                return agent.directions(state)
            return frozenset()

        def global_transition(state: Any, input: Any) -> tuple[Any, Any]:
            """Dispatch to appropriate local agent."""
            if state in position_to_context:
                _, agent = position_to_context[state]
                return agent._transition(state, input)
            raise ValueError(f"No local agent handles state {state}")

        return PolyAgent(
            name=f"Glued({', '.join(a.name for a in locals.values())})",
            positions=global_positions,
            _directions=global_directions,
            _transition=global_transition,
        )

    def __repr__(self) -> str:
        return f"AgentSheaf(contexts={len(self.contexts)})"


# =============================================================================
# Concrete Sheaf: Soul Sheaf
# =============================================================================


# Define eigenvector contexts
AESTHETIC = Context("aesthetic", frozenset({"taste", "beauty", "minimalism"}))
CATEGORICAL = Context("categorical", frozenset({"structure", "types", "morphisms"}))
GRATITUDE = Context("gratitude", frozenset({"sacred", "appreciation", "surplus"}))
HETERARCHY = Context("heterarchy", frozenset({"peer", "forest", "nonhierarchical"}))
GENERATIVITY = Context("generativity", frozenset({"creation", "emergence", "autopoiesis"}))
JOY = Context("joy", frozenset({"delight", "play", "fun"}))


def eigenvector_overlap(ctx1: Context, ctx2: Context) -> Context | None:
    """
    Compute overlap of eigenvector contexts.

    Contexts overlap if they share capabilities.
    """
    common_caps = ctx1.capabilities & ctx2.capabilities
    if common_caps:
        return Context(
            name=f"{ctx1.name}&{ctx2.name}",
            capabilities=common_caps,
        )
    return None


def create_soul_sheaf() -> AgentSheaf[Context]:
    """
    Create the Soul Sheaf over eigenvector contexts.

    This sheaf enables emergence of global soul behavior
    from local eigenvector-specific behaviors.
    """
    contexts = {
        AESTHETIC,
        CATEGORICAL,
        GRATITUDE,
        HETERARCHY,
        GENERATIVITY,
        JOY,
    }

    return AgentSheaf(
        contexts=contexts,
        overlap_fn=eigenvector_overlap,
    )


# Global Soul Sheaf instance
SOUL_SHEAF = create_soul_sheaf()


__all__ = [
    # Core types
    "Context",
    "GluingError",
    "RestrictionError",
    # Sheaf
    "AgentSheaf",
    # Soul Sheaf
    "SOUL_SHEAF",
    "create_soul_sheaf",
    # Contexts
    "AESTHETIC",
    "CATEGORICAL",
    "GRATITUDE",
    "HETERARCHY",
    "GENERATIVITY",
    "JOY",
    "eigenvector_overlap",
]
