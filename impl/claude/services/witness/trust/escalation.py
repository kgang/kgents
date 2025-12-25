"""
Escalation Criteria: Rules for Trust Level Transitions.

Each level transition has specific criteria:
- L0 → L1: 100+ observations, 24h active, <1% false positive rate
- L1 → L2: 100+ successful operations, <5% failure rate, 3+ operation types
- L2 → L3: 50+ suggestions, >90% acceptance, 7+ days at L2, 5+ suggestion types

Philosophy:
    "Trust is based on outcomes, not inputs."
    A daemon that consistently observes correctly earns trust,
    regardless of how complex the observations were.

See: plans/kgentsd-trust-system.md
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Generic, TypeVar

from agents.t.truth_functor import PolicyTrace, TraceEntry, ProbeState, ProbeAction, ConstitutionalScore
from services.witness.polynomial import TrustLevel

if TYPE_CHECKING:
    pass

# Type variable for stats types
StatsT = TypeVar("StatsT", "ObservationStats", "OperationStats", "SuggestionStats")


# =============================================================================
# Observation Stats (Input to Criteria)
# =============================================================================


@dataclass
class ObservationStats:
    """Statistics for L0 → L1 escalation."""

    hours_observing: float = 0.0
    total_observations: int = 0
    false_positives: int = 0

    @property
    def false_positive_rate(self) -> float:
        """Calculate false positive rate."""
        if self.total_observations == 0:
            return 0.0
        return self.false_positives / self.total_observations


@dataclass
class OperationStats:
    """Statistics for L1 → L2 escalation."""

    total_operations: int = 0
    failed_operations: int = 0
    unique_operation_types: int = 0

    @property
    def failure_rate(self) -> float:
        """Calculate failure rate."""
        if self.total_operations == 0:
            return 0.0
        return self.failed_operations / self.total_operations


@dataclass
class SuggestionStats:
    """Statistics for L2 → L3 escalation."""

    total_suggestions: int = 0
    confirmed_suggestions: int = 0
    unique_suggestion_types: int = 0
    days_at_level2: int = 0

    @property
    def acceptance_rate(self) -> float:
        """Calculate acceptance rate."""
        if self.total_suggestions == 0:
            return 0.0
        return self.confirmed_suggestions / self.total_suggestions


# =============================================================================
# Escalation Result
# =============================================================================


@dataclass
class EscalationResult:
    """Result of an escalation check."""

    is_met: bool
    from_level: TrustLevel
    to_level: TrustLevel
    reason: str
    criteria_details: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    trace: PolicyTrace[bool] | None = None  # PolicyTrace for security-critical decision

    @property
    def progress_summary(self) -> str:
        """Human-readable progress summary."""
        if self.is_met:
            return f"Ready for {self.to_level.description}"
        return self.reason


# =============================================================================
# Escalation Criteria (Abstract)
# =============================================================================


class EscalationCriteria(ABC, Generic[StatsT]):
    """Abstract base for escalation criteria."""

    @property
    @abstractmethod
    def from_level(self) -> TrustLevel:
        """Source trust level."""
        ...

    @property
    @abstractmethod
    def to_level(self) -> TrustLevel:
        """Target trust level."""
        ...

    @abstractmethod
    def check(self, stats: StatsT) -> EscalationResult:
        """Check if escalation criteria are met."""
        ...


# =============================================================================
# Level 1 Criteria (L0 → L1)
# =============================================================================


@dataclass
class Level1Criteria(EscalationCriteria[ObservationStats]):
    """
    Criteria for L0 → L1 escalation.

    Requirements:
    - Minimum 24 hours of observation
    - Minimum 100 observations
    - False positive rate < 1%
    """

    min_hours: int = 24
    min_observations: int = 100
    max_false_positive_rate: float = 0.01  # 1%

    @property
    def from_level(self) -> TrustLevel:
        return TrustLevel.READ_ONLY

    @property
    def to_level(self) -> TrustLevel:
        return TrustLevel.BOUNDED

    def check(self, stats: ObservationStats) -> EscalationResult:
        """Check if L1 criteria are met."""
        criteria_details = {}
        reasons = []

        # Initialize PolicyTrace for security-critical trust escalation
        trace = PolicyTrace(value=False)
        initial_state = ProbeState(
            phase="evaluating_L0_to_L1",
            observations=(
                f"hours={stats.hours_observing}",
                f"total_obs={stats.total_observations}",
                f"false_positives={stats.false_positives}"
            )
        )

        # Check hours
        hours_met = stats.hours_observing >= self.min_hours
        criteria_details["hours"] = f"{stats.hours_observing:.1f}/{self.min_hours}h"
        if not hours_met:
            reasons.append(f"Need {self.min_hours - stats.hours_observing:.1f} more hours")

        trace.append(TraceEntry(
            state_before=initial_state,
            action=ProbeAction("check_hours", (stats.hours_observing, self.min_hours)),
            state_after=initial_state.with_observation(f"hours_met={hours_met}"),
            reward=ConstitutionalScore(
                ethical=1.0 if hours_met else 0.3,  # Ethical: gradual trust buildup
                composable=0.8,  # Composable: criterion is independent
                tasteful=1.0  # Tasteful: clear threshold
            ),
            reasoning=f"Hours criterion: {stats.hours_observing:.1f}h {'≥' if hours_met else '<'} {self.min_hours}h"
        ))

        # Check observations
        obs_met = stats.total_observations >= self.min_observations
        criteria_details["observations"] = f"{stats.total_observations}/{self.min_observations}"
        if not obs_met:
            reasons.append(
                f"Need {self.min_observations - stats.total_observations} more observations"
            )

        trace.append(TraceEntry(
            state_before=initial_state,
            action=ProbeAction("check_observations", (stats.total_observations, self.min_observations)),
            state_after=initial_state.with_observation(f"obs_met={obs_met}"),
            reward=ConstitutionalScore(
                ethical=1.0 if obs_met else 0.3,  # Ethical: sufficient evidence
                composable=0.8,
                tasteful=1.0
            ),
            reasoning=f"Observations criterion: {stats.total_observations} {'≥' if obs_met else '<'} {self.min_observations}"
        ))

        # Check false positive rate
        fpr_met = stats.false_positive_rate <= self.max_false_positive_rate
        criteria_details["false_positive_rate"] = f"{stats.false_positive_rate:.1%}"
        if not fpr_met:
            reasons.append(
                f"False positive rate {stats.false_positive_rate:.1%} > {self.max_false_positive_rate:.1%}"
            )

        trace.append(TraceEntry(
            state_before=initial_state,
            action=ProbeAction("check_false_positive_rate", (stats.false_positive_rate, self.max_false_positive_rate)),
            state_after=initial_state.with_observation(f"fpr_met={fpr_met}"),
            reward=ConstitutionalScore(
                ethical=1.0 if fpr_met else 0.0,  # Ethical: accuracy is CRITICAL for trust
                composable=0.8,
                tasteful=1.0
            ),
            reasoning=f"False positive rate: {stats.false_positive_rate:.1%} {'≤' if fpr_met else '>'} {self.max_false_positive_rate:.1%}"
        ))

        is_met = hours_met and obs_met and fpr_met
        reason = "Criteria met" if is_met else "; ".join(reasons)

        # Final verdict trace entry
        final_state = ProbeState(
            phase="L0_to_L1_verdict",
            observations=(f"verdict={is_met}",)
        )
        trace.append(TraceEntry(
            state_before=initial_state,
            action=ProbeAction("render_verdict", (is_met,)),
            state_after=final_state,
            reward=ConstitutionalScore(
                ethical=1.0 if is_met else 0.5,  # Ethical: clear decision
                composable=1.0,  # Composable: produces clear yes/no
                tasteful=1.0
            ),
            reasoning=f"Final verdict: {'ESCALATE to L1' if is_met else 'DENY escalation'}"
        ))
        trace.value = is_met

        return EscalationResult(
            is_met=is_met,
            from_level=self.from_level,
            to_level=self.to_level,
            reason=reason,
            criteria_details=criteria_details,
            trace=trace,
        )


# =============================================================================
# Level 2 Criteria (L1 → L2)
# =============================================================================


@dataclass
class Level2Criteria(EscalationCriteria[OperationStats]):
    """
    Criteria for L1 → L2 escalation.

    Requirements:
    - Minimum 100 successful bounded operations
    - Failure rate < 5%
    - At least 3 different operation types
    """

    min_operations: int = 100
    max_failure_rate: float = 0.05  # 5%
    min_operation_types: int = 3

    @property
    def from_level(self) -> TrustLevel:
        return TrustLevel.BOUNDED

    @property
    def to_level(self) -> TrustLevel:
        return TrustLevel.SUGGESTION

    def check(self, stats: OperationStats) -> EscalationResult:
        """Check if L2 criteria are met."""
        criteria_details = {}
        reasons = []

        # Initialize PolicyTrace for security-critical trust escalation
        trace = PolicyTrace(value=False)
        initial_state = ProbeState(
            phase="evaluating_L1_to_L2",
            observations=(
                f"total_ops={stats.total_operations}",
                f"failed_ops={stats.failed_operations}",
                f"op_types={stats.unique_operation_types}"
            )
        )

        # Check operations
        ops_met = stats.total_operations >= self.min_operations
        criteria_details["operations"] = f"{stats.total_operations}/{self.min_operations}"
        if not ops_met:
            reasons.append(f"Need {self.min_operations - stats.total_operations} more operations")

        trace.append(TraceEntry(
            state_before=initial_state,
            action=ProbeAction("check_operations", (stats.total_operations, self.min_operations)),
            state_after=initial_state.with_observation(f"ops_met={ops_met}"),
            reward=ConstitutionalScore(
                ethical=1.0 if ops_met else 0.3,  # Ethical: proven capability
                composable=0.8,
                tasteful=1.0
            ),
            reasoning=f"Operations criterion: {stats.total_operations} {'≥' if ops_met else '<'} {self.min_operations}"
        ))

        # Check failure rate
        fr_met = stats.failure_rate <= self.max_failure_rate
        criteria_details["failure_rate"] = f"{stats.failure_rate:.1%}"
        if not fr_met:
            reasons.append(f"Failure rate {stats.failure_rate:.1%} > {self.max_failure_rate:.1%}")

        trace.append(TraceEntry(
            state_before=initial_state,
            action=ProbeAction("check_failure_rate", (stats.failure_rate, self.max_failure_rate)),
            state_after=initial_state.with_observation(f"fr_met={fr_met}"),
            reward=ConstitutionalScore(
                ethical=1.0 if fr_met else 0.0,  # Ethical: reliability is CRITICAL
                composable=0.8,
                tasteful=1.0
            ),
            reasoning=f"Failure rate: {stats.failure_rate:.1%} {'≤' if fr_met else '>'} {self.max_failure_rate:.1%}"
        ))

        # Check operation types
        types_met = stats.unique_operation_types >= self.min_operation_types
        criteria_details["operation_types"] = (
            f"{stats.unique_operation_types}/{self.min_operation_types}"
        )
        if not types_met:
            reasons.append(
                f"Need {self.min_operation_types - stats.unique_operation_types} more operation types"
            )

        trace.append(TraceEntry(
            state_before=initial_state,
            action=ProbeAction("check_operation_types", (stats.unique_operation_types, self.min_operation_types)),
            state_after=initial_state.with_observation(f"types_met={types_met}"),
            reward=ConstitutionalScore(
                ethical=0.8,  # Ethical: diversity shows adaptability
                composable=1.0 if types_met else 0.5,  # Composable: diverse ops can compose better
                tasteful=1.0
            ),
            reasoning=f"Operation types: {stats.unique_operation_types} {'≥' if types_met else '<'} {self.min_operation_types}"
        ))

        is_met = ops_met and fr_met and types_met
        reason = "Criteria met" if is_met else "; ".join(reasons)

        # Final verdict trace entry
        final_state = ProbeState(
            phase="L1_to_L2_verdict",
            observations=(f"verdict={is_met}",)
        )
        trace.append(TraceEntry(
            state_before=initial_state,
            action=ProbeAction("render_verdict", (is_met,)),
            state_after=final_state,
            reward=ConstitutionalScore(
                ethical=1.0 if is_met else 0.5,
                composable=1.0,
                tasteful=1.0
            ),
            reasoning=f"Final verdict: {'ESCALATE to L2' if is_met else 'DENY escalation'}"
        ))
        trace.value = is_met

        return EscalationResult(
            is_met=is_met,
            from_level=self.from_level,
            to_level=self.to_level,
            reason=reason,
            criteria_details=criteria_details,
            trace=trace,
        )


# =============================================================================
# Level 3 Criteria (L2 → L3)
# =============================================================================


@dataclass
class Level3Criteria(EscalationCriteria[SuggestionStats]):
    """
    Criteria for L2 → L3 escalation.

    Requirements:
    - Minimum 50 confirmed suggestions
    - Acceptance rate > 90%
    - At least 5 different suggestion types
    - Minimum 7 days at Level 2
    """

    min_suggestions: int = 50
    min_acceptance_rate: float = 0.90  # 90%
    min_suggestion_types: int = 5
    min_days_at_level2: int = 7

    @property
    def from_level(self) -> TrustLevel:
        return TrustLevel.SUGGESTION

    @property
    def to_level(self) -> TrustLevel:
        return TrustLevel.AUTONOMOUS

    def check(self, stats: SuggestionStats) -> EscalationResult:
        """Check if L3 criteria are met."""
        criteria_details = {}
        reasons = []

        # Initialize PolicyTrace for security-critical trust escalation
        trace = PolicyTrace(value=False)
        initial_state = ProbeState(
            phase="evaluating_L2_to_L3",
            observations=(
                f"total_suggestions={stats.total_suggestions}",
                f"confirmed={stats.confirmed_suggestions}",
                f"suggestion_types={stats.unique_suggestion_types}",
                f"days_at_L2={stats.days_at_level2}"
            )
        )

        # Check days at L2
        days_met = stats.days_at_level2 >= self.min_days_at_level2
        criteria_details["days_at_l2"] = f"{stats.days_at_level2}/{self.min_days_at_level2}d"
        if not days_met:
            reasons.append(
                f"Need {self.min_days_at_level2 - stats.days_at_level2} more days at Level 2"
            )

        trace.append(TraceEntry(
            state_before=initial_state,
            action=ProbeAction("check_days_at_L2", (stats.days_at_level2, self.min_days_at_level2)),
            state_after=initial_state.with_observation(f"days_met={days_met}"),
            reward=ConstitutionalScore(
                ethical=1.0 if days_met else 0.3,  # Ethical: time proves stability
                composable=0.8,
                tasteful=1.0
            ),
            reasoning=f"Days at L2: {stats.days_at_level2} {'≥' if days_met else '<'} {self.min_days_at_level2}"
        ))

        # Check suggestions
        sug_met = stats.total_suggestions >= self.min_suggestions
        criteria_details["suggestions"] = f"{stats.total_suggestions}/{self.min_suggestions}"
        if not sug_met:
            reasons.append(
                f"Need {self.min_suggestions - stats.total_suggestions} more suggestions"
            )

        trace.append(TraceEntry(
            state_before=initial_state,
            action=ProbeAction("check_suggestions", (stats.total_suggestions, self.min_suggestions)),
            state_after=initial_state.with_observation(f"sug_met={sug_met}"),
            reward=ConstitutionalScore(
                ethical=1.0 if sug_met else 0.3,  # Ethical: sufficient sample
                composable=0.8,
                tasteful=1.0
            ),
            reasoning=f"Suggestions criterion: {stats.total_suggestions} {'≥' if sug_met else '<'} {self.min_suggestions}"
        ))

        # Check acceptance rate
        ar_met = stats.acceptance_rate >= self.min_acceptance_rate
        criteria_details["acceptance_rate"] = f"{stats.acceptance_rate:.1%}"
        if not ar_met:
            reasons.append(
                f"Acceptance rate {stats.acceptance_rate:.1%} < {self.min_acceptance_rate:.1%}"
            )

        trace.append(TraceEntry(
            state_before=initial_state,
            action=ProbeAction("check_acceptance_rate", (stats.acceptance_rate, self.min_acceptance_rate)),
            state_after=initial_state.with_observation(f"ar_met={ar_met}"),
            reward=ConstitutionalScore(
                ethical=1.0 if ar_met else 0.0,  # Ethical: high acceptance = trusted judgment
                composable=0.8,
                joy_inducing=1.0 if ar_met else 0.3  # Joy: good suggestions delight users
            ),
            reasoning=f"Acceptance rate: {stats.acceptance_rate:.1%} {'≥' if ar_met else '<'} {self.min_acceptance_rate:.1%}"
        ))

        # Check suggestion types
        types_met = stats.unique_suggestion_types >= self.min_suggestion_types
        criteria_details["suggestion_types"] = (
            f"{stats.unique_suggestion_types}/{self.min_suggestion_types}"
        )
        if not types_met:
            reasons.append(
                f"Need {self.min_suggestion_types - stats.unique_suggestion_types} more suggestion types"
            )

        trace.append(TraceEntry(
            state_before=initial_state,
            action=ProbeAction("check_suggestion_types", (stats.unique_suggestion_types, self.min_suggestion_types)),
            state_after=initial_state.with_observation(f"types_met={types_met}"),
            reward=ConstitutionalScore(
                ethical=0.8,
                composable=1.0 if types_met else 0.5,  # Composable: diverse suggestions compose better
                curated=1.0 if types_met else 0.5  # Curated: variety shows sophistication
            ),
            reasoning=f"Suggestion types: {stats.unique_suggestion_types} {'≥' if types_met else '<'} {self.min_suggestion_types}"
        ))

        is_met = days_met and sug_met and ar_met and types_met
        reason = "Criteria met" if is_met else "; ".join(reasons)

        # Final verdict trace entry
        final_state = ProbeState(
            phase="L2_to_L3_verdict",
            observations=(f"verdict={is_met}",)
        )
        trace.append(TraceEntry(
            state_before=initial_state,
            action=ProbeAction("render_verdict", (is_met,)),
            state_after=final_state,
            reward=ConstitutionalScore(
                ethical=1.0 if is_met else 0.5,
                composable=1.0,
                tasteful=1.0
            ),
            reasoning=f"Final verdict: {'ESCALATE to L3 (AUTONOMOUS)' if is_met else 'DENY escalation'}"
        ))
        trace.value = is_met

        return EscalationResult(
            is_met=is_met,
            from_level=self.from_level,
            to_level=self.to_level,
            reason=reason,
            criteria_details=criteria_details,
            trace=trace,
        )


# =============================================================================
# Convenience Functions
# =============================================================================


def check_escalation(
    current_level: TrustLevel,
    stats: ObservationStats | OperationStats | SuggestionStats,
) -> EscalationResult | None:
    """
    Check if escalation is possible from current level.

    Args:
        current_level: Current trust level
        stats: Statistics for the escalation check

    Returns:
        EscalationResult if escalation is possible, None if at max level
    """
    if current_level == TrustLevel.READ_ONLY:
        if isinstance(stats, ObservationStats):
            return Level1Criteria().check(stats)
    elif current_level == TrustLevel.BOUNDED:
        if isinstance(stats, OperationStats):
            return Level2Criteria().check(stats)
    elif current_level == TrustLevel.SUGGESTION:
        if isinstance(stats, SuggestionStats):
            return Level3Criteria().check(stats)

    # Already at max level or wrong stats type
    return None


__all__ = [
    # Stats
    "ObservationStats",
    "OperationStats",
    "SuggestionStats",
    # Results
    "EscalationResult",
    # Criteria
    "EscalationCriteria",
    "Level1Criteria",
    "Level2Criteria",
    "Level3Criteria",
    # Functions
    "check_escalation",
]
