"""
Personal Constitution Service for Zero Seed Governance.

Manages a user's discovered axioms as their personal constitution.
Tracks evolution over time and detects contradictions between axioms.

Philosophy:
    "A constitution is not a static document but a living covenant.
     Axioms may conflict, and contradictions reveal growth opportunities."

Key Concepts:
    - Constitution: Collection of discovered axioms
    - Evolution: Track how axioms change over time
    - Contradiction: L(A U B) > L(A) + L(B) + tau signals conflict

See: spec/protocols/zero-seed1/axiomatics.md
See: plans/enlightened-synthesis/00-master-synthesis.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import TYPE_CHECKING
from uuid import uuid4

from .axiom_discovery import (
    AXIOM_THRESHOLD,
    DiscoveredAxiom,
)
from .galois.galois_loss import (
    CONTRADICTION_TOLERANCE,
    ContradictionAnalysis,
    ContradictionType,
    GaloisLossComputer,
    LossCache,
    detect_contradiction,
)

if TYPE_CHECKING:
    pass


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

# Default contradiction tolerance (tau)
DEFAULT_CONTRADICTION_TOLERANCE: float = CONTRADICTION_TOLERANCE


# -----------------------------------------------------------------------------
# Data Types
# -----------------------------------------------------------------------------


class AxiomStatus(Enum):
    """Status of an axiom in the constitution."""

    ACTIVE = auto()  # Currently in force
    SUSPENDED = auto()  # Temporarily suspended (pending review)
    RETIRED = auto()  # No longer active
    CONFLICTING = auto()  # In conflict with another axiom


@dataclass
class ConstitutionalAxiom:
    """
    An axiom stored in the personal constitution.

    Extends DiscoveredAxiom with governance metadata.
    """

    id: str
    content: str
    loss: float
    stability: float
    confidence: float
    status: AxiomStatus = AxiomStatus.ACTIVE
    added_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    retired_at: datetime | None = None
    retirement_reason: str | None = None
    source_decisions: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_discovered(cls, axiom: DiscoveredAxiom) -> "ConstitutionalAxiom":
        """Create from a discovered axiom."""
        return cls(
            id=f"axiom-{uuid4().hex[:12]}",
            content=axiom.content,
            loss=axiom.loss,
            stability=axiom.stability,
            confidence=axiom.confidence,
            source_decisions=axiom.source_decisions,
        )

    def retire(self, reason: str) -> "ConstitutionalAxiom":
        """Return a retired copy of this axiom."""
        return ConstitutionalAxiom(
            id=self.id,
            content=self.content,
            loss=self.loss,
            stability=self.stability,
            confidence=self.confidence,
            status=AxiomStatus.RETIRED,
            added_at=self.added_at,
            retired_at=datetime.now(timezone.utc),
            retirement_reason=reason,
            source_decisions=self.source_decisions,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "content": self.content,
            "loss": self.loss,
            "stability": self.stability,
            "confidence": self.confidence,
            "status": self.status.name,
            "added_at": self.added_at.isoformat(),
            "retired_at": self.retired_at.isoformat() if self.retired_at else None,
            "retirement_reason": self.retirement_reason,
            "source_decisions": self.source_decisions,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ConstitutionalAxiom":
        """Create from dictionary."""
        return cls(
            id=str(data["id"]),
            content=str(data["content"]),
            loss=float(data["loss"]),  # type: ignore[arg-type]
            stability=float(data["stability"]),  # type: ignore[arg-type]
            confidence=float(data["confidence"]),  # type: ignore[arg-type]
            status=AxiomStatus[str(data["status"])],
            added_at=datetime.fromisoformat(str(data["added_at"])),
            retired_at=datetime.fromisoformat(str(data["retired_at"]))
            if data.get("retired_at")
            else None,
            retirement_reason=str(data["retirement_reason"])
            if data.get("retirement_reason")
            else None,
            source_decisions=list(data.get("source_decisions") or []),  # type: ignore[call-overload]
            metadata=dict(data.get("metadata") or {}),  # type: ignore[call-overload]
        )


@dataclass
class Contradiction:
    """
    A detected contradiction between two axioms.

    Captures the super-additive loss analysis and potential resolution.
    """

    axiom_a_id: str
    axiom_b_id: str
    axiom_a_content: str
    axiom_b_content: str
    strength: float  # Super-additive excess
    type: ContradictionType
    loss_a: float
    loss_b: float
    loss_combined: float
    synthesis_hint: str | None = None
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False
    resolution: str | None = None

    @property
    def is_strong(self) -> bool:
        """True if contradiction is strong (irreconcilable without synthesis)."""
        return self.type == ContradictionType.STRONG

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary."""
        return {
            "axiom_a_id": self.axiom_a_id,
            "axiom_b_id": self.axiom_b_id,
            "axiom_a_content": self.axiom_a_content,
            "axiom_b_content": self.axiom_b_content,
            "strength": self.strength,
            "type": self.type.name,
            "loss_a": self.loss_a,
            "loss_b": self.loss_b,
            "loss_combined": self.loss_combined,
            "synthesis_hint": self.synthesis_hint,
            "detected_at": self.detected_at.isoformat(),
            "resolved": self.resolved,
            "resolution": self.resolution,
        }


@dataclass
class ConstitutionSnapshot:
    """
    A snapshot of the constitution at a point in time.

    Used for tracking evolution.
    """

    timestamp: datetime
    axiom_count: int
    active_count: int
    average_loss: float
    axiom_ids: list[str]

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "axiom_count": self.axiom_count,
            "active_count": self.active_count,
            "average_loss": self.average_loss,
            "axiom_ids": self.axiom_ids,
        }


@dataclass
class Constitution:
    """
    A personal constitution: a collection of axioms.

    Attributes:
        id: Unique constitution ID
        name: Optional name for the constitution
        axioms: Dictionary of axiom_id -> ConstitutionalAxiom
        contradictions: List of detected contradictions
        snapshots: Evolution snapshots over time
        created_at: When the constitution was created
        updated_at: When last modified
    """

    id: str = field(default_factory=lambda: f"constitution-{uuid4().hex[:12]}")
    name: str = "Personal Constitution"
    axioms: dict[str, ConstitutionalAxiom] = field(default_factory=dict)
    contradictions: list[Contradiction] = field(default_factory=list)
    snapshots: list[ConstitutionSnapshot] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def active_axioms(self) -> list[ConstitutionalAxiom]:
        """Get all active axioms."""
        return [a for a in self.axioms.values() if a.status == AxiomStatus.ACTIVE]

    @property
    def axiom_count(self) -> int:
        """Total number of axioms (all statuses)."""
        return len(self.axioms)

    @property
    def active_count(self) -> int:
        """Number of active axioms."""
        return len(self.active_axioms)

    @property
    def average_loss(self) -> float:
        """Average loss of active axioms."""
        active = self.active_axioms
        if not active:
            return 1.0
        return sum(a.loss for a in active) / len(active)

    @property
    def unresolved_contradictions(self) -> list[Contradiction]:
        """Get unresolved contradictions."""
        return [c for c in self.contradictions if not c.resolved]

    def snapshot(self) -> ConstitutionSnapshot:
        """Create a snapshot of current state."""
        return ConstitutionSnapshot(
            timestamp=datetime.now(timezone.utc),
            axiom_count=self.axiom_count,
            active_count=self.active_count,
            average_loss=self.average_loss,
            axiom_ids=[a.id for a in self.active_axioms],
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "axioms": {k: v.to_dict() for k, v in self.axioms.items()},
            "contradictions": [c.to_dict() for c in self.contradictions],
            "snapshots": [s.to_dict() for s in self.snapshots],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "active_count": self.active_count,
            "average_loss": self.average_loss,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Constitution":
        """Create from dictionary."""
        axioms_data = data.get("axioms", {})
        axioms_dict: dict[str, ConstitutionalAxiom] = {}
        if isinstance(axioms_data, dict):
            for k, v in axioms_data.items():
                if isinstance(v, dict):
                    axioms_dict[k] = ConstitutionalAxiom.from_dict(v)
        return cls(
            id=str(data["id"]),
            name=str(data.get("name", "Personal Constitution")),
            axioms=axioms_dict,
            contradictions=[],  # Contradictions re-detected on load
            snapshots=[],  # Snapshots re-computed on demand
            created_at=datetime.fromisoformat(str(data["created_at"])),
            updated_at=datetime.fromisoformat(str(data["updated_at"])),
        )


# -----------------------------------------------------------------------------
# Personal Constitution Service
# -----------------------------------------------------------------------------


class PersonalConstitutionService:
    """
    Service for managing personal constitutions.

    Provides:
    - Add/retire axioms
    - Detect contradictions between axioms
    - Track constitution evolution
    - Query constitution state

    Example:
        >>> service = PersonalConstitutionService()
        >>> constitution = service.create_constitution("My Values")
        >>> constitution = await service.add_axiom(constitution, discovered_axiom)
        >>> contradictions = await service.detect_contradictions(constitution)
    """

    def __init__(
        self,
        computer: GaloisLossComputer | None = None,
        cache: LossCache | None = None,
    ) -> None:
        """
        Initialize constitution service.

        Args:
            computer: Optional GaloisLossComputer for contradiction detection
            cache: Optional LossCache for caching loss computations
        """
        self._cache = cache or LossCache()
        self._computer = computer or GaloisLossComputer(cache=self._cache)

    def create_constitution(self, name: str = "Personal Constitution") -> Constitution:
        """
        Create a new empty constitution.

        Args:
            name: Name for the constitution

        Returns:
            New Constitution instance
        """
        return Constitution(name=name)

    async def add_axiom(
        self,
        constitution: Constitution,
        axiom: DiscoveredAxiom,
        check_contradictions: bool = True,
    ) -> Constitution:
        """
        Add an axiom to the constitution.

        Optionally checks for contradictions with existing axioms.

        Args:
            constitution: The constitution to update
            axiom: The axiom to add
            check_contradictions: Whether to check for contradictions

        Returns:
            Updated constitution
        """
        # Only add if loss qualifies
        if axiom.loss >= AXIOM_THRESHOLD:
            raise ValueError(f"Axiom loss {axiom.loss:.3f} >= threshold {AXIOM_THRESHOLD}")

        # Check for duplicate content
        for existing in constitution.active_axioms:
            if existing.content.lower() == axiom.content.lower():
                raise ValueError(f"Axiom already exists: {existing.id}")

        # Create constitutional axiom
        const_axiom = ConstitutionalAxiom.from_discovered(axiom)
        constitution.axioms[const_axiom.id] = const_axiom
        constitution.updated_at = datetime.now(timezone.utc)

        # Check contradictions if requested
        if check_contradictions:
            for existing in constitution.active_axioms:
                if existing.id == const_axiom.id:
                    continue

                analysis = await detect_contradiction(
                    const_axiom.content,
                    existing.content,
                    self._computer,
                )

                if analysis.is_contradiction:
                    contradiction = Contradiction(
                        axiom_a_id=const_axiom.id,
                        axiom_b_id=existing.id,
                        axiom_a_content=const_axiom.content,
                        axiom_b_content=existing.content,
                        strength=analysis.strength,
                        type=analysis.type,
                        loss_a=analysis.loss_a,
                        loss_b=analysis.loss_b,
                        loss_combined=analysis.loss_combined,
                        synthesis_hint=analysis.synthesis_hint.content
                        if analysis.synthesis_hint
                        else None,
                    )
                    constitution.contradictions.append(contradiction)

        # Take snapshot
        constitution.snapshots.append(constitution.snapshot())

        return constitution

    async def retire_axiom(
        self,
        constitution: Constitution,
        axiom_id: str,
        reason: str,
    ) -> Constitution:
        """
        Retire an axiom from the constitution.

        The axiom is not deleted but marked as retired.

        Args:
            constitution: The constitution to update
            axiom_id: ID of axiom to retire
            reason: Reason for retirement

        Returns:
            Updated constitution
        """
        if axiom_id not in constitution.axioms:
            raise ValueError(f"Axiom not found: {axiom_id}")

        axiom = constitution.axioms[axiom_id]
        constitution.axioms[axiom_id] = axiom.retire(reason)
        constitution.updated_at = datetime.now(timezone.utc)

        # Mark related contradictions as resolved
        for contradiction in constitution.contradictions:
            if axiom_id in (contradiction.axiom_a_id, contradiction.axiom_b_id):
                contradiction.resolved = True
                contradiction.resolution = f"Axiom {axiom_id} retired: {reason}"

        # Take snapshot
        constitution.snapshots.append(constitution.snapshot())

        return constitution

    async def detect_contradictions(
        self,
        constitution: Constitution,
        tolerance: float = DEFAULT_CONTRADICTION_TOLERANCE,
    ) -> list[Contradiction]:
        """
        Detect all contradictions between active axioms.

        A contradiction exists when L(A U B) > L(A) + L(B) + tau.

        Args:
            constitution: The constitution to analyze
            tolerance: Tau tolerance for super-additivity

        Returns:
            List of detected contradictions
        """
        active = constitution.active_axioms
        contradictions: list[Contradiction] = []

        # Check all pairs
        for i, axiom_a in enumerate(active):
            for axiom_b in active[i + 1 :]:
                analysis = await detect_contradiction(
                    axiom_a.content,
                    axiom_b.content,
                    self._computer,
                )

                # Check against provided tolerance
                is_contradiction = analysis.strength > tolerance

                if is_contradiction:
                    contradiction = Contradiction(
                        axiom_a_id=axiom_a.id,
                        axiom_b_id=axiom_b.id,
                        axiom_a_content=axiom_a.content,
                        axiom_b_content=axiom_b.content,
                        strength=analysis.strength,
                        type=analysis.type,
                        loss_a=analysis.loss_a,
                        loss_b=analysis.loss_b,
                        loss_combined=analysis.loss_combined,
                        synthesis_hint=analysis.synthesis_hint.content
                        if analysis.synthesis_hint
                        else None,
                    )
                    contradictions.append(contradiction)

        return contradictions

    async def refresh_contradictions(
        self,
        constitution: Constitution,
        tolerance: float = DEFAULT_CONTRADICTION_TOLERANCE,
    ) -> Constitution:
        """
        Refresh all contradiction detection for constitution.

        Clears existing unresolved contradictions and re-detects.

        Args:
            constitution: Constitution to refresh
            tolerance: Tau tolerance

        Returns:
            Updated constitution with fresh contradictions
        """
        # Remove unresolved contradictions
        constitution.contradictions = [c for c in constitution.contradictions if c.resolved]

        # Re-detect
        new_contradictions = await self.detect_contradictions(constitution, tolerance)
        constitution.contradictions.extend(new_contradictions)
        constitution.updated_at = datetime.now(timezone.utc)

        return constitution

    def get_constitution(self, constitution: Constitution) -> Constitution:
        """
        Get the current state of a constitution.

        This is primarily for API compatibility.
        In a real implementation, this would load from storage.

        Args:
            constitution: Constitution to return

        Returns:
            The constitution
        """
        return constitution

    def get_evolution(self, constitution: Constitution) -> list[ConstitutionSnapshot]:
        """
        Get the evolution history of a constitution.

        Args:
            constitution: Constitution to analyze

        Returns:
            List of snapshots over time
        """
        return constitution.snapshots

    async def synthesize_contradiction(
        self,
        constitution: Constitution,
        contradiction: Contradiction,
    ) -> DiscoveredAxiom | None:
        """
        Attempt to synthesize a contradiction into a new axiom.

        Uses the ghost alternative hint from contradiction detection
        to propose a synthesis.

        Args:
            constitution: The constitution
            contradiction: The contradiction to synthesize

        Returns:
            A new DiscoveredAxiom if synthesis succeeds, None otherwise
        """
        if not contradiction.synthesis_hint:
            return None

        # Validate the synthesis hint as a potential axiom
        from .galois import detect_fixed_point

        result = await detect_fixed_point(
            content=contradiction.synthesis_hint,
            computer=self._computer,
        )

        if result.is_fixed_point and result.loss < AXIOM_THRESHOLD:
            return DiscoveredAxiom(
                content=contradiction.synthesis_hint,
                loss=result.loss,
                stability=result.stability,
                iterations=result.iterations,
                confidence=1.0 - result.loss,
                source_decisions=[
                    contradiction.axiom_a_content,
                    contradiction.axiom_b_content,
                ],
            )

        return None


# -----------------------------------------------------------------------------
# In-Memory Store (for testing/prototyping)
# -----------------------------------------------------------------------------


class InMemoryConstitutionStore:
    """
    Simple in-memory store for constitutions.

    For production, replace with PostgresConstitutionStore.
    """

    def __init__(self) -> None:
        self._constitutions: dict[str, Constitution] = {}

    def save(self, constitution: Constitution) -> None:
        """Save constitution to store."""
        self._constitutions[constitution.id] = constitution

    def load(self, constitution_id: str) -> Constitution | None:
        """Load constitution by ID."""
        return self._constitutions.get(constitution_id)

    def delete(self, constitution_id: str) -> bool:
        """Delete constitution by ID."""
        if constitution_id in self._constitutions:
            del self._constitutions[constitution_id]
            return True
        return False

    def list_all(self) -> list[Constitution]:
        """List all constitutions."""
        return list(self._constitutions.values())


# -----------------------------------------------------------------------------
# Module-Level Store Access
# -----------------------------------------------------------------------------

_store: InMemoryConstitutionStore | None = None


def get_constitution_store() -> InMemoryConstitutionStore:
    """Get the global constitution store."""
    global _store
    if _store is None:
        _store = InMemoryConstitutionStore()
    return _store


def reset_constitution_store() -> None:
    """Reset the global store (for testing)."""
    global _store
    _store = None


# -----------------------------------------------------------------------------
# Module Exports
# -----------------------------------------------------------------------------

__all__ = [
    # Constants
    "DEFAULT_CONTRADICTION_TOLERANCE",
    # Data types
    "AxiomStatus",
    "ConstitutionalAxiom",
    "Contradiction",
    "ConstitutionSnapshot",
    "Constitution",
    # Service
    "PersonalConstitutionService",
    # Store
    "InMemoryConstitutionStore",
    "get_constitution_store",
    "reset_constitution_store",
]
