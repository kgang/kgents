"""
Garden: The Witness Assurance Surface Types.

This module defines the types for the WitnessGarden polynomial - a living
visualization where specs grow as plants, evidence accumulates as soil depth,
and orphans appear as weeds to tend.

The Core Insight:
    "Trust is not a badge—it's a living organism."

Philosophy:
    "The UI IS the trust surface. Every pixel grows or wilts."

See: spec/protocols/witness-assurance-surface.md
See: docs/skills/elastic-ui-patterns.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal, NewType

# =============================================================================
# Type Aliases
# =============================================================================

SpecPath = NewType("SpecPath", str)  # e.g., "spec/protocols/witness-assurance-surface.md"


# =============================================================================
# Plant Health (Visual State)
# =============================================================================


class PlantHealth(Enum):
    """
    Health states for spec visualization.

    From spec:
        - blooming: witnessed, high confidence
        - healthy: in_progress, stable
        - wilting: contested or decaying
        - dead: superseded
    """

    BLOOMING = "blooming"  # Witnessed, high confidence (≥0.9)
    HEALTHY = "healthy"  # In progress, stable (0.6-0.9)
    WILTING = "wilting"  # Contested or decaying (0.3-0.6)
    DEAD = "dead"  # Superseded or no evidence (<0.3)
    SEEDLING = "seedling"  # New, not yet witnessed (confidence = 0)


class SpecStatus(Enum):
    """
    Lifecycle status of a spec in the garden.

    Positions in the WitnessGarden polynomial:
        unwitnessed → in_progress → witnessed → contested → superseded
    """

    UNWITNESSED = "unwitnessed"  # No evidence yet
    IN_PROGRESS = "in_progress"  # Some evidence, not complete
    WITNESSED = "witnessed"  # Full witness status earned
    CONTESTED = "contested"  # Conflicting evidence
    SUPERSEDED = "superseded"  # Replaced by newer spec (terminal)


# =============================================================================
# Accountability Lens (Observer Filter)
# =============================================================================


class AccountabilityLens(Enum):
    """
    Simplifying isomorphism for observer types (AD-008 pattern).

    Instead of scattered "who is viewing?" conditionals, we name the dimension.

    | Lens | What It Shows | Who It's For |
    |------|---------------|--------------|
    | AUDIT | Full evidence chain, all levels, rebuttals | External reviewers |
    | AUTHOR | My marks, my contributions, attention items | Contributors |
    | TRUST | Confidence only, green/yellow/red at a glance | Executives |
    """

    AUDIT = "audit"  # Full evidence chain, all levels, rebuttals prominent
    AUTHOR = "author"  # My marks, my contributions, attention items
    TRUST = "trust"  # Confidence only, green/yellow/red at a glance

    @property
    def key_binding(self) -> str:
        """Keyboard shortcut for this lens."""
        return {"audit": "A", "author": "U", "trust": "T"}[self.value]


# =============================================================================
# Evidence Ladder (L-∞ to L3)
# =============================================================================


@dataclass(frozen=True)
class EvidenceLadder:
    """
    The complete evidence stack from L-∞ (orphan) to L3 (bet).

    Each level is a COUNT of evidence instances at that level.
    This is orthogonal to EvidenceTier (which classifies types, not counts).

    Ladder levels:
        L-∞ orphan: Artifacts without prompt lineage
        L-2 prompt: PromptAncestor count
        L-1 trace:  TraceWitness count
        L0 mark:    Human marks
        L1 test:    Test artifacts
        L2 proof:   Formal proofs
        L3 bet:     Economic bets
    """

    orphan: int = 0  # L-∞: Artifacts without lineage (negative = bad)
    prompt: int = 0  # L-2: PromptAncestor count
    trace: int = 0  # L-1: TraceWitness count
    mark: int = 0  # L0: Human marks
    test: int = 0  # L1: Test artifacts
    proof: int = 0  # L2: Formal proofs
    bet: int = 0  # L3: Economic bets (future)

    @property
    def total_evidence(self) -> int:
        """Total positive evidence (excludes orphans)."""
        return self.prompt + self.trace + self.mark + self.test + self.proof + self.bet

    @property
    def confidence_score(self) -> float:
        """
        Compute confidence from ladder.

        Higher levels count more. Orphans are a negative signal.
        Returns value in [0, 1].
        """
        # Weighted sum: higher levels = more weight
        weights = {
            "orphan": -0.5,  # Negative contribution
            "prompt": 0.5,
            "trace": 0.8,
            "mark": 1.0,
            "test": 1.5,
            "proof": 2.0,
            "bet": 3.0,
        }

        weighted = (
            weights["orphan"] * self.orphan
            + weights["prompt"] * self.prompt
            + weights["trace"] * self.trace
            + weights["mark"] * self.mark
            + weights["test"] * self.test
            + weights["proof"] * self.proof
            + weights["bet"] * self.bet
        )

        # Normalize to [0, 1] with sigmoid-like curve
        # 0 evidence = 0.0, 10+ weighted evidence = ~1.0
        if weighted <= 0:
            return max(0.0, 0.3 + weighted * 0.1)  # Low floor for orphan-only

        import math

        return min(1.0, 0.3 + 0.7 * (1 - math.exp(-weighted / 5)))

    def to_dict(self) -> dict[str, int]:
        """Convert to dictionary for serialization."""
        return {
            "orphan": self.orphan,
            "prompt": self.prompt,
            "trace": self.trace,
            "mark": self.mark,
            "test": self.test,
            "proof": self.proof,
            "bet": self.bet,
        }

    @classmethod
    def from_dict(cls, data: dict[str, int]) -> EvidenceLadder:
        """Create from dictionary."""
        return cls(
            orphan=data.get("orphan", 0),
            prompt=data.get("prompt", 0),
            trace=data.get("trace", 0),
            mark=data.get("mark", 0),
            test=data.get("test", 0),
            proof=data.get("proof", 0),
            bet=data.get("bet", 0),
        )

    @classmethod
    def empty(cls) -> EvidenceLadder:
        """Create an empty ladder (unwitnessed spec)."""
        return cls()


# =============================================================================
# Confidence Pulse (Heartbeat)
# =============================================================================


class PulseRate(Enum):
    """
    The heartbeat rate based on confidence.

    From spec:
        "Flatline IS the animation at low confidence. Stillness communicates."

    | Rate | Confidence | Animation |
    |------|------------|-----------|
    | FLATLINE | <0.3 | No animation, stillness |
    | AWAKENING | 0.3-0.6 | Slow pulse |
    | ALIVE | 0.6-0.9 | Steady pulse |
    | THRIVING | >0.9 | Strong pulse |
    """

    FLATLINE = 0  # confidence < 0.3: no animation
    AWAKENING = 0.5  # confidence 0.3-0.6: slow pulse
    ALIVE = 1.0  # confidence 0.6-0.9: steady pulse
    THRIVING = 1.5  # confidence > 0.9: strong pulse

    @classmethod
    def from_confidence(cls, confidence: float) -> PulseRate:
        """Get pulse rate from confidence score."""
        if confidence < 0.3:
            return cls.FLATLINE
        elif confidence < 0.6:
            return cls.AWAKENING
        elif confidence < 0.9:
            return cls.ALIVE
        else:
            return cls.THRIVING


@dataclass(frozen=True)
class ConfidencePulse:
    """
    Heartbeat of trust for a spec.

    Not decorative—diagnostic. The pulse reflects actual confidence.
    """

    confidence: float  # Current confidence [0, 1]
    previous_confidence: float | None = None  # For delta calculation
    pulse_rate: PulseRate = PulseRate.FLATLINE
    delta_direction: Literal["increasing", "decreasing", "stable"] = "stable"

    def __post_init__(self) -> None:
        """Derive pulse_rate and delta from confidence."""
        # Use object.__setattr__ for frozen dataclass
        object.__setattr__(self, "pulse_rate", PulseRate.from_confidence(self.confidence))

        if self.previous_confidence is not None:
            delta = self.confidence - self.previous_confidence
            if delta > 0.01:
                object.__setattr__(self, "delta_direction", "increasing")
            elif delta < -0.01:
                object.__setattr__(self, "delta_direction", "decreasing")

    @classmethod
    def from_confidence(
        cls,
        confidence: float,
        previous: float | None = None,
    ) -> ConfidencePulse:
        """Create pulse from confidence values."""
        return cls(
            confidence=confidence,
            previous_confidence=previous,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "confidence": self.confidence,
            "previous_confidence": self.previous_confidence,
            "pulse_rate": self.pulse_rate.value,
            "delta_direction": self.delta_direction,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConfidencePulse:
        """Create from dictionary."""
        return cls(
            confidence=data.get("confidence", 0.0),
            previous_confidence=data.get("previous_confidence"),
        )


# =============================================================================
# Spec Plant (Visualization Unit)
# =============================================================================


@dataclass(frozen=True)
class SpecPlant:
    """
    A spec rendered as a plant in the garden.

    Visual properties are derived from evidence:
        - height: Taller = more evidence
        - health: blooming → dead based on confidence
    """

    path: SpecPath  # e.g., "spec/protocols/witness.md"
    name: str  # Human-friendly name
    status: SpecStatus  # Lifecycle position
    confidence: float  # 0.0-1.0
    evidence_levels: EvidenceLadder  # The ladder
    pulse: ConfidencePulse  # Heartbeat

    # Derived visual properties
    height: int = 0  # Taller = more evidence
    health: PlantHealth = PlantHealth.SEEDLING

    # Metadata
    last_evidence_at: datetime | None = None
    mark_count: int = 0
    test_count: int = 0

    def __post_init__(self) -> None:
        """Derive visual properties."""
        # Height from total evidence (logarithmic)
        import math

        total = self.evidence_levels.total_evidence
        height = int(math.log2(total + 1) * 3) if total > 0 else 0
        object.__setattr__(self, "height", min(height, 10))  # Cap at 10

        # Health from confidence
        if self.confidence >= 0.9:
            health = PlantHealth.BLOOMING
        elif self.confidence >= 0.6:
            health = PlantHealth.HEALTHY
        elif self.confidence >= 0.3:
            health = PlantHealth.WILTING
        elif self.evidence_levels.total_evidence > 0:
            health = PlantHealth.DEAD
        else:
            health = PlantHealth.SEEDLING
        object.__setattr__(self, "health", health)

    @classmethod
    def from_spec_file(
        cls,
        path: str,
        name: str,
        ladder: EvidenceLadder | None = None,
        last_evidence_at: datetime | None = None,
    ) -> SpecPlant:
        """Create a plant from a spec file path."""
        ladder = ladder or EvidenceLadder.empty()
        confidence = ladder.confidence_score

        # Determine status from evidence
        if ladder.total_evidence == 0:
            status = SpecStatus.UNWITNESSED
        elif confidence >= 0.9:
            status = SpecStatus.WITNESSED
        else:
            status = SpecStatus.IN_PROGRESS

        return cls(
            path=SpecPath(path),
            name=name,
            status=status,
            confidence=confidence,
            evidence_levels=ladder,
            pulse=ConfidencePulse.from_confidence(confidence),
            last_evidence_at=last_evidence_at,
            mark_count=ladder.mark,
            test_count=ladder.test,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": str(self.path),
            "name": self.name,
            "status": self.status.value,
            "confidence": self.confidence,
            "evidence_levels": self.evidence_levels.to_dict(),
            "pulse": self.pulse.to_dict(),
            "height": self.height,
            "health": self.health.value,
            "last_evidence_at": self.last_evidence_at.isoformat()
            if self.last_evidence_at
            else None,
            "mark_count": self.mark_count,
            "test_count": self.test_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SpecPlant:
        """Create from dictionary."""
        ladder = EvidenceLadder.from_dict(data.get("evidence_levels", {}))
        confidence = data.get("confidence", 0.0)

        return cls(
            path=SpecPath(data["path"]),
            name=data.get("name", ""),
            status=SpecStatus(data.get("status", "unwitnessed")),
            confidence=confidence,
            evidence_levels=ladder,
            pulse=ConfidencePulse.from_dict(data.get("pulse", {"confidence": confidence})),
            last_evidence_at=datetime.fromisoformat(data["last_evidence_at"])
            if data.get("last_evidence_at")
            else None,
            mark_count=data.get("mark_count", 0),
            test_count=data.get("test_count", 0),
        )


# =============================================================================
# Orphan Weed (Artifacts Without Lineage)
# =============================================================================


@dataclass(frozen=True)
class OrphanWeed:
    """
    An artifact without prompt lineage.

    From spec:
        "Orphans are weeds to tend, not shame to conceal."
        "Orphan Visibility Law: Orphans are ALWAYS visible."
    """

    path: str  # Path to orphaned artifact
    artifact_type: str  # "file", "mark", "crystal", etc.
    created_at: datetime  # When the orphan was created
    suggested_prompt: str | None = None  # If we can guess origin

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "path": self.path,
            "artifact_type": self.artifact_type,
            "created_at": self.created_at.isoformat(),
            "suggested_prompt": self.suggested_prompt,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OrphanWeed:
        """Create from dictionary."""
        return cls(
            path=data["path"],
            artifact_type=data.get("artifact_type", "file"),
            created_at=datetime.fromisoformat(data["created_at"]),
            suggested_prompt=data.get("suggested_prompt"),
        )


# =============================================================================
# Provenance Node (Genealogy)
# =============================================================================


@dataclass(frozen=True)
class ProvenanceNode:
    """
    A node in the artifact genealogy.

    Genealogy is rendered horizontally (time flows left → right).
    AI nodes shimmer subtly; human nodes are solid.
    """

    id: str
    node_type: Literal["orphan", "prompt", "artifact", "mark", "crystal", "test", "proof"]
    label: str
    timestamp: datetime
    confidence: float | None = None
    author: Literal["kent", "claude", "system"] = "system"
    children: tuple["ProvenanceNode", ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "node_type": self.node_type,
            "label": self.label,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "author": self.author,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ProvenanceNode:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            node_type=data["node_type"],
            label=data.get("label", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            confidence=data.get("confidence"),
            author=data.get("author", "system"),
            children=tuple(cls.from_dict(c) for c in data.get("children", [])),
        )


# =============================================================================
# Garden Scene (The Complete Visualization)
# =============================================================================


@dataclass(frozen=True)
class GardenScene:
    """
    The complete garden visualization.

    This is the output of the TrustSurface functor:
        TrustSurface : WitnessGarden × AccountabilityLens × Density → Scene
    """

    specs: tuple[SpecPlant, ...]
    orphans: tuple[OrphanWeed, ...]
    overall_health: float  # Average confidence
    lens: AccountabilityLens  # Current viewing lens
    density: Literal["compact", "comfortable", "spacious"] = "comfortable"

    # Aggregates
    total_specs: int = 0
    witnessed_count: int = 0
    orphan_count: int = 0

    # Timestamp
    generated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Compute aggregates."""
        object.__setattr__(self, "total_specs", len(self.specs))
        object.__setattr__(
            self,
            "witnessed_count",
            sum(1 for s in self.specs if s.status == SpecStatus.WITNESSED),
        )
        object.__setattr__(self, "orphan_count", len(self.orphans))

    @classmethod
    def empty(cls, lens: AccountabilityLens = AccountabilityLens.AUDIT) -> GardenScene:
        """Create an empty garden scene."""
        return cls(
            specs=(),
            orphans=(),
            overall_health=0.0,
            lens=lens,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "specs": [s.to_dict() for s in self.specs],
            "orphans": [o.to_dict() for o in self.orphans],
            "overall_health": self.overall_health,
            "lens": self.lens.value,
            "density": self.density,
            "total_specs": self.total_specs,
            "witnessed_count": self.witnessed_count,
            "orphan_count": self.orphan_count,
            "generated_at": self.generated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GardenScene:
        """Create from dictionary."""
        return cls(
            specs=tuple(SpecPlant.from_dict(s) for s in data.get("specs", [])),
            orphans=tuple(OrphanWeed.from_dict(o) for o in data.get("orphans", [])),
            overall_health=data.get("overall_health", 0.0),
            lens=AccountabilityLens(data.get("lens", "audit")),
            density=data.get("density", "comfortable"),
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Type aliases
    "SpecPath",
    # Enums
    "PlantHealth",
    "SpecStatus",
    "AccountabilityLens",
    "PulseRate",
    # Data classes
    "EvidenceLadder",
    "ConfidencePulse",
    "SpecPlant",
    "OrphanWeed",
    "ProvenanceNode",
    "GardenScene",
]
