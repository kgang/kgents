"""
Evidence from Exploration: Trail-based proof accumulation.

The core insight: exploration is not just navigation—it's evidence gathering.
Every trail can support or refute claims.

Two main components:
1. TrailAsEvidence: Converts a Trail into Evidence for a claim
2. EvidenceScope: Scopes evidence to exploration context

Laws:
1. Evidence Monotonicity: evidence(trail ++ step) >= evidence(trail)
2. Trail Determines Scope: Only visited nodes contribute evidence
3. Strength from Variety: More diverse trails = stronger evidence

Teaching:
    gotcha: Evidence strength is computed from trail properties, not set manually.
            Use TrailAsEvidence.to_evidence() which computes it for you.

    gotcha: EvidenceScope.accessible() only returns evidence reachable from
            the exploration trail. Evidence exists but may not be accessible.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .types import (
    ContextNode,
    Evidence,
    EvidenceStrength,
    Observer,
    Trail,
    TrailStep,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


# =============================================================================
# Trail as Evidence
# =============================================================================


@dataclass
class TrailAsEvidence:
    """
    Converts exploration trails into evidence for claims.

    A trail IS evidence. The conversion captures:
    - Which nodes were visited
    - Which edges were followed
    - The order of exploration
    - Annotations made during exploration
    """

    def to_evidence(self, trail: Trail, claim: str) -> Evidence:
        """
        Convert a trail to evidence for a specific claim.

        The evidence strength is computed from trail properties:
        - Weak: < 3 steps OR only one edge type
        - Moderate: 3-10 steps with variety
        - Strong: > 10 steps with multiple edge types
        """
        strength = self._compute_strength(trail)

        return Evidence(
            id=str(uuid.uuid4()),
            claim=claim,
            source="exploration_trail",
            content=trail.serialize(),
            strength=strength,
            metadata={
                "trail_id": trail.id,
                "trail_name": trail.name,
                "steps": str(len(trail.steps)),
                "nodes_visited": ",".join(trail.nodes_visited),
                "edges_followed": ",".join(trail.edges_followed),
                "unique_edges": str(len(set(trail.edges_followed))),
                "created_by": trail.created_by,
            },
            created_at=datetime.now(timezone.utc),
        )

    def _compute_strength(self, trail: Trail) -> EvidenceStrength:
        """
        Compute evidence strength from trail properties.

        Criteria:
        - Weak: < 3 steps OR only one edge type followed
        - Moderate: 3-10 steps with at least 2 edge types
        - Strong: > 10 steps with multiple edge types
        """
        step_count = len(trail.steps)
        unique_edges = len(set(trail.edges_followed))

        if step_count < 3:
            return EvidenceStrength.WEAK

        if unique_edges < 2:
            return EvidenceStrength.WEAK  # Only followed one edge type

        if step_count > 10:
            return EvidenceStrength.STRONG

        return EvidenceStrength.MODERATE


# =============================================================================
# Evidence Collector
# =============================================================================


@dataclass
class EvidenceCollector:
    """
    Collects evidence during exploration.

    Records navigation actions as they happen, building up
    a corpus of evidence that can be used for claims.
    """

    _evidence: list[Evidence] = field(default_factory=list)
    _navigation_log: list[dict[str, str]] = field(default_factory=list)

    async def record_navigation(
        self,
        source: set[ContextNode],
        edge: str,
        destinations: set[ContextNode],
    ) -> None:
        """
        Record a navigation step.

        Creates an implicit evidence entry for "Agent explored [edge] from [source]".
        """
        source_paths = [n.path for n in source]
        dest_paths = [n.path for n in destinations]

        self._navigation_log.append(
            {
                "action": "navigate",
                "edge": edge,
                "source": ",".join(source_paths),
                "destinations": ",".join(dest_paths),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def record_observation(
        self,
        node: ContextNode,
        observation: str,
        strength: EvidenceStrength = EvidenceStrength.MODERATE,
    ) -> Evidence:
        """
        Record an observation at a node.

        This creates explicit evidence that can support claims.
        """
        evidence = Evidence(
            id=str(uuid.uuid4()),
            claim="",  # Will be filled when used for a claim
            source="observation",
            content=observation,
            strength=strength,
            metadata={
                "node_path": node.path,
                "holon": node.holon,
            },
        )
        self._evidence.append(evidence)
        return evidence

    def record_dead_end(self, node: ContextNode, reason: str) -> Evidence:
        """Record finding a dead end (useful negative evidence)."""
        evidence = Evidence(
            id=str(uuid.uuid4()),
            claim="",
            source="dead_end",
            content=f"Dead end at {node.path}: {reason}",
            strength=EvidenceStrength.WEAK,
            metadata={
                "node_path": node.path,
                "reason": reason,
            },
        )
        self._evidence.append(evidence)
        return evidence

    async def for_claim(self, claim: str) -> list[Evidence]:
        """
        Get all evidence relevant to a claim.

        Filters collected evidence and updates claim field.
        """
        # For now, return all evidence with updated claim
        # In real impl, would use semantic similarity to filter
        return [
            Evidence(
                id=e.id,
                claim=claim,
                source=e.source,
                content=e.content,
                strength=e.strength,
                metadata=e.metadata,
                created_at=e.created_at,
            )
            for e in self._evidence
        ]

    @property
    def evidence_count(self) -> int:
        """Number of evidence items collected."""
        return len(self._evidence)

    @property
    def strong_count(self) -> int:
        """Number of strong evidence items."""
        return sum(1 for e in self._evidence if e.strength == EvidenceStrength.STRONG)

    @property
    def navigation_steps(self) -> int:
        """Number of navigation steps recorded."""
        return len(self._navigation_log)


# =============================================================================
# Evidence Scope
# =============================================================================


@dataclass
class EvidenceScope:
    """
    Scopes evidence to exploration context.

    Only evidence about visited nodes is accessible.
    This prevents agents from claiming access to evidence
    they haven't actually explored.

    Accessibility rules:
    1. Evidence about a visited node is accessible
    2. Evidence reachable via 'evidence' hyperedges from visited nodes
    3. Evidence about claims the agent is investigating
    """

    trail: Trail
    observer: Observer = field(
        default_factory=lambda: Observer(id="default", archetype="developer")
    )
    _all_evidence: list[Evidence] = field(default_factory=list)
    _accessible_ids: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        """Build accessibility set from trail."""
        self._build_accessibility()

    def _build_accessibility(self) -> None:
        """Compute which evidence IDs are accessible from this trail."""
        self._accessible_ids = set()
        visited_nodes = self.trail.nodes_visited

        # Evidence about visited nodes is accessible
        for evidence in self._all_evidence:
            node_path = evidence.metadata.get("node_path", "")
            if node_path in visited_nodes:
                self._accessible_ids.add(evidence.id)

    def add_evidence(self, evidence: Evidence) -> None:
        """Add evidence to the scope's knowledge."""
        self._all_evidence.append(evidence)
        self._build_accessibility()  # Rebuild accessibility

    def accessible(self) -> list[Evidence]:
        """Only evidence reachable from exploration."""
        return [e for e in self._all_evidence if e.id in self._accessible_ids]

    def inaccessible(self) -> list[Evidence]:
        """Evidence that exists but is not accessible from this trail."""
        return [e for e in self._all_evidence if e.id not in self._accessible_ids]

    def is_accessible(self, evidence: Evidence) -> bool:
        """Check if a specific piece of evidence is accessible."""
        return evidence.id in self._accessible_ids

    @property
    def accessibility_ratio(self) -> float:
        """Fraction of evidence that is accessible (0.0 to 1.0)."""
        if not self._all_evidence:
            return 1.0
        return len(self._accessible_ids) / len(self._all_evidence)


# =============================================================================
# Evidence Summary
# =============================================================================


@dataclass(frozen=True)
class EvidenceSummary:
    """Summary of evidence for display/reporting."""

    total_count: int
    weak_count: int
    moderate_count: int
    strong_count: int
    sources: frozenset[str]

    @classmethod
    def from_evidence(cls, evidence: list[Evidence]) -> EvidenceSummary:
        """Create summary from evidence list."""
        weak = sum(1 for e in evidence if e.strength == EvidenceStrength.WEAK)
        moderate = sum(1 for e in evidence if e.strength == EvidenceStrength.MODERATE)
        strong = sum(1 for e in evidence if e.strength == EvidenceStrength.STRONG)
        sources = frozenset(e.source for e in evidence)

        return cls(
            total_count=len(evidence),
            weak_count=weak,
            moderate_count=moderate,
            strong_count=strong,
            sources=sources,
        )

    def __str__(self) -> str:
        return (
            f"{self.total_count} items "
            f"({self.strong_count} strong, "
            f"{self.moderate_count} moderate, "
            f"{self.weak_count} weak)"
        )


# =============================================================================
# Portal Expansion Evidence
# =============================================================================


@dataclass(frozen=True)
class PortalExpansionEvidence:
    """
    Weak evidence from portal expansion (exploration fact).

    Portal expansion is navigation, not conclusion. Opening a portal
    creates weak evidence that can contribute to claims but doesn't
    constitute proof on its own.

    From spec/protocols/portal-token.md section 10.2:
        "Opening a portal creates evidence... strength='weak'"

    Properties:
        portal_path: The path through the portal tree (e.g., "tests/unit")
        edge_type: The hyperedge type followed (e.g., "tests", "implements")
        files_opened: Files that were opened by this expansion
        parent_path: Where the expansion started from

    Laws:
        1. Immutability: Evidence is frozen, cannot be modified
        2. Weakness: Portal expansion is always weak evidence
        3. Completeness: All fields needed to reconstruct the expansion
    """

    id: str
    portal_path: str
    edge_type: str
    files_opened: tuple[str, ...]
    parent_path: str = ""
    depth: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def strength(self) -> EvidenceStrength:
        """Portal expansion is always weak evidence."""
        return EvidenceStrength.WEAK

    @property
    def source(self) -> str:
        """Source identifier for this type of evidence."""
        return "portal_expansion"

    @property
    def claim(self) -> str:
        """Implicit claim from the expansion."""
        return f"Explored [{self.edge_type}] at {self.portal_path}"

    @property
    def content(self) -> str:
        """Serialized content for evidence matching."""
        files = ", ".join(self.files_opened) if self.files_opened else "no files"
        return f"Portal expansion [{self.edge_type}] → {files}"

    def to_evidence(self) -> Evidence:
        """
        Convert to base Evidence type for compatibility.

        Useful when collecting portal evidence alongside other evidence types.
        """
        return Evidence(
            id=self.id,
            claim=self.claim,
            source=self.source,
            content=self.content,
            strength=self.strength,
            metadata={
                "portal_path": self.portal_path,
                "edge_type": self.edge_type,
                "files_opened": ",".join(self.files_opened),
                "parent_path": self.parent_path,
                "depth": str(self.depth),
            },
            created_at=self.created_at,
        )

    @classmethod
    def from_expansion(
        cls,
        portal_path: str,
        edge_type: str,
        files_opened: list[str] | tuple[str, ...],
        parent_path: str = "",
        depth: int = 0,
    ) -> "PortalExpansionEvidence":
        """
        Factory method to create evidence from an expansion.

        Args:
            portal_path: Path to the expanded portal
            edge_type: Type of hyperedge followed
            files_opened: Files opened by the expansion
            parent_path: Parent path (where expansion started)
            depth: Nesting depth in the portal tree
        """
        return cls(
            id=str(uuid.uuid4()),
            portal_path=portal_path,
            edge_type=edge_type,
            files_opened=tuple(files_opened) if isinstance(files_opened, list) else files_opened,
            parent_path=parent_path,
            depth=depth,
        )


__all__ = [
    "TrailAsEvidence",
    "EvidenceCollector",
    "EvidenceScope",
    "EvidenceSummary",
    "PortalExpansionEvidence",
]
