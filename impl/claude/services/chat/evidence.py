"""
Chat Evidence: Bayesian Evidence Accumulation for Chat Turns.

Implements ASHC-inspired Bayesian evidence tracking per conversation turn.
Uses BetaPrior for confidence modeling and adaptive stopping criteria.

Philosophy:
    "Evidence accumulates. Confidence emerges. Stopping is principled."

See: spec/protocols/chat-web.md §2.4, §3.3
See: spec/protocols/ASHC-agentic-self-hosting-compiler.md
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


def generate_evidence_id() -> str:
    """Generate unique evidence ID."""
    return f"chat-evd-{uuid4().hex[:12]}"


# =============================================================================
# BetaPrior: Bayesian Prior Distribution
# =============================================================================


@dataclass(frozen=True)
class BetaPrior:
    """
    Beta distribution prior for Bayesian evidence.

    Represents belief about success probability using Beta(alpha, beta).
    - alpha: successes observed + 1
    - beta: failures observed + 1

    The posterior mean is: alpha / (alpha + beta)

    Example:
        >>> prior = BetaPrior(1, 1)  # Uniform prior (no observations)
        >>> prior.mean()
        0.5
        >>> updated = prior.update(success=True)
        >>> updated.mean()
        0.6666...  # 2/3 after 1 success
    """

    alpha: float = 1.0  # Success count + 1
    beta: float = 1.0  # Failure count + 1

    def mean(self) -> float:
        """Expected value (posterior mean)."""
        return self.alpha / (self.alpha + self.beta)

    def variance(self) -> float:
        """Variance of the distribution."""
        a, b = self.alpha, self.beta
        return (a * b) / ((a + b) ** 2 * (a + b + 1))

    def update(self, success: bool) -> BetaPrior:
        """
        Bayesian update with new observation.

        Args:
            success: True if turn succeeded, False otherwise

        Returns:
            New BetaPrior with updated belief
        """
        if success:
            return BetaPrior(self.alpha + 1, self.beta)
        else:
            return BetaPrior(self.alpha, self.beta + 1)

    def confidence(self) -> float:
        """
        Confidence in the estimate.

        Higher total observations = higher confidence.
        Returns value in [0, 1].
        """
        total = self.alpha + self.beta
        # Normalize by max reasonable observations (100)
        return min(1.0, total / 100.0)

    def prob_success_above(self, threshold: float) -> float:
        """
        Probability that success rate > threshold.

        Approximation using normal distribution for large samples.
        For exact computation, would need scipy.stats.beta.cdf.
        """
        mean = self.mean()
        # Simple threshold comparison for now
        # TODO: Replace with proper beta CDF if scipy available
        if mean > threshold:
            return min(0.99, 0.5 + (mean - threshold) * 2)
        else:
            return max(0.01, 0.5 - (threshold - mean) * 2)


# =============================================================================
# StoppingDecision: When to Stop Conversation
# =============================================================================


class StoppingDecision(Enum):
    """
    Adaptive stopping decision for chat turns.

    Based on ASHC's StoppingState but adapted for conversation flow.
    """

    CONTINUE = "continue"  # Keep going, goal not achieved
    STOP = "stop"  # High confidence goal achieved
    USER_OVERRIDE = "user_override"  # User chose to continue despite STOP

    @property
    def should_suggest_stop(self) -> bool:
        """True if we should suggest stopping to user."""
        return self == StoppingDecision.STOP


# =============================================================================
# TurnResult: Result of Single Conversation Turn
# =============================================================================


@dataclass
class TurnResult:
    """
    Result of processing a single chat turn.

    Contains tool execution results and user signals for evidence update.
    """

    # Tool execution
    tools_passed: bool = True
    tools: list[dict[str, Any]] = field(default_factory=list)

    # User signals (reactions, corrections)
    user_corrected: bool = False
    signals: list[dict[str, Any]] = field(default_factory=list)

    # Response content
    response: str = ""

    # Stopping suggestion
    stopping_suggestion: str | None = None


# =============================================================================
# ChatEvidence: Evidence State for Chat Session
# =============================================================================


@dataclass
class ChatEvidence:
    """
    Bayesian evidence accumulation for chat sessions.

    Simplified evidence model for non-spec chat turns. Uses ASHC's
    Bayesian primitives without full chaos testing.

    Philosophy:
        Evidence comes from: tool results, user feedback, claim verification.

    See: spec/protocols/chat-web.md §3.3
    """

    # Identity
    id: str = field(default_factory=generate_evidence_id)

    # Bayesian state
    prior: BetaPrior = field(default_factory=lambda: BetaPrior(1, 1))

    # Tool results
    tools_succeeded: int = 0
    tools_failed: int = 0

    # User signals
    user_signals: list[dict[str, Any]] = field(default_factory=list)

    # ASHC equivalence score (if spec was edited)
    ashc_equivalence: float | None = None

    # Temporal
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def confidence(self) -> float:
        """P(goal_achieved) under posterior."""
        return self.prior.mean()

    @property
    def should_stop(self) -> bool:
        """
        ASHC-style stopping: confidence >= 0.95 or margin reached.

        Stopping criterion: P(success > 0.5) >= 0.95
        """
        return self.prior.prob_success_above(0.5) >= 0.95

    def update(self, turn_result: TurnResult) -> ChatEvidence:
        """
        Update evidence based on turn result.

        Creates new ChatEvidence (immutable pattern like Evidence).

        Args:
            turn_result: Result of the turn

        Returns:
            New ChatEvidence with updated belief
        """
        # Determine turn success
        success = turn_result.tools_passed and not turn_result.user_corrected

        # Bayesian update
        new_prior = self.prior.update(success)

        # Update tool counts
        new_succeeded = self.tools_succeeded + (1 if turn_result.tools_passed else 0)
        new_failed = self.tools_failed + (0 if turn_result.tools_passed else 1)

        return ChatEvidence(
            id=generate_evidence_id(),  # New evidence ID
            prior=new_prior,
            tools_succeeded=new_succeeded,
            tools_failed=new_failed,
            user_signals=self.user_signals + turn_result.signals,
            ashc_equivalence=self.ashc_equivalence,
            created_at=self.created_at,
            updated_at=datetime.now(),
            metadata=self.metadata.copy(),
        )

    def integrate_ashc(self, ashc_evidence: dict[str, Any]) -> ChatEvidence:
        """
        Integrate ASHC evidence from spec compilation.

        Args:
            ashc_evidence: Evidence dict from ASHCHarness

        Returns:
            New ChatEvidence with ASHC integration
        """
        equivalence = ashc_evidence.get("equivalence_score", 0.0)

        return ChatEvidence(
            id=self.id,
            prior=self.prior,
            tools_succeeded=self.tools_succeeded,
            tools_failed=self.tools_failed,
            user_signals=self.user_signals,
            ashc_equivalence=equivalence,
            created_at=self.created_at,
            updated_at=datetime.now(),
            metadata={**self.metadata, "ashc_evidence": ashc_evidence},
        )

    def join_equivalent(self, other: ChatEvidence) -> bool:
        """
        Check if evidence states are equivalent under EvidenceJoin.

        Used for session equivalence checking in fork/merge operations.

        Laws:
            join(e, e) = e                              # Idempotence
            join(e1, e2) = join(e2, e1)                 # Commutativity
            join(join(e1, e2), e3) = join(e1, join(e2, e3))  # Associativity

        Args:
            other: Other evidence to compare

        Returns:
            True if evidence states are equivalent
        """
        # Evidence is equivalent if priors are close
        return (
            abs(self.prior.alpha - other.prior.alpha) < 1e-6
            and abs(self.prior.beta - other.prior.beta) < 1e-6
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "prior_alpha": self.prior.alpha,
            "prior_beta": self.prior.beta,
            "confidence": self.confidence,
            "should_stop": self.should_stop,
            "tools_succeeded": self.tools_succeeded,
            "tools_failed": self.tools_failed,
            "ashc_equivalence": self.ashc_equivalence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChatEvidence:
        """Create from dictionary."""
        prior = BetaPrior(alpha=data.get("prior_alpha", 1.0), beta=data.get("prior_beta", 1.0))

        return cls(
            id=data.get("id", generate_evidence_id()),
            prior=prior,
            tools_succeeded=data.get("tools_succeeded", 0),
            tools_failed=data.get("tools_failed", 0),
            user_signals=data.get("user_signals", []),
            ashc_equivalence=data.get("ashc_equivalence"),
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else datetime.now(),
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data.get("updated_at")
            else datetime.now(),
            metadata=data.get("metadata", {}),
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "BetaPrior",
    "ChatEvidence",
    "StoppingDecision",
    "TurnResult",
    "generate_evidence_id",
]
