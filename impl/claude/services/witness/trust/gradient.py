"""
Trust Polynomial Functor.

Amendment E: Trust as Polynomial Functor with Asymmetric Dynamics

This module formalizes trust as a categorical object with:
- 5 trust levels (1-5) as polynomial modes
- Asymmetric dynamics: 3x faster loss than gain
- Weekly decay without activity
- Irreversible action gate (Tier 4 always requires approval)

Philosophy:
    "Trust is earned slowly and lost quickly."
    "High-risk acts require explicit approval regardless of trust."

The polynomial functor maps:
    TrustPoly(y) = sum of (InputType_i x y^Action)

Each trust level has different input types (what can be done autonomously)
but the same output type (Action).

See: plans/enlightened-synthesis/01-theoretical-amendments.md (Amendment E)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# -----------------------------------------------------------------------------
# Trust Level (Polynomial Modes)
# -----------------------------------------------------------------------------


class TrustLevel(IntEnum):
    """
    Trust levels as polynomial modes.

    Each level unlocks more autonomous capabilities.
    Level progression requires demonstrated alignment.
    """

    LEVEL_1 = 1  # Every action requires approval
    LEVEL_2 = 2  # Routine actions auto-approved
    LEVEL_3 = 3  # Most actions auto-approved
    LEVEL_4 = 4  # Only high-impact requires approval
    LEVEL_5 = 5  # Autonomous execution (subject to veto)

    @property
    def description(self) -> str:
        """Human-readable description."""
        return {
            TrustLevel.LEVEL_1: "Novice (all actions need approval)",
            TrustLevel.LEVEL_2: "Beginner (routine auto-approved)",
            TrustLevel.LEVEL_3: "Intermediate (most auto-approved)",
            TrustLevel.LEVEL_4: "Advanced (only high-impact needs approval)",
            TrustLevel.LEVEL_5: "Expert (autonomous, subject to veto)",
        }[self]

    @property
    def auto_approve_up_to_tier(self) -> int:
        """
        Maximum risk tier that can be auto-approved at this level.

        Returns 0 if no auto-approval is allowed.
        Tier 4 NEVER auto-approves (irreversible action gate).
        """
        return {
            TrustLevel.LEVEL_1: 0,  # Nothing auto-approved
            TrustLevel.LEVEL_2: 1,  # Tier 1 only
            TrustLevel.LEVEL_3: 2,  # Tiers 1-2
            TrustLevel.LEVEL_4: 3,  # Tiers 1-3
            TrustLevel.LEVEL_5: 3,  # Tiers 1-3 (Tier 4 never auto)
        }[self]


# -----------------------------------------------------------------------------
# Action (with Risk Tier)
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class Action:
    """
    An action to be evaluated.

    Risk tiers:
    - Tier 1: Trivial, easily reversible (e.g., formatting, comments)
    - Tier 2: Low-risk, reversible (e.g., refactoring, tests)
    - Tier 3: Medium-risk, needs care (e.g., schema changes, API)
    - Tier 4: High-risk, irreversible (e.g., production deploy, delete)
    """

    name: str
    description: str
    risk_tier: int  # 1-4

    def __post_init__(self) -> None:
        if not 1 <= self.risk_tier <= 4:
            raise ValueError(f"risk_tier must be 1-4, got {self.risk_tier}")


# -----------------------------------------------------------------------------
# Trust State (with Asymmetric Dynamics)
# -----------------------------------------------------------------------------


@dataclass
class TrustState:
    """
    Trust state with asymmetric dynamics.

    Key properties:
    - Trust gained slowly (GAIN_RATE per aligned action)
    - Trust lost quickly (LOSS_RATE = 3x GAIN_RATE)
    - Trust decays without activity (DECAY_RATE per week)

    Score is a float in [0, 1] representing progress within a level.
    When score reaches 1.0, level up and reset to 0.
    When score reaches 0.0, level down and reset to 1.0.
    """

    level: TrustLevel = TrustLevel.LEVEL_1
    score: float = 0.0  # 0.0 to 1.0 within level
    aligned_count: int = 0
    misaligned_count: int = 0
    last_activity: float = field(default_factory=time.time)

    # Asymmetric dynamics constants
    GAIN_RATE: float = 0.01  # Trust gained per aligned action
    LOSS_RATE: float = 0.03  # Trust lost per misaligned action (3x faster)
    DECAY_RATE: float = 0.10  # Weekly decay without activity

    def __post_init__(self) -> None:
        # Clamp score to valid range
        self.score = max(0.0, min(1.0, self.score))

    def update_aligned(self) -> "TrustState":
        """
        Update trust after aligned action.

        Gains GAIN_RATE score. Level up at 1.0.

        Returns:
            New TrustState with updated values
        """
        new_score = min(1.0, self.score + self.GAIN_RATE)
        new_level = self.level

        # Level up at score 1.0
        if new_score >= 1.0 and self.level < TrustLevel.LEVEL_5:
            new_level = TrustLevel(self.level + 1)
            new_score = 0.0

        return TrustState(
            level=new_level,
            score=new_score,
            aligned_count=self.aligned_count + 1,
            misaligned_count=self.misaligned_count,
            last_activity=time.time(),
        )

    def update_misaligned(self) -> "TrustState":
        """
        Update trust after misaligned action.

        Loses LOSS_RATE score (3x penalty). Level down at 0.0.

        Returns:
            New TrustState with updated values
        """
        new_score = max(0.0, self.score - self.LOSS_RATE)
        new_level = self.level

        # Level down at score 0.0
        if new_score <= 0.0 and self.level > TrustLevel.LEVEL_1:
            new_level = TrustLevel(self.level - 1)
            new_score = 1.0  # Start at top of lower level

        return TrustState(
            level=new_level,
            score=new_score,
            aligned_count=self.aligned_count,
            misaligned_count=self.misaligned_count + 1,
            last_activity=time.time(),
        )

    def apply_decay(self, current_time: float | None = None) -> "TrustState":
        """
        Apply weekly decay without activity.

        Decays DECAY_RATE per week of inactivity.

        Args:
            current_time: Optional current time (defaults to time.time())

        Returns:
            New TrustState with decay applied
        """
        if current_time is None:
            current_time = time.time()

        seconds_per_week = 7 * 24 * 60 * 60
        weeks_inactive = (current_time - self.last_activity) / seconds_per_week

        if weeks_inactive < 1:
            return self

        decay = self.DECAY_RATE * weeks_inactive
        new_score = max(0.0, self.score - decay)

        new_level = self.level
        if new_score <= 0.0 and self.level > TrustLevel.LEVEL_1:
            new_level = TrustLevel(self.level - 1)
            new_score = 0.5  # Decay to middle of lower level

        return TrustState(
            level=new_level,
            score=new_score,
            aligned_count=self.aligned_count,
            misaligned_count=self.misaligned_count,
            last_activity=self.last_activity,  # Don't update last_activity on decay
        )

    @property
    def alignment_rate(self) -> float:
        """
        Ratio of aligned to total actions.

        Returns 1.0 if no actions taken.
        """
        total = self.aligned_count + self.misaligned_count
        if total == 0:
            return 1.0
        return self.aligned_count / total

    def actions_to_level_up(self) -> int:
        """
        Estimate actions needed to level up.

        Returns -1 if already at max level.
        """
        if self.level >= TrustLevel.LEVEL_5:
            return -1

        remaining_score = 1.0 - self.score
        return int(remaining_score / self.GAIN_RATE) + 1

    def __str__(self) -> str:
        return (
            f"Trust L{self.level.value} ({self.score:.2f}) - "
            f"{self.aligned_count} aligned, {self.misaligned_count} misaligned, "
            f"rate={self.alignment_rate:.1%}"
        )


# -----------------------------------------------------------------------------
# Autonomous Execution Gate
# -----------------------------------------------------------------------------


def can_execute_autonomously(state: TrustState, action: Action) -> bool:
    """
    Determine if action can execute autonomously given trust state.

    Respects irreversible action gate:
    - Tier 4 (irreversible) ALWAYS requires approval
    - Lower tiers gated by trust level

    Args:
        state: Current trust state
        action: Action to evaluate

    Returns:
        True if action can be executed without human approval
    """
    # Tier 4 (irreversible) ALWAYS requires approval
    if action.risk_tier >= 4:
        return False

    # Check against level's auto-approve threshold
    return action.risk_tier <= state.level.auto_approve_up_to_tier


def requires_approval(state: TrustState, action: Action) -> tuple[bool, str]:
    """
    Check if action requires approval and provide reason.

    Args:
        state: Current trust state
        action: Action to evaluate

    Returns:
        Tuple of (requires_approval, reason)
    """
    if action.risk_tier >= 4:
        return True, "Tier 4 (irreversible) actions always require approval"

    if action.risk_tier > state.level.auto_approve_up_to_tier:
        return True, (
            f"Trust level {state.level.value} cannot auto-approve Tier {action.risk_tier} actions"
        )

    return False, "Action can be executed autonomously"


# -----------------------------------------------------------------------------
# Trust Polynomial Input Types
# -----------------------------------------------------------------------------

# These represent the different input types for each trust level
# In the polynomial functor: TrustPoly(y) = sum of (InputType_i x y^Action)


@dataclass(frozen=True)
class ApprovalRequired:
    """Input type for Level 1: requires approval."""

    action: Action
    reasoning: str


@dataclass(frozen=True)
class RoutineApproved:
    """Input type for Level 2: routine is auto-approved."""

    action: Action
    is_routine: bool


@dataclass(frozen=True)
class MostApproved:
    """Input type for Level 3: most is auto-approved."""

    action: Action
    is_high_impact: bool


@dataclass(frozen=True)
class HighImpactOnly:
    """Input type for Level 4: only high-impact needs approval."""

    action: Action


@dataclass(frozen=True)
class Autonomous:
    """Input type for Level 5: autonomous execution."""

    action: Action
    veto_window_open: bool


# -----------------------------------------------------------------------------
# Trust State Factory
# -----------------------------------------------------------------------------


def create_trust_state(
    level: int = 1,
    score: float = 0.0,
    aligned_count: int = 0,
    misaligned_count: int = 0,
) -> TrustState:
    """
    Create a new trust state.

    Args:
        level: Trust level (1-5)
        score: Score within level (0.0-1.0)
        aligned_count: Number of aligned actions
        misaligned_count: Number of misaligned actions

    Returns:
        New TrustState
    """
    return TrustState(
        level=TrustLevel(level),
        score=score,
        aligned_count=aligned_count,
        misaligned_count=misaligned_count,
        last_activity=time.time(),
    )


# -----------------------------------------------------------------------------
# Action Factories
# -----------------------------------------------------------------------------


def trivial_action(name: str, description: str = "") -> Action:
    """Create a Tier 1 (trivial) action."""
    return Action(name=name, description=description or name, risk_tier=1)


def low_risk_action(name: str, description: str = "") -> Action:
    """Create a Tier 2 (low-risk) action."""
    return Action(name=name, description=description or name, risk_tier=2)


def medium_risk_action(name: str, description: str = "") -> Action:
    """Create a Tier 3 (medium-risk) action."""
    return Action(name=name, description=description or name, risk_tier=3)


def high_risk_action(name: str, description: str = "") -> Action:
    """Create a Tier 4 (high-risk, irreversible) action."""
    return Action(name=name, description=description or name, risk_tier=4)


# -----------------------------------------------------------------------------
# Module Exports
# -----------------------------------------------------------------------------

__all__ = [
    # Trust level
    "TrustLevel",
    # Action
    "Action",
    # Trust state
    "TrustState",
    # Gate functions
    "can_execute_autonomously",
    "requires_approval",
    # Input types (polynomial functor modes)
    "ApprovalRequired",
    "RoutineApproved",
    "MostApproved",
    "HighImpactOnly",
    "Autonomous",
    # Factories
    "create_trust_state",
    "trivial_action",
    "low_risk_action",
    "medium_risk_action",
    "high_risk_action",
]
