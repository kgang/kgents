"""
TripleBackedMemory: Memory backed by the D-gent triple.

Implements the DataAgent protocol using three coordinated components:
- TemporalWitness: Event sourcing, provides load() via current state
- SemanticManifold: Embeddings, provides semantic search
- RelationalLattice: Relationships, provides lineage tracking

On save():
1. Records event to witness (temporal)
2. Updates embedding in manifold (semantic)
3. Updates relationships in lattice (relational)

Philosophy: "State is not stored—it is witnessed, embedded, and related."

Spec: spec/protocols/crown-symbiont.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any, Generic, List, TypeVar

if TYPE_CHECKING:
    from agents.d.lattice import RelationalLattice
    from agents.d.manifold import SemanticManifold
    from agents.d.witness import TemporalWitness

S = TypeVar("S")  # State type


@dataclass
class WitnessReport:
    """Observation metadata for event recording."""

    observer_id: str
    timestamp: datetime
    confidence: float = 1.0
    context: dict[str, Any] | None = None


@dataclass
class TripleBackedMemory(Generic[S]):
    """
    Memory backed by the D-gent triple (Witness + Manifold + Lattice).

    Implements DataAgent[S] protocol:
    - load() reconstructs state from latest witness event
    - save() records event, updates embedding, updates lattice
    - history() returns state evolution from witness

    Each component is optional:
    - If witness is None, uses initial_state for load()
    - If manifold is None, skips embedding on save()
    - If lattice is None, skips relationship updates on save()

    Example:
        >>> memory = TripleBackedMemory(
        ...     witness=TemporalWitness(fold=lambda s, e: e, initial={}),
        ...     manifold=SemanticManifold(dimension=768),
        ...     lattice=RelationalLattice(),
        ... )
        >>> state = await memory.load()
        >>> await memory.save({"key": "value"})
    """

    witness: "TemporalWitness[Any, S] | None" = None
    manifold: "SemanticManifold[S] | None" = None
    lattice: "RelationalLattice[S] | None" = None
    initial_state: S | None = None

    # Internal state cache (for when witness is None)
    _current_state: S | None = None

    # Track previous node ID for lineage
    _previous_node_id: str | None = None

    # Counter for generating node IDs
    _node_counter: int = 0

    async def load(self) -> S:
        """
        Load current state from D-gent triple.

        Priority:
        1. TemporalWitness.current_state() if witness exists
        2. Cached _current_state if set
        3. initial_state if provided
        4. Empty dict as fallback

        Returns:
            Current state value
        """
        # Try witness first
        if self.witness is not None:
            try:
                return await self.witness.current_state()
            except Exception:
                pass

        # Fall back to cached state
        if self._current_state is not None:
            return self._current_state

        # Fall back to initial state
        if self.initial_state is not None:
            return self.initial_state

        # Last resort: return empty dict (type-cast to S)
        return {} if self._is_dict_state() else None  # type: ignore

    async def save(self, state: S, context: dict[str, Any] | None = None) -> None:
        """
        Save state to all D-gent triple components.

        Steps:
        1. Record event to witness (temporal layer)
        2. Update embedding in manifold (semantic layer)
        3. Update relationships in lattice (relational layer)

        Args:
            state: New state to save
            context: Optional context for the save (e.g., input that caused it)
        """
        # Generate node ID for this state
        node_id = self._generate_node_id(state)

        # 1. Event sourcing (Witness)
        if self.witness is not None:
            try:
                await self.witness.observe(
                    event=state,
                    witness=self._create_witness_report(context),
                )
            except Exception:
                # Log but don't fail the save
                pass

        # 2. Semantic embedding (Manifold)
        if self.manifold is not None:
            try:
                point = await self.manifold.embed(state)
                await self.manifold.store(
                    id=node_id,
                    point=point,
                    state=state,
                )
            except Exception:
                # Log but don't fail the save
                pass

        # 3. Relational update (Lattice)
        if self.lattice is not None:
            try:
                await self.lattice.add(node_id, state)

                # Link to previous state (lineage)
                if self._previous_node_id is not None:
                    from agents.d.graph import EdgeKind

                    await self.lattice.relate(
                        source=node_id,
                        target=self._previous_node_id,
                        edge=EdgeKind.DERIVED_FROM,
                    )
            except Exception:
                # Log but don't fail the save
                pass

        # Update tracking state
        self._current_state = state
        self._previous_node_id = node_id

    async def history(self, limit: int | None = None) -> List[S]:
        """
        Get state history from witness.

        Args:
            limit: Maximum number of historical states

        Returns:
            List of states, newest first
        """
        if self.witness is None:
            return []

        try:
            from datetime import timedelta

            timeline = await self.witness.timeline(timedelta(days=7))
            states = [entry.state for entry in timeline if hasattr(entry, "state")]
            return states[:limit] if limit else states
        except Exception:
            return []

    # === Private Helpers ===

    def _generate_node_id(self, state: S) -> str:
        """Generate unique node ID for state."""
        self._node_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        state_hash = abs(hash(str(state))) % 10000
        return f"state_{timestamp}_{state_hash}_{self._node_counter}"

    def _create_witness_report(
        self, context: dict[str, Any] | None = None
    ) -> WitnessReport:
        """Create witness report for event recording."""
        return WitnessReport(
            observer_id="triple_backed_memory",
            timestamp=datetime.now(),
            confidence=1.0,
            context=context,
        )

    def _is_dict_state(self) -> bool:
        """Check if state type is dict-like."""
        if self.initial_state is not None:
            return isinstance(self.initial_state, dict)
        if self._current_state is not None:
            return isinstance(self._current_state, dict)
        return True

    # === Query Helpers (expose D-gent triple affordances) ===

    async def semantic_neighbors(self, state: S, radius: float = 0.5) -> List[S]:
        """Find semantically similar states via manifold."""
        if self.manifold is None:
            return []

        try:
            point = await self.manifold.embed(state)
            return await self.manifold.neighbors(point, radius)
        except Exception:
            return []

    async def lineage_chain(self, node_id: str) -> List[str]:
        """Get ancestry chain via lattice."""
        if self.lattice is None:
            return []

        try:
            return await self.lattice.lineage(node_id)
        except Exception:
            return []

    async def event_timeline(self, hours: int = 24) -> List[dict[str, Any]]:
        """Get event timeline from witness."""
        if self.witness is None:
            return []

        try:
            from datetime import timedelta

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
        except Exception:
            return []


# === Factory Functions ===


def create_triple_backed_memory(
    initial_state: S,
    witness: "TemporalWitness[Any, S] | None" = None,
    manifold: "SemanticManifold[S] | None" = None,
    lattice: "RelationalLattice[S] | None" = None,
) -> TripleBackedMemory[S]:
    """
    Factory for creating TripleBackedMemory instances.

    Args:
        initial_state: Initial state value
        witness: Optional TemporalWitness
        manifold: Optional SemanticManifold
        lattice: Optional RelationalLattice

    Returns:
        Configured TripleBackedMemory
    """
    return TripleBackedMemory(
        witness=witness,
        manifold=manifold,
        lattice=lattice,
        initial_state=initial_state,
    )


__all__ = [
    "TripleBackedMemory",
    "WitnessReport",
    "create_triple_backed_memory",
]
