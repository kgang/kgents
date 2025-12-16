"""
CrownSymbiont: Wraps Crown Jewel surface handlers with D-gent infrastructure.

The Crown Symbiont pattern separates pure handler logic from state infrastructure:
- Surface handlers remain pure: (I, S) → (O, S)
- D-gent triple provides persistence, history, and projections

The D-gent Triple:
- TemporalWitness: Event stream, drift detection, momentum
- SemanticManifold: Vectors, curvature, voids (Ma)
- RelationalLattice: Graph structure, lineage, entailment

Philosophy: "The surface is for experience; the substrate is for memory."

Spec: spec/protocols/crown-symbiont.md
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    TypeVar,
    Union,
    cast,
)

if TYPE_CHECKING:
    from agents.d.lattice import RelationalLattice
    from agents.d.manifold import SemanticManifold
    from agents.d.witness import TemporalWitness

from .triple_backed_memory import TripleBackedMemory

I = TypeVar("I")  # Input type
O = TypeVar("O")  # Output type
S = TypeVar("S")  # State type


@dataclass
class CrownTripleConfig:
    """
    Configuration for D-gent triple components per Crown path.

    Each aspect specifies how the component is used:
    - witness_aspect: How TemporalWitness is used (timeline, record, query, etc.)
    - manifold_aspect: How SemanticManifold is used (embed, search, topology, etc.)
    - lattice_aspect: How RelationalLattice is used (graph, link, traverse, etc.)

    None means the component is not used for this path.
    """

    witness_aspect: str | None = None
    manifold_aspect: str | None = None
    lattice_aspect: str | None = None

    @property
    def uses_witness(self) -> bool:
        return self.witness_aspect is not None

    @property
    def uses_manifold(self) -> bool:
        return self.manifold_aspect is not None

    @property
    def uses_lattice(self) -> bool:
        return self.lattice_aspect is not None


@dataclass
class CrownSymbiont(Generic[I, O, S]):
    """
    Wraps a Crown Jewel surface handler with D-gent infrastructure.

    The logic function remains pure: (I, S) → (O, S)
    The D-gent triple provides:
        - TemporalWitness: Event sourcing, drift detection, momentum
        - SemanticManifold: Embeddings, curvature, voids
        - RelationalLattice: Graph structure, lineage, entailment

    Principle: Surface handlers are pure projections of state;
               the D-gent triple IS the state.

    Example:
        >>> async def capture_logic(input: CaptureInput, state: MemoryState):
        ...     crystal = create_crystal(input.content)
        ...     new_state = state.with_crystal(crystal)
        ...     return CaptureResult(crystal_id=crystal.id), new_state
        ...
        >>> symbiont = CrownSymbiont(
        ...     logic=capture_logic,
        ...     witness=TemporalWitness(...),
        ...     manifold=SemanticManifold(...),
        ...     lattice=RelationalLattice(...),
        ... )
        >>> result = await symbiont.invoke(CaptureInput(content="hello"))
    """

    # The pure handler logic
    logic: Union[
        Callable[[I, S], tuple[O, S]],
        Callable[[I, S], Awaitable[tuple[O, S]]],
    ]

    # The D-gent triple (any can be None if not needed for this path)
    witness: "TemporalWitness[Any, S] | None" = None
    manifold: "SemanticManifold[S] | None" = None
    lattice: "RelationalLattice[S] | None" = None

    # Initial state (required if witness is None)
    initial_state: S | None = None

    # Configuration
    config: CrownTripleConfig = field(default_factory=CrownTripleConfig)

    # Internal triple-backed memory
    _memory: TripleBackedMemory[S] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Wire the triple-backed memory."""
        self._memory = TripleBackedMemory(
            witness=self.witness,
            manifold=self.manifold,
            lattice=self.lattice,
            initial_state=self.initial_state,
        )

    @property
    def name(self) -> str:
        """Name for composition chains."""
        logic_name = getattr(self.logic, "__name__", "logic")
        return f"CrownSymbiont({logic_name})"

    async def invoke(self, input_data: I) -> O:
        """
        Execute the stateful computation.

        Steps:
        1. Load current state from D-gent triple
        2. Run pure logic: (input, state) → (output, new_state)
        3. Save new state to D-gent triple (events, embeddings, links)
        4. Return output
        """
        # 1. Load current state
        current_state = await self._memory.load()

        # 2. Pure computation (detect sync vs async)
        result: tuple[O, S]
        if asyncio.iscoroutinefunction(self.logic):
            result = await self.logic(input_data, current_state)
        else:
            sync_logic = cast(Callable[[I, S], tuple[O, S]], self.logic)
            result = sync_logic(input_data, current_state)

        output, new_state = result

        # 3. Save to D-gent triple
        await self._memory.save(new_state, context={"input": input_data})

        # 4. Return output
        return output

    # === Temporal Affordances (from Witness) ===

    async def event_stream(
        self, window: timedelta | None = None
    ) -> list[dict[str, Any]]:
        """
        Get event history from TemporalWitness.

        Args:
            window: Time window to query (default: 1 hour)

        Returns:
            List of timeline entries with timestamp, state, event
        """
        if self.witness is None:
            return []

        entries = await self.witness.timeline(window or timedelta(hours=1))
        return [
            {
                "timestamp": e.timestamp.isoformat()
                if hasattr(e, "timestamp")
                else None,
                "state": e.state if hasattr(e, "state") else e,
                "event": e.event if hasattr(e, "event") else None,
            }
            for e in entries
        ]

    async def detect_drift(self, trajectory: str) -> dict[str, Any]:
        """
        Detect behavioral drift in a trajectory.

        Args:
            trajectory: Name of trajectory to check (e.g., "mood", "decisions")

        Returns:
            Drift report with severity, magnitude, explanation
        """
        if self.witness is None:
            return {"drift_detected": False, "reason": "No witness configured"}

        try:
            report = await self.witness.check_drift(trajectory)
            return {
                "drift_detected": report.drift_detected,
                "severity": report.severity.value
                if hasattr(report.severity, "value")
                else str(report.severity),
                "magnitude": report.magnitude,
                "explanation": report.explanation,
            }
        except Exception as e:
            return {"drift_detected": False, "error": str(e)}

    async def momentum(self) -> dict[str, Any]:
        """
        Get semantic velocity of state.

        Returns:
            Momentum vector with direction and magnitude
        """
        if self.witness is None:
            return {"magnitude": 0.0, "direction": None}

        try:
            vec = await self.witness.momentum()
            return {
                "magnitude": vec.magnitude if hasattr(vec, "magnitude") else 0.0,
                "direction": vec.direction if hasattr(vec, "direction") else None,
                "values": list(vec.values) if hasattr(vec, "values") else [],
            }
        except Exception as e:
            return {"magnitude": 0.0, "error": str(e)}

    async def entropy(self, window: timedelta | None = None) -> float:
        """
        Get entropy (rate of change) over a window.

        Returns:
            Entropy value 0.0 (calm) to 1.0 (chaotic)
        """
        if self.witness is None:
            return 0.0

        try:
            return await self.witness.entropy(window or timedelta(hours=1))
        except Exception:
            return 0.0

    # === Semantic Affordances (from Manifold) ===

    async def neighbors(self, state: S, radius: float = 0.5) -> list[S]:
        """
        Find semantically similar states.

        Args:
            state: Reference state
            radius: Search radius in semantic space

        Returns:
            List of similar states
        """
        if self.manifold is None:
            return []

        try:
            point = await self.manifold.embed(state)
            return await self.manifold.neighbors(point, radius)
        except Exception:
            return []

    async def curvature_at(self, state: S) -> float:
        """
        Get local semantic complexity.

        High curvature = conceptual boundary (synthesis opportunity)
        Low curvature = stable semantic region

        Returns:
            Curvature value 0.0 (flat) to 1.0 (high)
        """
        if self.manifold is None:
            return 0.0

        try:
            point = await self.manifold.embed(state)
            return await self.manifold.curvature_at(point)
        except Exception:
            return 0.0

    async def voids_nearby(self, state: S) -> list[dict[str, Any]]:
        """
        Find unexplored regions (Ma) with generative potential.

        Returns:
            List of semantic voids with center, radius, potential
        """
        if self.manifold is None:
            return []

        try:
            point = await self.manifold.embed(state)
            void = await self.manifold.void_nearby(point)
            if void is None:
                return []
            return [
                {
                    "radius": void.radius,
                    "potential": void.potential,
                    "nearest_concepts": void.nearest_concepts,
                    "suggested_exploration": void.suggested_exploration,
                }
            ]
        except Exception:
            return []

    # === Relational Affordances (from Lattice) ===

    async def lineage(self, node_id: str) -> list[str]:
        """
        Get ancestry chain (provenance).

        Args:
            node_id: Node to trace lineage from

        Returns:
            List of ancestor node IDs
        """
        if self.lattice is None:
            return []

        try:
            return await self.lattice.lineage(node_id)
        except Exception:
            return []

    async def meet(self, a: str, b: str) -> str | None:
        """
        Find greatest common sub-state (what a and b have in common).

        Returns:
            Node ID of meet, or None if not found
        """
        if self.lattice is None:
            return None

        try:
            result = await self.lattice.meet(a, b)
            return result.node_id if result.found else None
        except Exception:
            return None

    async def join(self, a: str, b: str) -> str | None:
        """
        Find least common super-state (smallest containing both).

        Returns:
            Node ID of join, or None if not found
        """
        if self.lattice is None:
            return None

        try:
            result = await self.lattice.join(a, b)
            return result.node_id if result.found else None
        except Exception:
            return None

    async def entails(self, a: str, b: str) -> bool:
        """
        Check if a entails (implies) b.

        Returns:
            True if a ≤ b in the lattice order
        """
        if self.lattice is None:
            return False

        try:
            return await self.lattice.entails(a, b)
        except Exception:
            return False

    # === Projection Methods ===

    async def project_timeline(self, window: timedelta | None = None) -> dict[str, Any]:
        """
        Project temporal view from witness.

        Returns visualization data for timeline rendering.
        """
        events = await self.event_stream(window)
        return {
            "type": "timeline",
            "events": events,
            "count": len(events),
            "window_hours": (window or timedelta(hours=1)).total_seconds() / 3600,
        }

    async def project_topology(self) -> dict[str, Any]:
        """
        Project semantic topology from manifold.

        Returns visualization data for 2D/3D semantic space.
        """
        if self.manifold is None:
            return {"type": "topology", "entries": [], "dimension": 0}

        try:
            stats = await self.manifold.stats()
            return {
                "type": "topology",
                "dimension": stats.dimension,
                "total_entries": stats.total_entries,
                "num_clusters": stats.num_clusters,
                "average_curvature": stats.average_curvature,
                "void_count": stats.void_count,
                "coverage": stats.coverage,
            }
        except Exception as e:
            return {"type": "topology", "error": str(e)}

    async def project_graph(self, root: str | None = None) -> dict[str, Any]:
        """
        Project relational graph from lattice.

        Returns visualization data for knowledge graph rendering.
        """
        if self.lattice is None:
            return {"type": "graph", "nodes": [], "edges": []}

        try:
            stats = await self.lattice.stats()
            return {
                "type": "graph",
                "root": root,
                "total_nodes": stats.total_nodes,
                "total_edges": stats.total_edges,
                "depth": stats.depth,
                "num_atoms": stats.num_atoms,
                "num_coatoms": stats.num_coatoms,
                "is_bounded": stats.is_bounded,
            }
        except Exception as e:
            return {"type": "graph", "error": str(e)}

    async def project_holographic(self, focus: str | None = None) -> dict[str, Any]:
        """
        Synthesize all three D-gent projections.

        The holographic view shows:
        - Temporal layer: Events flowing through time
        - Semantic layer: Embeddings in curved space
        - Relational layer: Graph structure beneath

        These three layers are consistent because they derive
        from the same CrownSymbiont state.
        """
        return {
            "type": "holographic",
            "focus": focus,
            "temporal": await self.project_timeline(),
            "semantic": await self.project_topology(),
            "relational": await self.project_graph(root=focus),
        }


# === Composition Support ===


def compose_crown_symbionts(
    first: CrownSymbiont[I, Any, Any],
    second: CrownSymbiont[Any, O, Any],
) -> Callable[[I], Awaitable[O]]:
    """
    Compose two CrownSymbionts into a pipeline.

    Each stage:
    1. Loads state from its D-gent triple
    2. Applies pure logic
    3. Saves state to its D-gent triple

    The output of first becomes input to second.
    """

    async def composed(input_data: I) -> O:
        intermediate = await first.invoke(input_data)
        return await second.invoke(intermediate)

    return composed


# === Factory ===


def create_crown_symbiont(
    logic: Union[
        Callable[[I, S], tuple[O, S]],
        Callable[[I, S], Awaitable[tuple[O, S]]],
    ],
    initial_state: S,
    witness: "TemporalWitness[Any, S] | None" = None,
    manifold: "SemanticManifold[S] | None" = None,
    lattice: "RelationalLattice[S] | None" = None,
    config: CrownTripleConfig | None = None,
) -> CrownSymbiont[I, O, S]:
    """
    Factory for creating CrownSymbionts.

    Args:
        logic: Pure handler function (I, S) → (O, S)
        initial_state: Initial state value
        witness: Optional TemporalWitness for event sourcing
        manifold: Optional SemanticManifold for embeddings
        lattice: Optional RelationalLattice for relationships
        config: Optional configuration for triple usage

    Returns:
        Configured CrownSymbiont
    """
    return CrownSymbiont(
        logic=logic,
        witness=witness,
        manifold=manifold,
        lattice=lattice,
        initial_state=initial_state,
        config=config or CrownTripleConfig(),
    )


__all__ = [
    "CrownSymbiont",
    "CrownTripleConfig",
    "compose_crown_symbionts",
    "create_crown_symbiont",
]
