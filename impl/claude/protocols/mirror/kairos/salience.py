"""
Tension Salience Calculator - Determine urgency at moment t.

Computes how urgent a tension is based on:
- Base severity (intrinsic importance)
- Momentum factor (rate of drift/change)
- Recency weight (fresh tensions prioritized)

From spec/protocols/kairos.md:
  S(t) = base_severity × momentum_factor × recency_weight
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocols.mirror.types import Tension


class TensionSeverity(Enum):
    """
    Intrinsic severity classification for tensions.

    Values represent base severity score (0.0-1.0):
    - CRITICAL: 0.95 (foundational contradiction)
    - HIGH: 0.75 (significant divergence)
    - MEDIUM: 0.50 (notable tension)
    - LOW: 0.20 (minor inconsistency)
    """

    CRITICAL = 0.95
    HIGH = 0.75
    MEDIUM = 0.50
    LOW = 0.20


@dataclass
class TensionSalience:
    """
    Computed salience for a tension at moment t.

    Captures all factors that contribute to urgency.
    """

    tension_id: str
    timestamp: datetime
    base_severity: TensionSeverity
    momentum_factor: float  # 1.0 = stable, >1.5 = accelerating
    recency_weight: float  # 1.0 = fresh, decays exponentially
    salience: float  # Final S(t) score
    age_minutes: float  # Age of tension since detection


class SalienceCalculator:
    """
    Calculates tension salience (urgency) at moment t.

    Combines intrinsic severity with temporal dynamics:
    - Momentum: How fast is the tension changing?
    - Recency: How fresh is the tension?

    More momentum + fresher = higher salience.
    """

    def __init__(
        self,
        recency_half_life: timedelta = timedelta(hours=24),
        momentum_threshold: float = 1.5,
    ):
        """
        Initialize salience calculator.

        Args:
            recency_half_life: Time for recency weight to decay to 50%
            momentum_threshold: Momentum above this is "accelerating"
        """
        self.recency_half_life = recency_half_life
        self.momentum_threshold = momentum_threshold

    def compute_salience(
        self,
        tension: Tension,
        momentum_factor: float,
        detected_at: datetime | None = None,
    ) -> TensionSalience:
        """
        Compute salience for a tension at current moment.

        Args:
            tension: The tension to evaluate
            momentum_factor: Semantic drift velocity from SemanticMomentumTracker
            detected_at: When tension was first detected (defaults to now)

        Returns:
            TensionSalience with computed urgency score
        """
        now = datetime.now()
        detected_at = detected_at or now

        # Determine base severity
        severity = self._classify_severity(tension)

        # Compute recency weight (exponential decay)
        age = now - detected_at
        recency = self._compute_recency_weight(age)

        # Compute final salience
        salience = severity.value * momentum_factor * recency

        return TensionSalience(
            tension_id=tension.id,
            timestamp=now,
            base_severity=severity,
            momentum_factor=momentum_factor,
            recency_weight=recency,
            salience=salience,
            age_minutes=age.total_seconds() / 60,
        )

    def _classify_severity(self, tension: Tension) -> TensionSeverity:
        """
        Classify tension severity based on type and context.

        Heuristics (can be refined):
        - FUNDAMENTAL tensions → CRITICAL
        - OUTDATED with high drift → HIGH
        - BEHAVIORAL → MEDIUM
        - ASPIRATIONAL → LOW (often expected)
        - CONTEXTUAL → MEDIUM
        """
        from protocols.mirror.types import TensionType

        # Map tension types to severity
        severity_map = {
            TensionType.FUNDAMENTAL: TensionSeverity.CRITICAL,
            TensionType.OUTDATED: TensionSeverity.HIGH,
            TensionType.BEHAVIORAL: TensionSeverity.MEDIUM,
            TensionType.CONTEXTUAL: TensionSeverity.MEDIUM,
            TensionType.ASPIRATIONAL: TensionSeverity.LOW,
        }

        return severity_map.get(tension.tension_type, TensionSeverity.MEDIUM)

    def _compute_recency_weight(self, age: timedelta) -> float:
        """
        Compute exponential decay weight based on age.

        Uses half-life formula:
            weight(t) = 2^(-t / half_life)

        Examples with 24h half-life:
        - 0 hours: 1.0
        - 24 hours: 0.5
        - 48 hours: 0.25
        - 72 hours: 0.125
        """
        age_hours = age.total_seconds() / 3600
        half_life_hours = self.recency_half_life.total_seconds() / 3600

        return 2.0 ** (-age_hours / half_life_hours)

    def is_accelerating(self, salience: TensionSalience) -> bool:
        """
        Check if tension is rapidly accelerating.

        Used for emergency override decisions.
        """
        return salience.momentum_factor > self.momentum_threshold

    def estimate_momentum_from_tension(self, tension: Tension) -> float:
        """
        Estimate momentum when SemanticMomentumTracker unavailable.

        Uses simple heuristics based on tension mode:
        - TEMPORAL tensions suggest drift → higher momentum
        - LOGICAL/EMPIRICAL are more stable
        """
        from protocols.mirror.types import TensionMode

        # Default momentum estimates by mode
        momentum_estimates = {
            TensionMode.TEMPORAL: 1.8,  # Drift implies momentum
            TensionMode.PRAGMATIC: 1.5,  # Actions create momentum
            TensionMode.EMPIRICAL: 1.2,  # Evidence is somewhat stable
            TensionMode.LOGICAL: 1.0,  # Logic is stable
        }

        return momentum_estimates.get(tension.mode, 1.0)
