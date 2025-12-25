"""
TrustProbe: Generative gating for regenerability testing.

Mode: GENERATIVE
Purpose: Verify outputs can be regenerated from spec.
Reward: Generative (regenerability) + Ethical (no hidden state)

The TrustProbe implements capital-backed trust gating:
- Capital depletion signals regenerability failure
- Fool's Bypass allows temporary override (OCap pattern)
- Galois loss measures spec-implementation gap
- Proposal/decision workflow for verification

This probe tests the GENERATIVE principle: can we regenerate this output
from specification alone? Hidden state violates regenerability.

DP Semantics:
- States: {READY, EVALUATING, APPROVED, DENIED, BYPASSED}
- Actions: {propose, evaluate, approve, deny, bypass}
- Transition: READY --propose--> EVALUATING --{approve|deny|bypass}--> {APPROVED|DENIED|BYPASSED}
- Reward: Generative (regenerability) + Ethical (transparency)

Example:
    >>> probe = TrustProbe(initial_capital=1.0)
    >>> proposal = {"action": "refactor", "spec": "..."}
    >>> decision = await probe.invoke(proposal)
    >>> decision.approved  # True if regenerable from spec
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Generic, TypeVar

from agents.poly.types import Agent
from services.categorical.dp_bridge import PolicyTrace, Principle, TraceEntry

A = TypeVar("A")


class TrustState(Enum):
    """DP states for TrustProbe."""

    READY = auto()
    EVALUATING = auto()
    APPROVED = auto()
    DENIED = auto()
    BYPASSED = auto()


@dataclass
class Proposal:
    """
    A proposal to be evaluated by TrustProbe.

    Contains action and evidence of regenerability.
    """

    action: str  # What is being proposed
    spec: str = ""  # Specification this derives from
    galois_loss: float = 0.0  # Measured spec-impl gap
    context: dict[str, Any] | None = None  # Additional context


@dataclass
class TrustDecision:
    """
    Result of TrustProbe evaluation.

    Either approved (regenerable), denied (not regenerable), or bypassed.
    """

    approved: bool
    bypassed: bool = False
    capital_spent: float = 0.0
    capital_earned: float = 0.0
    galois_loss: float = 0.0
    regenerability_score: float = 0.0  # How regenerable (0.0-1.0)
    reason: str = ""


@dataclass
class TrustConfig:
    """Configuration for TrustProbe."""

    initial_capital: float = 1.0  # Starting capital
    regenerability_threshold: float = 0.8  # Min score to approve
    galois_threshold: float = 0.2  # Max loss to approve
    bypass_cost: float = 0.1  # Capital cost to bypass
    good_proposal_reward: float = 0.05  # Capital earned


class TrustProbe(Agent[Proposal, TrustDecision], Generic[A]):
    """
    TrustProbe: Generative gating for regenerability testing.

    Input: Proposal with action and spec
    Output: TrustDecision with approval status

    Category Theory: Trust morphism T: Proposal → Decision
    Maps proposals to approval decisions based on regenerability.

    DP Semantics:
    - State space: {READY, EVALUATING, APPROVED, DENIED, BYPASSED}
    - Action space: {propose, evaluate, approve, deny, bypass}
    - Transition: READY --propose--> EVALUATING --decision--> {APPROVED|DENIED|BYPASSED}
    - Reward: R(s, a) = GENERATIVE + ETHICAL (regenerability + transparency)

    TruthFunctor Interface:
    - states(): Returns DP state space
    - actions(s): Returns available actions from state s
    - transition(s, a): Returns next state after action a from state s
    - reward(s, a): Returns constitutional reward for action a in state s
    - verify(): Verifies regenerability from spec
    """

    def __init__(self, config: TrustConfig):
        """Initialize TrustProbe with configuration."""
        self.config = config
        self._capital = config.initial_capital
        self._state = TrustState.READY
        self._trace_log: list[TraceEntry] = []
        self._proposal_count = 0
        self._approval_count = 0
        self._bypass_count = 0
        self.__is_test__ = True  # T-gent marker

    @property
    def name(self) -> str:
        """Return agent name."""
        return f"TrustProbe(capital={self._capital:.3f})"

    # === Agent Interface ===

    async def invoke(self, input: Proposal) -> TrustDecision:
        """
        Evaluate proposal and return trust decision.

        Args:
            input: Proposal to evaluate

        Returns:
            TrustDecision with approval status
        """
        prev_state = self._state
        self._state = TrustState.EVALUATING
        self._proposal_count += 1

        # Compute regenerability score
        regenerability = self._compute_regenerability(input)

        # Check if proposal meets thresholds
        meets_threshold = (
            regenerability >= self.config.regenerability_threshold and
            input.galois_loss <= self.config.galois_threshold
        )

        if meets_threshold:
            # Approve: good regenerability
            self._state = TrustState.APPROVED
            self._approval_count += 1

            # Earn capital
            self._capital += self.config.good_proposal_reward

            decision = TrustDecision(
                approved=True,
                bypassed=False,
                capital_earned=self.config.good_proposal_reward,
                galois_loss=input.galois_loss,
                regenerability_score=regenerability,
                reason=f"Approved: regenerability={regenerability:.3f}, galois_loss={input.galois_loss:.3f}",
            )

        else:
            # Check if bypass is possible
            can_bypass = self._capital >= self.config.bypass_cost

            if can_bypass:
                # Bypass: spend capital
                self._state = TrustState.BYPASSED
                self._bypass_count += 1

                self._capital -= self.config.bypass_cost

                decision = TrustDecision(
                    approved=True,
                    bypassed=True,
                    capital_spent=self.config.bypass_cost,
                    galois_loss=input.galois_loss,
                    regenerability_score=regenerability,
                    reason=f"Bypassed: spent {self.config.bypass_cost:.3f} capital",
                )

            else:
                # Deny: insufficient regenerability and no capital
                self._state = TrustState.DENIED

                decision = TrustDecision(
                    approved=False,
                    bypassed=False,
                    galois_loss=input.galois_loss,
                    regenerability_score=regenerability,
                    reason=f"Denied: regenerability={regenerability:.3f} < {self.config.regenerability_threshold}, "
                           f"galois_loss={input.galois_loss:.3f} > {self.config.galois_threshold}",
                )

        # Emit trace entry
        entry = TraceEntry(
            state_before=prev_state,
            action="evaluate",
            state_after=self._state,
            value=self._compute_reward(prev_state, "evaluate", decision),
            rationale=decision.reason,
            timestamp=datetime.now(timezone.utc),
        )
        self._trace_log.append(entry)

        # Reset for next proposal
        self._state = TrustState.READY

        return decision

    def _compute_regenerability(self, proposal: Proposal) -> float:
        """
        Compute regenerability score for proposal.

        Regenerability = 1 - galois_loss (inverse of spec-impl gap)
        Plus bonus if spec is non-empty (evidence provided)

        Args:
            proposal: Proposal to evaluate

        Returns:
            Regenerability score 0.0-1.0
        """
        # Base score from galois loss
        base_score = 1.0 - proposal.galois_loss

        # Bonus for having spec
        spec_bonus = 0.1 if proposal.spec else 0.0

        # Clamp to [0, 1]
        return max(0.0, min(1.0, base_score + spec_bonus))

    # === TruthFunctor Interface ===

    def states(self) -> frozenset[TrustState]:
        """Return DP state space."""
        return frozenset([
            TrustState.READY,
            TrustState.EVALUATING,
            TrustState.APPROVED,
            TrustState.DENIED,
            TrustState.BYPASSED,
        ])

    def actions(self, state: TrustState) -> frozenset[str]:
        """Return available actions from state."""
        if state == TrustState.READY:
            return frozenset(["propose"])
        elif state == TrustState.EVALUATING:
            return frozenset(["approve", "deny", "bypass"])
        return frozenset()

    def transition(self, state: TrustState, action: str) -> TrustState:
        """Return next state after action."""
        if state == TrustState.READY and action == "propose":
            return TrustState.EVALUATING
        elif state == TrustState.EVALUATING:
            if action == "approve":
                return TrustState.APPROVED
            elif action == "deny":
                return TrustState.DENIED
            elif action == "bypass":
                return TrustState.BYPASSED
        return state

    def reward(self, state: TrustState, action: str, decision: TrustDecision | None = None) -> float:
        """Return constitutional reward for action in state."""
        return self._compute_reward(state, action, decision)

    def _compute_reward(self, state: TrustState, action: str, decision: TrustDecision | None = None) -> float:
        """
        Compute constitutional reward.

        TrustProbe satisfies:
        - GENERATIVE: Regenerability from spec (compression)
        - ETHICAL: Transparency (no hidden state)
        """
        if state == TrustState.EVALUATING and action == "evaluate":
            generative_score = Principle.GENERATIVE.weight
            ethical_score = Principle.ETHICAL.weight

            # Bonus for high regenerability
            bonus = 0.0
            if decision and decision.regenerability_score > 0.9:
                bonus = 0.5

            return generative_score + ethical_score + bonus

        return 0.0

    def verify(self) -> bool:
        """
        Verify regenerability property.

        Returns:
            True if system maintains regenerability
        """
        # Verification: capital should never go negative (bounded)
        capital_valid = self._capital >= 0.0

        # Verification: approvals should outnumber bypasses (regenerability preferred)
        regenerability_preferred = self._approval_count >= self._bypass_count

        return capital_valid and regenerability_preferred

    async def get_trace(self) -> PolicyTrace[TrustDecision]:
        """
        Get PolicyTrace with accumulated entries.

        Returns:
            PolicyTrace with value and log
        """
        # For TrustProbe, the "value" is the trust statistics
        value = {
            "proposal_count": self._proposal_count,
            "approval_count": self._approval_count,
            "bypass_count": self._bypass_count,
            "capital": self._capital,
            "approval_rate": self._approval_count / max(1, self._proposal_count),
        }

        return PolicyTrace(
            value=value,  # type: ignore
            log=tuple(self._trace_log),
        )

    def reset(self) -> None:
        """Reset state and trace for test isolation."""
        self._capital = self.config.initial_capital
        self._state = TrustState.READY
        self._trace_log.clear()
        self._proposal_count = 0
        self._approval_count = 0
        self._bypass_count = 0

    @property
    def call_count(self) -> int:
        """Number of times invoke was called."""
        return self._proposal_count

    @property
    def capital(self) -> float:
        """Current capital balance."""
        return self._capital

    @property
    def approval_rate(self) -> float:
        """Proportion of proposals approved (without bypass)."""
        if self._proposal_count == 0:
            return 0.0
        return self._approval_count / self._proposal_count


# === Convenience Functions ===


def trust_probe(
    initial_capital: float = 1.0,
    regenerability_threshold: float = 0.8,
    galois_threshold: float = 0.2,
) -> TrustProbe[Any]:
    """
    Create a TrustProbe with given configuration.

    Args:
        initial_capital: Starting capital
        regenerability_threshold: Min score to approve
        galois_threshold: Max loss to approve

    Returns:
        Configured TrustProbe

    Example:
        >>> probe = trust_probe(initial_capital=1.0)
        >>> proposal = Proposal(action="refactor", galois_loss=0.15)
        >>> decision = await probe.invoke(proposal)
        >>> decision.approved
    """
    return TrustProbe(TrustConfig(
        initial_capital=initial_capital,
        regenerability_threshold=regenerability_threshold,
        galois_threshold=galois_threshold,
    ))
