"""
Derivation Types: Core data structures for the Derivation Framework.

This module defines the frozen, immutable types that form the derivation
ontology. All types are frozen dataclasses for several reasons:

1. Composability: Immutable types compose cleanly (Principle 5)
2. Trust: Derivations are proofs; proofs shouldn't mutate
3. Performance: Frozen dataclasses cache hashes (bootstrap.md §Performance)

The Derivation type captures:
- The chain of agents this derives from (ancestry)
- The principles drawn upon with their evidence strength
- The accumulated confidence from inheritance + evidence

Teaching:
    gotcha: Inherited confidence is computed from ancestors, not set manually.
            Use DerivationRegistry.register() which computes it for you.

    gotcha: EvidenceType.SOMATIC has no evidence_sources. Kent's judgment
            isn't formalized—it's the ethical floor (Constitution Article IV).
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Callable


class DerivationTier(str, Enum):
    """
    Tiers in the derivation hierarchy.

    Each tier has a confidence ceiling—no matter how much evidence,
    an APP agent can't exceed JEWEL confidence. This is Law 2.

    The ordering: AXIOM < BOOTSTRAP < FUNCTOR < POLYNOMIAL < OPERAD < JEWEL < APP
    (by confidence ceiling, descending)

    AXIOM tier is special: it has confidence 1.0 by definition—it IS the ground truth.
    CONSTITUTION is the only AXIOM-tier agent. All bootstrap agents derive from it.
    """

    AXIOM = "axiom"  # Ceiling: 1.00 (the constitution itself—axiomatic truth)
    BOOTSTRAP = "bootstrap"  # Ceiling: 1.00 (categorical proofs, derive from AXIOM)
    FUNCTOR = "functor"  # Ceiling: 0.98 (derived functors: Flux, Cooled, etc.)
    POLYNOMIAL = "polynomial"  # Ceiling: 0.95 (state machines: SOUL, MEMORY)
    OPERAD = "operad"  # Ceiling: 0.92 (composition grammars)
    JEWEL = "jewel"  # Ceiling: 0.85 (Crown Jewels: Brain, Witness, etc.)
    APP = "app"  # Ceiling: 0.75 (Application agents: Morning Coffee)

    @property
    def ceiling(self) -> float:
        """Maximum confidence this tier can achieve."""
        ceilings = {
            DerivationTier.AXIOM: 1.00,
            DerivationTier.BOOTSTRAP: 1.00,
            DerivationTier.FUNCTOR: 0.98,
            DerivationTier.POLYNOMIAL: 0.95,
            DerivationTier.OPERAD: 0.92,
            DerivationTier.JEWEL: 0.85,
            DerivationTier.APP: 0.75,
        }
        return ceilings[self]

    @property
    def rank(self) -> int:
        """Numeric rank for tier ordering (lower = more foundational)."""
        ranks = {
            DerivationTier.AXIOM: -1,  # Most foundational—the ground itself
            DerivationTier.BOOTSTRAP: 0,
            DerivationTier.FUNCTOR: 1,
            DerivationTier.POLYNOMIAL: 2,
            DerivationTier.OPERAD: 3,
            DerivationTier.JEWEL: 4,
            DerivationTier.APP: 5,
        }
        return ranks[self]

    def __lt__(self, other: object) -> bool:
        """Lower tier = more foundational."""
        if not isinstance(other, DerivationTier):
            return NotImplemented
        return self.rank < other.rank


class EvidenceType(str, Enum):
    """
    Types of evidence for principle draws.

    Different evidence types have different decay rates and verification methods:
    - CATEGORICAL: Laws verified formally (Dafny, Lean4) - no decay
    - EMPIRICAL: ASHC chaos test results - slow decay
    - AESTHETIC: Hardy beauty criteria - medium decay
    - GENEALOGICAL: Git archaeology - slow decay
    - SOMATIC: Kent's Mirror Test - no formalization (Constitution Article IV)
    """

    CATEGORICAL = "categorical"  # Formal proofs (no decay)
    EMPIRICAL = "empirical"  # ASHC runs (slow decay: 0.02/day)
    AESTHETIC = "aesthetic"  # Hardy criteria (medium decay: 0.03/day)
    GENEALOGICAL = "genealogical"  # Git archaeology (slow decay: 0.01/day)
    SOMATIC = "somatic"  # Mirror test (Kent's judgment, not formalized)

    @property
    def decay_rate(self) -> float:
        """Per-day decay rate for this evidence type."""
        rates = {
            EvidenceType.CATEGORICAL: 0.0,  # Never decays
            EvidenceType.EMPIRICAL: 0.02,
            EvidenceType.AESTHETIC: 0.03,
            EvidenceType.GENEALOGICAL: 0.01,
            EvidenceType.SOMATIC: 0.0,  # Not formalized, doesn't decay
        }
        return rates[self]


@dataclass(frozen=True)
class PrincipleDraw:
    """
    Evidence that an agent instantiates a principle.

    A "draw" on a principle is like citing a source—the agent claims to
    embody this principle, backed by evidence of a certain type and strength.

    The seven principles from spec/principles.md:
    - Tasteful, Curated, Ethical, Joy-Inducing
    - Composable, Heterarchical, Generative

    Teaching:
        gotcha: draw_strength of 1.0 means "fully instantiates this principle"
                but is only achievable with CATEGORICAL evidence (formal proofs).
    """

    principle: str
    draw_strength: float  # 0.0-1.0, how strongly the agent draws on this principle
    evidence_type: EvidenceType
    evidence_sources: tuple[str, ...] = ()  # IDs of supporting evidence
    last_verified: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        """Validate draw_strength is in [0, 1]."""
        if not 0.0 <= self.draw_strength <= 1.0:
            object.__setattr__(self, "draw_strength", max(0.0, min(1.0, self.draw_strength)))

    @property
    def is_categorical(self) -> bool:
        """Categorical draws don't decay—they're formal proofs."""
        return self.evidence_type == EvidenceType.CATEGORICAL

    def decay(self, days_elapsed: float) -> PrincipleDraw:
        """
        Apply time-based decay to non-categorical evidence.

        Decay formula: strength' = strength * (1 - rate)^days
        With a floor of 0.1 to prevent complete disappearance.

        Categorical and somatic evidence doesn't decay.
        """
        if self.evidence_type in (EvidenceType.CATEGORICAL, EvidenceType.SOMATIC):
            return self

        rate = self.evidence_type.decay_rate
        decayed_strength = self.draw_strength * ((1 - rate) ** days_elapsed)
        return replace(self, draw_strength=max(0.1, decayed_strength))


@dataclass(frozen=True)
class Derivation:
    """
    A derivation is a morphism from bootstrap axioms to a derived agent.

    It carries:
    - The chain of agents this derives from (ancestry in the DAG)
    - The principles drawn upon with their evidence strength
    - The accumulated confidence from inheritance + evidence

    The derivation IS the justification. An agent without derivation is
    not an agent—it's a mystery. (spec/protocols/derivation-framework.md)

    Laws this type must satisfy:
    1. Monotonicity: tier(D) > tier(parent(D))
    2. Confidence Ceiling: total_confidence <= tier_ceiling(tier)
    3. Bootstrap Indefeasibility: bootstrap agents have confidence = 1.0
    4. Acyclicity: No cycles in derives_from (enforced by registry)
    5. Propagation: Confidence changes propagate through DAG

    Teaching:
        gotcha: Don't create Derivation directly for derived agents.
                Use DerivationRegistry.register() which computes inherited_confidence.

        gotcha: total_confidence is a property, not a stored value.
                It's computed fresh from components each time.
    """

    # Identity
    agent_name: str
    tier: DerivationTier

    # The derivation chain (ancestors in the DAG)
    # Empty for bootstrap agents (they ARE the axioms)
    derives_from: tuple[str, ...] = ()

    # Principle draws with evidence
    principle_draws: tuple[PrincipleDraw, ...] = ()

    # Confidence components
    inherited_confidence: float = 1.0  # From derivation chain
    empirical_confidence: float = 0.0  # From ASHC evidence
    stigmergic_confidence: float = 0.0  # From usage patterns (Witness marks)

    @property
    def total_confidence(self) -> float:
        """
        Combined confidence with diminishing returns.

        The formula:
        - Base: inherited_confidence (from derivation chain)
        - Boost: min(0.2, empirical_confidence * 0.3) - evidence can't dominate
        - Stigmergy: stigmergic_confidence * 0.1 - usage is weak signal

        Result is capped at tier ceiling. This ensures Law 2:
        no APP agent can exceed 0.75 even with perfect evidence.
        """
        base = self.inherited_confidence
        boost = min(0.2, self.empirical_confidence * 0.3)
        stigmergy = self.stigmergic_confidence * 0.1

        raw_confidence = base + boost + stigmergy
        return min(self.tier.ceiling, raw_confidence)

    @property
    def is_bootstrap(self) -> bool:
        """Bootstrap agents are axioms—they don't derive from anything."""
        return self.tier == DerivationTier.BOOTSTRAP

    @property
    def is_axiom(self) -> bool:
        """AXIOM tier is the constitution itself—the ground truth."""
        return self.tier == DerivationTier.AXIOM

    @property
    def is_indefeasible(self) -> bool:
        """AXIOM and BOOTSTRAP tiers are indefeasible—confidence can't be modified."""
        return self.tier in (DerivationTier.AXIOM, DerivationTier.BOOTSTRAP)

    def with_evidence(
        self,
        empirical: float | None = None,
        stigmergic: float | None = None,
    ) -> Derivation:
        """
        Return new derivation with updated evidence.

        This is the functional update pattern—derivations are immutable.
        """
        return replace(
            self,
            empirical_confidence=(
                empirical if empirical is not None else self.empirical_confidence
            ),
            stigmergic_confidence=(
                stigmergic if stigmergic is not None else self.stigmergic_confidence
            ),
        )

    def with_principle_draws(self, draws: tuple[PrincipleDraw, ...]) -> Derivation:
        """Return new derivation with updated principle draws."""
        return replace(self, principle_draws=draws)

    def decay_evidence(self, days_elapsed: float) -> Derivation:
        """
        Apply time-based decay to all non-categorical principle draws.

        Returns a new Derivation with decayed draws.
        """
        decayed_draws = tuple(draw.decay(days_elapsed) for draw in self.principle_draws)
        return replace(self, principle_draws=decayed_draws)


# --- Bootstrap Principle Draws (the axiom base) ---
#
# These are the principle draws for the 7 bootstrap agents.
# They have categorical evidence (confidence = 1.0) because
# they ARE the axioms—verified by BootstrapWitness.


def _make_categorical_draw(
    principle: str,
    strength: float,
    evidence_source: str,
) -> PrincipleDraw:
    """Helper to create categorical principle draws."""
    return PrincipleDraw(
        principle=principle,
        draw_strength=strength,
        evidence_type=EvidenceType.CATEGORICAL,
        evidence_sources=(evidence_source,),
    )


# The bootstrap agents and their principle draws
# See spec/bootstrap.md and spec/principles.md
BOOTSTRAP_PRINCIPLE_DRAWS: dict[str, tuple[PrincipleDraw, ...]] = {
    "Id": (_make_categorical_draw("Composable", 1.0, "identity-law"),),
    "Compose": (
        _make_categorical_draw("Composable", 1.0, "associativity-law"),
        _make_categorical_draw("Generative", 0.9, "pipelines-derive"),
    ),
    "Judge": (
        _make_categorical_draw("Tasteful", 1.0, "judgment-function"),
        _make_categorical_draw("Curated", 1.0, "selection-function"),
        _make_categorical_draw("Ethical", 1.0, "ethics-embedded"),
    ),
    "Ground": (
        _make_categorical_draw("Generative", 1.0, "facts-seed-generation"),
        _make_categorical_draw("Ethical", 0.9, "human-values-source"),
    ),
    "Contradict": (_make_categorical_draw("Heterarchical", 0.9, "tension-detection"),),
    "Sublate": (
        _make_categorical_draw("Heterarchical", 1.0, "synthesis-function"),
        # Joy-Inducing is aesthetic, not categorical—the creative leap
        PrincipleDraw(
            principle="Joy-Inducing",
            draw_strength=0.7,
            evidence_type=EvidenceType.AESTHETIC,
            evidence_sources=("creative-leap",),
        ),
    ),
    "Fix": (
        _make_categorical_draw("Composable", 0.95, "fixed-point-enables-recursion"),
        _make_categorical_draw("Generative", 1.0, "self-reference"),
    ),
}


__all__ = [
    "Derivation",
    "DerivationTier",
    "EvidenceType",
    "PrincipleDraw",
    "BOOTSTRAP_PRINCIPLE_DRAWS",
]
