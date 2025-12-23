"""
WitnessedGraph Types: Unified edge types across all graph sources.

This module defines the core types for the WitnessedGraph system:
- EdgeKind: Enumeration of all edge types across sources
- HyperEdge: Unified edge type that composes across Sovereign, Witness, SpecLedger

Design Principle:
    "Three sources, one graph. Composition is the unifier."

The HyperEdge enables graph composition via the >> operator:
    graph = sovereign >> witness >> spec_ledger
    edges = await graph.neighbors("spec/agents/d-gent.md")

Each source maps its native types to HyperEdge:
- Sovereign: DiscoveredEdge -> HyperEdge (code structure)
- Witness: Mark tags -> HyperEdge (evidence, decisions)
- SpecLedger: Harmony/Contradiction -> HyperEdge (spec relations)

Teaching:
    gotcha: HyperEdge is frozen. Use dataclasses.replace() for updates.
            This enables safe caching and hashing.

    gotcha: origin field is a discriminator. Always filter by origin
            when you need source-specific behavior.

See: spec/protocols/witnessed-graph.md (conceptual model)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

# =============================================================================
# Edge Kind Enumeration
# =============================================================================


class EdgeKind(Enum):
    """
    Types of edges across all sources.

    Each source contributes its own edge kinds:
    - Sovereign: IMPORTS, CALLS, INHERITS, REFERENCES (code structure)
    - Witness: EVIDENCE, DECISION, GOTCHA, EUREKA (mark-based)
    - SpecLedger: HARMONY, CONTRADICTION, DEPENDENCY (spec relations)
    """

    # --- From Sovereign (code structure) ---
    IMPORTS = auto()  # File imports another
    CALLS = auto()  # Function calls another
    INHERITS = auto()  # Class inherits from another
    REFERENCES = auto()  # General reference

    # --- From Witness (mark-based) ---
    EVIDENCE = auto()  # Mark proves/supports spec
    DECISION = auto()  # Mark records choice
    GOTCHA = auto()  # Mark warns about trap
    EUREKA = auto()  # Mark records breakthrough
    FRICTION = auto()  # Mark records pain point
    TASTE = auto()  # Mark records aesthetic judgment

    # --- From SpecLedger (spec relations) ---
    HARMONY = auto()  # Specs align
    CONTRADICTION = auto()  # Specs conflict
    DEPENDENCY = auto()  # Spec requires spec
    EXTENDS = auto()  # Spec extends spec
    IMPLEMENTS = auto()  # Code implements spec

    @classmethod
    def from_witness_tag(cls, tag: str) -> EdgeKind | None:
        """Map witness mark tags to edge kinds."""
        tag_map = {
            "evidence": cls.EVIDENCE,
            "decision": cls.DECISION,
            "gotcha": cls.GOTCHA,
            "eureka": cls.EUREKA,
            "friction": cls.FRICTION,
            "taste": cls.TASTE,
        }
        return tag_map.get(tag.lower())

    @classmethod
    def from_sovereign_type(cls, edge_type: str) -> EdgeKind:
        """Map sovereign edge types to edge kinds."""
        type_map = {
            "imports": cls.IMPORTS,
            "calls": cls.CALLS,
            "inherits": cls.INHERITS,
            "references": cls.REFERENCES,
        }
        return type_map.get(edge_type.lower(), cls.REFERENCES)


# =============================================================================
# HyperEdge: The Unified Edge Type
# =============================================================================


@dataclass(frozen=True)
class HyperEdge:
    """
    A unified edge across all graph sources.

    HyperEdge is the lingua franca for graph composition:
    - Sovereign produces HyperEdges from code analysis
    - Witness produces HyperEdges from mark tags
    - SpecLedger produces HyperEdges from spec relations

    Composition works because all sources emit the same type:
        sovereign >> witness >> spec_ledger  # All produce HyperEdges

    Fields:
        kind: The semantic type of this edge
        source_path: Where the edge originates (from node)
        target_path: Where the edge points (to node)
        origin: Which source produced this edge

        context: Surrounding text/context (optional)
        line_number: Line in source file (optional)
        confidence: How confident we are (0.0-1.0)
        timestamp: When edge was discovered (optional)
        mark_id: Link to witness mark if from Witness (optional)
        metadata: Source-specific additional data (optional)

    Example:
        >>> edge = HyperEdge(
        ...     kind=EdgeKind.EVIDENCE,
        ...     source_path="impl/claude/services/brain/persistence.py",
        ...     target_path="spec/agents/d-gent.md",
        ...     origin="witness",
        ...     mark_id="mark-abc123",
        ... )
    """

    # Required fields
    kind: EdgeKind
    source_path: str
    target_path: str
    origin: str  # "sovereign" | "witness" | "spec_ledger"

    # Optional metadata
    context: str | None = None
    line_number: int | None = None
    confidence: float = 1.0
    timestamp: datetime | None = None
    mark_id: str | None = None  # For witness-sourced edges
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate edge on creation."""
        if not self.source_path:
            raise ValueError("source_path cannot be empty")
        if not self.target_path:
            raise ValueError("target_path cannot be empty")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"confidence must be 0.0-1.0, got {self.confidence}")
        # Ensure metadata is hashable-safe (converted to tuple of items if dict)
        if self.metadata and not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dict")

    def __hash__(self) -> int:
        """Hash for use in sets (ignores mutable metadata)."""
        return hash(
            (
                self.kind,
                self.source_path,
                self.target_path,
                self.origin,
                self.line_number,
                self.mark_id,
            )
        )

    def __str__(self) -> str:
        """Human-readable representation."""
        return f"{self.source_path} --[{self.kind.name}:{self.origin}]--> {self.target_path}"

    @property
    def is_sovereign(self) -> bool:
        """Edge from code structure analysis."""
        return self.origin == "sovereign"

    @property
    def is_witness(self) -> bool:
        """Edge from witness marks."""
        return self.origin == "witness"

    @property
    def is_spec_ledger(self) -> bool:
        """Edge from spec relations."""
        return self.origin == "spec_ledger"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "kind": self.kind.name,
            "source_path": self.source_path,
            "target_path": self.target_path,
            "origin": self.origin,
            "context": self.context,
            "line_number": self.line_number,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "mark_id": self.mark_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HyperEdge:
        """Create from dictionary."""
        from datetime import datetime

        timestamp = data.get("timestamp")
        if timestamp and isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        return cls(
            kind=EdgeKind[data["kind"]],
            source_path=data["source_path"],
            target_path=data["target_path"],
            origin=data["origin"],
            context=data.get("context"),
            line_number=data.get("line_number"),
            confidence=data.get("confidence", 1.0),
            timestamp=timestamp,
            mark_id=data.get("mark_id"),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "EdgeKind",
    "HyperEdge",
]
