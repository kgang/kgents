"""
Validation Schema: Type definitions for the validation framework.

The Three Primitives:
- Proposition: Atomic measurable claim
- Gate: Decision checkpoint
- Initiative: Body of work with validation criteria

Design:
- All dataclasses are frozen (immutable)
- Enums for constrained values
- Results separate from definitions

See: spec/validation/schema.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, NewType

# =============================================================================
# Type Aliases
# =============================================================================

PropositionId = NewType("PropositionId", str)
GateId = NewType("GateId", str)
PhaseId = NewType("PhaseId", str)
InitiativeId = NewType("InitiativeId", str)
MarkId = NewType("MarkId", str)


# =============================================================================
# Enums
# =============================================================================


class MetricType(Enum):
    """Kinds of measurements."""

    # Quantitative (0.0 - 1.0)
    ACCURACY = "accuracy"
    RECALL = "recall"
    PRECISION = "precision"
    F1 = "f1"
    AUC = "auc"
    PEARSON_R = "pearson_r"  # -1.0 to 1.0

    # Quantitative (counts)
    COUNT = "count"
    PERCENT = "percent"  # 0 - 100
    DURATION_MS = "duration_ms"

    # Qualitative
    BINARY = "binary"  # 0 or 1
    ORDINAL = "ordinal"  # 1-5 rating
    JUDGMENT = "judgment"  # Human assessment


class Direction(Enum):
    """Comparison direction for threshold checking."""

    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    EQ = "="


class GateCondition(Enum):
    """How to aggregate proposition results into a gate decision."""

    ALL_REQUIRED = "all_required"  # All required props must pass
    ANY = "any"  # Any prop passes
    QUORUM = "quorum"  # N of M pass
    CUSTOM = "custom"  # Custom aggregation function


# =============================================================================
# Core Primitives
# =============================================================================


@dataclass(frozen=True)
class Proposition:
    """
    A measurable claim.

    The atomic unit of validation. A proposition has:
    - A unique ID (within its initiative)
    - A description (human-readable claim)
    - A metric type (how to measure)
    - A threshold (success boundary)
    - A direction (comparison operator)
    - A required flag (does this block gates?)

    For qualitative propositions:
    - judgment_required: needs human input
    - judgment_criteria: what to assess
    """

    id: PropositionId
    description: str
    metric: MetricType
    threshold: float
    direction: Direction
    required: bool = True

    # For qualitative propositions
    judgment_required: bool = False
    judgment_criteria: str = ""

    def __post_init__(self) -> None:
        """Validate proposition invariants."""
        if self.metric == MetricType.JUDGMENT and not self.judgment_required:
            # Auto-fix: judgment metrics always require human input
            object.__setattr__(self, "judgment_required", True)


@dataclass(frozen=True)
class Gate:
    """
    A decision checkpoint.

    Aggregates propositions into a go/no-go moment.
    """

    id: GateId
    name: str
    condition: GateCondition
    proposition_ids: tuple[PropositionId, ...] = ()

    # For quorum condition
    quorum_n: int = 0  # N of M must pass

    # For custom condition
    custom_fn: str = ""  # Function name to call


@dataclass(frozen=True)
class Phase:
    """
    A stage within a phased initiative.

    Phases form a linear DAG via depends_on.
    """

    id: PhaseId
    name: str
    gate: Gate
    propositions: tuple[Proposition, ...] = ()
    depends_on: tuple[PhaseId, ...] = ()
    description: str = ""


@dataclass(frozen=True)
class Initiative:
    """
    A validatable body of work.

    May be:
    - Flat: single gate with propositions
    - Phased: multiple phases with dependencies

    Exactly one of (phases, propositions) should be non-empty.
    """

    id: InitiativeId
    name: str
    description: str

    # Structure (one of these)
    phases: tuple[Phase, ...] = ()
    propositions: tuple[Proposition, ...] = ()

    # For flat initiatives
    gate: Gate | None = None

    # Witness integration
    witness_tags: tuple[str, ...] = ("validation",)

    @property
    def is_phased(self) -> bool:
        """Check if this initiative has phases."""
        return len(self.phases) > 0

    def get_all_propositions(self) -> tuple[Proposition, ...]:
        """Get all propositions across all phases."""
        if self.is_phased:
            return tuple(p for phase in self.phases for p in phase.propositions)
        return self.propositions

    def get_proposition(self, prop_id: PropositionId) -> Proposition | None:
        """Get a proposition by ID."""
        for prop in self.get_all_propositions():
            if prop.id == prop_id:
                return prop
        return None

    def get_phase(self, phase_id: PhaseId) -> Phase | None:
        """Get a phase by ID."""
        for phase in self.phases:
            if phase.id == phase_id:
                return phase
        return None


# =============================================================================
# Results
# =============================================================================


@dataclass(frozen=True)
class PropositionResult:
    """Result of validating a single proposition."""

    proposition_id: PropositionId
    value: float | None  # None if not measured
    passed: bool
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Witness integration
    mark_id: MarkId | None = None


@dataclass(frozen=True)
class GateResult:
    """Result of evaluating a gate."""

    gate_id: GateId
    proposition_results: tuple[PropositionResult, ...]
    passed: bool
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Witness integration (decision)
    decision_id: str | None = None

    @property
    def failed_propositions(self) -> tuple[PropositionResult, ...]:
        """Get propositions that failed."""
        return tuple(r for r in self.proposition_results if not r.passed)

    @property
    def passed_propositions(self) -> tuple[PropositionResult, ...]:
        """Get propositions that passed."""
        return tuple(r for r in self.proposition_results if r.passed)


@dataclass(frozen=True)
class ValidationRun:
    """Complete validation run for an initiative."""

    initiative_id: InitiativeId
    phase_id: PhaseId | None  # None for flat initiatives
    gate_result: GateResult
    measurements: dict[str, float]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def passed(self) -> bool:
        """Check if the validation run passed."""
        return self.gate_result.passed


# =============================================================================
# Status & Blockers
# =============================================================================


@dataclass(frozen=True)
class Blocker:
    """A proposition that is blocking progress."""

    initiative_id: InitiativeId
    phase_id: PhaseId | None
    proposition: Proposition
    current_value: float | None
    gap: float | None  # How far from threshold


@dataclass(frozen=True)
class InitiativeStatus:
    """Current status of an initiative."""

    initiative_id: InitiativeId
    current_phase_id: PhaseId | None
    phases_complete: tuple[PhaseId, ...]
    total_phases: int
    blockers: tuple[Blocker, ...]
    last_run: ValidationRun | None

    @property
    def progress_percent(self) -> float:
        """Calculate progress as percentage."""
        if self.total_phases == 0:
            return 100.0 if self.last_run and self.last_run.passed else 0.0
        return (len(self.phases_complete) / self.total_phases) * 100


# =============================================================================
# YAML Loading Utilities
# =============================================================================


def proposition_from_dict(data: dict[str, Any]) -> Proposition:
    """Create a Proposition from YAML dict."""
    return Proposition(
        id=PropositionId(data["id"]),
        description=data.get("description", ""),
        metric=MetricType(data["metric"]),
        threshold=float(data["threshold"]),
        direction=Direction(data["direction"]),
        required=data.get("required", True),
        judgment_required=data.get("judgment_required", False),
        judgment_criteria=data.get("judgment_criteria", ""),
    )


def gate_from_dict(data: dict[str, Any], proposition_ids: tuple[PropositionId, ...] = ()) -> Gate:
    """Create a Gate from YAML dict."""
    return Gate(
        id=GateId(data.get("id", "default_gate")),
        name=data.get("name", ""),
        condition=GateCondition(data.get("condition", "all_required")),
        proposition_ids=proposition_ids,
        quorum_n=data.get("quorum_n", 0),
        custom_fn=data.get("custom_fn", ""),
    )


def phase_from_dict(data: dict[str, Any]) -> Phase:
    """Create a Phase from YAML dict."""
    propositions = tuple(proposition_from_dict(p) for p in data.get("propositions", []))
    prop_ids = tuple(p.id for p in propositions)

    gate_data = data.get("gate", {"id": f"{data['id']}_gate", "condition": "all_required"})
    gate = gate_from_dict(gate_data, prop_ids)

    return Phase(
        id=PhaseId(data["id"]),
        name=data.get("name", ""),
        gate=gate,
        propositions=propositions,
        depends_on=tuple(PhaseId(d) for d in data.get("depends_on", [])),
        description=data.get("description", ""),
    )


def initiative_from_dict(data: dict[str, Any]) -> Initiative:
    """Create an Initiative from YAML dict."""
    # Phased initiative
    if "phases" in data:
        phases = tuple(phase_from_dict(p) for p in data["phases"])
        return Initiative(
            id=InitiativeId(data["id"]),
            name=data.get("name", ""),
            description=data.get("description", ""),
            phases=phases,
            witness_tags=tuple(data.get("witness_tags", ["validation"])),
        )

    # Flat initiative
    propositions = tuple(proposition_from_dict(p) for p in data.get("propositions", []))
    prop_ids = tuple(p.id for p in propositions)

    gate_data = data.get("gate", {"id": f"{data['id']}_gate", "condition": "all_required"})
    gate = gate_from_dict(gate_data, prop_ids)

    return Initiative(
        id=InitiativeId(data["id"]),
        name=data.get("name", ""),
        description=data.get("description", ""),
        propositions=propositions,
        gate=gate,
        witness_tags=tuple(data.get("witness_tags", ["validation"])),
    )
