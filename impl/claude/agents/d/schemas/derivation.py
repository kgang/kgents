"""
D-gent Schema for ASHC DerivationPath.

Provides a Crystal contract for DerivationPath, enabling storage
via D-gent Universe.

Philosophy:
    "A DerivationPath stored is a proof preserved.
     A Crystal persisted is an axiom grounded."

This schema bridges the ASHC categorical types with D-gent's
storage system, preserving all categorical properties.

See: spec/protocols/unified-data-crystal.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from agents.d.universe import DataclassSchema

# =============================================================================
# DerivationPathCrystal - Frozen dataclass for Universe storage
# =============================================================================


@dataclass(frozen=True)
class DerivationPathCrystal:
    """
    Crystal contract for DerivationPath storage.

    This is the persistence-layer representation of DerivationPath.
    It mirrors the structure of DerivationPath but is optimized for
    serialization and storage via D-gent Universe.

    Mapping from DerivationPath:
        path_id -> path_id
        path_kind -> path_kind (as string)
        source_id -> source_id
        target_id -> target_id
        witnesses -> witnesses (list of dicts)
        galois_loss -> galois_loss
        principle_scores -> principle_scores
        kblock_lineage -> kblock_lineage (list)
        created_at -> created_at

    Philosophy:
        "The Crystal IS the frozen proof. Immutability IS integrity."
    """

    # Identity
    path_id: str
    path_kind: str  # PathKind.name (REFL, DERIVE, COMPOSE, etc.)

    # Endpoints
    source_id: str
    target_id: str

    # Evidence (serialized witnesses)
    witnesses: tuple[dict[str, Any], ...] = ()

    # Galois metrics
    galois_loss: float = 0.0
    principle_scores: dict[str, float] = field(default_factory=dict)

    # K-Block lineage
    kblock_lineage: tuple[str, ...] = ()

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def coherence(self) -> float:
        """Coherence = 1 - galois_loss."""
        return 1.0 - self.galois_loss

    @property
    def is_identity(self) -> bool:
        """Is this a reflexive/identity path?"""
        return self.path_kind == "REFL"

    @property
    def is_composed(self) -> bool:
        """Is this a composed path?"""
        return self.path_kind == "COMPOSE"

    @property
    def witness_count(self) -> int:
        """Number of witnesses."""
        return len(self.witnesses)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for Universe storage."""
        return {
            "path_id": self.path_id,
            "path_kind": self.path_kind,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "witnesses": list(self.witnesses),
            "galois_loss": self.galois_loss,
            "principle_scores": self.principle_scores,
            "kblock_lineage": list(self.kblock_lineage),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DerivationPathCrystal:
        """Deserialize from dictionary."""
        return cls(
            path_id=d["path_id"],
            path_kind=d["path_kind"],
            source_id=d["source_id"],
            target_id=d["target_id"],
            witnesses=tuple(d.get("witnesses", [])),
            galois_loss=d.get("galois_loss", 0.0),
            principle_scores=d.get("principle_scores", {}),
            kblock_lineage=tuple(d.get("kblock_lineage", [])),
            created_at=datetime.fromisoformat(d["created_at"])
            if "created_at" in d
            else datetime.now(UTC),
        )

    @classmethod
    def from_derivation_path(cls, path: Any) -> DerivationPathCrystal:
        """
        Create Crystal from a DerivationPath instance.

        Args:
            path: DerivationPath[Source, Target] instance

        Returns:
            DerivationPathCrystal ready for storage
        """
        return cls(
            path_id=path.path_id,
            path_kind=path.path_kind.name,
            source_id=path.source_id,
            target_id=path.target_id,
            witnesses=tuple(w.to_dict() for w in path.witnesses),
            galois_loss=path.galois_loss,
            principle_scores=path.principle_scores,
            kblock_lineage=path.kblock_lineage,
            created_at=path.created_at,
        )

    def to_derivation_path(self) -> Any:
        """
        Convert Crystal back to DerivationPath.

        Returns:
            DerivationPath instance

        Note:
            Imports DerivationPath at runtime to avoid circular imports.
        """
        from protocols.ashc.paths.types import (
            DerivationPath,
            DerivationWitness,
            PathKind,
        )

        return DerivationPath(
            path_id=self.path_id,
            path_kind=PathKind[self.path_kind],
            source_id=self.source_id,
            target_id=self.target_id,
            witnesses=tuple(DerivationWitness.from_dict(w) for w in self.witnesses),
            galois_loss=self.galois_loss,
            principle_scores=self.principle_scores,
            kblock_lineage=self.kblock_lineage,
            created_at=self.created_at,
        )


# =============================================================================
# Schema for Universe Registration
# =============================================================================

DERIVATION_PATH_SCHEMA = DataclassSchema(
    name="ashc.derivation_path",
    type_cls=DerivationPathCrystal,
)

# =============================================================================
# Helper Functions for Universe Operations
# =============================================================================


async def store_derivation_path(
    path: Any,
    universe: Any | None = None,
) -> str:
    """
    Store a DerivationPath in the Universe.

    Args:
        path: DerivationPath instance to store
        universe: Universe instance (uses global if None)

    Returns:
        The datum ID for retrieval
    """
    from agents.d.universe import get_universe

    univ = universe or get_universe()

    # Ensure schema is registered
    if "ashc.derivation_path" not in [s.name for s in univ._schemas.values()]:
        univ.register_schema(DERIVATION_PATH_SCHEMA)

    # Convert to Crystal and store
    crystal = DerivationPathCrystal.from_derivation_path(path)
    return await univ.store(crystal, "ashc.derivation_path")


async def get_derivation_path(
    path_id: str,
    universe: Any | None = None,
) -> Any | None:
    """
    Retrieve a DerivationPath from the Universe.

    Args:
        path_id: The datum ID (from store_derivation_path)
        universe: Universe instance (uses global if None)

    Returns:
        DerivationPath instance or None if not found
    """
    from agents.d.universe import get_universe

    univ = universe or get_universe()

    # Ensure schema is registered
    if "ashc.derivation_path" not in [s.name for s in univ._schemas.values()]:
        univ.register_schema(DERIVATION_PATH_SCHEMA)

    # Get and convert
    crystal = await univ.get(path_id)
    if crystal is None:
        return None

    if isinstance(crystal, DerivationPathCrystal):
        return crystal.to_derivation_path()

    # If we got raw data, try to deserialize
    if isinstance(crystal, dict):
        return DerivationPathCrystal.from_dict(crystal).to_derivation_path()

    return None


async def query_derivation_paths(
    source_id: str | None = None,
    target_id: str | None = None,
    path_kind: str | None = None,
    limit: int = 100,
    universe: Any | None = None,
) -> list[Any]:
    """
    Query DerivationPaths from the Universe.

    Args:
        source_id: Filter by source (optional)
        target_id: Filter by target (optional)
        path_kind: Filter by kind (optional)
        limit: Maximum results
        universe: Universe instance (uses global if None)

    Returns:
        List of matching DerivationPath instances
    """
    from agents.d.universe import Query, get_universe

    univ = universe or get_universe()

    # Ensure schema is registered
    if "ashc.derivation_path" not in [s.name for s in univ._schemas.values()]:
        univ.register_schema(DERIVATION_PATH_SCHEMA)

    # Query by schema
    q = Query(schema="ashc.derivation_path", limit=limit)
    crystals = await univ.query(q)

    # Filter in memory (Universe doesn't support arbitrary field filtering)
    results = []
    for crystal in crystals:
        if isinstance(crystal, DerivationPathCrystal):
            if source_id and crystal.source_id != source_id:
                continue
            if target_id and crystal.target_id != target_id:
                continue
            if path_kind and crystal.path_kind != path_kind:
                continue
            results.append(crystal.to_derivation_path())

    return results


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "DerivationPathCrystal",
    "DERIVATION_PATH_SCHEMA",
    "store_derivation_path",
    "get_derivation_path",
    "query_derivation_paths",
]
