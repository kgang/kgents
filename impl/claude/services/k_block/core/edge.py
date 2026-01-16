"""
KBlockEdge: Edges in the K-Block/Document derivation DAG.

An edge connects two K-Blocks, representing relationships like:
- derives_from: Zero Seed derivation (child → parent axiom)
- implements: Implementation of a specification
- tests: Test coverage relationship
- references: Cross-references between documents
- contradicts: Logical contradiction (for Zero Seed conflict detection)

Philosophy:
    "The edge IS the proof. The mark IS the witness."

    Every edge captures a semantic relationship that can be witnessed.
    Zero Seed nodes use edges to track lineage (axiom → value → goal → spec).

See: spec/protocols/k-block.md, spec/protocols/zero-seed.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class KBlockEdge:
    """
    Edge between two K-Blocks in the derivation DAG.

    An edge represents a semantic relationship with optional witness mark.
    Used for:
    - Zero Seed lineage tracking (derives_from edges form the DAG)
    - Implementation relationships (spec → impl)
    - Test coverage (test → source)
    - References (doc → doc)
    - Contradictions (for Zero Seed conflict detection)

    Attributes:
        id: Unique edge identifier
        source_id: Source K-Block ID
        target_id: Target K-Block ID
        edge_type: Semantic relationship type
        context: Optional context/reason for this edge
        confidence: Confidence score [0.0, 1.0]
        mark_id: Optional witness mark ID
        created_at: When this edge was created

    Example:
        >>> edge = KBlockEdge(
        ...     id="edge-abc123",
        ...     source_id="kb-spec-001",
        ...     target_id="kb-impl-002",
        ...     edge_type="implements",
        ...     context="Implements Zero Seed Layer 4 spec",
        ...     confidence=0.95,
        ...     mark_id="mark-xyz789"
        ... )
    """

    id: str
    source_id: str
    target_id: str
    edge_type: str  # derives_from, implements, tests, references, contradicts
    context: str | None = None
    confidence: float = 1.0
    mark_id: str | None = None  # Witness mark for this edge
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate edge fields."""
        # Validate confidence range
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0.0, 1.0], got {self.confidence}")

        # Validate edge type
        valid_types = {
            "derives_from",
            "implements",
            "tests",
            "references",
            "contradicts",
        }
        if self.edge_type not in valid_types:
            raise ValueError(f"Invalid edge_type '{self.edge_type}'. Must be one of: {valid_types}")

    def to_dict(self) -> dict[str, Any]:
        """Serialize edge to dictionary."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type,
            "context": self.context,
            "confidence": self.confidence,
            "mark_id": self.mark_id,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KBlockEdge:
        """Deserialize edge from dictionary."""
        return cls(
            id=data["id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            edge_type=data["edge_type"],
            context=data.get("context"),
            confidence=data.get("confidence", 1.0),
            mark_id=data.get("mark_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
        )

    def is_derivation(self) -> bool:
        """Check if this is a Zero Seed derivation edge."""
        return self.edge_type == "derives_from"

    def is_contradiction(self) -> bool:
        """Check if this edge represents a contradiction."""
        return self.edge_type == "contradicts"

    def __repr__(self) -> str:
        """Readable representation."""
        mark_str = f", mark={self.mark_id[:12]}..." if self.mark_id else ""
        return (
            f"KBlockEdge(type={self.edge_type}, "
            f"{self.source_id[:12]}... → {self.target_id[:12]}...{mark_str})"
        )


__all__ = ["KBlockEdge"]
