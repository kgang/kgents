"""
Crown D-gent Mappings Registry

Maps every self.* and time.* Crown Jewel path to its D-gent triple configuration:
- TemporalWitness aspect (event stream, drift detection, momentum)
- SemanticManifold aspect (embeddings, curvature, voids)
- RelationalLattice aspect (graph, lineage, entailment)

This registry enables automatic wiring of CrownSymbiont instances
with the correct D-gent triple configuration per path.

Spec: spec/protocols/crown-symbiont.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from .crown_symbiont import CrownSymbiont, CrownTripleConfig

I = TypeVar("I")
O = TypeVar("O")
S = TypeVar("S")


# =============================================================================
# D-gent Triple Mappings
# =============================================================================

CROWN_DGENT_MAPPINGS: dict[str, CrownTripleConfig] = {
    # =========================================================================
    # self.memory.* (Holographic Second Brain)
    # =========================================================================
    "self.memory.manifest": CrownTripleConfig(
        witness_aspect="timeline",  # Show recent memory events
        manifold_aspect="topology",  # Memory curvature map
        lattice_aspect="graph",  # Memory relationships
    ),
    "self.memory.capture": CrownTripleConfig(
        witness_aspect="record",  # Log capture event
        manifold_aspect="embed",  # Create embedding
        lattice_aspect="link",  # Link to related crystals
    ),
    "self.memory.recall": CrownTripleConfig(
        witness_aspect="query",  # Find in history
        manifold_aspect="search",  # Semantic retrieval
        lattice_aspect="traverse",  # Follow relationships
    ),
    "self.memory.ghost.surface": CrownTripleConfig(
        witness_aspect="drift",  # Detect forgotten patterns
        manifold_aspect="voids",  # Find semantic gaps
        lattice_aspect="orphans",  # Find disconnected nodes
    ),
    "self.memory.ghost.dismiss": CrownTripleConfig(
        witness_aspect="record",  # Log dismissal
        manifold_aspect=None,  # No embedding needed
        lattice_aspect="archive",  # Archive ghost node
    ),
    "self.memory.cartography.manifest": CrownTripleConfig(
        witness_aspect=None,  # No temporal aspect
        manifold_aspect="topology",  # Show semantic map
        lattice_aspect="graph",  # Show relationship graph
    ),
    "self.memory.cartography.navigate": CrownTripleConfig(
        witness_aspect=None,  # No temporal aspect
        manifold_aspect="geodesic",  # Path through semantic space
        lattice_aspect="traverse",  # Graph traversal
    ),
    # =========================================================================
    # self.tokens.* (Atelier Experience Platform)
    # =========================================================================
    "self.tokens.manifest": CrownTripleConfig(
        witness_aspect="timeline",  # Token balance history
        manifold_aspect=None,  # Tokens not embedded
        lattice_aspect="balance_graph",  # Token flow graph
    ),
    "self.tokens.purchase": CrownTripleConfig(
        witness_aspect="record",  # Log purchase event
        manifold_aspect=None,  # Purchases not embedded
        lattice_aspect="session_link",  # Link to session
    ),
    # =========================================================================
    # self.credits.* (Coalition Forge)
    # =========================================================================
    "self.credits.manifest": CrownTripleConfig(
        witness_aspect="timeline",  # Credit history
        manifold_aspect=None,  # Credits not embedded
        lattice_aspect="allocation_graph",  # Credit allocation
    ),
    "self.credits.purchase": CrownTripleConfig(
        witness_aspect="record",  # Log purchase event
        manifold_aspect=None,  # Purchases not embedded
        lattice_aspect="session_link",  # Link to session
    ),
    # =========================================================================
    # self.consent.* (Punchdrunk Park)
    # =========================================================================
    "self.consent.manifest": CrownTripleConfig(
        witness_aspect="history",  # Consent ledger history
        manifold_aspect=None,  # Consents not embedded
        lattice_aspect="consent_chain",  # Force/apology chain
    ),
    "self.consent.force": CrownTripleConfig(
        witness_aspect="record",  # Log force event
        manifold_aspect=None,  # Forces not embedded
        lattice_aspect="apology_link",  # Link apology to force
    ),
    # =========================================================================
    # self.forest.* (The Gardener)
    # =========================================================================
    "self.forest.manifest": CrownTripleConfig(
        witness_aspect="evolution",  # Plan evolution timeline
        manifold_aspect=None,  # Plans not embedded (yet)
        lattice_aspect="dependency_graph",  # Plan dependencies
    ),
    "self.forest.evolve": CrownTripleConfig(
        witness_aspect="record",  # Log evolution event
        manifold_aspect=None,  # Evolutions not embedded
        lattice_aspect="proposal_chain",  # Link proposals
    ),
    # =========================================================================
    # self.meta.* (The Gardener)
    # =========================================================================
    "self.meta.append": CrownTripleConfig(
        witness_aspect="record",  # Log meta update
        manifold_aspect="semantic_index",  # Index meta content
        lattice_aspect=None,  # No graph structure
    ),
    # =========================================================================
    # time.inhabit.* (Punchdrunk Park)
    # =========================================================================
    "time.inhabit.witness": CrownTripleConfig(
        witness_aspect="replay",  # Session replay
        manifold_aspect=None,  # Sessions not embedded
        lattice_aspect="character_graph",  # Character interactions
    ),
    # =========================================================================
    # time.simulation.* (Domain Simulation Engine)
    # =========================================================================
    "time.simulation.witness": CrownTripleConfig(
        witness_aspect="replay",  # Audit replay
        manifold_aspect=None,  # Simulations not embedded
        lattice_aspect="causality_graph",  # Event causality
    ),
    "time.simulation.export": CrownTripleConfig(
        witness_aspect="export",  # Export events
        manifold_aspect=None,  # No embedding needed
        lattice_aspect="compliance_graph",  # Compliance structure
    ),
}


# =============================================================================
# Helper Functions
# =============================================================================


def get_triple_config(path: str) -> CrownTripleConfig | None:
    """
    Get the D-gent triple configuration for a Crown path.

    Args:
        path: AGENTESE path (e.g., "self.memory.capture")

    Returns:
        CrownTripleConfig or None if path not mapped
    """
    return CROWN_DGENT_MAPPINGS.get(path)


def is_crown_path(path: str) -> bool:
    """Check if path is a mapped Crown path."""
    return path in CROWN_DGENT_MAPPINGS


def needs_witness(path: str) -> bool:
    """Check if path requires TemporalWitness."""
    config = CROWN_DGENT_MAPPINGS.get(path)
    return config is not None and config.uses_witness


def needs_manifold(path: str) -> bool:
    """Check if path requires SemanticManifold."""
    config = CROWN_DGENT_MAPPINGS.get(path)
    return config is not None and config.uses_manifold


def needs_lattice(path: str) -> bool:
    """Check if path requires RelationalLattice."""
    config = CROWN_DGENT_MAPPINGS.get(path)
    return config is not None and config.uses_lattice


def list_paths_by_aspect(aspect: str) -> list[str]:
    """
    List paths that use a specific aspect.

    Args:
        aspect: Aspect name (e.g., "record", "timeline", "embed")

    Returns:
        List of paths using that aspect in any triple component
    """
    result = []
    for path, config in CROWN_DGENT_MAPPINGS.items():
        if (
            config.witness_aspect == aspect
            or config.manifold_aspect == aspect
            or config.lattice_aspect == aspect
        ):
            result.append(path)
    return result


def list_paths_by_context(context: str) -> list[str]:
    """
    List paths by AGENTESE context.

    Args:
        context: One of "self", "time"

    Returns:
        List of paths in that context
    """
    return [p for p in CROWN_DGENT_MAPPINGS if p.startswith(f"{context}.")]


# =============================================================================
# Factory Integration
# =============================================================================


def create_symbiont_for_path(
    path: str,
    logic: Callable[[I, S], tuple[O, S]],
    initial_state: S,
    **kwargs: Any,
) -> CrownSymbiont[I, O, S] | None:
    """
    Create a CrownSymbiont configured for a specific path.

    Uses CROWN_DGENT_MAPPINGS to determine which D-gent triple
    components to create.

    Args:
        path: AGENTESE path (e.g., "self.memory.capture")
        logic: Pure handler function
        initial_state: Initial state value
        **kwargs: Additional arguments passed to D-gent constructors

    Returns:
        Configured CrownSymbiont or None if path not mapped
    """
    config = CROWN_DGENT_MAPPINGS.get(path)
    if config is None:
        return None

    # Lazy imports to avoid circular dependencies
    witness: Any = None
    manifold: Any = None
    lattice: Any = None

    if config.uses_witness:
        try:
            from agents.d.witness import TemporalWitness

            witness = TemporalWitness(
                fold=lambda s, e: e,  # Simple event replacement
                initial=initial_state,
                **kwargs.get("witness_kwargs", {}),
            )
        except ImportError:
            pass

    if config.uses_manifold:
        try:
            from agents.d.manifold import SemanticManifold

            dimension = kwargs.get("manifold_dimension", 768)
            manifold = SemanticManifold(
                dimension=dimension,
                **kwargs.get("manifold_kwargs", {}),
            )
        except ImportError:
            pass

    if config.uses_lattice:
        try:
            from agents.d.lattice import RelationalLattice

            persistence_path = kwargs.get(
                "lattice_path", f"data/{path.replace('.', '_')}_lattice.json"
            )
            lattice = RelationalLattice(
                persistence_path=persistence_path,
                **kwargs.get("lattice_kwargs", {}),
            )
        except ImportError:
            pass

    return CrownSymbiont(
        logic=logic,
        witness=witness,
        manifold=manifold,
        lattice=lattice,
        initial_state=initial_state,
        config=config,
    )


# =============================================================================
# Statistics
# =============================================================================


@dataclass
class MappingStats:
    """Statistics about the Crown D-gent mappings."""

    total_paths: int
    self_paths: int
    time_paths: int
    paths_with_witness: int
    paths_with_manifold: int
    paths_with_lattice: int
    unique_witness_aspects: list[str]
    unique_manifold_aspects: list[str]
    unique_lattice_aspects: list[str]


def get_mapping_stats() -> MappingStats:
    """Get statistics about the Crown D-gent mappings."""
    witness_aspects = set()
    manifold_aspects = set()
    lattice_aspects = set()

    for config in CROWN_DGENT_MAPPINGS.values():
        if config.witness_aspect:
            witness_aspects.add(config.witness_aspect)
        if config.manifold_aspect:
            manifold_aspects.add(config.manifold_aspect)
        if config.lattice_aspect:
            lattice_aspects.add(config.lattice_aspect)

    return MappingStats(
        total_paths=len(CROWN_DGENT_MAPPINGS),
        self_paths=len(list_paths_by_context("self")),
        time_paths=len(list_paths_by_context("time")),
        paths_with_witness=sum(
            1 for c in CROWN_DGENT_MAPPINGS.values() if c.uses_witness
        ),
        paths_with_manifold=sum(
            1 for c in CROWN_DGENT_MAPPINGS.values() if c.uses_manifold
        ),
        paths_with_lattice=sum(
            1 for c in CROWN_DGENT_MAPPINGS.values() if c.uses_lattice
        ),
        unique_witness_aspects=sorted(witness_aspects),
        unique_manifold_aspects=sorted(manifold_aspects),
        unique_lattice_aspects=sorted(lattice_aspects),
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Main registry
    "CROWN_DGENT_MAPPINGS",
    # Query functions
    "get_triple_config",
    "is_crown_path",
    "needs_witness",
    "needs_manifold",
    "needs_lattice",
    "list_paths_by_aspect",
    "list_paths_by_context",
    # Factory
    "create_symbiont_for_path",
    # Statistics
    "MappingStats",
    "get_mapping_stats",
]
