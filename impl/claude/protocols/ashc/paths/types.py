"""
ASHC DerivationPath Core Types.

A DerivationPath represents a categorical morphism from Source to Target,
carrying evidence (witnesses) and Galois loss quantification.

Philosophy:
    "The path IS the proof. The loss IS the confidence.
     Composition IS closure under derivation."

Key insight: DerivationPath WRAPS K-Block's DerivationDAG for lineage tracking.
We don't reinvent lineage - we compose it with categorical semantics.

See: spec/protocols/zero-seed1/ashc.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, auto
from typing import Any, Generic, TypeVar
from uuid import uuid4

# =============================================================================
# Type Variables for Generic Path
# =============================================================================

Source = TypeVar("Source")
Target = TypeVar("Target")


# =============================================================================
# Enums
# =============================================================================


class PathKind(Enum):
    """
    Kind of derivation path in the categorical sense.

    REFL: Identity path (a -> a)
    DERIVE: Direct derivation (principle -> spec)
    COMPOSE: Composed path (a -> b -> c)
    TRANSPORT: Path equality transport
    UNIVALENCE: Equivalence-as-identity
    """

    REFL = auto()  # Identity: a -> a
    DERIVE = auto()  # Direct derivation: a -> b with witnesses
    COMPOSE = auto()  # Composed: path1 ; path2
    TRANSPORT = auto()  # Transport across equivalence
    UNIVALENCE = auto()  # Equivalence as identity (HoTT)


class WitnessType(Enum):
    """
    Type of evidence/witness in a derivation path.

    Based on evidence tiers from Galois loss computation:
    - PRINCIPLE: Constitutional principle (near-lossless)
    - SPEC: Specification document
    - TEST: Passing test suite
    - PROOF: Formal proof (Lean, Coq, etc.)
    - LLM: LLM-generated reasoning
    - COMPOSITION: Composed from other witnesses
    - GALOIS: Galois loss measurement
    """

    PRINCIPLE = auto()  # Constitutional principle (L1-L2)
    SPEC = auto()  # Specification (L3-L4)
    TEST = auto()  # Test evidence
    PROOF = auto()  # Formal proof
    LLM = auto()  # LLM-generated
    COMPOSITION = auto()  # Composed witness
    GALOIS = auto()  # Galois loss measurement


# =============================================================================
# DerivationWitness
# =============================================================================


@dataclass(frozen=True)
class DerivationWitness:
    """
    A witness providing evidence for a derivation step.

    Each witness carries:
    - witness_type: What kind of evidence (PRINCIPLE, TEST, LLM, etc.)
    - evidence: The actual evidence payload
    - confidence: How confident we are (0.0 - 1.0)
    - grounding_principle: Optional link to constitutional principle
    - reasoning_trace: Optional reasoning chain

    Philosophy: "A witness is evidence with skin in the game."
    """

    witness_id: str
    witness_type: WitnessType
    evidence: dict[str, Any]
    confidence: float  # 0.0 - 1.0

    # Optional grounding
    grounding_principle: str | None = None
    reasoning_trace: str | None = None

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        witness_type: WitnessType,
        evidence: dict[str, Any],
        confidence: float = 0.5,
        grounding_principle: str | None = None,
        reasoning_trace: str | None = None,
    ) -> DerivationWitness:
        """Create a new witness with generated ID."""
        return cls(
            witness_id=f"wit_{uuid4().hex[:12]}",
            witness_type=witness_type,
            evidence=evidence,
            confidence=max(0.0, min(1.0, confidence)),  # Clamp to [0, 1]
            grounding_principle=grounding_principle,
            reasoning_trace=reasoning_trace,
        )

    @classmethod
    def from_principle(
        cls,
        principle_id: str,
        principle_text: str,
    ) -> DerivationWitness:
        """Create a witness grounded in a constitutional principle."""
        return cls.create(
            witness_type=WitnessType.PRINCIPLE,
            evidence={"principle_id": principle_id, "text": principle_text},
            confidence=0.95,  # High confidence for principles
            grounding_principle=principle_id,
        )

    @classmethod
    def from_test(
        cls,
        test_id: str,
        test_result: bool,
        test_output: str = "",
    ) -> DerivationWitness:
        """Create a witness from test results."""
        return cls.create(
            witness_type=WitnessType.TEST,
            evidence={
                "test_id": test_id,
                "passed": test_result,
                "output": test_output,
            },
            confidence=0.9 if test_result else 0.1,
        )

    @classmethod
    def from_galois(
        cls,
        galois_loss: float,
        method: str = "llm",
    ) -> DerivationWitness:
        """Create a witness from Galois loss computation."""
        coherence = 1.0 - galois_loss
        return cls.create(
            witness_type=WitnessType.GALOIS,
            evidence={
                "galois_loss": galois_loss,
                "coherence": coherence,
                "method": method,
            },
            confidence=coherence,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "witness_id": self.witness_id,
            "witness_type": self.witness_type.name,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "grounding_principle": self.grounding_principle,
            "reasoning_trace": self.reasoning_trace,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DerivationWitness:
        """Deserialize from dictionary."""
        return cls(
            witness_id=d["witness_id"],
            witness_type=WitnessType[d["witness_type"]],
            evidence=d["evidence"],
            confidence=d["confidence"],
            grounding_principle=d.get("grounding_principle"),
            reasoning_trace=d.get("reasoning_trace"),
            created_at=datetime.fromisoformat(d["created_at"])
            if "created_at" in d
            else datetime.now(UTC),
        )


# =============================================================================
# DerivationPath
# =============================================================================


@dataclass(frozen=True)
class DerivationPath(Generic[Source, Target]):
    """
    A categorical morphism from Source to Target with evidence.

    DerivationPath is the core type of ASHC's type system. It represents
    a traceable derivation from one artifact to another, carrying:
    - path_kind: How this path was constructed (REFL, DERIVE, COMPOSE)
    - witnesses: Evidence supporting the derivation
    - galois_loss: Accumulated semantic loss
    - principle_scores: Per-principle alignment scores
    - kblock_lineage: K-Block IDs for lineage tracking

    Categorical Laws:
    1. Identity: refl(a).compose(p) == p == p.compose(refl(b))
    2. Associativity: (p.compose(q)).compose(r) == p.compose(q.compose(r))
    3. Loss Accumulation: L(p;q) = 1 - (1-L(p))*(1-L(q))

    Philosophy: "The path IS the proof. Composition IS closure."
    """

    # Identity
    path_id: str
    path_kind: PathKind

    # Source and Target (stored as their string IDs or descriptions)
    source_id: str
    target_id: str

    # Evidence
    witnesses: tuple[DerivationWitness, ...] = ()

    # Galois metrics
    galois_loss: float = 0.0
    principle_scores: dict[str, float] = field(default_factory=dict)

    # K-Block lineage integration
    kblock_lineage: tuple[str, ...] = ()

    # Metadata
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def coherence(self) -> float:
        """Coherence = 1 - galois_loss."""
        return 1.0 - self.galois_loss

    @property
    def witness_confidence(self) -> float:
        """Combined confidence from all witnesses."""
        if not self.witnesses:
            return 0.0
        return sum(w.confidence for w in self.witnesses) / len(self.witnesses)

    @property
    def overall_confidence(self) -> float:
        """
        Overall confidence combining Galois coherence and witness confidence.

        Formula: coherence * witness_confidence
        """
        return self.coherence * self.witness_confidence

    def is_grounded(self) -> bool:
        """
        Check if this path is grounded in L1 axioms.

        A path is grounded if:
        1. It's a reflexive path (always grounded), OR
        2. It has at least one witness with a grounding principle, AND
        3. Its galois_loss < 0.5 (maintains structural coherence)
        """
        if self.path_kind == PathKind.REFL:
            return True

        has_grounded_witness = any(w.grounding_principle is not None for w in self.witnesses)
        has_acceptable_loss = self.galois_loss < 0.5

        return has_grounded_witness and has_acceptable_loss

    # -------------------------------------------------------------------------
    # Constructors
    # -------------------------------------------------------------------------

    @classmethod
    def refl(cls, source_id: str) -> "DerivationPath[Any, Any]":
        """
        Create an identity/reflexive path.

        refl(a) : a -> a

        Identity paths have zero loss and are always grounded.
        """
        return cls(
            path_id=f"refl_{uuid4().hex[:8]}",
            path_kind=PathKind.REFL,
            source_id=source_id,
            target_id=source_id,
            witnesses=(),
            galois_loss=0.0,
            kblock_lineage=(),
        )

    @classmethod
    def derive(
        cls,
        source_id: str,
        target_id: str,
        witnesses: list[DerivationWitness] | None = None,
        galois_loss: float = 0.0,
        principle_scores: dict[str, float] | None = None,
        kblock_lineage: list[str] | None = None,
    ) -> DerivationPath[Source, Target]:
        """
        Create a direct derivation path.

        derive(a, b, witnesses) : a -> b

        This is the primary constructor for new derivations.
        """
        return cls(
            path_id=f"deriv_{uuid4().hex[:8]}",
            path_kind=PathKind.DERIVE,
            source_id=source_id,
            target_id=target_id,
            witnesses=tuple(witnesses) if witnesses else (),
            galois_loss=galois_loss,
            principle_scores=principle_scores or {},
            kblock_lineage=tuple(kblock_lineage) if kblock_lineage else (),
        )

    def compose(self, other: DerivationPath[Target, Any]) -> DerivationPath[Source, Any]:
        """
        Compose two paths: self ; other

        Given:
            self: Source -> Target
            other: Target -> X

        Returns:
            composed: Source -> X

        Categorical Law: Composition is associative
            (p ; q) ; r == p ; (q ; r)

        Loss Accumulation:
            L(p;q) = 1 - (1-L(p))*(1-L(q))

        This formula ensures:
        - L(p;q) >= max(L(p), L(q))  # Loss never decreases
        - L(p;q) < L(p) + L(q) when L(p), L(q) < 1  # Sub-additive (not super-additive)
        - L(refl;p) = L(p) = L(p;refl)  # Identity law for loss
        """
        # Validate composition: self.target_id must match other.source_id
        if self.target_id != other.source_id:
            raise ValueError(
                f"Cannot compose: target '{self.target_id}' != source '{other.source_id}'"
            )

        # Identity optimization: refl;p = p = p;refl
        if self.path_kind == PathKind.REFL:
            return DerivationPath(
                path_id=other.path_id,
                path_kind=other.path_kind,
                source_id=self.source_id,  # Use self's source (which equals target)
                target_id=other.target_id,
                witnesses=other.witnesses,
                galois_loss=other.galois_loss,
                principle_scores=other.principle_scores,
                kblock_lineage=other.kblock_lineage,
                created_at=other.created_at,
            )
        if other.path_kind == PathKind.REFL:
            return DerivationPath(
                path_id=self.path_id,
                path_kind=self.path_kind,
                source_id=self.source_id,
                target_id=other.target_id,  # Use other's target (which equals source)
                witnesses=self.witnesses,
                galois_loss=self.galois_loss,
                principle_scores=self.principle_scores,
                kblock_lineage=self.kblock_lineage,
                created_at=self.created_at,
            )

        # Compute accumulated loss: L(p;q) = 1 - (1-L(p))*(1-L(q))
        accumulated_loss = 1.0 - (1.0 - self.galois_loss) * (1.0 - other.galois_loss)

        # Merge witnesses
        combined_witnesses = self.witnesses + other.witnesses

        # Merge principle scores (average if both have same principle)
        merged_scores: dict[str, float] = dict(self.principle_scores)
        for principle, score in other.principle_scores.items():
            if principle in merged_scores:
                merged_scores[principle] = (merged_scores[principle] + score) / 2
            else:
                merged_scores[principle] = score

        # Merge lineage (concatenate, preserving order)
        combined_lineage = self.kblock_lineage + other.kblock_lineage

        return DerivationPath(
            path_id=f"comp_{uuid4().hex[:8]}",
            path_kind=PathKind.COMPOSE,
            source_id=self.source_id,
            target_id=other.target_id,
            witnesses=combined_witnesses,
            galois_loss=accumulated_loss,
            principle_scores=merged_scores,
            kblock_lineage=combined_lineage,
        )

    def __rshift__(self, other: DerivationPath[Target, Any]) -> DerivationPath[Source, Any]:
        """
        Operator overload for composition: p >> q means p.compose(q).

        This follows the kgents convention of using >> for morphism composition.
        """
        return self.compose(other)

    # -------------------------------------------------------------------------
    # Serialization
    # -------------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "path_id": self.path_id,
            "path_kind": self.path_kind.name,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "witnesses": [w.to_dict() for w in self.witnesses],
            "galois_loss": self.galois_loss,
            "principle_scores": self.principle_scores,
            "kblock_lineage": list(self.kblock_lineage),
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> DerivationPath[Any, Any]:
        """Deserialize from dictionary."""
        return cls(
            path_id=d["path_id"],
            path_kind=PathKind[d["path_kind"]],
            source_id=d["source_id"],
            target_id=d["target_id"],
            witnesses=tuple(DerivationWitness.from_dict(w) for w in d.get("witnesses", [])),
            galois_loss=d.get("galois_loss", 0.0),
            principle_scores=d.get("principle_scores", {}),
            kblock_lineage=tuple(d.get("kblock_lineage", [])),
            created_at=datetime.fromisoformat(d["created_at"])
            if "created_at" in d
            else datetime.now(UTC),
        )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "PathKind",
    "WitnessType",
    "DerivationWitness",
    "DerivationPath",
]
