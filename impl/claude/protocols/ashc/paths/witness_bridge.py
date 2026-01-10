"""
ASHC Witness Bridge: Connect ASHC Evidence to Witness Primitives.

This bridge wires ASHC compilation evidence to the witness mark system,
enabling:
- Mark emission during compilation
- Constitutional evaluation of ASHC actions
- Galois loss integration for confidence computation
- Run.witnesses population (NO MORE `witnesses=()`)

Key Insight:
    "Every ASHC run is a witnessed action. Every witness has constitutional standing."

Integration Points:
    - EvidenceCompiler.compile() -> emit_ashc_mark() -> Mark + DerivationWitness
    - AdaptiveCompiler stopping decisions -> emit_ashc_mark()
    - ASHCBet resolution -> emit_ashc_mark()

Teaching:
    gotcha: Marks are IMMUTABLE. Once created, you cannot modify them.
            To add constitutional alignment, use mark.with_constitutional().

    gotcha: DerivationWitness.confidence is computed from Galois loss:
            confidence = 1.0 - galois_loss (higher = more trustworthy)

    gotcha: WitnessType determines how the mark is categorized:
            - TEST: verification results (pytest, mypy, ruff)
            - LLM: LLM-based decisions (stopping, generation)
            - COMPOSITION: structural composition successes
            - ECONOMIC: bet resolution and credibility updates
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from services.witness.mark import (
    ConstitutionalAlignment,
    EvidenceTier,
    Mark,
    MarkId,
    NPhase,
    Proof,
    Response,
    Stimulus,
    UmweltSnapshot,
    generate_mark_id,
)
from services.witness.trace_store import MarkStore, get_mark_store

logger = logging.getLogger("kgents.ashc.witness_bridge")


# =============================================================================
# Witness Type Classification
# =============================================================================


class WitnessType(str, Enum):
    """
    Classification of ASHC witness types.

    Each type determines:
    - How the mark is categorized
    - Which evidence tier is appropriate
    - How confidence is computed
    """

    TEST = "test"  # Verification results (pytest, mypy, ruff)
    LLM = "llm"  # LLM-based decisions (stopping, generation)
    COMPOSITION = "composition"  # Structural composition successes
    ECONOMIC = "economic"  # Bet resolution, credibility updates
    ADAPTIVE = "adaptive"  # Bayesian stopping decisions


# =============================================================================
# DerivationWitness: ASHC-specific Witness
# =============================================================================


@dataclass(frozen=True)
class DerivationWitness:
    """
    ASHC-specific witness capturing derivation evidence.

    This is the ASHC-side representation that gets converted to/from Marks.
    It captures the specific semantics of ASHC evidence:
    - Action performed
    - Evidence collected
    - Confidence level (from Galois loss)
    - Constitutional alignment

    Philosophy:
        "A DerivationWitness is ASHC's way of saying 'I did this, and here's
        the evidence that it was correct.'"

    Fields:
        witness_id: Unique identifier (maps to mark_id)
        witness_type: Classification (TEST, LLM, COMPOSITION, ECONOMIC)
        action: What was done (e.g., "Verified implementation", "Stopped sampling")
        evidence: Evidence payload (test results, posterior, etc.)
        confidence: Confidence level [0, 1] where 1 = perfect (from Galois coherence)
        timestamp: When the witness was created
        spec_hash: Hash of the spec being compiled (for correlation)
        run_id: ID of the Run this witness belongs to
        constitutional: Optional constitutional alignment
        galois_loss: Optional Galois loss value
    """

    witness_id: str
    witness_type: WitnessType
    action: str
    evidence: dict[str, Any]
    confidence: float = 0.5
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    spec_hash: str = ""
    run_id: str = ""
    constitutional: ConstitutionalAlignment | None = None
    galois_loss: float | None = None

    @classmethod
    def create(
        cls,
        witness_type: WitnessType,
        action: str,
        evidence: dict[str, Any],
        confidence: float = 0.5,
        spec_hash: str = "",
        run_id: str = "",
        galois_loss: float | None = None,
    ) -> "DerivationWitness":
        """
        Create a new DerivationWitness.

        Args:
            witness_type: Classification of the witness
            action: What was done
            evidence: Evidence payload
            confidence: Confidence level [0, 1]
            spec_hash: Hash of the spec (for correlation)
            run_id: ID of the Run
            galois_loss: Optional Galois loss

        Returns:
            New DerivationWitness instance
        """
        # Compute confidence from Galois loss if provided
        if galois_loss is not None:
            confidence = 1.0 - galois_loss

        return cls(
            witness_id=f"ashc-witness-{uuid4().hex[:12]}",
            witness_type=witness_type,
            action=action,
            evidence=evidence,
            confidence=confidence,
            spec_hash=spec_hash,
            run_id=run_id,
            galois_loss=galois_loss,
        )

    def with_constitutional(self, alignment: ConstitutionalAlignment) -> "DerivationWitness":
        """Create new witness with constitutional alignment (immutable pattern)."""
        return DerivationWitness(
            witness_id=self.witness_id,
            witness_type=self.witness_type,
            action=self.action,
            evidence=self.evidence,
            confidence=self.confidence,
            timestamp=self.timestamp,
            spec_hash=self.spec_hash,
            run_id=self.run_id,
            constitutional=alignment,
            galois_loss=self.galois_loss,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "witness_id": self.witness_id,
            "witness_type": self.witness_type.value,
            "action": self.action,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "spec_hash": self.spec_hash,
            "run_id": self.run_id,
            "constitutional": self.constitutional.to_dict() if self.constitutional else None,
            "galois_loss": self.galois_loss,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DerivationWitness":
        """Create from dictionary."""
        constitutional = None
        if data.get("constitutional"):
            constitutional = ConstitutionalAlignment.from_dict(data["constitutional"])

        return cls(
            witness_id=data["witness_id"],
            witness_type=WitnessType(data["witness_type"]),
            action=data["action"],
            evidence=data.get("evidence", {}),
            confidence=data.get("confidence", 0.5),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            spec_hash=data.get("spec_hash", ""),
            run_id=data.get("run_id", ""),
            constitutional=constitutional,
            galois_loss=data.get("galois_loss"),
        )


# =============================================================================
# Conversion: DerivationWitness <-> Mark
# =============================================================================


def derivation_to_mark(
    witness: DerivationWitness,
    umwelt: UmweltSnapshot | None = None,
    phase: NPhase | None = None,
) -> Mark:
    """
    Convert DerivationWitness to Mark for the witness system.

    This is the forward conversion: ASHC evidence -> Mark storage.

    Mapping:
        witness.action -> mark.response.content
        witness.evidence -> mark.metadata["ashc_evidence"]
        witness.confidence -> mark.proof.qualifier
        witness.witness_type -> mark.tags + mark.stimulus.kind

    Args:
        witness: The ASHC witness to convert
        umwelt: Observer context (defaults to system umwelt)
        phase: N-Phase workflow context

    Returns:
        Mark instance ready for storage

    Teaching:
        gotcha: The mark origin is always "ashc" to identify ASHC-generated marks.
                Use mark.metadata["witness_type"] to determine the witness classification.
    """
    # Map confidence to proof qualifier
    qualifier = _confidence_to_qualifier(witness.confidence)

    # Map witness type to evidence tier
    tier = _witness_type_to_tier(witness.witness_type)

    # Build proof from evidence
    proof = Proof(
        data=f"ASHC {witness.witness_type.value}: {_summarize_evidence(witness.evidence)}",
        warrant=f"Evidence from ASHC {witness.witness_type.value} operation",
        claim=witness.action,
        qualifier=qualifier,
        tier=tier,
        principles=("composable", "generative"),  # ASHC always targets these
    )

    # Build stimulus
    stimulus = Stimulus(
        kind=f"ashc_{witness.witness_type.value}",
        content=f"ASHC {witness.witness_type.value} operation",
        source="ashc",
        metadata={
            "spec_hash": witness.spec_hash,
            "run_id": witness.run_id,
        },
    )

    # Build response
    response = Response(
        kind="ashc_witness",
        content=witness.action,
        success=witness.confidence >= 0.5,
        metadata={
            "confidence": witness.confidence,
            "witness_id": witness.witness_id,
        },
    )

    # Build mark
    mark = Mark(
        id=MarkId(witness.witness_id.replace("ashc-witness-", "mark-")),
        origin="ashc",
        domain="system",
        stimulus=stimulus,
        response=response,
        umwelt=umwelt or UmweltSnapshot.system(),
        phase=phase,
        proof=proof,
        constitutional=witness.constitutional,
        tags=("ashc", witness.witness_type.value, "derivation"),
        metadata={
            "ashc_evidence": witness.evidence,
            "witness_type": witness.witness_type.value,
            "spec_hash": witness.spec_hash,
            "run_id": witness.run_id,
            "galois_loss": witness.galois_loss,
        },
    )

    return mark


def mark_to_derivation(mark: Mark) -> DerivationWitness | None:
    """
    Convert Mark back to DerivationWitness for ASHC queries.

    This is the reverse conversion: Mark storage -> ASHC queries.

    Only works for marks with origin="ashc" and metadata containing
    witness_type and ashc_evidence.

    Args:
        mark: The mark to convert

    Returns:
        DerivationWitness if mark is ASHC-originated, None otherwise

    Teaching:
        gotcha: This only works for ASHC-generated marks. Marks from other
                origins (witness, brain, etc.) will return None.
    """
    if mark.origin != "ashc":
        logger.debug(f"Mark {mark.id} is not ASHC-originated, skipping conversion")
        return None

    if "witness_type" not in mark.metadata:
        logger.warning(f"Mark {mark.id} is ASHC but missing witness_type")
        return None

    try:
        witness_type = WitnessType(mark.metadata["witness_type"])
    except ValueError:
        logger.warning(f"Mark {mark.id} has invalid witness_type: {mark.metadata['witness_type']}")
        return None

    # Extract confidence from response metadata or compute from proof
    confidence = mark.response.metadata.get("confidence", 0.5)
    if mark.proof:
        confidence = _qualifier_to_confidence(mark.proof.qualifier)

    return DerivationWitness(
        witness_id=mark.response.metadata.get("witness_id", str(mark.id)),
        witness_type=witness_type,
        action=mark.response.content,
        evidence=mark.metadata.get("ashc_evidence", {}),
        confidence=confidence,
        timestamp=mark.timestamp,
        spec_hash=mark.metadata.get("spec_hash", ""),
        run_id=mark.metadata.get("run_id", ""),
        constitutional=mark.constitutional,
        galois_loss=mark.metadata.get("galois_loss"),
    )


# =============================================================================
# Mark Emission
# =============================================================================


async def emit_ashc_mark(
    action: str,
    evidence: dict[str, Any],
    witness_type: WitnessType,
    mark_store: MarkStore | None = None,
    spec_hash: str = "",
    run_id: str = "",
    galois_loss: float | None = None,
    evaluate_constitutional: bool = True,
) -> tuple[Mark, DerivationWitness]:
    """
    Emit a mark and create corresponding witness.

    This is the primary integration point for ASHC -> Witness.
    It handles:
    1. Creating the DerivationWitness
    2. Converting to Mark
    3. Computing constitutional alignment (optional)
    4. Storing in MarkStore

    Args:
        action: What was done (e.g., "Verified implementation")
        evidence: Evidence payload (test results, posterior, etc.)
        witness_type: Classification of the witness
        mark_store: Store to persist marks (uses global if None)
        spec_hash: Hash of the spec being compiled
        run_id: ID of the Run
        galois_loss: Optional Galois loss for confidence computation
        evaluate_constitutional: Whether to compute constitutional alignment

    Returns:
        Tuple of (Mark, DerivationWitness)

    Example:
        >>> mark, witness = await emit_ashc_mark(
        ...     action="Verified implementation",
        ...     evidence={"tests_passed": 5, "tests_failed": 0},
        ...     witness_type=WitnessType.TEST,
        ...     mark_store=mark_store,
        ...     spec_hash="abc123",
        ...     run_id="run-001",
        ... )
        >>> assert mark.origin == "ashc"
        >>> assert witness.confidence >= 0.5
    """
    store = mark_store or get_mark_store()

    # Create the witness
    witness = DerivationWitness.create(
        witness_type=witness_type,
        action=action,
        evidence=evidence,
        spec_hash=spec_hash,
        run_id=run_id,
        galois_loss=galois_loss,
    )

    # Optionally compute constitutional alignment
    if evaluate_constitutional:
        try:
            from services.witness.constitutional_evaluator import MarkConstitutionalEvaluator

            # First convert to mark for evaluation
            temp_mark = derivation_to_mark(witness)
            evaluator = MarkConstitutionalEvaluator()
            alignment = await evaluator.evaluate(temp_mark)
            witness = witness.with_constitutional(alignment)

            logger.debug(
                f"Constitutional alignment for {witness.witness_id}: "
                f"total={alignment.weighted_total:.3f}, compliant={alignment.is_compliant}"
            )
        except Exception as e:
            logger.warning(f"Failed to compute constitutional alignment: {e}")

    # Convert to mark
    mark = derivation_to_mark(witness)

    # Store the mark
    try:
        store.append(mark)
        logger.info(f"Emitted ASHC mark {mark.id}: {action}")
    except Exception as e:
        logger.error(f"Failed to store ASHC mark: {e}")
        raise

    return mark, witness


async def batch_emit_ashc_marks(
    actions: list[tuple[str, dict[str, Any], WitnessType]],
    mark_store: MarkStore | None = None,
    spec_hash: str = "",
    run_id: str = "",
    evaluate_constitutional: bool = True,
) -> list[tuple[Mark, DerivationWitness]]:
    """
    Emit multiple marks in batch.

    More efficient than calling emit_ashc_mark repeatedly as it:
    - Reuses the MarkStore instance
    - Batches constitutional evaluations

    Args:
        actions: List of (action, evidence, witness_type) tuples
        mark_store: Store to persist marks
        spec_hash: Hash of the spec being compiled
        run_id: ID of the Run
        evaluate_constitutional: Whether to compute constitutional alignment

    Returns:
        List of (Mark, DerivationWitness) tuples
    """
    store = mark_store or get_mark_store()
    results: list[tuple[Mark, DerivationWitness]] = []

    for action, evidence, witness_type in actions:
        mark, witness = await emit_ashc_mark(
            action=action,
            evidence=evidence,
            witness_type=witness_type,
            mark_store=store,
            spec_hash=spec_hash,
            run_id=run_id,
            evaluate_constitutional=evaluate_constitutional,
        )
        results.append((mark, witness))

    return results


# =============================================================================
# Helper Functions
# =============================================================================


def _confidence_to_qualifier(confidence: float) -> str:
    """Map confidence to Toulmin qualifier."""
    if confidence >= 0.95:
        return "definitely"
    elif confidence >= 0.85:
        return "almost certainly"
    elif confidence >= 0.70:
        return "probably"
    elif confidence >= 0.50:
        return "arguably"
    else:
        return "possibly"


def _qualifier_to_confidence(qualifier: str) -> float:
    """Map Toulmin qualifier back to confidence."""
    mapping = {
        "definitely": 0.97,
        "almost certainly": 0.90,
        "probably": 0.75,
        "arguably": 0.55,
        "possibly": 0.35,
        "personally": 0.80,  # somatic
    }
    return mapping.get(qualifier.lower(), 0.5)


def _witness_type_to_tier(witness_type: WitnessType) -> EvidenceTier:
    """Map witness type to evidence tier."""
    mapping = {
        WitnessType.TEST: EvidenceTier.EMPIRICAL,
        WitnessType.LLM: EvidenceTier.EMPIRICAL,
        WitnessType.COMPOSITION: EvidenceTier.CATEGORICAL,
        WitnessType.ECONOMIC: EvidenceTier.EMPIRICAL,
        WitnessType.ADAPTIVE: EvidenceTier.EMPIRICAL,
    }
    return mapping.get(witness_type, EvidenceTier.EMPIRICAL)


def _summarize_evidence(evidence: dict[str, Any]) -> str:
    """Create a brief summary of evidence for proof data field."""
    if not evidence:
        return "no evidence"

    parts = []
    for key, value in list(evidence.items())[:3]:  # Limit to 3 items
        if isinstance(value, bool):
            parts.append(f"{key}={value}")
        elif isinstance(value, (int, float)):
            parts.append(f"{key}={value}")
        elif isinstance(value, str) and len(value) < 50:
            parts.append(f"{key}={value[:30]}")
        else:
            parts.append(f"{key}=<{type(value).__name__}>")

    return ", ".join(parts)


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "WitnessType",
    "DerivationWitness",
    "emit_ashc_mark",
    "derivation_to_mark",
    "mark_to_derivation",
    "batch_emit_ashc_marks",
]
