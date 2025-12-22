"""
Evidence Ladder: Stratified Evidence Infrastructure for Witness Assurance.

Evidence is stratified. Each level unlocks trust:

| Level | Name | Source | Meaning | kgents Artifact |
|------:|------|--------|---------|-----------------|
| L-2 | PromptAncestor | LLM invocation | Generative thought | Phase 3 |
| L-1 | TraceWitness | Runtime trace | Actual behavior | TraceWitness |
| L0 | Mark | Human attention | "This matters" | WitnessMark |
| L1 | Test | Automated check | Repeatable claim | Test artifact |
| L2 | Proof | Formal discharge | Law verified | ASHC proof |
| L3 | Economic Bet | Credibility stake | Confidence calibration | ASHC bet |

The Core Insight:
    Evidence is not flat. Marks are not proofs. Tests are not proofs.
    TraceWitness is the runtime proof primitive. ASHC provides the
    confidence economics. And beneath it all: the prompts that
    generated every artifact.

Philosophy:
    "The proof IS the decision. The mark IS the witness.
     Every line of code has a genealogy."

See: plans/witness-assurance-protocol.md
See: spec/protocols/witness-supersession.md

Teaching:
    gotcha: EvidenceLevel uses IntEnum for natural ordering. L-2 < L-1 < L0.
            Negative levels represent evidence "beneath" human attention -
            the generative substrate that produced the code.
            (Evidence: test_evidence.py::test_evidence_level_ordering)

    gotcha: Evidence dataclass is frozen (immutable). To "update" evidence,
            create a new Evidence linked via metadata. This matches the
            Mark and Crystal patterns.
            (Evidence: test_evidence.py::test_evidence_immutability)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Any
from uuid import uuid4

if TYPE_CHECKING:
    from .mark import Proof


# =============================================================================
# Type Aliases
# =============================================================================


def generate_evidence_id() -> str:
    """Generate a unique Evidence ID."""
    return f"evd-{uuid4().hex[:12]}"


def compute_content_hash(content: str) -> str:
    """Compute SHA-256 hash of content for deduplication."""
    return hashlib.sha256(content.encode()).hexdigest()[:16]


# =============================================================================
# EvidenceLevel IntEnum (L-2 to L3)
# =============================================================================


class EvidenceLevel(IntEnum):
    """
    Evidence stratification levels (L-∞ to L3).

    Uses IntEnum for natural ordering:
        EvidenceLevel.ORPHAN < EvidenceLevel.PROMPT < EvidenceLevel.TRACE < EvidenceLevel.MARK

    Levels:
    - ORPHAN (-3): No lineage - artifact exists but has no known genealogy
    - PROMPT (-2): Generative origin - the prompt that created an artifact
    - TRACE (-1): Runtime observation - actual behavior via TraceWitness
    - MARK (0): Human attention - "this matters" via WitnessMark
    - TEST (1): Automated test - repeatable claim via pytest/etc
    - PROOF (2): Formal proof - law verified via ASHC discharge
    - BET (3): Economic stake - confidence calibration via ASHC bet

    The negative levels are "beneath" human attention - they capture
    the generative provenance that produced the code. ORPHAN (L-∞) is
    special: it represents artifacts WITHOUT lineage - weeds in the garden
    that need tending.

    Philosophy:
        "Orphans are weeds. Weeds exist; we tend them."
        There is no "hide orphans" option. The garden is honest.
    """

    ORPHAN = -3  # L-∞: No lineage (the weeds - need tending)
    PROMPT = -2  # L-2: Generative origin (PromptAncestor) - Phase 3
    TRACE = -1  # L-1: Runtime observation (TraceWitness)
    MARK = 0  # L0: Human attention (WitnessMark)
    TEST = 1  # L1: Automated test artifact
    PROOF = 2  # L2: Formal proof (ASHC discharge)
    BET = 3  # L3: Economic stake (ASHC bet/settlement)

    @property
    def display_name(self) -> str:
        """Human-readable name for display."""
        return {
            EvidenceLevel.ORPHAN: "Orphan",
            EvidenceLevel.PROMPT: "Prompt",
            EvidenceLevel.TRACE: "Trace",
            EvidenceLevel.MARK: "Mark",
            EvidenceLevel.TEST: "Test",
            EvidenceLevel.PROOF: "Proof",
            EvidenceLevel.BET: "Bet",
        }[self]

    @property
    def level_label(self) -> str:
        """Compact level label (L-∞, L-2, L-1, L0, etc)."""
        if self == EvidenceLevel.ORPHAN:
            return "L-∞"
        return f"L{self.value}"

    @property
    def description(self) -> str:
        """Brief description of what this level represents."""
        return {
            EvidenceLevel.ORPHAN: "Artifact without lineage (weed)",
            EvidenceLevel.PROMPT: "Generative thought that created artifact",
            EvidenceLevel.TRACE: "Runtime behavior observation",
            EvidenceLevel.MARK: "Human attention marker",
            EvidenceLevel.TEST: "Automated repeatable check",
            EvidenceLevel.PROOF: "Formal law verification",
            EvidenceLevel.BET: "Economic stake on confidence",
        }[self]

    @property
    def is_orphan(self) -> bool:
        """True if this is an orphan (no lineage) level."""
        return self == EvidenceLevel.ORPHAN

    @property
    def color(self) -> str:
        """Living Earth palette color for visualization."""
        return {
            EvidenceLevel.ORPHAN: "#991B1B",  # Red - needs attention
            EvidenceLevel.PROMPT: "#84A98C",  # Sage - generative
            EvidenceLevel.TRACE: "#06B6D4",  # Cyan - runtime
            EvidenceLevel.MARK: "#B87333",  # Copper - human
            EvidenceLevel.TEST: "#22C55E",  # Green - automation
            EvidenceLevel.PROOF: "#A855F7",  # Purple - formal
            EvidenceLevel.BET: "#F59E0B",  # Amber - economic
        }[self]


# =============================================================================
# EvidenceRelation Enum
# =============================================================================


class EvidenceRelation(Enum):
    """
    Types of relationships between Evidence artifacts.

    These relations enable building an evidence graph (genealogy):
    - SUPPORTS: This evidence strengthens the claim
    - REFUTES: This evidence contradicts/weakens the claim
    - SUPERSEDES: This evidence replaces an older version
    - EXTENDS: This evidence adds to (but doesn't replace) existing evidence
    - QUALIFIES: This evidence adds conditions/limitations

    Philosophy:
        "Evidence is not flat. Relations matter."
        Just knowing evidence exists isn't enough - we need to know
        how it relates to other evidence for proper assurance.
    """

    SUPPORTS = "supports"  # Strengthens the claim
    REFUTES = "refutes"  # Contradicts the claim
    SUPERSEDES = "supersedes"  # Replaces older evidence
    EXTENDS = "extends"  # Adds to without replacing
    QUALIFIES = "qualifies"  # Adds conditions/limitations

    @property
    def is_positive(self) -> bool:
        """True if this relation strengthens the claim."""
        return self in (EvidenceRelation.SUPPORTS, EvidenceRelation.EXTENDS)

    @property
    def is_negative(self) -> bool:
        """True if this relation weakens the claim."""
        return self in (EvidenceRelation.REFUTES, EvidenceRelation.QUALIFIES)

    @property
    def symbol(self) -> str:
        """Symbol for compact display."""
        return {
            EvidenceRelation.SUPPORTS: "+",
            EvidenceRelation.REFUTES: "−",
            EvidenceRelation.SUPERSEDES: "→",
            EvidenceRelation.EXTENDS: "⊕",
            EvidenceRelation.QUALIFIES: "?",
        }[self]


# =============================================================================
# Evidence Dataclass
# =============================================================================


@dataclass(frozen=True)
class Evidence:
    """
    Unified evidence artifact across all levels.

    Evidence captures:
    - WHAT level of trust it represents (level)
    - WHAT type of source produced it (source_type)
    - WHAT spec it evidences (target_spec)
    - WHEN it was created (created_at)
    - WHO created it (created_by)
    - HOW confident we are (confidence)

    Laws:
    - Immutability: Evidence is frozen after creation
    - Deduplication: content_hash enables duplicate detection
    - Provenance: metadata can link to source artifacts

    Example:
        >>> evidence = Evidence(
        ...     id=generate_evidence_id(),
        ...     level=EvidenceLevel.MARK,
        ...     source_type="mark",
        ...     target_spec="spec/protocols/witness.md",
        ...     content_hash=compute_content_hash("Test passes"),
        ...     created_at=datetime.now(),
        ...     created_by="kent",
        ...     metadata={"mark_id": "mark-abc123"},
        ... )
        >>> evidence.is_runtime  # True (MARK is L0, runtime)
        >>> evidence.is_automated  # False (MARK < TEST)
    """

    # Identity
    id: str = field(default_factory=generate_evidence_id)

    # Stratification
    level: EvidenceLevel = EvidenceLevel.MARK

    # Source classification
    source_type: str = "unknown"  # "prompt", "trace", "mark", "test", "proof", "bet"

    # Target (what this evidences)
    target_spec: str | None = None  # Spec path, e.g., "spec/protocols/witness.md"

    # Content deduplication
    content_hash: str = ""

    # Temporal
    created_at: datetime = field(default_factory=datetime.now)

    # Authorship
    created_by: str = "system"  # Agent/human identifier

    # Metadata (for linking to source artifacts)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Confidence (for Phase 5 decay integration)
    confidence: float = 1.0  # [0, 1] - matches Crystal pattern

    # Optional Toulmin argumentation structure (for MARK level and above)
    proof: "Proof | None" = None

    # =========================================================================
    # Lineage/Ancestry (for genealogy tracking)
    # =========================================================================

    # Parent evidence IDs (enables genealogy graph traversal)
    parent_ids: tuple[str, ...] = ()

    # Relation to parent(s) - how this evidence relates to its ancestors
    relation: EvidenceRelation | None = None

    # ==========================================================================
    # Properties (classification helpers)
    # ==========================================================================

    @property
    def is_orphan(self) -> bool:
        """True if this evidence is an orphan (no lineage)."""
        return self.level == EvidenceLevel.ORPHAN

    @property
    def is_generative(self) -> bool:
        """True if this evidence is generative (prompt-level)."""
        return self.level == EvidenceLevel.PROMPT

    @property
    def is_runtime(self) -> bool:
        """True if this evidence is runtime or below (trace, mark, prompt, orphan)."""
        return self.level <= EvidenceLevel.MARK

    @property
    def is_automated(self) -> bool:
        """True if this evidence is automated (test, proof, bet)."""
        return self.level >= EvidenceLevel.TEST

    @property
    def is_formal(self) -> bool:
        """True if this evidence is formally verified (proof, bet)."""
        return self.level >= EvidenceLevel.PROOF

    @property
    def has_economic_stake(self) -> bool:
        """True if this evidence has economic stake (bet level)."""
        return self.level == EvidenceLevel.BET

    @property
    def has_lineage(self) -> bool:
        """True if this evidence has parent evidence (is not an orphan)."""
        return len(self.parent_ids) > 0 or self.level > EvidenceLevel.ORPHAN

    @property
    def needs_tending(self) -> bool:
        """True if this evidence needs human attention (weed in the garden)."""
        return self.is_orphan or (self.confidence < 0.3 and not self.is_automated)

    # ==========================================================================
    # Factory methods (for common creation patterns)
    # ==========================================================================

    @classmethod
    def from_orphan(
        cls,
        artifact_path: str,
        artifact_type: str = "file",
        suggested_prompt: str | None = None,
    ) -> "Evidence":
        """
        Create L-∞ (ORPHAN) evidence for an artifact without lineage.

        Orphans are weeds in the garden - they exist, we tend them.
        This factory is used when we discover an artifact (file, function,
        test) that has no known genealogy.

        Args:
            artifact_path: Path to the orphaned artifact
            artifact_type: Type of artifact ("file", "function", "test", etc.)
            suggested_prompt: Optional suggested prompt that might have created this

        Returns:
            Evidence at ORPHAN level with needs_tending=True
        """
        return cls(
            id=generate_evidence_id(),
            level=EvidenceLevel.ORPHAN,
            source_type="orphan",
            target_spec=None,  # Orphans don't evidence specs yet
            content_hash=compute_content_hash(artifact_path),
            created_at=datetime.now(),
            created_by="witness",
            metadata={
                "artifact_path": artifact_path,
                "artifact_type": artifact_type,
                "suggested_prompt": suggested_prompt,
            },
            confidence=0.0,  # Zero confidence - needs human tending
        )

    @classmethod
    def from_prompt(
        cls,
        prompt_text: str,
        prompt_id: str | None = None,
        model: str = "unknown",
        session_id: str | None = None,
        target_spec: str | None = None,
        created_by: str = "claude",
    ) -> "Evidence":
        """
        Create L-2 (PROMPT) evidence from a generative prompt.

        PromptAncestors are the generative substrate beneath all code.
        Every artifact has a genealogy; prompts are the roots.

        Args:
            prompt_text: The actual prompt text
            prompt_id: Optional ID of the prompt (from LLM tracking)
            model: Model that processed the prompt (e.g., "claude-3.5-sonnet")
            session_id: Session/conversation ID for context
            target_spec: Spec this prompt was meant to implement
            created_by: Agent that generated the prompt

        Returns:
            Evidence at PROMPT level (generative origin)
        """
        return cls(
            id=generate_evidence_id(),
            level=EvidenceLevel.PROMPT,
            source_type="prompt",
            target_spec=target_spec,
            content_hash=compute_content_hash(prompt_text[:1000]),  # Truncate for hashing
            created_at=datetime.now(),
            created_by=created_by,
            metadata={
                "prompt_preview": prompt_text[:200],  # Preview only
                "prompt_id": prompt_id,
                "model": model,
                "session_id": session_id,
                "prompt_length": len(prompt_text),
            },
            confidence=0.7,  # Prompts are confident but not witnessed
        )

    @classmethod
    def from_trace_witness(
        cls,
        trace_id: str,
        agent_path: str,
        target_spec: str | None = None,
        created_by: str = "system",
    ) -> Evidence:
        """Create L-1 (TRACE) evidence from a TraceWitness."""
        return cls(
            id=generate_evidence_id(),
            level=EvidenceLevel.TRACE,
            source_type="trace",
            target_spec=target_spec,
            content_hash=compute_content_hash(trace_id),
            created_at=datetime.now(),
            created_by=created_by,
            metadata={
                "trace_id": trace_id,
                "agent_path": agent_path,
            },
            confidence=0.9,  # Runtime traces are strong evidence
        )

    @classmethod
    def from_witness_mark(
        cls,
        mark_id: str,
        action: str,
        target_spec: str | None = None,
        created_by: str = "kent",
        proof: "Proof | None" = None,
    ) -> Evidence:
        """Create L0 (MARK) evidence from a WitnessMark."""
        return cls(
            id=generate_evidence_id(),
            level=EvidenceLevel.MARK,
            source_type="mark",
            target_spec=target_spec,
            content_hash=compute_content_hash(action),
            created_at=datetime.now(),
            created_by=created_by,
            metadata={"mark_id": mark_id},
            confidence=0.8,  # Marks are human attention, high confidence
            proof=proof,
        )

    @classmethod
    def from_test(
        cls,
        test_path: str,
        test_name: str,
        passed: bool,
        target_spec: str | None = None,
    ) -> Evidence:
        """Create L1 (TEST) evidence from a test result."""
        return cls(
            id=generate_evidence_id(),
            level=EvidenceLevel.TEST,
            source_type="test",
            target_spec=target_spec,
            content_hash=compute_content_hash(f"{test_path}::{test_name}"),
            created_at=datetime.now(),
            created_by="pytest",
            metadata={
                "test_path": test_path,
                "test_name": test_name,
                "passed": passed,
            },
            confidence=1.0 if passed else 0.0,
        )

    @classmethod
    def from_proof(
        cls,
        proof_id: str,
        obligation_discharged: str,
        target_spec: str | None = None,
    ) -> Evidence:
        """Create L2 (PROOF) evidence from an ASHC proof."""
        return cls(
            id=generate_evidence_id(),
            level=EvidenceLevel.PROOF,
            source_type="proof",
            target_spec=target_spec,
            content_hash=compute_content_hash(proof_id),
            created_at=datetime.now(),
            created_by="ashc",
            metadata={
                "proof_id": proof_id,
                "obligation": obligation_discharged,
            },
            confidence=1.0,  # Proofs are definitive
        )

    @classmethod
    def from_bet(
        cls,
        bet_id: str,
        stake: float,
        settled: bool,
        settlement_value: float = 0.0,
        target_spec: str | None = None,
    ) -> Evidence:
        """Create L3 (BET) evidence from an ASHC bet."""
        return cls(
            id=generate_evidence_id(),
            level=EvidenceLevel.BET,
            source_type="bet",
            target_spec=target_spec,
            content_hash=compute_content_hash(bet_id),
            created_at=datetime.now(),
            created_by="ashc",
            metadata={
                "bet_id": bet_id,
                "stake": stake,
                "settled": settled,
                "settlement_value": settlement_value,
            },
            confidence=settlement_value if settled else 0.5,
        )

    # ==========================================================================
    # Serialization
    # ==========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "id": self.id,
            "level": self.level.value,
            "level_label": self.level.level_label,
            "source_type": self.source_type,
            "target_spec": self.target_spec,
            "content_hash": self.content_hash,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "metadata": self.metadata,
            "confidence": self.confidence,
            # Lineage fields
            "parent_ids": list(self.parent_ids),
            "relation": self.relation.value if self.relation else None,
        }
        if self.proof is not None:
            result["proof"] = self.proof.to_dict()
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Evidence:
        """Create from dictionary."""
        from .mark import Proof

        proof = None
        if data.get("proof"):
            proof = Proof.from_dict(data["proof"])

        # Parse relation if present
        relation = None
        if data.get("relation"):
            relation = EvidenceRelation(data["relation"])

        return cls(
            id=data.get("id", generate_evidence_id()),
            level=EvidenceLevel(data.get("level", 0)),
            source_type=data.get("source_type", "unknown"),
            target_spec=data.get("target_spec"),
            content_hash=data.get("content_hash", ""),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.now(),
            created_by=data.get("created_by", "system"),
            metadata=data.get("metadata", {}),
            confidence=data.get("confidence", 1.0),
            proof=proof,
            parent_ids=tuple(data.get("parent_ids", [])),
            relation=relation,
        )

    def __repr__(self) -> str:
        """Concise representation."""
        spec_preview = ""
        if self.target_spec:
            spec_preview = f", spec={self.target_spec[:30]}..."
        return (
            f"Evidence("
            f"id={self.id[:12]}..., "
            f"level={self.level.level_label}, "
            f"source={self.source_type}, "
            f"confidence={self.confidence:.2f}"
            f"{spec_preview})"
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Utilities
    "generate_evidence_id",
    "compute_content_hash",
    # Enums
    "EvidenceLevel",
    "EvidenceRelation",
    # Dataclass
    "Evidence",
]
