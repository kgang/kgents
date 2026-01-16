"""
Reflection and Interpretation Crystals - Layers 6-7 of the Zero Seed hierarchy.

Layer 6 (Reflection): Looking back at artifacts, synthesizing insights
Layer 7 (Interpretation): Patterns across time, trends, predictions

Philosophy:
- L6 reflects on specific artifacts (synthesis, comparison, delta, audit)
- L7 interprets patterns across artifacts and time
- Both carry GaloisWitnessedProof for self-justification
- Reflection is "what did we learn?"
- Interpretation is "what does it mean over time?"
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from .proof import GaloisWitnessedProof


@dataclass(frozen=True)
class ReflectionCrystal:
    """
    Layer 6 Crystal: Reflection on specific artifacts.

    Reflections synthesize insights from one or more artifacts:
    - "synthesis": Combining multiple artifacts into unified understanding
    - "comparison": Contrasting artifacts to reveal differences
    - "delta": Measuring change between artifact states
    - "audit": Evaluating artifact quality against criteria

    A reflection always points back at specific target artifacts and
    carries its own proof justifying the insight.

    Attributes:
        id: Unique identifier for this reflection
        target_ids: Artifact IDs being reflected upon
        reflection_type: Type of reflection (synthesis/comparison/delta/audit)
        insight: The core insight or learning
        recommendations: Actionable recommendations from this reflection
        derived_from: Lineage - which artifacts/proofs led to this
        layer: Always 6 (reflection layer)
        proof: Self-justifying proof for this reflection
        created_at: When this reflection was created
    """

    id: str
    """Unique identifier for this reflection."""

    target_ids: tuple[str, ...]
    """Artifact IDs being reflected upon."""

    reflection_type: str
    """Type of reflection: synthesis/comparison/delta/audit."""

    insight: str
    """The core insight or learning from reflection."""

    recommendations: tuple[str, ...]
    """Actionable recommendations derived from this reflection."""

    derived_from: tuple[str, ...]
    """Lineage: artifact IDs that led to this reflection."""

    layer: int = 6
    """Zero Seed layer (always 6 for reflections)."""

    proof: GaloisWitnessedProof | None = None
    """Self-justifying proof for this reflection's validity."""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    """When this reflection was created."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "id": self.id,
            "target_ids": list(self.target_ids),
            "reflection_type": self.reflection_type,
            "insight": self.insight,
            "recommendations": list(self.recommendations),
            "derived_from": list(self.derived_from),
            "layer": self.layer,
            "proof": self.proof.to_dict() if self.proof else None,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ReflectionCrystal":
        """Deserialize from dict."""
        return cls(
            id=data["id"],
            target_ids=tuple(data.get("target_ids", [])),
            reflection_type=data["reflection_type"],
            insight=data["insight"],
            recommendations=tuple(data.get("recommendations", [])),
            derived_from=tuple(data.get("derived_from", [])),
            layer=data.get("layer", 6),
            proof=GaloisWitnessedProof.from_dict(data["proof"]) if data.get("proof") else None,
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(UTC),
        )


@dataclass(frozen=True)
class InterpretationCrystal:
    """
    Layer 7 Crystal: Interpretation of patterns across time.

    Interpretations find patterns, trends, and make predictions:
    - "trend": Observing direction of change over time
    - "pattern": Identifying recurring structures
    - "prediction": Forecasting future states based on history

    Unlike reflections (which target specific artifacts), interpretations
    target patterns across artifacts and time ranges.

    Attributes:
        id: Unique identifier for this interpretation
        artifact_pattern: Glob pattern for artifacts interpreted (e.g., "impl/**/*.py")
        time_range: Time window for interpretation (start, end)
        insight_type: Type of insight (trend/pattern/prediction)
        content: The interpretation narrative
        confidence: Confidence in this interpretation [0, 1]
        supporting_ids: Artifact IDs supporting this interpretation
        layer: Always 7 (interpretation layer)
        proof: Self-justifying proof for this interpretation
        created_at: When this interpretation was created
    """

    id: str
    """Unique identifier for this interpretation."""

    artifact_pattern: str
    """Glob pattern for artifacts (e.g., 'impl/claude/agents/**/*.py')."""

    time_range: tuple[datetime, datetime]
    """Time window: (start, end)."""

    insight_type: str
    """Type of insight: trend/pattern/prediction."""

    content: str
    """The interpretation narrative."""

    confidence: float
    """Confidence in this interpretation [0, 1]."""

    supporting_ids: tuple[str, ...]
    """Artifact IDs supporting this interpretation."""

    layer: int = 7
    """Zero Seed layer (always 7 for interpretations)."""

    proof: GaloisWitnessedProof | None = None
    """Self-justifying proof for this interpretation's validity."""

    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    """When this interpretation was created."""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict."""
        return {
            "id": self.id,
            "artifact_pattern": self.artifact_pattern,
            "time_range": [self.time_range[0].isoformat(), self.time_range[1].isoformat()],
            "insight_type": self.insight_type,
            "content": self.content,
            "confidence": self.confidence,
            "supporting_ids": list(self.supporting_ids),
            "layer": self.layer,
            "proof": self.proof.to_dict() if self.proof else None,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InterpretationCrystal":
        """Deserialize from dict."""
        time_range_data = data.get("time_range", [])
        time_range = (
            (datetime.fromisoformat(time_range_data[0]), datetime.fromisoformat(time_range_data[1]))
            if time_range_data and len(time_range_data) == 2
            else (datetime.now(UTC), datetime.now(UTC))
        )

        return cls(
            id=data["id"],
            artifact_pattern=data["artifact_pattern"],
            time_range=time_range,
            insight_type=data["insight_type"],
            content=data["content"],
            confidence=data.get("confidence", 0.0),
            supporting_ids=tuple(data.get("supporting_ids", [])),
            layer=data.get("layer", 7),
            proof=GaloisWitnessedProof.from_dict(data["proof"]) if data.get("proof") else None,
            created_at=datetime.fromisoformat(data["created_at"])
            if "created_at" in data
            else datetime.now(UTC),
        )


# Schema registration for Universe
from agents.d.universe import DataclassSchema

REFLECTION_CRYSTAL_SCHEMA = DataclassSchema(name="reflection.crystal", type_cls=ReflectionCrystal)

INTERPRETATION_CRYSTAL_SCHEMA = DataclassSchema(
    name="interpretation.crystal", type_cls=InterpretationCrystal
)


__all__ = [
    "ReflectionCrystal",
    "InterpretationCrystal",
    "REFLECTION_CRYSTAL_SCHEMA",
    "INTERPRETATION_CRYSTAL_SCHEMA",
]
