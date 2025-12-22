"""
DisgustVeto: The Absolute Veto Mechanism.

The Disgust Veto (from 2025-12-21-symmetric-supersession.md):
    The somatic disgust signal is the ultimate veto. It is:
    - Phenomenological (felt, not reasoned)
    - Non-negotiable (cannot be argued away)
    - Ethical floor (minimum standard)
    - Aesthetic minimum (curdles beauty)

When Kent feels disgust at a proposal:
    - The proposal is rejected
    - No amount of evidence overrides this
    - The system must find another path

This is NOT:
    - Discomfort (can be worked through)
    - Disagreement (can be resolved)
    - Unfamiliarity (can be adapted to)

This IS:
    - Visceral wrongness
    - Ethical violation
    - Aesthetic failure

Philosophy:
    "Ethics is part of beauty. Ethical violations curdle beauty—
    they are aesthetic failures, not separate failures."

See: brainstorming/2025-12-21-symmetric-supersession.md
See: brainstorming/2025-12-21-agent-as-witness.md (The Felt Sense Is The Arbiter)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Awaitable, Callable

from .types import Synthesis

# =============================================================================
# Veto Source
# =============================================================================


class VetoSource(Enum):
    """
    How the veto was triggered.

    Phase 0: Only EXPLICIT is supported.
    Future phases may infer disgust from behavioral patterns.
    """

    EXPLICIT = "explicit"  # Kent explicitly said "disgust"
    INFERRED = "inferred"  # System inferred from behavior (future)
    TIMEOUT = "timeout"  # No response interpreted as rejection (future)


# =============================================================================
# DisgustSignal
# =============================================================================


@dataclass
class DisgustSignal:
    """
    A disgust signal from Kent.

    This is phenomenological—it cannot be argued away.
    The system can only observe and respect it.

    Intensity scale:
        0.0 = mild discomfort (not a veto)
        0.5 = moderate concern (borderline)
        0.7+ = visceral rejection (absolute veto)
        1.0 = maximum disgust

    The threshold for veto is 0.7 (configurable).
    Below this, the signal is informational but not blocking.
    """

    timestamp: datetime
    source: VetoSource
    reason: str | None
    intensity: float = 1.0  # 0.0 = mild discomfort, 1.0 = visceral rejection
    veto_threshold: float = 0.7

    @property
    def is_veto(self) -> bool:
        """Strong disgust is absolute veto."""
        return self.intensity >= self.veto_threshold

    @property
    def is_warning(self) -> bool:
        """Moderate disgust is a warning but not a veto."""
        return 0.3 <= self.intensity < self.veto_threshold

    def __repr__(self) -> str:
        status = "VETO" if self.is_veto else "WARNING" if self.is_warning else "mild"
        return f"DisgustSignal({status}, intensity={self.intensity:.2f})"


# =============================================================================
# DisgustVeto
# =============================================================================


class DisgustVeto:
    """
    The disgust veto mechanism.

    Phase 0: Simple explicit veto.
    Future phases: Inferred from patterns, somatic signals.

    The disgust veto embodies the Ethical principle:
        "Kent's somatic disgust is an absolute veto.
        It cannot be argued away or evidence'd away.
        It is the ethical floor beneath which no decision may fall."

    Usage:
        >>> veto = DisgustVeto()
        >>> signal = veto.explicit_veto("This feels wrong at a visceral level")
        >>> if signal.is_veto:
        ...     result = await engine.apply_veto(result, signal.reason)
    """

    def __init__(self, veto_threshold: float = 0.7):
        """
        Initialize the veto mechanism.

        Args:
            veto_threshold: Intensity level that triggers absolute veto (0.0-1.0)
        """
        self.veto_threshold = veto_threshold
        self._pending_checks: dict[str, Synthesis] = {}

    async def check(
        self,
        synthesis: Synthesis,
        *,
        callback: Callable[[Synthesis], Awaitable[bool]] | None = None,
    ) -> DisgustSignal | None:
        """
        Check if Kent feels disgust at this synthesis.

        Phase 0: Requires explicit callback from Kent.
        Returns None if no disgust, DisgustSignal if disgust detected.

        Args:
            synthesis: The proposed synthesis to check
            callback: Async function that returns True if Kent feels disgust

        Returns:
            DisgustSignal if disgust detected, None otherwise
        """
        if callback is None:
            # No way to check—assume no disgust
            # (In production, this would be a UI prompt)
            return None

        feels_disgust = await callback(synthesis)

        if feels_disgust:
            return DisgustSignal(
                timestamp=datetime.utcnow(),
                source=VetoSource.EXPLICIT,
                reason="Kent indicated disgust",
                intensity=1.0,
                veto_threshold=self.veto_threshold,
            )

        return None

    def explicit_veto(
        self,
        reason: str,
        intensity: float = 1.0,
    ) -> DisgustSignal:
        """
        Kent explicitly vetoes.

        This is the primary mechanism in Phase 0. Kent directly
        indicates that a proposal triggers disgust.

        Args:
            reason: Why this triggers disgust
            intensity: How strong the disgust is (0.0-1.0, default 1.0)

        Returns:
            DisgustSignal representing the veto
        """
        return DisgustSignal(
            timestamp=datetime.utcnow(),
            source=VetoSource.EXPLICIT,
            reason=reason,
            intensity=min(1.0, max(0.0, intensity)),  # Clamp to [0, 1]
            veto_threshold=self.veto_threshold,
        )

    def warning(
        self,
        reason: str,
        intensity: float = 0.5,
    ) -> DisgustSignal:
        """
        Kent registers discomfort but not full disgust.

        This is below the veto threshold but signals concern.
        Future phases may accumulate warnings into vetoes.

        Args:
            reason: Why this causes discomfort
            intensity: How strong the discomfort is (default 0.5)

        Returns:
            DisgustSignal representing the warning
        """
        return DisgustSignal(
            timestamp=datetime.utcnow(),
            source=VetoSource.EXPLICIT,
            reason=reason,
            intensity=min(self.veto_threshold - 0.01, max(0.0, intensity)),
            veto_threshold=self.veto_threshold,
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "VetoSource",
    "DisgustSignal",
    "DisgustVeto",
]
