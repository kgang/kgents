"""
Galois-Witnessed Proof: Toulmin Proofs with Quantitative Coherence.

This module implements the Galois upgrade to the Zero Seed proof system:
- GaloisWitnessedProof: Toulmin proof extended with Galois loss metrics
- ProofLossDecomposition: Per-component loss breakdown for diagnostics
- Alternative: Ghost alternative proofs (deferred, not chosen)
- ProofValidation: Validation results with coherence scoring

The Core Insight:
    proof_quality(proof) = 1 - galois_loss(proof)

Evidence Tiers by Loss:
    CATEGORICAL: L < 0.1 (logical necessity)
    EMPIRICAL:   L < 0.3 (data-driven)
    AESTHETIC:   L < 0.5 (taste-based)
    SOMATIC:     L < 0.7 (gut feeling)
    CHAOTIC:     L >= 0.7 (incoherent)

Witness Modes by Loss:
    SINGLE:  L < 0.1 (important, witness immediately)
    SESSION: L < 0.4 (batch with session)
    LAZY:    L >= 0.4 (defer, might be discarded)

Philosophy:
    "The coherence IS the inverse loss. The witness IS the mark.
     The contradiction IS the super-additive signal."

See: spec/protocols/zero-seed1/proof.md
See: docs/skills/crown-jewel-patterns.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, computed_field

if TYPE_CHECKING:
    pass


# =============================================================================
# Evidence Tier Enum (Loss-Grounded)
# =============================================================================


class EvidenceTier(str, Enum):
    """
    Evidence tiers from Zero Seed, grounded in Galois loss.

    Each tier represents a level of epistemic strength:
    - CATEGORICAL: Near-lossless (proof is tight, necessary)
    - EMPIRICAL: Low loss (proof grounded in data)
    - AESTHETIC: Medium loss (proof appeals to values)
    - SOMATIC: High loss (proof is intuitive, not explicit)
    - CHAOTIC: Very high loss (proof doesn't cohere)

    The thresholds are:
    - CATEGORICAL: L < 0.1
    - EMPIRICAL:   L < 0.3
    - AESTHETIC:   L < 0.5
    - SOMATIC:     L < 0.7
    - CHAOTIC:     L >= 0.7
    """

    CATEGORICAL = "categorical"  # L < 0.1 (logical necessity)
    EMPIRICAL = "empirical"  # L < 0.3 (data-driven)
    AESTHETIC = "aesthetic"  # L < 0.5 (taste-based)
    SOMATIC = "somatic"  # L < 0.7 (gut feeling)
    CHAOTIC = "chaotic"  # L >= 0.7 (incoherent)


# =============================================================================
# Witness Mode Enum
# =============================================================================


class WitnessMode(str, Enum):
    """
    Witness modes based on Galois loss triage.

    Core insight: Low-loss edits are "routine" (batch them).
    High-loss edits are "important" (witness immediately).

    Modes:
    - SINGLE: Important, witness immediately (L < 0.1)
    - SESSION: Batch, witness at session end (L < 0.4)
    - LAZY: Deferred, witness only if referenced (L >= 0.4)
    - ARCHIVE: Background, witness to cold storage

    See: spec/protocols/zero-seed1/proof.md Part III
    """

    SINGLE = "single"  # Important: witness immediately
    SESSION = "session"  # Batch: witness at session end
    LAZY = "lazy"  # Deferred: witness only if referenced
    ARCHIVE = "archive"  # Background: witness to cold storage


# =============================================================================
# Classification Functions
# =============================================================================


def classify_by_loss(loss: float) -> EvidenceTier:
    """
    Map Galois loss to evidence tier.

    Thresholds chosen to match epistemic strength:
    - CATEGORICAL: Near-lossless (proof is tight, necessary)
    - EMPIRICAL: Low loss (proof grounded in data)
    - AESTHETIC: Medium loss (proof appeals to values)
    - SOMATIC: High loss (proof is intuitive, not explicit)
    - CHAOTIC: Very high loss (proof doesn't cohere)

    Args:
        loss: Galois loss value in [0, 1]

    Returns:
        EvidenceTier corresponding to the loss level

    Example:
        >>> classify_by_loss(0.05)
        EvidenceTier.CATEGORICAL
        >>> classify_by_loss(0.25)
        EvidenceTier.EMPIRICAL
        >>> classify_by_loss(0.8)
        EvidenceTier.CHAOTIC
    """
    if loss < 0.1:
        return EvidenceTier.CATEGORICAL
    elif loss < 0.3:
        return EvidenceTier.EMPIRICAL
    elif loss < 0.5:
        return EvidenceTier.AESTHETIC
    elif loss < 0.7:
        return EvidenceTier.SOMATIC
    else:
        return EvidenceTier.CHAOTIC


def select_witness_mode_from_loss(loss: float) -> WitnessMode:
    """
    Select witness mode based on Galois loss.

    Thresholds (empirically determined):
    - L < 0.1: IMPORTANT -> SINGLE (witness immediately)
    - L < 0.4: ROUTINE -> SESSION (batch with session)
    - L >= 0.4: EPHEMERAL -> LAZY (defer, might be discarded)

    Args:
        loss: Galois loss value in [0, 1]

    Returns:
        WitnessMode for triage

    Example:
        >>> select_witness_mode_from_loss(0.05)
        WitnessMode.SINGLE
        >>> select_witness_mode_from_loss(0.3)
        WitnessMode.SESSION
        >>> select_witness_mode_from_loss(0.6)
        WitnessMode.LAZY
    """
    if loss < 0.1:
        return WitnessMode.SINGLE
    elif loss < 0.4:
        return WitnessMode.SESSION
    else:
        return WitnessMode.LAZY


# =============================================================================
# Tier Bounds Configuration
# =============================================================================


class TierBounds(BaseModel):
    """
    Loss bounds for evidence tiers with rationale.

    Provides both classification and explanation for tier assignments.
    These bounds are configurable for domain-specific tuning.

    Attributes:
        categorical_max: Maximum loss for CATEGORICAL tier (default 0.1)
        empirical_max: Maximum loss for EMPIRICAL tier (default 0.3)
        aesthetic_max: Maximum loss for AESTHETIC tier (default 0.5)
        somatic_max: Maximum loss for SOMATIC tier (default 0.7)
    """

    categorical_max: float = Field(default=0.1, ge=0.0, le=1.0)
    empirical_max: float = Field(default=0.3, ge=0.0, le=1.0)
    aesthetic_max: float = Field(default=0.5, ge=0.0, le=1.0)
    somatic_max: float = Field(default=0.7, ge=0.0, le=1.0)

    def get_tier(self, loss: float) -> EvidenceTier:
        """
        Get tier for given loss using configured bounds.

        Args:
            loss: Galois loss value in [0, 1]

        Returns:
            EvidenceTier based on configured bounds
        """
        if loss < self.categorical_max:
            return EvidenceTier.CATEGORICAL
        elif loss < self.empirical_max:
            return EvidenceTier.EMPIRICAL
        elif loss < self.aesthetic_max:
            return EvidenceTier.AESTHETIC
        elif loss < self.somatic_max:
            return EvidenceTier.SOMATIC
        else:
            return EvidenceTier.CHAOTIC

    def get_rationale(self, tier: EvidenceTier) -> str:
        """
        Explain tier assignment with pedagogical rationale.

        Args:
            tier: The evidence tier to explain

        Returns:
            Human-readable explanation of the tier meaning
        """
        rationales = {
            EvidenceTier.CATEGORICAL: (
                f"Loss < {self.categorical_max}: Proof structure is nearly lossless "
                "under modularization. This indicates logical necessity--the proof's "
                "conclusions follow rigorously from its premises with minimal implicit "
                "assumptions."
            ),
            EvidenceTier.EMPIRICAL: (
                f"Loss < {self.empirical_max}: Proof has low but non-zero loss. This "
                "suggests the argument is grounded in empirical observations with some "
                "implicit inductive steps. The structure is mostly explicit."
            ),
            EvidenceTier.AESTHETIC: (
                f"Loss < {self.aesthetic_max}: Moderate loss indicates the proof appeals "
                "to values, taste, or design principles. Some connections are aesthetic "
                "rather than logical. The argument is coherent but not rigorous."
            ),
            EvidenceTier.SOMATIC: (
                f"Loss < {self.somatic_max}: High loss suggests the proof relies on "
                "intuition, gut feeling, or tacit knowledge. Much of the reasoning is "
                "implicit. The conclusion may be true, but the path is not fully "
                "articulable."
            ),
            EvidenceTier.CHAOTIC: (
                f"Loss >= {self.somatic_max}: Very high loss indicates the proof doesn't "
                "cohere under modularization. This may signal confusion, contradiction, "
                "or a task that's genuinely too complex to modularize. Consider "
                "simplifying or decomposing further."
            ),
        }
        return rationales.get(tier, "Unknown tier")


# =============================================================================
# Proof Loss Decomposition
# =============================================================================


class ProofLossDecomposition(BaseModel):
    """
    Galois loss broken down by Toulmin component.

    Each component contributes to total loss when proof is modularized.
    High loss in a component indicates implicit structure that isn't
    captured in the explicit representation.

    Attributes:
        data_loss: Loss in evidence statement
        warrant_loss: Loss in reasoning chain
        claim_loss: Loss in conclusion
        backing_loss: Loss in warrant support
        qualifier_loss: Loss in confidence expression
        rebuttal_loss: Loss in defeater enumeration
        composition_loss: Loss in how components connect (residual)

    Example:
        >>> decomp = ProofLossDecomposition(
        ...     data_loss=0.05,
        ...     warrant_loss=0.15,
        ...     claim_loss=0.03,
        ...     backing_loss=0.08,
        ...     qualifier_loss=0.02,
        ...     rebuttal_loss=0.04,
        ...     composition_loss=0.03,
        ... )
        >>> decomp.total
        0.4
    """

    data_loss: float = Field(default=0.0, ge=0.0, le=1.0)
    warrant_loss: float = Field(default=0.0, ge=0.0, le=1.0)
    claim_loss: float = Field(default=0.0, ge=0.0, le=1.0)
    backing_loss: float = Field(default=0.0, ge=0.0, le=1.0)
    qualifier_loss: float = Field(default=0.0, ge=0.0, le=1.0)
    rebuttal_loss: float = Field(default=0.0, ge=0.0, le=1.0)
    composition_loss: float = Field(default=0.0, ge=0.0, le=1.0)

    @computed_field
    @property
    def total(self) -> float:
        """Total loss = sum of component losses."""
        return (
            self.data_loss
            + self.warrant_loss
            + self.claim_loss
            + self.backing_loss
            + self.qualifier_loss
            + self.rebuttal_loss
            + self.composition_loss
        )

    def normalized(self) -> "ProofLossDecomposition":
        """
        Normalize so total = 1.0 (shows relative contributions).

        Returns:
            New ProofLossDecomposition with normalized values

        Example:
            >>> decomp = ProofLossDecomposition(data_loss=0.2, warrant_loss=0.3)
            >>> norm = decomp.normalized()
            >>> norm.total
            1.0
        """
        total = self.total
        if total == 0:
            return self

        return ProofLossDecomposition(
            data_loss=self.data_loss / total,
            warrant_loss=self.warrant_loss / total,
            claim_loss=self.claim_loss / total,
            backing_loss=self.backing_loss / total,
            qualifier_loss=self.qualifier_loss / total,
            rebuttal_loss=self.rebuttal_loss / total,
            composition_loss=self.composition_loss / total,
        )

    def to_dict(self) -> dict[str, float]:
        """
        Convert to dictionary for GaloisWitnessedProof.loss_decomposition.

        Returns:
            Dictionary mapping component names to loss values
        """
        return {
            "data": self.data_loss,
            "warrant": self.warrant_loss,
            "claim": self.claim_loss,
            "backing": self.backing_loss,
            "qualifier": self.qualifier_loss,
            "rebuttals": self.rebuttal_loss,
            "composition": self.composition_loss,
        }

    @classmethod
    def from_dict(cls, data: dict[str, float]) -> "ProofLossDecomposition":
        """
        Create from dictionary.

        Args:
            data: Dictionary with component losses

        Returns:
            ProofLossDecomposition instance
        """
        return cls(
            data_loss=data.get("data", 0.0),
            warrant_loss=data.get("warrant", 0.0),
            claim_loss=data.get("claim", 0.0),
            backing_loss=data.get("backing", 0.0),
            qualifier_loss=data.get("qualifier", 0.0),
            rebuttal_loss=data.get("rebuttals", 0.0),
            composition_loss=data.get("composition", 0.0),
        )

    def high_loss_components(self, threshold: float = 0.3) -> list[tuple[str, float]]:
        """
        Get components with loss above threshold.

        Useful for identifying weak points in proof structure.

        Args:
            threshold: Minimum loss to be considered "high" (default 0.3)

        Returns:
            List of (component_name, loss) tuples for high-loss components

        Example:
            >>> decomp = ProofLossDecomposition(warrant_loss=0.35, backing_loss=0.4)
            >>> decomp.high_loss_components()
            [('warrant', 0.35), ('backing', 0.4)]
        """
        components = [
            ("data", self.data_loss),
            ("warrant", self.warrant_loss),
            ("claim", self.claim_loss),
            ("backing", self.backing_loss),
            ("qualifier", self.qualifier_loss),
            ("rebuttals", self.rebuttal_loss),
            ("composition", self.composition_loss),
        ]
        return [(name, loss) for name, loss in components if loss > threshold]


# =============================================================================
# Alternative (Ghost Proof)
# =============================================================================


class Alternative(BaseModel):
    """
    A ghost alternative proof (deferred, not chosen).

    Ghost alternatives represent paths not taken--different ways the
    proof could have been structured. Each has its own Galois loss,
    enabling comparison with the chosen proof.

    From Differance philosophy: the meaning of the chosen proof is
    partly constituted by what was deferred.

    Attributes:
        description: What this alternative would have been
        galois_loss: Loss if this had been chosen
        deferral_cost: Cost of deferring (vs chosen proof)
        rationale: Why it was deferred

    Example:
        >>> alt = Alternative(
        ...     description="Bottom-up implementation approach",
        ...     galois_loss=0.19,
        ...     deferral_cost=0.04,
        ...     rationale="Top-down was chosen for clarity",
        ... )
    """

    description: str = Field(description="What this alternative would have been")
    galois_loss: float = Field(ge=0.0, le=1.0, description="Loss if chosen")
    deferral_cost: float = Field(ge=0.0, description="Cost of deferring vs chosen")
    rationale: str = Field(description="Why it was deferred")

    @computed_field
    @property
    def coherence(self) -> float:
        """Coherence of this alternative (1 - loss)."""
        return 1.0 - self.galois_loss

    def is_better_than(self, chosen_loss: float) -> bool:
        """
        Check if this alternative has lower loss than chosen proof.

        Args:
            chosen_loss: Galois loss of the chosen proof

        Returns:
            True if this alternative would have been better
        """
        return self.galois_loss < chosen_loss


# =============================================================================
# Galois Witnessed Proof
# =============================================================================


class GaloisWitnessedProof(BaseModel):
    """
    Toulmin proof extended with Galois loss quantification.

    The Galois loss measures how much coherence is lost when the proof
    is modularized and reconstituted. Low loss = tight, necessary structure.
    High loss = implicit dependencies not captured in explicit structure.

    Core Formula:
        coherence(P) = 1 - galois_loss(P)

    Attributes:
        data: Evidence supporting the claim
        warrant: Reasoning connecting data to claim
        claim: The conclusion being argued for
        backing: Support for the warrant itself
        qualifier: Degree of certainty ("definitely", "probably", etc.)
        rebuttals: Conditions that would defeat the argument
        tier: Original evidence tier (may differ from tier_from_loss)
        principles: Referenced Constitution principles
        galois_loss: L(proof) in [0, 1]
        loss_decomposition: Loss per Toulmin component
        ghost_alternatives: Deferred proof alternatives

    Example:
        >>> proof = GaloisWitnessedProof(
        ...     data="Tests pass (100% coverage)",
        ...     warrant="Passing tests indicate correctness",
        ...     claim="The refactoring preserves behavior",
        ...     backing="CLAUDE.md: 'DI > mocking' pattern",
        ...     qualifier="almost certainly",
        ...     rebuttals=("unless API changes", "unless edge case missed"),
        ...     tier=EvidenceTier.EMPIRICAL,
        ...     principles=("composable", "tasteful"),
        ...     galois_loss=0.18,
        ...     loss_decomposition={"warrant": 0.08, "backing": 0.10},
        ... )
        >>> proof.coherence
        0.82
        >>> proof.tier_from_loss
        EvidenceTier.EMPIRICAL
    """

    # Core Toulmin fields
    data: str = Field(description="Evidence supporting the claim")
    warrant: str = Field(description="Reasoning connecting data to claim")
    claim: str = Field(description="The conclusion being argued for")
    backing: str = Field(default="", description="Support for the warrant")
    qualifier: str = Field(
        default="probably", description="Confidence level: definitely, probably, etc."
    )
    rebuttals: tuple[str, ...] = Field(
        default_factory=tuple, description="Conditions that defeat the argument"
    )

    # Evidence tier (original classification, may differ from loss-based)
    tier: EvidenceTier = Field(default=EvidenceTier.EMPIRICAL, description="Original evidence tier")

    # Constitution principles
    principles: tuple[str, ...] = Field(default_factory=tuple, description="Referenced principles")

    # Galois metrics
    galois_loss: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Galois loss L(proof) in [0, 1]"
    )
    loss_decomposition: dict[str, float] = Field(
        default_factory=dict, description="Loss per component"
    )

    # Ghost alternatives (Differance)
    ghost_alternatives: tuple[Alternative, ...] = Field(
        default_factory=tuple, description="Deferred proof alternatives"
    )

    model_config = {"frozen": True}

    @computed_field
    @property
    def coherence(self) -> float:
        """
        Coherence = 1 - loss.

        This is the core insight of the Galois upgrade: proof quality
        is the inverse of information loss under modularization.

        Returns:
            Coherence value in [0, 1]
        """
        return 1.0 - self.galois_loss

    @computed_field
    @property
    def tier_from_loss(self) -> EvidenceTier:
        """
        Map loss to evidence tier.

        This may differ from the original tier assignment if the proof's
        actual coherence doesn't match its claimed evidence level.

        Returns:
            EvidenceTier derived from Galois loss
        """
        return classify_by_loss(self.galois_loss)

    @computed_field
    @property
    def rebuttals_from_loss(self) -> tuple[str, ...]:
        """
        Generate rebuttals from loss decomposition.

        High loss in specific components indicates potential defeaters.
        These are "ghost rebuttals" that surface implicit assumptions.

        Returns:
            Tuple of generated rebuttal strings

        Example:
            If warrant_loss is 0.35:
            "Unless implicit assumption in warrant fails (loss: 0.35)"
        """
        generated = []
        for component, loss in self.loss_decomposition.items():
            if loss > 0.3:  # Significant loss threshold
                generated.append(
                    f"Unless implicit assumption in {component} fails (loss: {loss:.2f})"
                )
        return tuple(generated)

    @computed_field
    @property
    def witness_mode(self) -> WitnessMode:
        """
        Triage witness mode based on loss.

        Low loss -> important, witness immediately
        Medium loss -> batch with session
        High loss -> lazy, might be discarded

        Returns:
            WitnessMode for witness triage
        """
        return select_witness_mode_from_loss(self.galois_loss)

    @computed_field
    @property
    def all_rebuttals(self) -> tuple[str, ...]:
        """
        Combine explicit rebuttals with loss-derived ghost rebuttals.

        Returns:
            All rebuttals (explicit + ghost)
        """
        return self.rebuttals + self.rebuttals_from_loss

    def get_decomposition(self) -> ProofLossDecomposition:
        """
        Get loss decomposition as ProofLossDecomposition instance.

        Returns:
            ProofLossDecomposition for detailed analysis
        """
        return ProofLossDecomposition.from_dict(self.loss_decomposition)

    def with_alternatives(self, alternatives: list[Alternative]) -> "GaloisWitnessedProof":
        """
        Return new proof with ghost alternatives added.

        Immutable pattern: creates new instance.

        Args:
            alternatives: List of alternative proofs to add

        Returns:
            New GaloisWitnessedProof with alternatives
        """
        return GaloisWitnessedProof(
            data=self.data,
            warrant=self.warrant,
            claim=self.claim,
            backing=self.backing,
            qualifier=self.qualifier,
            rebuttals=self.rebuttals,
            tier=self.tier,
            principles=self.principles,
            galois_loss=self.galois_loss,
            loss_decomposition=self.loss_decomposition,
            ghost_alternatives=self.ghost_alternatives + tuple(alternatives),
        )

    def with_loss(
        self, loss: float, decomposition: dict[str, float] | None = None
    ) -> "GaloisWitnessedProof":
        """
        Return new proof with updated Galois loss.

        Immutable pattern: creates new instance.

        Args:
            loss: New Galois loss value
            decomposition: Optional updated decomposition

        Returns:
            New GaloisWitnessedProof with updated loss
        """
        return GaloisWitnessedProof(
            data=self.data,
            warrant=self.warrant,
            claim=self.claim,
            backing=self.backing,
            qualifier=self.qualifier,
            rebuttals=self.rebuttals,
            tier=self.tier,
            principles=self.principles,
            galois_loss=loss,
            loss_decomposition=decomposition or self.loss_decomposition,
            ghost_alternatives=self.ghost_alternatives,
        )

    def quality_summary(self) -> str:
        """
        Generate human-readable quality summary.

        Returns:
            Multi-line summary of proof quality
        """
        stars = int(self.coherence * 5)
        star_display = "*" * stars + "." * (5 - stars)

        decomp = self.get_decomposition()
        high_loss = decomp.high_loss_components(threshold=0.25)

        summary_lines = [
            f"Coherence: {self.coherence:.2f} [{star_display}]",
            f"Tier: {self.tier_from_loss.value.upper()}",
            f"Witness Mode: {self.witness_mode.value}",
        ]

        if high_loss:
            summary_lines.append("Weak Points:")
            for name, loss in high_loss:
                summary_lines.append(f"  - {name}: {loss:.2f}")

        if self.ghost_alternatives:
            summary_lines.append(f"Ghost Alternatives: {len(self.ghost_alternatives)}")
            for alt in self.ghost_alternatives[:2]:  # Show first 2
                better = " (better)" if alt.is_better_than(self.galois_loss) else ""
                summary_lines.append(
                    f"  - {alt.description[:40]}... L={alt.galois_loss:.2f}{better}"
                )

        return "\n".join(summary_lines)

    def is_valid(self) -> bool:
        """Check if proof is valid (not CHAOTIC tier)."""
        return self.tier_from_loss != EvidenceTier.CHAOTIC

    def needs_revision(self) -> bool:
        """Check if proof needs revision (coherence < 0.5)."""
        return self.coherence < 0.5


# =============================================================================
# Proof Validation Result
# =============================================================================


class ProofValidation(BaseModel):
    """
    Result of Galois-based proof validation.

    Contains coherence score, classified tier, diagnostic issues,
    and overall assessment of proof quality.

    Attributes:
        coherence: 1 - loss (proof quality score)
        tier: Classified evidence tier
        issues: List of diagnostic issues found
        assessment: Overall assessment string
        loss_decomposition: Per-component loss breakdown

    Example:
        >>> validation = ProofValidation(
        ...     coherence=0.77,
        ...     tier=EvidenceTier.EMPIRICAL,
        ...     issues=["Warrant has high implicit structure"],
        ...     assessment="Reasonable proof with some implicit steps",
        ...     loss_decomposition={"warrant": 0.15, "backing": 0.08},
        ... )
        >>> validation.is_valid
        True
    """

    coherence: float = Field(ge=0.0, le=1.0, description="1 - loss")
    tier: EvidenceTier = Field(description="Classified evidence tier")
    issues: list[str] = Field(default_factory=list, description="Diagnostic issues")
    assessment: str = Field(description="Overall assessment")
    loss_decomposition: dict[str, float] = Field(
        default_factory=dict, description="Per-component losses"
    )

    @computed_field
    @property
    def is_valid(self) -> bool:
        """Proof is valid if tier is not CHAOTIC."""
        return self.tier != EvidenceTier.CHAOTIC

    @computed_field
    @property
    def needs_revision(self) -> bool:
        """Proof needs revision if coherence < 0.5."""
        return self.coherence < 0.5

    @computed_field
    @property
    def galois_loss(self) -> float:
        """Galois loss (1 - coherence)."""
        return 1.0 - self.coherence

    def summary(self) -> str:
        """
        Generate human-readable validation summary.

        Returns:
            Multi-line summary string
        """
        status = "VALID" if self.is_valid else "INVALID"
        revision = " (needs revision)" if self.needs_revision else ""

        lines = [
            f"Status: {status}{revision}",
            f"Coherence: {self.coherence:.3f}",
            f"Tier: {self.tier.value}",
            f"Assessment: {self.assessment}",
        ]

        if self.issues:
            lines.append("Issues:")
            for issue in self.issues:
                lines.append(f"  - {issue}")

        return "\n".join(lines)


# =============================================================================
# Contradiction Analysis
# =============================================================================


@dataclass
class ContradictionAnalysis:
    """
    Analysis of potential contradiction between proofs.

    Contradictions are detected via super-additive loss: if combining
    two proofs produces more loss than the sum of individual losses,
    they contradict (their combination introduces additional incoherence).

    Attributes:
        loss_a: Galois loss of first proof
        loss_b: Galois loss of second proof
        loss_combined: Galois loss of combined proof

    Example:
        >>> analysis = ContradictionAnalysis(
        ...     loss_a=0.2,
        ...     loss_b=0.25,
        ...     loss_combined=0.7,
        ... )
        >>> analysis.super_additivity
        0.25
        >>> analysis.contradicts()
        True
    """

    loss_a: float
    loss_b: float
    loss_combined: float

    @property
    def expected_loss(self) -> float:
        """Expected combined loss (additive baseline)."""
        return self.loss_a + self.loss_b

    @property
    def super_additivity(self) -> float:
        """How much more loss than expected."""
        return self.loss_combined - self.expected_loss

    def contradicts(self, tolerance: float = 0.1) -> bool:
        """
        Do proofs contradict (super-additive beyond tolerance)?

        Args:
            tolerance: Threshold for super-additivity (default 0.1)

        Returns:
            True if proofs contradict
        """
        return self.super_additivity > tolerance

    def severity(self) -> str:
        """
        Assess contradiction severity.

        Returns:
            Human-readable severity description
        """
        sa = self.super_additivity
        if sa < 0:
            return "COMPATIBLE (sub-additive, proofs reinforce each other)"
        elif sa < 0.1:
            return "COMPATIBLE (additive, proofs are independent)"
        elif sa < 0.3:
            return "TENSION (mild super-additivity, proofs create friction)"
        elif sa < 0.6:
            return "CONTRADICTION (significant super-additivity, proofs clash)"
        else:
            return "STRONG CONTRADICTION (extreme super-additivity, proofs are incompatible)"


# =============================================================================
# Coherence Error
# =============================================================================


class CoherenceError(Exception):
    """
    Raised when marks don't cohere for crystallization.

    This error indicates that a set of proofs or marks cannot be
    meaningfully combined because their Galois loss is too high.

    Attributes:
        message: Error description
        loss: The actual loss value
        threshold: The maximum acceptable loss
    """

    def __init__(self, message: str, loss: float = 0.0, threshold: float = 0.3):
        super().__init__(message)
        self.loss = loss
        self.threshold = threshold


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core types
    "GaloisWitnessedProof",
    "ProofLossDecomposition",
    "Alternative",
    "ProofValidation",
    "ContradictionAnalysis",
    # Enums
    "EvidenceTier",
    "WitnessMode",
    # Configuration
    "TierBounds",
    # Functions
    "classify_by_loss",
    "select_witness_mode_from_loss",
    # Errors
    "CoherenceError",
]
