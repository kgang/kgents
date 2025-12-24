"""
Annotation Types: Spec ↔ Implementation Mapping.

> *"Every spec section should trace to implementation. Every gotcha should be captured."*

This module defines the core types for the annotation system:
- SpecAnnotation: Links spec sections to principles, impl, gotchas, decisions
- AnnotationKind: The taxonomy of annotations
- AnnotationStatus: Lifecycle tracking (active, superseded, archived)

Annotations enable bidirectional tracing:
- Spec → Impl: Find the code that implements a spec section
- Impl → Spec: Find the spec that justifies this code
- Principle → Spec: Find sections that honor a principle
- Decision → Spec: Link design decisions to their spec context

AGENTESE: concept.annotate.* (conceptual layer of spec-impl coherence)

Teaching:
    taste: Annotations are metadata, not content modification.
           We NEVER modify spec files automatically—only link to them.

    principle: Composable - Annotations are first-class values that can be queried,
               filtered, transformed, and composed into larger structures.

See: brainstorming/tool-use/CLAUDE_CODE_CLI_STRATEGY.md (Phase 2)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# =============================================================================
# Enums
# =============================================================================


class AnnotationKind(str, Enum):
    """
    Taxonomy of annotation types.

    Each kind serves a different purpose in spec ↔ impl tracking:
    - PRINCIPLE: Links section to constitutional principle (tasteful, composable, etc.)
    - IMPL_LINK: Direct pointer from spec section to implementing code
    - GOTCHA: Trap to avoid (learned the hard way)
    - TASTE: Aesthetic judgment (why we chose X over Y)
    - DECISION: Design decision (links to `kg decide` fusion record)
    """

    PRINCIPLE = "principle"
    IMPL_LINK = "impl_link"
    GOTCHA = "gotcha"
    TASTE = "taste"
    DECISION = "decision"


class AnnotationStatus(str, Enum):
    """
    Lifecycle status of an annotation.

    Annotations evolve as the codebase changes:
    - ACTIVE: Current, valid annotation
    - SUPERSEDED: Replaced by newer annotation (still kept for history)
    - ARCHIVED: No longer relevant (spec section removed, impl changed, etc.)
    """

    ACTIVE = "active"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


# =============================================================================
# Core Types
# =============================================================================


@dataclass
class SpecAnnotation:
    """
    A single annotation linking spec to principles/impl/gotchas.

    Example usage:
        # Principle annotation
        ann = SpecAnnotation(
            id="ann-abc123",
            spec_path="spec/protocols/witness.md",
            section="Mark Structure",
            kind=AnnotationKind.PRINCIPLE,
            principle="composable",
            note="Single output per mark (not arrays)",
            created_by="kent",
            mark_id="mark-xyz789",
        )

        # Implementation link
        ann = SpecAnnotation(
            id="ann-def456",
            spec_path="spec/protocols/witness.md",
            section="MarkStore",
            kind=AnnotationKind.IMPL_LINK,
            impl_path="services/witness/store.py:MarkStore",
            note="Primary storage implementation",
            created_by="claude",
            mark_id="mark-qrs456",
        )

        # Gotcha annotation
        ann = SpecAnnotation(
            id="ann-ghi789",
            spec_path="spec/protocols/witness.md",
            section="Event Emission",
            kind=AnnotationKind.GOTCHA,
            note="Bus publish is fire-and-forget, don't await",
            created_by="kent",
            mark_id="mark-lmn123",
        )

    Fields:
        id: Unique annotation identifier
        spec_path: Path to spec file (relative to repo root)
        section: Section/heading in spec file
        kind: Type of annotation (principle, impl_link, gotcha, taste, decision)
        principle: Which constitutional principle (if kind=PRINCIPLE)
        impl_path: Path to implementation (if kind=IMPL_LINK)
        decision_id: Link to fusion decision record (if kind=DECISION)
        note: Human-readable annotation content
        created_by: Author (kent, claude, etc.)
        created_at: When annotation was created
        mark_id: Witness mark ID (every annotation is witnessed)
        status: Lifecycle status (active, superseded, archived)
    """

    id: str
    spec_path: str
    section: str
    kind: AnnotationKind

    # Optional content fields (depends on kind)
    principle: str | None = None
    impl_path: str | None = None
    decision_id: str | None = None
    note: str = ""

    # Metadata
    created_by: str = "kent"
    created_at: datetime = field(default_factory=datetime.utcnow)
    mark_id: str = ""  # Witness trace

    # Lifecycle
    status: AnnotationStatus = AnnotationStatus.ACTIVE

    def __post_init__(self) -> None:
        """Validate annotation based on kind."""
        if self.kind == AnnotationKind.PRINCIPLE and not self.principle:
            raise ValueError("PRINCIPLE annotations must specify principle field")
        if self.kind == AnnotationKind.IMPL_LINK and not self.impl_path:
            raise ValueError("IMPL_LINK annotations must specify impl_path field")
        if self.kind == AnnotationKind.DECISION and not self.decision_id:
            raise ValueError("DECISION annotations must specify decision_id field")


@dataclass
class ImplEdge:
    """
    A single edge in the spec ↔ impl graph.

    Represents a verified link from a spec section to implementing code.

    Fields:
        spec_section: Section in spec file
        impl_path: Path to implementation code
        verified: Whether impl_path exists and is accessible
        annotation_id: Source annotation ID
    """

    spec_section: str
    impl_path: str
    verified: bool
    annotation_id: str


@dataclass
class ImplGraph:
    """
    Bidirectional graph of spec ↔ impl relationships.

    Built from IMPL_LINK annotations. Enables queries like:
    - "Show all impl files for this spec section"
    - "Show all spec sections implemented by this file"
    - "Calculate coverage: % of spec sections with impl links"

    Fields:
        spec_path: The spec file being analyzed
        edges: All spec → impl edges
        coverage: Fraction of spec sections with impl links (0.0 - 1.0)
        uncovered_sections: Spec sections without impl links
    """

    spec_path: str
    edges: list[ImplEdge] = field(default_factory=list)
    coverage: float = 0.0
    uncovered_sections: list[str] = field(default_factory=list)

    def sections_for_impl(self, impl_path: str) -> list[str]:
        """Get all spec sections implemented by this file."""
        return [e.spec_section for e in self.edges if e.impl_path == impl_path]

    def impls_for_section(self, section: str) -> list[str]:
        """Get all impl paths for this spec section."""
        return [e.impl_path for e in self.edges if e.spec_section == section]


@dataclass
class AnnotationQueryResult:
    """
    Result of querying annotations.

    Supports multiple query modes:
    - By spec path
    - By kind (principle, gotcha, etc.)
    - By principle name
    - By impl path
    - By status (active, superseded, archived)

    Fields:
        annotations: Matching annotations
        total_count: Total number of matches
        grouped_by_kind: Annotations grouped by AnnotationKind
        grouped_by_principle: Annotations grouped by principle name
    """

    annotations: list[SpecAnnotation] = field(default_factory=list)
    total_count: int = 0
    grouped_by_kind: dict[AnnotationKind, list[SpecAnnotation]] = field(default_factory=dict)
    grouped_by_principle: dict[str, list[SpecAnnotation]] = field(default_factory=dict)


__all__ = [
    "AnnotationKind",
    "AnnotationStatus",
    "SpecAnnotation",
    "ImplEdge",
    "ImplGraph",
    "AnnotationQueryResult",
]
