"""
Concept Nursery: Where ideas grow from seeds to implementations.

The nursery tracks JIT concepts through their growth lifecycle:
- SEED: Just created, minimal usage
- SPROUTING: Getting traction (10+ uses)
- GROWING: Proving value (50+ uses, 60%+ success)
- READY: Ready for promotion (100+ uses, 80%+ success)
- PROMOTED: Accepted into permanent implementation

Unlike the old JITPromoter, the nursery doesn't write to the filesystem.
It tracks growth state and emits events for the Gardener UI.

See: spec/protocols/gardener-logos.md (Concept Nursery extension)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any


class ConceptStage(Enum):
    """
    Growth stages for concepts in the nursery.

    Maps to garden seasons for visual consistency:
    - SEED → DORMANT (small, no glow)
    - SPROUTING → SPROUTING (tiny sprout, faint pulse)
    - GROWING → BLOOMING (larger plant, steady glow)
    - READY → HARVEST (full plant, bright pulse - asking to be picked)
    - PROMOTED → (removed from nursery, persisted elsewhere)
    """

    SEED = auto()
    SPROUTING = auto()
    GROWING = auto()
    READY = auto()
    PROMOTED = auto()

    @property
    def icon(self) -> str:
        """Lucide icon name for this stage."""
        return {
            ConceptStage.SEED: "circle-dot",
            ConceptStage.SPROUTING: "sprout",
            ConceptStage.GROWING: "leaf",
            ConceptStage.READY: "flower-2",
            ConceptStage.PROMOTED: "check-circle",
        }[self]

    @property
    def glow_intensity(self) -> float:
        """CSS glow intensity (0-1) for visual feedback."""
        return {
            ConceptStage.SEED: 0.0,
            ConceptStage.SPROUTING: 0.2,
            ConceptStage.GROWING: 0.5,
            ConceptStage.READY: 0.8,
            ConceptStage.PROMOTED: 0.0,
        }[self]

    @property
    def should_pulse(self) -> bool:
        """Whether this stage should have breathing animation."""
        return self == ConceptStage.READY


# Growth thresholds
SPROUTING_THRESHOLD = 10
GROWING_THRESHOLD = 50
GROWING_SUCCESS_RATE = 0.6
READY_THRESHOLD = 100
READY_SUCCESS_RATE = 0.8


@dataclass
class ConceptSeed:
    """
    A concept in the nursery, growing toward promotion.

    The seed tracks usage and success metrics to determine growth stage.
    Growth is automatic based on thresholds; promotion is user-initiated.
    """

    handle: str  # AGENTESE path, e.g., "world.garden.concept"
    usage_count: int = 0
    success_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_invoked: datetime = field(default_factory=datetime.now)

    # Cached stage (recomputed on metric changes)
    _stage: ConceptStage = field(default=ConceptStage.SEED, repr=False)

    def __post_init__(self) -> None:
        """Recompute stage after initialization."""
        self._stage = self._compute_stage()

    @property
    def success_rate(self) -> float:
        """Success rate as a decimal (0-1)."""
        if self.usage_count == 0:
            return 0.0
        return self.success_count / self.usage_count

    @property
    def stage(self) -> ConceptStage:
        """Current growth stage based on metrics."""
        return self._stage

    def _compute_stage(self) -> ConceptStage:
        """Determine stage from usage metrics."""
        if self.usage_count >= READY_THRESHOLD and self.success_rate >= READY_SUCCESS_RATE:
            return ConceptStage.READY
        if self.usage_count >= GROWING_THRESHOLD and self.success_rate >= GROWING_SUCCESS_RATE:
            return ConceptStage.GROWING
        if self.usage_count >= SPROUTING_THRESHOLD:
            return ConceptStage.SPROUTING
        return ConceptStage.SEED

    def record_invocation(self, success: bool) -> ConceptStage | None:
        """
        Record an invocation and return new stage if changed.

        Args:
            success: Whether the invocation succeeded

        Returns:
            New stage if growth occurred, None otherwise
        """
        old_stage = self._stage

        self.usage_count += 1
        if success:
            self.success_count += 1
        self.last_invoked = datetime.now()

        self._stage = self._compute_stage()

        if self._stage != old_stage:
            return self._stage
        return None

    def promote(self) -> bool:
        """
        Mark as promoted. Returns True if ready for promotion.

        This doesn't write files—it just updates stage.
        Actual code generation is a separate concern.
        """
        if self._stage != ConceptStage.READY:
            return False

        self._stage = ConceptStage.PROMOTED
        return True

    def to_dict(self) -> dict[str, Any]:
        """Serialize for API/persistence."""
        return {
            "handle": self.handle,
            "stage": self._stage.name,
            "usage_count": self.usage_count,
            "success_count": self.success_count,
            "success_rate": self.success_rate,
            "created_at": self.created_at.isoformat(),
            "last_invoked": self.last_invoked.isoformat(),
            "glow_intensity": self._stage.glow_intensity,
            "should_pulse": self._stage.should_pulse,
            "icon": self._stage.icon,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConceptSeed:
        """Deserialize from API/persistence."""
        seed = cls(
            handle=data["handle"],
            usage_count=data.get("usage_count", 0),
            success_count=data.get("success_count", 0),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if data.get("created_at")
                else datetime.now()
            ),
            last_invoked=(
                datetime.fromisoformat(data["last_invoked"])
                if data.get("last_invoked")
                else datetime.now()
            ),
        )
        # Stage is recomputed in __post_init__
        return seed


class ConceptNursery:
    """
    The nursery: a collection of concept seeds growing toward promotion.

    This is the in-memory implementation. For persistence, wrap with D-gent.

    Usage:
        nursery = ConceptNursery()
        nursery.plant("world.garden.concept")
        nursery.record_invocation("world.garden.concept", success=True)
        ready = nursery.get_ready_concepts()
    """

    def __init__(self) -> None:
        self._seeds: dict[str, ConceptSeed] = {}

    def plant(self, handle: str) -> ConceptSeed:
        """
        Plant a new seed (or return existing).

        Args:
            handle: AGENTESE path for the concept

        Returns:
            The seed (new or existing)
        """
        if handle not in self._seeds:
            self._seeds[handle] = ConceptSeed(handle=handle)
        return self._seeds[handle]

    def get(self, handle: str) -> ConceptSeed | None:
        """Get a seed by handle."""
        return self._seeds.get(handle)

    def record_invocation(
        self, handle: str, success: bool
    ) -> tuple[ConceptSeed, ConceptStage | None]:
        """
        Record an invocation for a concept.

        Plants the seed if it doesn't exist.

        Args:
            handle: AGENTESE path
            success: Whether invocation succeeded

        Returns:
            Tuple of (seed, new_stage if grew else None)
        """
        seed = self.plant(handle)
        new_stage = seed.record_invocation(success)
        return seed, new_stage

    def promote(self, handle: str) -> bool:
        """
        Promote a ready concept.

        Returns:
            True if promotion succeeded, False if not ready
        """
        seed = self._seeds.get(handle)
        if seed is None:
            return False
        return seed.promote()

    def dismiss(self, handle: str) -> bool:
        """
        Dismiss a ready concept (reset to SEED stage).

        Returns:
            True if found and reset, False otherwise
        """
        seed = self._seeds.get(handle)
        if seed is None:
            return False

        # Reset metrics
        seed.usage_count = 0
        seed.success_count = 0
        seed._stage = ConceptStage.SEED
        return True

    def get_ready_concepts(self) -> list[ConceptSeed]:
        """Get all concepts ready for promotion."""
        return [s for s in self._seeds.values() if s.stage == ConceptStage.READY]

    def get_growing_concepts(self) -> list[ConceptSeed]:
        """Get all concepts in SPROUTING or GROWING stages."""
        return [
            s
            for s in self._seeds.values()
            if s.stage in (ConceptStage.SPROUTING, ConceptStage.GROWING)
        ]

    def get_all_seeds(self) -> list[ConceptSeed]:
        """Get all non-promoted seeds."""
        return [s for s in self._seeds.values() if s.stage != ConceptStage.PROMOTED]

    def to_dict(self) -> dict[str, Any]:
        """Serialize the entire nursery."""
        return {
            "seeds": {handle: seed.to_dict() for handle, seed in self._seeds.items()},
            "counts": {
                "total": len(self._seeds),
                "seeds": sum(1 for s in self._seeds.values() if s.stage == ConceptStage.SEED),
                "sprouting": sum(
                    1 for s in self._seeds.values() if s.stage == ConceptStage.SPROUTING
                ),
                "growing": sum(1 for s in self._seeds.values() if s.stage == ConceptStage.GROWING),
                "ready": sum(1 for s in self._seeds.values() if s.stage == ConceptStage.READY),
                "promoted": sum(
                    1 for s in self._seeds.values() if s.stage == ConceptStage.PROMOTED
                ),
            },
        }


# Singleton nursery (can be replaced with DI-injected instance)
_nursery: ConceptNursery | None = None


def get_nursery() -> ConceptNursery:
    """Get the global nursery instance."""
    global _nursery
    if _nursery is None:
        _nursery = ConceptNursery()
    return _nursery


def set_nursery(nursery: ConceptNursery) -> None:
    """Set the global nursery instance (for testing/DI)."""
    global _nursery
    _nursery = nursery


__all__ = [
    "ConceptStage",
    "ConceptSeed",
    "ConceptNursery",
    "get_nursery",
    "set_nursery",
    "SPROUTING_THRESHOLD",
    "GROWING_THRESHOLD",
    "GROWING_SUCCESS_RATE",
    "READY_THRESHOLD",
    "READY_SUCCESS_RATE",
]
