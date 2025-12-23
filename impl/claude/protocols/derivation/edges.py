"""
Witnessed Edges: Evidence on Derivation Relationships.

Phase 3 of the Derivation Framework adds metadata to edges:
- Derivation rationale: WHY this parent was chosen
- Principle flow tracking: WHICH principles flow through
- Witness attachment: Mark IDs proving the edge works

The key insight: Edges carry justification, not just structure.

    "The edge IS the proof. The mark IS the witness."

Teaching:
    gotcha: WitnessedEdge is separate from the derives_from tuple.
            The tuple is structural (required for registration).
            WitnessedEdge adds metadata (optional, accumulates over time).

    gotcha: Bootstrap edges (CONSTITUTION -> Id, etc.) are pre-populated
            with categorical evidence. Don't try to weaken them.

    gotcha: Edge key is (source, target) tuple, not a string.
            Use edge.edge_key property for consistent access.

Heritage:
    - Derivation Framework -> spec/protocols/derivation-framework.md
    - Witness Primitives -> services/witness/mark.py
    - Agent-as-Witness -> spec/heritage.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum

from .types import EvidenceType


class EdgeType(str, Enum):
    """
    Types of derivation relationships.

    Most edges are DERIVES_FROM, but we support richer relationships
    for spec-to-impl mappings and extension patterns.
    """

    DERIVES_FROM = "derives_from"  # Standard derivation (categorical/empirical)
    IMPLEMENTS = "implements"  # Spec -> Impl relationship
    EXTENDS = "extends"  # Extension without full derivation
    INSTANTIATES = "instantiates"  # Template -> Instance


@dataclass(frozen=True)
class PrincipleFlow:
    """
    Which principles flow through this edge.

    Not all parents contribute all principles equally.
    Id contributes Composable (weight=1.0), but not Joy-Inducing.
    Judge contributes Ethical (weight=1.0), but not Composable.

    The seven principles from spec/principles.md:
    - Tasteful, Curated, Ethical, Joy-Inducing
    - Composable, Heterarchical, Generative

    Teaching:
        gotcha: contribution_weight is about THIS edge, not the principle globally.
                A principle can flow through multiple edges with different weights.
    """

    principle: str
    source_draw_strength: float  # How strongly source instantiates (0.0-1.0)
    contribution_weight: float  # How much flows to child (0.0-1.0)
    evidence: tuple[str, ...] = ()  # Evidence sources for this flow

    def __post_init__(self) -> None:
        """Validate strength and weight are in [0, 1]."""
        if not 0.0 <= self.source_draw_strength <= 1.0:
            object.__setattr__(
                self,
                "source_draw_strength",
                max(0.0, min(1.0, self.source_draw_strength)),
            )
        if not 0.0 <= self.contribution_weight <= 1.0:
            object.__setattr__(
                self,
                "contribution_weight",
                max(0.0, min(1.0, self.contribution_weight)),
            )


@dataclass(frozen=True)
class DerivationRationale:
    """
    WHY this edge exists - the reasoning behind the derivation choice.

    Captures the decision trail that led to this parent-child relationship.
    This is the "proof" in "the proof IS the decision."

    Teaching:
        gotcha: decision_id links to kg decide records. Use it to trace
                the full dialectic (Kent's view, Claude's view, synthesis).
    """

    summary: str  # One-line summary (e.g., "Inherits composition laws")
    reasoning: str  # Full reasoning text
    decided_at: datetime
    decision_id: str | None = None  # Optional link to kg decide record
    alternatives_considered: tuple[str, ...] = ()  # Other parents considered


@dataclass(frozen=True)
class WitnessedEdge:
    """
    A derivation edge enriched with witness evidence.

    Immutable (frozen) following the Derivation pattern.
    Edges accumulate evidence over time via functional updates.

    The three aspects of edge evidence:
    1. Rationale: WHY this parent was chosen
    2. Principle flows: WHICH principles flow through
    3. Witness marks: Mark IDs proving the edge works

    Laws:
    1. Immutability: Edges are frozen; updates return new edges
    2. Categorical Indefeasibility: Bootstrap edges can't be weakened
    3. Logarithmic Strengthening: More marks = stronger, with diminishing returns

    Teaching:
        gotcha: Empty edges (no metadata) are valid and common.
                Use get_edge() which returns WitnessedEdge.empty() if not stored.

        gotcha: edge_strength is computed from evidence, not set directly.
                Use with_mark() to add evidence and auto-update strength.
    """

    # Edge identity
    source: str  # Parent agent name
    target: str  # Child agent name
    edge_type: EdgeType = EdgeType.DERIVES_FROM

    # Derivation rationale (WHY this edge exists)
    rationale: DerivationRationale | None = None

    # Principle flows (WHICH principles flow through)
    principle_flows: tuple[PrincipleFlow, ...] = ()

    # Witness evidence (Mark IDs proving the edge works)
    mark_ids: tuple[str, ...] = ()  # L0: Human attention markers
    test_ids: tuple[str, ...] = ()  # L1: Automated tests
    proof_ids: tuple[str, ...] = ()  # L2: Formal proofs (Dafny/Lean4)

    # Edge confidence (computed from evidence)
    evidence_type: EvidenceType = EvidenceType.EMPIRICAL
    edge_strength: float = 0.5  # How strongly this edge is evidenced
    last_witnessed: datetime | None = None

    @classmethod
    def empty(cls, source: str, target: str) -> WitnessedEdge:
        """
        Create an empty edge (no evidence yet).

        This is the default for edges that exist structurally
        (in derives_from tuple) but have no metadata yet.
        """
        return cls(source=source, target=target)

    @classmethod
    def axiomatic(cls, source: str, target: str) -> WitnessedEdge:
        """
        Create a bootstrap edge with categorical evidence.

        Used for CONSTITUTION -> Bootstrap agent edges.
        These edges are definitional, not discovered.
        """
        return cls(
            source=source,
            target=target,
            edge_type=EdgeType.DERIVES_FROM,
            rationale=DerivationRationale(
                summary="Axiomatic derivation from CONSTITUTION",
                reasoning="Bootstrap agents derive from CONSTITUTION by definition. "
                "This is the ground truth of the derivation framework.",
                decided_at=datetime.now(timezone.utc),
                decision_id="bootstrap",
            ),
            evidence_type=EvidenceType.CATEGORICAL,
            edge_strength=1.0,
            last_witnessed=datetime.now(timezone.utc),
        )

    def with_mark(self, mark_id: str) -> WitnessedEdge:
        """
        Return new edge with added mark.

        Marks strengthen the edge logarithmically:
        - 1 mark: ~0.55
        - 10 marks: ~0.70
        - 100 marks: ~0.85
        - 1000 marks: ~0.95 (capped)

        This prevents gaming via mark spam while rewarding genuine usage.
        """
        if mark_id in self.mark_ids:
            return self  # Idempotent

        new_marks = self.mark_ids + (mark_id,)

        # Logarithmic strengthening: base 0.5, +0.15 per order of magnitude
        # log10(n+1) ensures 1 mark gives strength > 0.5 (since log10(2) > 0)
        new_strength = min(0.95, 0.5 + 0.15 * math.log10(len(new_marks) + 1))

        # Don't weaken categorical edges
        if self.is_categorical:
            new_strength = 1.0

        return replace(
            self,
            mark_ids=new_marks,
            edge_strength=new_strength,
            last_witnessed=datetime.now(timezone.utc),
        )

    def with_test(self, test_id: str) -> WitnessedEdge:
        """Return new edge with added test ID (L1 evidence)."""
        if test_id in self.test_ids:
            return self

        new_tests = self.test_ids + (test_id,)

        # Tests are stronger evidence than marks
        # Base 0.55, +0.12 per order of magnitude
        # log10(n+1) ensures 1 test gives strength > 0.55
        test_contribution = 0.55 + 0.12 * math.log10(len(new_tests) + 1)
        new_strength = min(0.95, max(self.edge_strength, test_contribution))

        if self.is_categorical:
            new_strength = 1.0

        return replace(
            self,
            test_ids=new_tests,
            edge_strength=new_strength,
            last_witnessed=datetime.now(timezone.utc),
        )

    def with_proof(self, proof_id: str) -> WitnessedEdge:
        """
        Return new edge with added formal proof ID (L2 evidence).

        Proofs are categorical evidence - they make the edge indefeasible.
        """
        if proof_id in self.proof_ids:
            return self

        new_proofs = self.proof_ids + (proof_id,)

        return replace(
            self,
            proof_ids=new_proofs,
            evidence_type=EvidenceType.CATEGORICAL,  # Upgrade to categorical
            edge_strength=1.0,
            last_witnessed=datetime.now(timezone.utc),
        )

    def with_rationale(self, rationale: DerivationRationale) -> WitnessedEdge:
        """Return new edge with rationale."""
        return replace(self, rationale=rationale)

    def with_principle_flow(self, flow: PrincipleFlow) -> WitnessedEdge:
        """
        Return new edge with added principle flow.

        If a flow for the same principle already exists, it's replaced.
        """
        # Build dict keyed by principle, replace existing
        existing = {f.principle: f for f in self.principle_flows}
        existing[flow.principle] = flow

        # Sort by principle name for deterministic ordering
        sorted_flows = tuple(sorted(existing.values(), key=lambda f: f.principle))

        return replace(self, principle_flows=sorted_flows)

    @property
    def is_categorical(self) -> bool:
        """Categorical edges don't decay and can't be weakened."""
        return self.evidence_type == EvidenceType.CATEGORICAL

    @property
    def evidence_count(self) -> int:
        """Total evidence items attached to this edge."""
        return len(self.mark_ids) + len(self.test_ids) + len(self.proof_ids)

    @property
    def edge_key(self) -> tuple[str, str]:
        """Unique key for this edge: (source, target)."""
        return (self.source, self.target)

    def __repr__(self) -> str:
        """Compact representation for debugging."""
        return (
            f"WitnessedEdge({self.source} -> {self.target}, "
            f"strength={self.edge_strength:.0%}, "
            f"evidence={self.evidence_count})"
        )


__all__ = [
    "EdgeType",
    "PrincipleFlow",
    "DerivationRationale",
    "WitnessedEdge",
]
