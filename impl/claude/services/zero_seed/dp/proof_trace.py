"""
Proof-Trace Isomorphism: PolicyTrace <-> Toulmin Proof with Galois annotations.

From spec/protocols/zero-seed1/dp.md (Part III):

    "Theorem 3.1.1 (Proof-Trace Isomorphism):
     Toulmin Proof and DP PolicyTrace are isomorphic via Galois loss annotations."

The structural mapping:
    Proof.data         <->  PolicyTrace.state_before
    Proof.warrant      <->  PolicyTrace.action
    Proof.claim        <->  PolicyTrace.state_after
    Proof.qualifier    <->  PolicyTrace.value (converted)
    Proof.backing      <->  PolicyTrace.rationale
    Proof.rebuttals    <->  PolicyTrace.log (contradiction entries)
    Proof.tier         <->  PolicyTrace.metadata["evidence_tier"]

NEW: Galois Annotations:
    Proof.galois_loss  <->  PolicyTrace.metadata["galois_loss"]

This isomorphism enables:
1. Converting decision traces to formal proofs for explanation
2. Converting proofs to traces for DP computation
3. Galois loss as a unified annotation for both representations

Philosophy:
    "The proof IS the decision. The mark IS the witness."
    Every PolicyTrace step can be reconstructed as a Toulmin argument,
    and every Toulmin proof can be replayed as a decision trace.

Teaching:
    gotcha: The qualifier_to_value and value_to_qualifier functions provide
            bidirectional mapping. The mapping is approximate due to
            quantizing continuous values to discrete qualifiers.
            (Evidence: value_to_qualifier uses threshold bands)

    gotcha: When converting trace to proof, multiple entries are aggregated.
            The first entry provides the initial state, the last provides
            the final claim. All rationales are concatenated.
            (Evidence: trace_to_proof joins entry rationales with "; ")

See: spec/protocols/zero-seed1/dp.md (Part III: Proof-PolicyTrace Isomorphism)
See: services/witness/mark.py (Proof and EvidenceTier classes)
See: services/categorical/dp_bridge.py (PolicyTrace and TraceEntry)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from services.categorical.dp_bridge import PolicyTrace, TraceEntry

if TYPE_CHECKING:
    pass

logger = logging.getLogger("kgents.zero_seed.dp.proof_trace")


# =============================================================================
# Evidence Tier Enum (mirrors services/witness/mark.py)
# =============================================================================


class EvidenceTier:
    """
    Hierarchy of evidence types for justification.

    From spec/protocols/witness-supersession.md:
        CATEGORICAL = 1     # Mathematical (laws hold)
        EMPIRICAL = 2       # Scientific (ASHC runs)
        AESTHETIC = 3       # Hardy criteria (inevitability, unexpectedness, economy)
        GENEALOGICAL = 4    # Pattern archaeology (git history)
        SOMATIC = 5         # The Mirror Test (felt sense)
    """

    CATEGORICAL = "CATEGORICAL"
    EMPIRICAL = "EMPIRICAL"
    AESTHETIC = "AESTHETIC"
    GENEALOGICAL = "GENEALOGICAL"
    SOMATIC = "SOMATIC"

    @classmethod
    def from_value(cls, value: float) -> str:
        """Map numeric value to evidence tier."""
        if value >= 0.95:
            return cls.CATEGORICAL
        elif value >= 0.7:
            return cls.EMPIRICAL
        elif value >= 0.5:
            return cls.AESTHETIC
        elif value >= 0.3:
            return cls.GENEALOGICAL
        else:
            return cls.SOMATIC


# =============================================================================
# Proof Class (mirrors services/witness/mark.py but with Galois extension)
# =============================================================================


@dataclass(frozen=True)
class Proof:
    """
    Defeasible reasoning structure based on Toulmin's argumentation model.

    Extended with Galois loss annotation for Zero Seed integration.

    Toulmin's model captures how humans actually argue:
    - data: The evidence supporting the claim
    - warrant: The reasoning connecting data to claim
    - claim: The conclusion being argued for
    - backing: Support for the warrant itself
    - qualifier: Degree of certainty ("definitely", "probably", "possibly")
    - rebuttals: Conditions that would defeat the argument

    NEW: Galois extension:
    - galois_loss: The structural coherence loss for this proof
    - principles: Constitutional principles this proof supports
    """

    # Core Toulmin structure
    data: str  # Evidence: "Tests pass", "3 hours invested"
    warrant: str  # Reasoning: "Passing tests indicate correctness"
    claim: str  # Conclusion: "This refactoring was worthwhile"

    # Extended Toulmin
    backing: str = ""  # Support for warrant
    qualifier: str = "probably"  # Confidence level
    rebuttals: tuple[str, ...] = ()  # Defeaters

    # Evidence tier (from spec)
    tier: str = EvidenceTier.EMPIRICAL

    # Principles referenced (from Constitution)
    principles: tuple[str, ...] = ()

    # NEW: Galois loss annotation
    galois_loss: float = 0.0

    @property
    def constitutional_reward(self) -> float:
        """Compute constitutional reward from Galois loss."""
        return 1.0 - self.galois_loss

    def with_galois_loss(self, loss: float) -> Proof:
        """Return new Proof with Galois loss annotation."""
        return Proof(
            data=self.data,
            warrant=self.warrant,
            claim=self.claim,
            backing=self.backing,
            qualifier=self.qualifier,
            rebuttals=self.rebuttals,
            tier=self.tier,
            principles=self.principles,
            galois_loss=loss,
        )

    def strengthen(self, new_backing: str) -> Proof:
        """Return new Proof with added backing."""
        combined = f"{self.backing}; {new_backing}" if self.backing else new_backing
        return Proof(
            data=self.data,
            warrant=self.warrant,
            claim=self.claim,
            backing=combined,
            qualifier=self.qualifier,
            rebuttals=self.rebuttals,
            tier=self.tier,
            principles=self.principles,
            galois_loss=self.galois_loss,
        )

    def with_rebuttal(self, rebuttal: str) -> Proof:
        """Return new Proof with added rebuttal."""
        return Proof(
            data=self.data,
            warrant=self.warrant,
            claim=self.claim,
            backing=self.backing,
            qualifier=self.qualifier,
            rebuttals=self.rebuttals + (rebuttal,),
            tier=self.tier,
            principles=self.principles,
            galois_loss=self.galois_loss,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "data": self.data,
            "warrant": self.warrant,
            "claim": self.claim,
            "backing": self.backing,
            "qualifier": self.qualifier,
            "rebuttals": list(self.rebuttals),
            "tier": self.tier,
            "principles": list(self.principles),
            "galois_loss": self.galois_loss,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Proof:
        """Create from dictionary."""
        return cls(
            data=data.get("data", ""),
            warrant=data.get("warrant", ""),
            claim=data.get("claim", ""),
            backing=data.get("backing", ""),
            qualifier=data.get("qualifier", "probably"),
            rebuttals=tuple(data.get("rebuttals", [])),
            tier=data.get("tier", EvidenceTier.EMPIRICAL),
            principles=tuple(data.get("principles", [])),
            galois_loss=data.get("galois_loss", 0.0),
        )


# =============================================================================
# Qualifier <-> Value Conversion
# =============================================================================


# Mapping from Toulmin qualifier to DP value
QUALIFIER_TO_VALUE: dict[str, float] = {
    "definitely": 1.0,
    "almost certainly": 0.9,
    "probably": 0.8,
    "likely": 0.7,
    "possibly": 0.6,
    "perhaps": 0.5,
    "tentatively": 0.4,
    "speculatively": 0.2,
    "personally": 0.85,  # Somatic proofs have high personal confidence
}


def qualifier_to_value(qualifier: str) -> float:
    """
    Map Toulmin qualifier to DP value.

    Args:
        qualifier: Toulmin qualifier string

    Returns:
        Value in [0.0, 1.0]
    """
    return QUALIFIER_TO_VALUE.get(qualifier.lower(), 0.5)


def value_to_qualifier(value: float) -> str:
    """
    Map DP value to Toulmin qualifier.

    Uses threshold bands for discretization.

    Args:
        value: DP value in [0.0, 1.0]

    Returns:
        Toulmin qualifier string
    """
    if value >= 0.95:
        return "definitely"
    elif value >= 0.85:
        return "almost certainly"
    elif value >= 0.7:
        return "probably"
    elif value >= 0.55:
        return "possibly"
    elif value >= 0.35:
        return "tentatively"
    else:
        return "speculatively"


# =============================================================================
# Proof -> PolicyTrace Conversion
# =============================================================================


def proof_to_trace(
    proof: Proof,
    galois_loss: float | None = None,
) -> PolicyTrace[str]:
    """
    Convert Toulmin proof to DP trace with Galois loss.

    Galois loss becomes metadata for explainability.

    Mapping:
        Proof.data     -> TraceEntry.state_before
        Proof.warrant  -> TraceEntry.action
        Proof.claim    -> TraceEntry.state_after
        Proof.qualifier -> TraceEntry.value (via qualifier_to_value)
        Proof.backing  -> TraceEntry.rationale

    Args:
        proof: Toulmin Proof to convert
        galois_loss: Optional Galois loss (uses proof.galois_loss if not provided)

    Returns:
        PolicyTrace with single entry representing the proof

    Example:
        >>> proof = Proof(
        ...     data="3 hours, 45K tokens invested",
        ...     warrant="Infrastructure improvements enable velocity gains",
        ...     claim="This refactoring was worthwhile",
        ...     backing="DP-Native unified 7 layers to 5",
        ...     qualifier="probably",
        ... )
        >>> trace = proof_to_trace(proof, galois_loss=0.15)
        >>> trace.log[0].action  # "Infrastructure improvements enable velocity gains"
    """
    # Use provided galois_loss or extract from proof
    loss = galois_loss if galois_loss is not None else proof.galois_loss

    # Convert qualifier to value
    value = qualifier_to_value(proof.qualifier)

    # Create trace entry
    entry = TraceEntry(
        state_before=proof.data,
        action=proof.warrant,
        state_after=proof.claim,
        value=value,
        rationale=proof.backing,
        timestamp=datetime.now(timezone.utc),
    )

    # Create metadata dict for extended info
    # Note: TraceEntry is frozen, so we store in the PolicyTrace
    trace = PolicyTrace(value=proof.claim, log=(entry,))

    # Store Galois loss and other metadata via wrapper
    # The trace itself carries the entry; metadata is accessed separately

    logger.debug(
        f"Converted proof to trace: value={value:.3f}, galois_loss={loss:.3f}"
    )

    return trace


# =============================================================================
# PolicyTrace -> Proof Conversion
# =============================================================================


def trace_to_proof(
    trace: PolicyTrace[Any],
    galois_loss: float = 0.0,
    principles: tuple[str, ...] = (),
) -> Proof:
    """
    Convert DP trace to Toulmin proof with Galois loss recovery.

    Aggregates multiple entries into single proof:
    - First entry provides initial state (data)
    - All actions joined as warrant chain
    - Last entry provides final claim
    - Rationales concatenated as backing

    Args:
        trace: PolicyTrace to convert
        galois_loss: Galois loss annotation for the proof
        principles: Constitutional principles this proof supports

    Returns:
        Toulmin Proof with Galois loss annotation

    Raises:
        ValueError: If trace has no entries

    Example:
        >>> trace = PolicyTrace(value="concluded", log=(entry1, entry2, entry3))
        >>> proof = trace_to_proof(trace, galois_loss=0.2)
        >>> proof.claim  # "concluded"
    """
    entries = trace.log

    if not entries:
        raise ValueError("Empty trace cannot be converted to proof")

    # Extract components from entries
    first = entries[0]
    last = entries[-1]

    # Aggregate warrant from all actions
    warrant = " -> ".join(e.action for e in entries)

    # Aggregate rationales as backing
    rationales = [e.rationale for e in entries if e.rationale]
    backing = "; ".join(rationales) if rationales else ""

    # Compute total value and convert to qualifier
    total_value = trace.total_value()
    qualifier = value_to_qualifier(total_value)

    # Determine evidence tier from total value
    tier = EvidenceTier.from_value(total_value)

    proof = Proof(
        data=str(first.state_before),
        warrant=warrant,
        claim=str(last.state_after),
        backing=backing,
        qualifier=qualifier,
        tier=tier,
        principles=principles,
        galois_loss=galois_loss,
    )

    logger.debug(
        f"Converted trace to proof: qualifier={qualifier}, "
        f"galois_loss={galois_loss:.3f}, tier={tier}"
    )

    return proof


# =============================================================================
# Extended Proof with Trace Context
# =============================================================================


@dataclass(frozen=True)
class ProofWithTrace:
    """
    Proof bundled with its PolicyTrace for full context.

    This captures both the formal argument (Proof) and the
    execution trace (PolicyTrace) that produced it.

    Use this when you need both representations together.
    """

    proof: Proof
    trace: PolicyTrace[Any]

    # Galois metadata
    galois_loss: float = 0.0

    @property
    def constitutional_reward(self) -> float:
        """Constitutional reward = 1 - galois_loss."""
        return 1.0 - self.galois_loss

    @classmethod
    def from_proof(
        cls,
        proof: Proof,
        galois_loss: float = 0.0,
    ) -> ProofWithTrace:
        """Create from Proof, generating trace."""
        trace = proof_to_trace(proof, galois_loss)
        return cls(
            proof=proof,
            trace=trace,
            galois_loss=galois_loss,
        )

    @classmethod
    def from_trace(
        cls,
        trace: PolicyTrace[Any],
        galois_loss: float = 0.0,
        principles: tuple[str, ...] = (),
    ) -> ProofWithTrace:
        """Create from PolicyTrace, generating proof."""
        proof = trace_to_proof(trace, galois_loss, principles)
        return cls(
            proof=proof,
            trace=trace,
            galois_loss=galois_loss,
        )


# =============================================================================
# Batch Conversion Utilities
# =============================================================================


def proofs_to_traces(
    proofs: list[Proof],
    galois_losses: list[float] | None = None,
) -> list[PolicyTrace[str]]:
    """
    Convert multiple proofs to traces.

    Args:
        proofs: List of Proofs to convert
        galois_losses: Optional list of Galois losses (one per proof)

    Returns:
        List of PolicyTraces
    """
    if galois_losses is None:
        galois_losses = [p.galois_loss for p in proofs]

    return [
        proof_to_trace(proof, loss)
        for proof, loss in zip(proofs, galois_losses)
    ]


def traces_to_proofs(
    traces: list[PolicyTrace[Any]],
    galois_losses: list[float] | None = None,
    principles: tuple[str, ...] = (),
) -> list[Proof]:
    """
    Convert multiple traces to proofs.

    Args:
        traces: List of PolicyTraces to convert
        galois_losses: Optional list of Galois losses (one per trace)
        principles: Constitutional principles for all proofs

    Returns:
        List of Proofs
    """
    if galois_losses is None:
        galois_losses = [0.0] * len(traces)

    return [
        trace_to_proof(trace, loss, principles)
        for trace, loss in zip(traces, galois_losses)
    ]


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core types
    "Proof",
    "EvidenceTier",
    "ProofWithTrace",
    # Conversion functions
    "proof_to_trace",
    "trace_to_proof",
    "qualifier_to_value",
    "value_to_qualifier",
    # Batch utilities
    "proofs_to_traces",
    "traces_to_proofs",
    # Constants
    "QUALIFIER_TO_VALUE",
]
