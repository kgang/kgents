"""
E-gent v2 Core Types: Teleological Thermodynamic Evolution.

This module defines the foundational types for E-gent v2:
- Phage: Active mutation vector (not passive experiment)
- MutationVector: Concrete mutation with thermodynamic properties
- Intent: Teleological field constraining evolution
- Thermodynamic types: Gibbs, enthalpy, entropy

Spec Reference: spec/e-gents/thermodynamics.md
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal
from uuid import uuid4


# =============================================================================
# Phage Types (Active Mutation Vectors)
# =============================================================================


class PhageStatus(Enum):
    """
    Status of a Phage in the evolution cycle.

    Unlike v1's passive ExperimentStatus, PhageStatus reflects
    the active lifecycle of a mutation vector.
    """

    NASCENT = "nascent"  # Just created, not yet mutated
    MUTATED = "mutated"  # Mutation generated
    QUOTED = "quoted"  # Got market quote, awaiting wager
    STAKED = "staked"  # Wager placed, ready to infect
    INFECTING = "infecting"  # Currently applying mutation
    INFECTED = "infected"  # Mutation applied successfully
    REJECTED = "rejected"  # Failed selection (Demon rejected)
    FAILED = "failed"  # Failed validation (tests, types)
    SETTLED = "settled"  # Bets settled, lifecycle complete


@dataclass
class PhageLineage:
    """
    Lineage tracking for phages.

    Enables evolutionary history reconstruction and
    pattern recognition for viral library.
    """

    parent_id: str | None = None
    generation: int = 0
    schema_signature: str = ""  # L-gent schema that created this
    mutations_applied: list[str] = field(default_factory=list)

    def spawn_child(self, schema_signature: str) -> "PhageLineage":
        """Create lineage for a child phage."""
        return PhageLineage(
            parent_id=None,  # Will be set when phage is created
            generation=self.generation + 1,
            schema_signature=schema_signature,
            mutations_applied=list(self.mutations_applied),
        )


@dataclass
class MutationVector:
    """
    A concrete mutation proposal with thermodynamic properties.

    Unlike random mutations, MutationVectors are:
    - Schema-derived (from L-gent's mutation schemas)
    - Thermodynamically evaluated (ΔH, ΔS, ΔG)
    - Intent-aligned (teleological constraint)
    """

    id: str = field(default_factory=lambda: f"mv_{uuid4().hex[:8]}")

    # Source
    schema_signature: str = ""  # L-gent schema that generated this
    original_code: str = ""
    mutated_code: str = ""

    # Thermodynamic properties (from schema + analysis)
    enthalpy_delta: float = 0.0  # ΔH: Complexity change (- = simpler)
    entropy_delta: float = 0.0  # ΔS: Capability change (+ = more)
    temperature: float = 1.0  # T: System "temperature" (exploration vs exploitation)

    # Metadata
    description: str = ""
    confidence: float = 0.5  # Schema confidence (0.0-1.0)
    lines_changed: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def gibbs_free_energy(self) -> float:
        """
        ΔG = ΔH - TΔS

        The thermodynamic viability criterion.
        ΔG < 0 means mutation is spontaneously favorable.
        """
        return self.enthalpy_delta - (self.temperature * self.entropy_delta)

    @property
    def is_viable(self) -> bool:
        """Check if mutation is thermodynamically viable."""
        return self.gibbs_free_energy < 0

    @property
    def signature(self) -> str:
        """Unique signature for this mutation (for viral library)."""
        content = f"{self.schema_signature}:{self.original_code[:100]}:{self.mutated_code[:100]}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


@dataclass
class Phage:
    """
    A Phage is an active mutation vector that can "infect" code.

    Unlike v1's passive Experiment, a Phage:
    - Has agency (can spawn children, propagate DNA)
    - Has lineage (tracks evolutionary history)
    - Has economics (staking, betting, payoff)
    - Carries DNA (viral patterns for library)

    From spec/e-gents/thermodynamics.md:
    > A Phage is a self-contained evolution unit.
    > It carries mutation DNA, has a lifecycle, and can reproduce.
    """

    id: str = field(default_factory=lambda: f"phage_{uuid4().hex[:8]}")

    # Target
    target_path: Path | None = None
    target_module: str = ""

    # Mutation
    mutation: MutationVector | None = None
    hypothesis: str = ""  # Why this mutation might help

    # Lifecycle
    status: PhageStatus = PhageStatus.NASCENT
    lineage: PhageLineage = field(default_factory=PhageLineage)

    # Economics
    stake: int = 0  # Tokens staked for infect
    bet_id: str | None = None  # Associated market bet
    market_odds: float = 0.0  # Odds when bet was placed

    # Intent alignment (from Teleological Demon)
    intent_alignment: float = 0.0  # Cosine similarity to Intent
    intent_checked: bool = False

    # Results (populated after lifecycle)
    test_passed: bool | None = None
    type_check_passed: bool | None = None
    infection_result: "InfectionResult | None" = None

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    error: str | None = None

    @property
    def dna(self) -> str:
        """
        The "DNA" of this phage for viral library.

        Encodes the successful mutation pattern for propagation.
        """
        if self.mutation:
            return self.mutation.signature
        return ""

    def spawn(self, mutation: MutationVector) -> "Phage":
        """
        Spawn a child phage with this one's lineage.

        Used for evolutionary chains where successful mutations
        lead to further refinements.
        """
        child_lineage = self.lineage.spawn_child(mutation.schema_signature)
        child_lineage.parent_id = self.id

        return Phage(
            target_path=self.target_path,
            target_module=self.target_module,
            mutation=mutation,
            status=PhageStatus.MUTATED,
            lineage=child_lineage,
        )


# =============================================================================
# Infection Types (Result of Phage Application)
# =============================================================================


class InfectionStatus(Enum):
    """Status of a phage infection attempt."""

    SUCCESS = "success"  # Mutation applied, tests pass
    PARTIAL = "partial"  # Applied but tests fail
    REJECTED = "rejected"  # Rejected by Demon
    FAILED = "failed"  # Could not apply
    ROLLBACK = "rollback"  # Applied then rolled back


@dataclass
class InfectionResult:
    """
    Result of a phage infecting a codebase.

    Captures everything needed for:
    - Bet settlement
    - Viral library update
    - Lineage tracking
    """

    phage_id: str
    status: InfectionStatus

    # Validation results
    syntax_valid: bool = False
    types_valid: bool = False
    tests_passed: bool = False

    # Metrics
    test_count: int = 0
    test_failures: int = 0
    type_errors: int = 0

    # Economics
    tokens_consumed: int = 0
    stake_returned: bool = False
    bet_won: bool | None = None

    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    duration_ms: float = 0.0

    # Errors
    error_message: str | None = None
    rollback_reason: str | None = None


# =============================================================================
# Intent Types (Teleological Field)
# =============================================================================


@dataclass
class Intent:
    """
    The Teleological Field that constrains evolution.

    Without Intent, evolution drifts toward parasitic code
    (lowest energy = empty file or hardcoded values).

    With Intent, evolution is constrained to PURPOSE:
    the User's desired outcome.

    From spec:
    > Intent is the embedding of what the User wants.
    > It acts as a "teleological field" that guides evolution.
    > Mutations that drift too far from Intent are rejected
    > by the Teleological Demon regardless of test results.
    """

    embedding: list[float]
    source: Literal["user", "tests", "structure"]
    description: str
    confidence: float = 1.0  # How sure are we about this intent?

    # Context
    module_name: str = ""
    file_path: str = ""

    # Metrics (tracked over time)
    mutations_aligned: int = 0  # Mutations that passed alignment check
    mutations_rejected: int = 0  # Mutations rejected for misalignment

    def alignment_with(self, other_embedding: list[float]) -> float:
        """
        Calculate alignment (cosine similarity) with another embedding.

        Used by Teleological Demon to check if mutation drifts from intent.
        """
        if len(self.embedding) != len(other_embedding):
            return 0.0

        # Cosine similarity
        import math

        dot = sum(a * b for a, b in zip(self.embedding, other_embedding))
        mag1 = math.sqrt(sum(a * a for a in self.embedding))
        mag2 = math.sqrt(sum(b * b for b in other_embedding))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot / (mag1 * mag2)


# =============================================================================
# Thermodynamic Types
# =============================================================================


@dataclass
class GibbsEnergy:
    """
    Gibbs Free Energy calculation for a mutation.

    ΔG = ΔH - TΔS

    Where:
    - ΔH (enthalpy): Complexity change (negative = simpler)
    - ΔS (entropy): Capability change (positive = more capable)
    - T (temperature): System exploration rate

    A mutation is thermodynamically favorable when ΔG < 0.
    """

    enthalpy_delta: float  # ΔH: Complexity change
    entropy_delta: float  # ΔS: Capability change
    temperature: float  # T: System temperature

    @property
    def delta_g(self) -> float:
        """Calculate Gibbs free energy change."""
        return self.enthalpy_delta - (self.temperature * self.entropy_delta)

    @property
    def is_favorable(self) -> bool:
        """Check if the energy change is favorable (spontaneous)."""
        return self.delta_g < 0

    @property
    def favorability_margin(self) -> float:
        """How favorable/unfavorable (negative = more favorable)."""
        return self.delta_g


@dataclass
class ThermodynamicState:
    """
    Thermodynamic state of the evolution system.

    Tracks system-wide thermodynamic properties for
    temperature control and equilibrium detection.
    """

    temperature: float = 1.0  # Current system temperature

    # Cumulative metrics
    total_enthalpy_change: float = 0.0
    total_entropy_change: float = 0.0
    total_gibbs_change: float = 0.0

    # Rates
    mutation_rate: float = 0.0  # Mutations per unit time
    success_rate: float = 0.5  # Fraction of successful mutations
    rejection_rate: float = 0.0  # Fraction rejected by Demon

    # Temperature control
    cooling_rate: float = 0.001  # How fast temperature decreases
    min_temperature: float = 0.1  # Floor temperature
    max_temperature: float = 10.0  # Ceiling temperature

    def record_mutation(self, gibbs: GibbsEnergy, succeeded: bool) -> None:
        """Record a mutation outcome and update state."""
        self.total_enthalpy_change += gibbs.enthalpy_delta
        self.total_entropy_change += gibbs.entropy_delta
        self.total_gibbs_change += gibbs.delta_g

        # Update success rate (exponential moving average)
        alpha = 0.1
        outcome = 1.0 if succeeded else 0.0
        self.success_rate = (1 - alpha) * self.success_rate + alpha * outcome

    def cool(self) -> None:
        """Apply cooling (reduce exploration, increase exploitation)."""
        self.temperature = max(
            self.min_temperature,
            self.temperature * (1 - self.cooling_rate),
        )

    def heat(self, amount: float = 0.1) -> None:
        """Apply heating (increase exploration)."""
        self.temperature = min(
            self.max_temperature,
            self.temperature * (1 + amount),
        )


# =============================================================================
# Evolution Cycle State
# =============================================================================


@dataclass
class EvolutionCycleState:
    """
    State of the evolution cycle.

    Tracks the overall progress through:
    Sun → Mutate → Select → Wager → Infect → Payoff
    """

    cycle_id: str = field(default_factory=lambda: f"cycle_{uuid4().hex[:8]}")

    # Phase tracking
    current_phase: Literal["sun", "mutate", "select", "wager", "infect", "payoff"] = (
        "sun"
    )

    # Active phages
    phages: list[Phage] = field(default_factory=list)

    # Economics
    tokens_allocated: int = 0  # From grants
    tokens_staked: int = 0  # Currently at risk
    tokens_won: int = 0  # Winnings
    tokens_lost: int = 0  # Losses

    # Thermodynamics
    thermo_state: ThermodynamicState = field(default_factory=ThermodynamicState)

    # Intent
    intent: Intent | None = None

    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None

    # Results
    phages_succeeded: int = 0
    phages_failed: int = 0
    phages_rejected: int = 0

    @property
    def success_rate(self) -> float:
        """Success rate for this cycle."""
        total = self.phages_succeeded + self.phages_failed + self.phages_rejected
        if total == 0:
            return 0.0
        return self.phages_succeeded / total

    @property
    def roi(self) -> float:
        """Return on investment for this cycle."""
        if self.tokens_staked + self.tokens_lost == 0:
            return 0.0
        return (self.tokens_won - self.tokens_lost) / (
            self.tokens_staked + self.tokens_lost
        )
