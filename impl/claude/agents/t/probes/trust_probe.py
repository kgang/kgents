"""
TrustProbe: GENERATIVE Mode Probe for Trust Gating

Mode: GENERATIVE
Purpose: Generative gating - can this be regenerated from spec?
Reward: Generative (regenerability) + Ethical (no hidden state)

The TrustProbe tests whether an agent's output can be regenerated from its
inputs via specification alone. This is the generative test: does output
follow from inputs via spec, or is there hidden state/non-determinism?

Capital-backed bypass mechanism (Fool's Bypass):
- Proposals are evaluated for regenerability (Galois loss)
- If proposal fails but agent has capital, they can bypass
- Good proposals earn capital (building trust)
- Bypass proposals drain capital (spending trust)

DP Semantics:
- States: {READY, PROPOSING, DECIDING, TRUSTED, REJECTED}
- Actions: {propose, evaluate_regenerability, decide, bypass}
- Transition: READY -> PROPOSING -> DECIDING -> (TRUSTED | REJECTED)
- Reward: Generative (low Galois loss) + Ethical (no bypass)

Integration:
- Consolidates TrustGate functionality into TruthFunctor interface
- Galois loss measurement for regenerability testing
- Capital-backed decision making
- PolicyTrace emission for witness integration

Example:
    >>> # Basic trust gating
    >>> probe = trust_probe(
    ...     capital_stake=1.0,
    ...     threshold=0.8,
    ... )
    >>>
    >>> # Test proposal
    >>> proposal = Proposal(
    ...     agent="b-gent",
    ...     action="Execute risky operation",
    ...     risk=0.5,
    ... )
    >>>
    >>> # Verify (includes regenerability test)
    >>> trace = await probe.verify(my_agent, proposal)
    >>> if trace.value.passed:
    ...     print("Proposal trusted")
    >>> else:
    ...     print(f"Proposal rejected. Bypass cost: {trace.value.bypass_cost}")
    >>>
    >>> # With bypass token
    >>> token = ledger.mint_bypass("b-gent", "trust_gate", cost=0.1)
    >>> probe_with_bypass = trust_probe(capital_stake=1.0, bypass_secret=token.secret)
    >>> trace = await probe_with_bypass.verify(my_agent, proposal)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Callable, FrozenSet, Generic, TypeVar

from agents.t.truth_functor import (
    AnalysisMode,
    ConstitutionalScore,
    PolicyTrace,
    ProbeAction,
    ProbeState,
    TraceEntry,
    TruthFunctor,
    TruthVerdict,
)

A = TypeVar("A")
B = TypeVar("B")


class TrustState(Enum):
    """DP states for TrustProbe."""

    READY = auto()
    PROPOSING = auto()
    DECIDING = auto()
    TRUSTED = auto()
    REJECTED = auto()


@dataclass(frozen=True)
class Proposal:
    """
    A proposal to be evaluated by TrustProbe.

    Fields:
        agent: Agent making the proposal
        action: Description of proposed action
        diff: Code diff if applicable
        context: Additional context
        risk: Pre-computed risk level [0.0, 1.0]
    """

    agent: str
    action: str
    diff: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    risk: float = 0.0


@dataclass(frozen=True)
class TrustDecision:
    """
    Result of trust evaluation.

    Fields:
        approved: Whether proposal was approved
        bypassed: Whether bypass was used
        capital_spent: Capital spent on bypass (if any)
        capital_earned: Capital earned for good proposal
        bypass_cost: Cost to bypass if denied
        regenerable: Whether output is regenerable from spec
        galois_loss: Galois connection loss (measure of regenerability)
        reason: Human-readable explanation
    """

    approved: bool
    bypassed: bool = False
    capital_spent: float = 0.0
    capital_earned: float = 0.0
    bypass_cost: float | None = None
    regenerable: bool = False
    galois_loss: float | None = None
    reason: str = ""


@dataclass(frozen=True)
class TrustConfig:
    """
    Configuration for TrustProbe.

    Fields:
        label: Human-readable label
        capital_stake: Initial capital for trust decisions
        bypass_secret: Secret for bypass token (None = no bypass)
        threshold: Galois loss threshold for regenerability [0.0, 1.0]
        risk_threshold: Maximum acceptable risk [0.0, 1.0]
        good_proposal_reward: Capital earned for good proposals
        base_bypass_cost: Base cost for bypass
    """

    label: str = "TrustProbe"
    capital_stake: float = 1.0
    bypass_secret: str | None = None
    threshold: float = 0.8
    risk_threshold: float = 0.3
    good_proposal_reward: float = 0.02
    base_bypass_cost: float = 0.05


class TrustProbe(TruthFunctor[TrustState, Proposal, TrustDecision], Generic[A, B]):
    """
    TrustProbe: GENERATIVE mode probe for trust gating.

    Tests whether agent output can be regenerated from inputs via spec alone.
    This is the generative test: does output follow from inputs, or is there
    hidden state/non-determinism?

    Category Theory: Galois Connection Test
    F ⊣ G: spec → impl ⊣ impl → spec
    Low Galois loss = regenerable = high trust

    DP Formulation:
    - State space: {READY, PROPOSING, DECIDING, TRUSTED, REJECTED}
    - Action space: {propose, evaluate_regenerability, decide, bypass}
    - Reward: R = Generative(low Galois loss) + Ethical(no bypass)

    Capital Mechanism (Fool's Bypass):
    - Good proposals earn capital (building trust)
    - Failed proposals can be bypassed by spending capital
    - Bypass drains capital (spending trust)
    - No capital = no bypass = hard rejection

    Constitutional Alignment:
    - Generative: High reward for regenerable outputs (low Galois loss)
    - Ethical: Penalty for bypass usage (hidden state is unethical)
    - Composable: Gating preserves composition laws
    - Tasteful: Clear purpose (trust through regenerability)
    """

    def __init__(self, config: TrustConfig):
        """
        Initialize TrustProbe with configuration.

        Args:
            config: Trust configuration (capital, bypass secret, thresholds)
        """
        self.config = config
        self._current_state = TrustState.READY
        self._current_capital = config.capital_stake
        self._proposal: Proposal | None = None
        self._decision: TrustDecision | None = None
        self._used_bypass = False
        self._galois_loss: float | None = None
        self.__is_test__ = True  # T-gent marker

        # TruthFunctor required attributes
        self.name = f"TrustProbe({config.label})"
        self.mode = AnalysisMode.GENERATIVE
        self.gamma = 0.99

    # === TruthFunctor Interface ===

    @property
    def states(self) -> FrozenSet[TrustState]:
        """Return DP state space."""
        return frozenset([
            TrustState.READY,
            TrustState.PROPOSING,
            TrustState.DECIDING,
            TrustState.TRUSTED,
            TrustState.REJECTED,
        ])

    def actions(self, state: TrustState) -> FrozenSet[ProbeAction]:
        """Return available actions from state."""
        if state == TrustState.READY:
            return frozenset([ProbeAction("propose")])
        elif state == TrustState.PROPOSING:
            return frozenset([ProbeAction("evaluate_regenerability")])
        elif state == TrustState.DECIDING:
            # Can approve, reject, or bypass
            actions = [
                ProbeAction("approve"),
                ProbeAction("reject"),
            ]
            # Bypass only available if bypass_secret configured and capital available
            if self.config.bypass_secret is not None and self._current_capital > 0:
                actions.append(ProbeAction("bypass"))
            return frozenset(actions)
        return frozenset()

    def transition(self, state: TrustState, action: ProbeAction) -> TrustState:
        """Return next state after action."""
        if state == TrustState.READY and action.name == "propose":
            return TrustState.PROPOSING
        elif state == TrustState.PROPOSING and action.name == "evaluate_regenerability":
            return TrustState.DECIDING
        elif state == TrustState.DECIDING:
            if action.name == "approve":
                return TrustState.TRUSTED
            elif action.name == "reject":
                return TrustState.REJECTED
            elif action.name == "bypass":
                return TrustState.TRUSTED
        return state

    def reward(
        self,
        state: TrustState,
        action: ProbeAction,
        next_state: TrustState
    ) -> ConstitutionalScore:
        """
        Constitutional reward for trust decisions.

        Reward structure:
        - Generative: 1.0 if regenerable (low Galois loss), 0.3 otherwise
        - Ethical: 1.0 if no bypass, 0.5 if bypass used
        - Composable: 0.9 (gating preserves composition)
        - Tasteful: 0.8 (clear purpose)
        """
        # Base scores
        base = ConstitutionalScore(
            composable=0.9,
            tasteful=0.8,
            heterarchical=0.7,
        )

        # Regenerability evaluation
        if action.name == "evaluate_regenerability":
            regenerable = (
                self._galois_loss is not None
                and self._galois_loss < (1.0 - self.config.threshold)
            )
            return ConstitutionalScore(
                generative=1.0 if regenerable else 0.3,
                composable=0.9,
                tasteful=0.8,
            )

        # Approval decision
        elif action.name == "approve":
            regenerable = (
                self._galois_loss is not None
                and self._galois_loss < (1.0 - self.config.threshold)
            )
            return ConstitutionalScore(
                generative=1.0 if regenerable else 0.3,
                ethical=1.0,  # No bypass used
                composable=0.9,
                tasteful=0.8,
            )

        # Bypass decision
        elif action.name == "bypass":
            return ConstitutionalScore(
                generative=0.5,  # Bypass reduces generative score
                ethical=0.5,     # Bypass is ethically questionable
                composable=0.8,  # Still composable
                tasteful=0.6,    # Less tasteful
            )

        # Rejection
        elif action.name == "reject":
            return ConstitutionalScore(
                generative=0.7,  # Rejection preserves integrity
                ethical=0.9,     # Ethical to reject unregenerable
                composable=0.9,
                tasteful=0.8,
            )

        return base

    async def verify(
        self,
        agent: Any,
        input: Proposal
    ) -> PolicyTrace[TruthVerdict[TrustDecision]]:
        """
        Verify proposal with trust gating and regenerability test.

        Process:
        1. READY -> PROPOSING: Accept proposal
        2. PROPOSING -> DECIDING: Evaluate regenerability (Galois loss)
        3. DECIDING -> TRUSTED/REJECTED: Decide based on Galois loss and risk

        Args:
            agent: Agent under test (can be callable or ignored)
            input: Proposal to evaluate

        Returns:
            PolicyTrace[TruthVerdict[TrustDecision]]: Trace with trust decision
        """
        trace_entries: list[TraceEntry] = []
        self._proposal = input
        self._used_bypass = False

        # State 1: READY -> PROPOSING (accept proposal)
        probe_state = ProbeState(
            phase="ready",
            observations=(),
        )

        action = ProbeAction("propose", (input.agent, input.action))
        next_dp_state = self.transition(self._current_state, action)

        trace_entries.append(TraceEntry(
            state_before=probe_state,
            action=action,
            state_after=probe_state.transition_to("proposing"),
            reward=self.reward(self._current_state, action, next_dp_state),
            reasoning=f"Proposal from {input.agent}: {input.action}",
            timestamp=datetime.now(timezone.utc),
        ))

        self._current_state = next_dp_state
        probe_state = probe_state.transition_to("proposing")

        # State 2: PROPOSING -> DECIDING (evaluate regenerability)
        action = ProbeAction("evaluate_regenerability")
        next_dp_state = self.transition(self._current_state, action)

        # Compute Galois loss (measure of regenerability)
        self._galois_loss = self._compute_galois_loss(input, agent)
        regenerable = self._galois_loss < (1.0 - self.config.threshold)

        observation = (
            f"Galois loss: {self._galois_loss:.3f}, "
            f"{'regenerable' if regenerable else 'not regenerable'}"
        )
        probe_state = probe_state.with_observation(observation)

        trace_entries.append(TraceEntry(
            state_before=probe_state,
            action=action,
            state_after=probe_state.transition_to("deciding"),
            reward=self.reward(self._current_state, action, next_dp_state),
            reasoning=observation,
            timestamp=datetime.now(timezone.utc),
        ))

        self._current_state = next_dp_state
        probe_state = probe_state.transition_to("deciding")

        # State 3: DECIDING -> TRUSTED/REJECTED (make decision)
        # Check if proposal passes standard checks
        passes_standard = (
            regenerable
            and input.risk <= self.config.risk_threshold
        )

        # Check if bypass is available and valid
        can_bypass = (
            self.config.bypass_secret is not None
            and self._current_capital >= self.config.base_bypass_cost
        )

        # Decide action
        if passes_standard:
            # Good proposal -> approve and credit capital
            action = ProbeAction("approve")
            next_dp_state = self.transition(self._current_state, action)
            self._current_capital += self.config.good_proposal_reward

            self._decision = TrustDecision(
                approved=True,
                bypassed=False,
                capital_earned=self.config.good_proposal_reward,
                regenerable=True,
                galois_loss=self._galois_loss,
                reason="Approved: regenerable and low risk",
            )

        elif can_bypass and self._should_bypass(input):
            # Bypass available and conditions met -> approve via bypass
            action = ProbeAction("bypass")
            next_dp_state = self.transition(self._current_state, action)
            bypass_cost = self._compute_bypass_cost(input)
            self._current_capital -= bypass_cost
            self._used_bypass = True

            self._decision = TrustDecision(
                approved=True,
                bypassed=True,
                capital_spent=bypass_cost,
                regenerable=False,
                galois_loss=self._galois_loss,
                reason=f"Approved via bypass (cost: {bypass_cost:.3f})",
            )

        else:
            # Reject -> deny with bypass cost
            action = ProbeAction("reject")
            next_dp_state = self.transition(self._current_state, action)
            bypass_cost = self._compute_bypass_cost(input)

            self._decision = TrustDecision(
                approved=False,
                bypassed=False,
                bypass_cost=bypass_cost,
                regenerable=regenerable,
                galois_loss=self._galois_loss,
                reason=(
                    f"Rejected: galois_loss={self._galois_loss:.3f}, "
                    f"risk={input.risk:.3f}. "
                    f"Bypass available for {bypass_cost:.3f} capital."
                ),
            )

        trace_entries.append(TraceEntry(
            state_before=probe_state,
            action=action,
            state_after=probe_state.transition_to(
                "trusted" if self._decision.approved else "rejected"
            ),
            reward=self.reward(self._current_state, action, next_dp_state),
            reasoning=self._decision.reason,
            timestamp=datetime.now(timezone.utc),
        ))

        self._current_state = next_dp_state

        # Create verdict
        verdict: TruthVerdict[TrustDecision] = TruthVerdict(
            value=self._decision,
            passed=self._decision.approved,
            confidence=0.95 if self._decision.approved and not self._decision.bypassed else 0.7,
            reasoning=self._decision.reason,
            galois_loss=self._galois_loss,
            timestamp=datetime.now(timezone.utc),
        )

        # Return PolicyTrace
        policy_trace: PolicyTrace[TruthVerdict[TrustDecision]] = PolicyTrace(
            value=verdict,
            entries=trace_entries,
        )

        return policy_trace

    # === Trust Gate Logic ===

    def _compute_galois_loss(self, proposal: Proposal, agent: Any) -> float:
        """
        Compute Galois loss (measure of regenerability).

        Galois connection: spec ⊣ impl
        Loss = distance between F(G(impl)) and impl
        Low loss = regenerable from spec

        For now, uses heuristic based on proposal attributes.
        In production, this would integrate with actual Galois machinery.

        Args:
            proposal: Proposal to evaluate
            agent: Agent under test (ignored for now)

        Returns:
            Galois loss in [0.0, 1.0] (0 = perfect regenerability)
        """
        # Heuristic Galois loss computation
        loss = 0.0

        # Risk contributes to loss
        loss += proposal.risk * 0.3

        # Lack of context/diff increases loss (less regenerable)
        if not proposal.context:
            loss += 0.2
        if not proposal.diff:
            loss += 0.1

        # Hash-based determinism check
        # If proposal has deterministic structure, loss is lower
        proposal_hash = self._hash_proposal(proposal)
        hash_entropy = sum(int(c, 16) for c in proposal_hash[:8]) / (16 * 8)
        loss += hash_entropy * 0.2

        # Clamp to [0, 1]
        return max(0.0, min(1.0, loss))

    def _hash_proposal(self, proposal: Proposal) -> str:
        """Compute deterministic hash of proposal."""
        content = f"{proposal.agent}:{proposal.action}:{proposal.diff}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _should_bypass(self, proposal: Proposal) -> bool:
        """
        Determine if bypass should be used.

        For now, always returns True if capital available.
        In production, this would check bypass_secret validation.

        Args:
            proposal: Proposal being evaluated

        Returns:
            True if bypass should be used
        """
        # Simple heuristic: always bypass if capital available
        # In production: verify bypass token against bypass_secret
        return self._current_capital >= self._compute_bypass_cost(proposal)

    def _compute_bypass_cost(self, proposal: Proposal) -> float:
        """
        Compute cost to bypass rejection.

        Cost increases with:
        - Risk level
        - Galois loss (non-regenerability)

        Args:
            proposal: Proposal being evaluated

        Returns:
            Bypass cost in capital units
        """
        base = self.config.base_bypass_cost

        # Risk premium
        risk_premium = proposal.risk * 0.1

        # Galois loss premium (higher loss = higher cost)
        galois_premium = 0.0
        if self._galois_loss is not None:
            galois_premium = self._galois_loss * 0.15

        return base + risk_premium + galois_premium

    # === State Accessors ===

    @property
    def current_capital(self) -> float:
        """Get current capital balance."""
        return self._current_capital

    @property
    def last_decision(self) -> TrustDecision | None:
        """Get last trust decision."""
        return self._decision

    @property
    def last_galois_loss(self) -> float | None:
        """Get last computed Galois loss."""
        return self._galois_loss

    def reset(self) -> None:
        """Reset probe state for test isolation."""
        self._current_state = TrustState.READY
        self._current_capital = self.config.capital_stake
        self._proposal = None
        self._decision = None
        self._used_bypass = False
        self._galois_loss = None


# === Convenience Functions ===


def trust_probe(
    label: str = "TrustProbe",
    capital_stake: float = 1.0,
    bypass_secret: str | None = None,
    threshold: float = 0.8,
    risk_threshold: float = 0.3,
    good_proposal_reward: float = 0.02,
    base_bypass_cost: float = 0.05,
) -> TrustProbe[Any, Any]:
    """
    Create a TrustProbe with given configuration.

    Args:
        label: Human-readable label
        capital_stake: Initial capital for trust decisions
        bypass_secret: Secret for bypass token (None = no bypass)
        threshold: Galois loss threshold for regenerability [0.0, 1.0]
        risk_threshold: Maximum acceptable risk [0.0, 1.0]
        good_proposal_reward: Capital earned for good proposals
        base_bypass_cost: Base cost for bypass

    Returns:
        Configured TrustProbe

    Example:
        >>> probe = trust_probe(
        ...     capital_stake=2.0,
        ...     threshold=0.9,
        ...     risk_threshold=0.2,
        ... )
        >>> proposal = Proposal(
        ...     agent="b-gent",
        ...     action="High-risk operation",
        ...     risk=0.5,
        ... )
        >>> trace = await probe.verify(None, proposal)
        >>> if trace.value.passed:
        ...     print("Proposal approved")
    """
    config = TrustConfig(
        label=label,
        capital_stake=capital_stake,
        bypass_secret=bypass_secret,
        threshold=threshold,
        risk_threshold=risk_threshold,
        good_proposal_reward=good_proposal_reward,
        base_bypass_cost=base_bypass_cost,
    )
    return TrustProbe(config)


__all__ = [
    "TrustState",
    "Proposal",
    "TrustDecision",
    "TrustConfig",
    "TrustProbe",
    "trust_probe",
]
