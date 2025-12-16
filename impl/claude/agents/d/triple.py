"""
D-gent Triple: The canonical Noosphere storage pattern.

The D-gent Triple combines three complementary memory systems:
- TemporalWitness: Event stream + drift detection + momentum
- SemanticManifold: Embeddings + curvature + voids (Ma)
- RelationalLattice: Graph + lineage + entailment

Philosophy: "Memory is not stored—it is witnessed, embedded, and related."

Usage:
    >>> triple = create_dgent_triple(
    ...     initial_state={"count": 0},
    ...     embedding_dimension=768,
    ...     lattice_path="data/my_lattice.json",
    ... )
    >>> await triple.save({"count": 1})
    >>> state = await triple.load()

Spec: spec/protocols/crown-symbiont.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Generic, List, TypeVar

from .errors import NoosphereError
from .lattice import RelationalLattice
from .stream import DriftReport, WitnessReport
from .witness import TemporalWitness

S = TypeVar("S")  # State type
E = TypeVar("E")  # Event type

# Optional numpy-dependent imports
try:
    from .manifold import ManifoldStats, SemanticManifold, SemanticPoint, SemanticVoid

    MANIFOLD_AVAILABLE = True
except ImportError:
    MANIFOLD_AVAILABLE = False
    SemanticManifold = None  # type: ignore
    SemanticPoint = None  # type: ignore
    SemanticVoid = None  # type: ignore
    ManifoldStats = None  # type: ignore


@dataclass
class TripleStats:
    """Statistics about the D-gent triple."""

    # Temporal stats
    event_count: int = 0
    oldest_event: datetime | None = None
    newest_event: datetime | None = None
    entropy: float = 0.0

    # Semantic stats (if manifold available)
    embedding_count: int = 0
    dimension: int = 0
    average_curvature: float = 0.0
    void_count: int = 0

    # Relational stats
    node_count: int = 0
    edge_count: int = 0
    lattice_depth: int = 0


@dataclass
class DgentTriple(Generic[S]):
    """
    The canonical D-gent triple: Witness + Manifold + Lattice.

    Provides unified access to all three Noosphere memory systems:
    - witness: TemporalWitness for event sourcing
    - manifold: SemanticManifold for embeddings (optional, requires numpy)
    - lattice: RelationalLattice for relationships

    The triple maintains coherence across all three systems:
    - Events are witnessed when state changes
    - State is embedded in semantic space
    - State transitions create lineage links

    Example:
        >>> triple = DgentTriple(
        ...     witness=TemporalWitness(fold=lambda s, e: e, initial={}),
        ...     manifold=SemanticManifold(dimension=768),
        ...     lattice=RelationalLattice(),
        ... )
        >>> await triple.save({"key": "value"})
    """

    witness: TemporalWitness[Any, S]
    manifold: "SemanticManifold[S] | None" = None
    lattice: RelationalLattice[S] | None = None

    # Tracking state
    _current_state: S | None = field(default=None, repr=False)
    _previous_node_id: str | None = field(default=None, repr=False)
    _node_counter: int = field(default=0, repr=False)

    # === DataAgent Protocol ===

    async def load(self) -> S:
        """Load current state from witness."""
        return await self.witness.current_state()

    async def save(self, state: S, context: dict[str, Any] | None = None) -> None:
        """
        Save state to all three triple components.

        Args:
            state: New state to save
            context: Optional context metadata
        """
        node_id = self._generate_node_id(state)

        # 1. Record to witness (temporal)
        await self.witness.observe(
            event=state,
            witness=WitnessReport(
                observer_id="dgent_triple",
                timestamp=datetime.now(),
                confidence=1.0,
            ),
        )

        # 2. Embed in manifold (semantic)
        if self.manifold is not None:
            try:
                point = await self.manifold.embed(state)
                await self.manifold.store(
                    id=node_id,
                    point=point,
                    state=state,
                )
            except Exception:
                pass  # Manifold errors are non-fatal

        # 3. Add to lattice (relational)
        if self.lattice is not None:
            try:
                await self.lattice.add(node_id, state)
                if self._previous_node_id:
                    from .graph import EdgeKind

                    await self.lattice.relate(
                        source=node_id,
                        target=self._previous_node_id,
                        edge=EdgeKind.DERIVED_FROM,
                    )
            except Exception:
                pass  # Lattice errors are non-fatal

        self._current_state = state
        self._previous_node_id = node_id

    async def history(self, limit: int | None = None) -> List[S]:
        """Get state history from witness."""
        timeline = await self.witness.timeline(timedelta(days=7))
        states = [e.state for e in timeline if hasattr(e, "state")]
        return states[:limit] if limit else states

    # === Temporal Affordances ===

    async def event_stream(self, hours: int = 24) -> List[dict[str, Any]]:
        """Get event stream from witness."""
        timeline = await self.witness.timeline(timedelta(hours=hours))
        return [
            {
                "timestamp": e.timestamp.isoformat()
                if hasattr(e, "timestamp")
                else None,
                "state": e.state if hasattr(e, "state") else e,
            }
            for e in timeline
        ]

    async def detect_drift(self, trajectory: str) -> DriftReport | None:
        """Detect behavioral drift in a trajectory."""
        try:
            return await self.witness.check_drift(trajectory)
        except Exception:
            return None

    async def momentum(self) -> dict[str, Any]:
        """Get semantic velocity."""
        try:
            vec = await self.witness.momentum()
            return {
                "magnitude": getattr(vec, "magnitude", 0.0),
                "direction": getattr(vec, "direction", None),
            }
        except Exception:
            return {"magnitude": 0.0, "direction": None}

    async def entropy(self, hours: int = 1) -> float:
        """Get system entropy."""
        try:
            return await self.witness.entropy(timedelta(hours=hours))
        except Exception:
            return 0.0

    # === Semantic Affordances ===

    async def neighbors(self, state: S, radius: float = 0.5) -> List[S]:
        """Find semantically similar states."""
        if self.manifold is None:
            return []
        try:
            point = await self.manifold.embed(state)
            return await self.manifold.neighbors(point, radius)
        except Exception:
            return []

    async def curvature_at(self, state: S) -> float:
        """Get local semantic complexity."""
        if self.manifold is None:
            return 0.0
        try:
            point = await self.manifold.embed(state)
            return await self.manifold.curvature_at(point)
        except Exception:
            return 0.0

    async def voids_nearby(self, state: S) -> List[Any]:
        """Find semantic voids (Ma)."""
        if self.manifold is None:
            return []
        try:
            point = await self.manifold.embed(state)
            void = await self.manifold.void_nearby(point)
            return [void] if void else []
        except Exception:
            return []

    # === Relational Affordances ===

    async def lineage(self, node_id: str) -> List[str]:
        """Get ancestry chain."""
        if self.lattice is None:
            return []
        try:
            return await self.lattice.lineage(node_id)
        except Exception:
            return []

    async def meet(self, a: str, b: str) -> str | None:
        """Find greatest common sub-state."""
        if self.lattice is None:
            return None
        try:
            result = await self.lattice.meet(a, b)
            return result.node_id if result.found else None
        except Exception:
            return None

    async def join(self, a: str, b: str) -> str | None:
        """Find least common super-state."""
        if self.lattice is None:
            return None
        try:
            result = await self.lattice.join(a, b)
            return result.node_id if result.found else None
        except Exception:
            return None

    # === Statistics ===

    async def stats(self) -> TripleStats:
        """Get statistics about the triple."""
        stats = TripleStats()

        # Temporal stats
        try:
            timeline = await self.witness.timeline(timedelta(days=365))
            stats.event_count = len(timeline)
            if timeline:
                timestamps = [e.timestamp for e in timeline if hasattr(e, "timestamp")]
                if timestamps:
                    stats.oldest_event = min(timestamps)
                    stats.newest_event = max(timestamps)
            stats.entropy = await self.entropy()
        except Exception:
            pass

        # Semantic stats
        if self.manifold is not None:
            try:
                manifold_stats = await self.manifold.stats()
                stats.embedding_count = manifold_stats.total_entries
                stats.dimension = manifold_stats.dimension
                stats.average_curvature = manifold_stats.average_curvature
                stats.void_count = manifold_stats.void_count
            except Exception:
                pass

        # Relational stats
        if self.lattice is not None:
            try:
                lattice_stats = await self.lattice.stats()
                stats.node_count = lattice_stats.total_nodes
                stats.edge_count = lattice_stats.total_edges
                stats.lattice_depth = lattice_stats.depth
            except Exception:
                pass

        return stats

    # === Private Helpers ===

    def _generate_node_id(self, state: S) -> str:
        """Generate unique node ID."""
        self._node_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        state_hash = abs(hash(str(state))) % 10000
        return f"triple_{timestamp}_{state_hash}_{self._node_counter}"


# =============================================================================
# Factory Functions
# =============================================================================


def create_dgent_triple(
    initial_state: S,
    fold: Callable[[S, Any], S] | None = None,
    embedding_dimension: int = 768,
    lattice_path: str | Path | None = None,
    enable_manifold: bool = True,
    enable_lattice: bool = True,
) -> DgentTriple[S]:
    """
    Create a D-gent triple with all three components.

    Args:
        initial_state: Initial state value
        fold: Event fold function (default: replace state with event)
        embedding_dimension: Dimension for semantic embeddings
        lattice_path: Path for lattice persistence
        enable_manifold: Enable SemanticManifold (requires numpy)
        enable_lattice: Enable RelationalLattice

    Returns:
        Configured DgentTriple

    Example:
        >>> triple = create_dgent_triple(
        ...     initial_state={"count": 0},
        ...     embedding_dimension=384,
        ...     lattice_path="data/my_lattice.json",
        ... )
    """
    # Default fold: replace state with event
    if fold is None:
        fold = lambda s, e: e  # noqa: E731

    # Create witness (always)
    witness: TemporalWitness[Any, S] = TemporalWitness(
        fold=fold,
        initial=initial_state,
    )

    # Create manifold (if available and enabled)
    manifold = None
    if enable_manifold and MANIFOLD_AVAILABLE and SemanticManifold is not None:
        try:
            manifold = SemanticManifold(dimension=embedding_dimension)
        except Exception:
            pass

    # Create lattice (if enabled)
    lattice = None
    if enable_lattice:
        try:
            lattice = RelationalLattice(
                persistence_path=str(lattice_path) if lattice_path else None
            )
        except Exception:
            pass

    return DgentTriple(
        witness=witness,
        manifold=manifold,
        lattice=lattice,
    )


def create_witness_only(
    initial_state: S,
    fold: Callable[[S, Any], S] | None = None,
) -> DgentTriple[S]:
    """Create a triple with only TemporalWitness (no manifold or lattice)."""
    return create_dgent_triple(
        initial_state=initial_state,
        fold=fold,
        enable_manifold=False,
        enable_lattice=False,
    )


def create_temporal_semantic(
    initial_state: S,
    embedding_dimension: int = 768,
) -> DgentTriple[S]:
    """Create a triple with Witness + Manifold (no lattice)."""
    return create_dgent_triple(
        initial_state=initial_state,
        embedding_dimension=embedding_dimension,
        enable_lattice=False,
    )


def create_temporal_relational(
    initial_state: S,
    lattice_path: str | Path | None = None,
) -> DgentTriple[S]:
    """Create a triple with Witness + Lattice (no manifold)."""
    return create_dgent_triple(
        initial_state=initial_state,
        lattice_path=lattice_path,
        enable_manifold=False,
    )


__all__ = [
    "DgentTriple",
    "TripleStats",
    "create_dgent_triple",
    "create_witness_only",
    "create_temporal_semantic",
    "create_temporal_relational",
    "MANIFOLD_AVAILABLE",
]
