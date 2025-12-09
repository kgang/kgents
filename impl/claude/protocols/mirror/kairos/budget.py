"""
Entropy Budget - Rate limiting to prevent notification fatigue.

Limits maximum intervention frequency over time windows to maintain
user trust and prevent the Mirror from becoming a nagging presence.

From spec/protocols/kairos.md:
  Budget Levels:
  - LOW: 1 intervention per 4 hours (minimalist)
  - MEDIUM: 3 interventions per 2 hours (balanced) [DEFAULT]
  - HIGH: 6 interventions per hour (attentive)
  - UNLIMITED: No limit (development/debugging)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class BudgetLevel(Enum):
    """
    Predefined intervention budget levels.

    Each level specifies:
    - window: Observation time window
    - max_interventions: Maximum surfacings per window
    - recharge_rate: Budget recovery per minute
    """

    LOW = ("low", timedelta(hours=4), 1, 0.05)
    MEDIUM = ("medium", timedelta(hours=2), 3, 0.1)
    HIGH = ("high", timedelta(hours=1), 6, 0.2)
    UNLIMITED = ("unlimited", timedelta(hours=1), 999, 1.0)

    def __init__(
        self,
        label: str,
        window: timedelta,
        max_interventions: int,
        recharge_rate: float,
    ):
        self.label = label
        self.window = window
        self.max_interventions = max_interventions
        self.recharge_rate = recharge_rate


@dataclass
class InterventionLog:
    """Record of a single intervention (tension surfacing)."""

    timestamp: datetime
    tension_id: str
    severity: str
    benefit: float
    user_response: str | None = None  # "dismissed", "engaged", "resolved"


@dataclass
class EntropyBudget:
    """
    Tracks and enforces intervention rate limits.

    Prevents notification fatigue by limiting how often tensions
    can be surfaced within a time window.

    Budget recharges over time, allowing for bursty interventions
    followed by quiet periods.
    """

    level: BudgetLevel
    current_count: int = 0
    interventions: list[InterventionLog] = field(default_factory=list)
    last_recharge: datetime = field(default_factory=datetime.now)

    def can_intervene(self) -> bool:
        """
        Check if budget available for intervention.

        Returns:
            True if intervention allowed, False if budget exhausted
        """
        # Unlimited budget always allows
        if self.level == BudgetLevel.UNLIMITED:
            return True

        # Clean up old interventions outside window
        self._prune_old_interventions()

        # Check current count against max
        return self.current_count < self.level.max_interventions

    def consume(self, tension_id: str, severity: str, benefit: float) -> bool:
        """
        Attempt to consume budget for an intervention.

        Args:
            tension_id: ID of tension being surfaced
            severity: Severity level (for logging)
            benefit: Computed benefit score (for logging)

        Returns:
            True if budget consumed, False if exhausted
        """
        if not self.can_intervene():
            return False

        # Record intervention
        now = datetime.now()
        log = InterventionLog(
            timestamp=now,
            tension_id=tension_id,
            severity=severity,
            benefit=benefit,
        )

        self.interventions.append(log)
        self.current_count += 1

        return True

    def recharge(self, elapsed: timedelta | None = None) -> int:
        """
        Recover budget based on elapsed time.

        Args:
            elapsed: Time elapsed (defaults to time since last recharge)

        Returns:
            Amount of budget recovered
        """
        if elapsed is None:
            now = datetime.now()
            elapsed = now - self.last_recharge
            self.last_recharge = now

        elapsed_minutes = elapsed.total_seconds() / 60
        recovered = int(elapsed_minutes * self.level.recharge_rate)

        if recovered > 0:
            self.current_count = max(0, self.current_count - recovered)

        return recovered

    def record_user_response(self, tension_id: str, response: str):
        """
        Record user's response to an intervention.

        Args:
            tension_id: ID of tension that was surfaced
            response: One of "dismissed", "engaged", "resolved"
        """
        for log in reversed(self.interventions):
            if log.tension_id == tension_id:
                log.user_response = response
                break

    def get_recent_interventions(
        self, window: timedelta | None = None
    ) -> list[InterventionLog]:
        """
        Get interventions within time window.

        Args:
            window: Time window (defaults to budget level's window)

        Returns:
            List of recent interventions
        """
        window = window or self.level.window
        cutoff = datetime.now() - window

        return [log for log in self.interventions if log.timestamp >= cutoff]

    def get_engagement_rate(self, window: timedelta | None = None) -> float:
        """
        Compute engagement rate (fraction of interventions user engaged with).

        Used for Phase 3b: learning optimal timing.

        Args:
            window: Time window to analyze

        Returns:
            Engagement rate (0.0-1.0), or 0.0 if no interventions
        """
        recent = self.get_recent_interventions(window)
        if not recent:
            return 0.0

        # Count interventions with known responses
        responded = [log for log in recent if log.user_response is not None]
        if not responded:
            return 0.0  # Unknown, assume neutral

        # Count engaged/resolved (positive responses)
        engaged = [
            log for log in responded if log.user_response in ("engaged", "resolved")
        ]

        return len(engaged) / len(responded)

    def get_dismissal_rate(self, window: timedelta | None = None) -> float:
        """
        Compute dismissal rate (fraction of interventions dismissed).

        High dismissal rate suggests poor timing or too frequent interventions.

        Args:
            window: Time window to analyze

        Returns:
            Dismissal rate (0.0-1.0)
        """
        return 1.0 - self.get_engagement_rate(window)

    def _prune_old_interventions(self):
        """Remove interventions outside the budget window."""
        cutoff = datetime.now() - self.level.window
        self.interventions = [
            log for log in self.interventions if log.timestamp >= cutoff
        ]
        self.current_count = len(self.interventions)

    def get_status(self) -> dict:
        """
        Get current budget status for display.

        Returns:
            Dictionary with budget metrics
        """
        self._prune_old_interventions()

        return {
            "level": self.level.label,
            "window": str(self.level.window),
            "max_interventions": self.level.max_interventions,
            "current_count": self.current_count,
            "available": self.level.max_interventions - self.current_count,
            "can_intervene": self.can_intervene(),
            "recent_interventions": len(self.get_recent_interventions()),
            "engagement_rate": self.get_engagement_rate(),
        }
