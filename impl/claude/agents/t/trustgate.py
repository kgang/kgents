"""
TrustGate: Capital-Backed Trust Gate with Fool's Bypass

Combines T-gent judgment with capital system for trust decisions.

Philosophy:
- Gates can be bypassed by spending capital (Fool's Bypass)
- Good proposals earn capital (building trust)
- Bad proposals that bypass drain capital (spending trust)
- OCap Pattern: Gate accepts BypassToken, not agent name string

Integration:
- JudgeAgent: Semantic evaluation of proposals (optional LLM-based)
- EventSourcedLedger: Capital tracking
- CostFactor: Algebraic cost computation

AGENTESE: The Gate receives TOKEN, not agent name.
This satisfies "No View From Nowhere"—you need the token to pass.

See: plans/void/capital.md (Trust Gate Integration section)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Optional

from shared.capital import BypassToken, EventSourcedLedger
from shared.costs import BYPASS_COST, CostContext, CostFactor

if TYPE_CHECKING:
    from agents.t.judge import JudgeAgent, JudgmentResult
    from runtime.base import Runtime

logger = logging.getLogger(__name__)


# === Proposal Types ===


@dataclass
class Proposal:
    """
    A proposal to be evaluated by the TrustGate.

    Contains the agent's requested action and context.
    """

    agent: str
    action: str
    diff: str = ""  # Code diff if applicable
    context: dict[str, Any] = field(default_factory=dict)
    risk: float = 0.0  # Pre-computed risk (0.0-1.0)


@dataclass
class TrustDecision:
    """
    Result of TrustGate evaluation.

    Either approved (standard or bypassed) or denied with bypass cost.
    """

    approved: bool
    bypassed: bool = False
    capital_spent: float = 0.0
    capital_earned: float = 0.0
    bypass_cost: float | None = None  # Cost to bypass if denied
    judgment_score: float | None = None
    reason: str = ""


# === Trust Gate ===


@dataclass
class TrustGate:
    """
    Gate that combines T-gent judgment with capital bypass.

    OCap Pattern: Gate accepts BypassToken, not agent name.

    Flow:
    1. Evaluate proposal (judgment_score, risk)
    2. If judgment passes → APPROVE, credit agent
    3. If judgment fails but BypassToken provided → APPROVE with bypass
    4. If judgment fails, no token → DENY, return bypass_cost

    AGENTESE Integration:
    - Uses void.capital.* for ledger operations
    - Uses CostContext for algebraic cost computation

    JudgeAgent Integration:
    - When judge_agent and runtime are provided, uses LLM-based semantic evaluation
    - Falls back to heuristic when not provided or when LLM call fails
    - High-risk proposals (risk > 0.5) always use JudgeAgent when available

    Example:
        gate = TrustGate(capital_ledger=ledger)

        # Standard evaluation (no bypass)
        decision = await gate.evaluate(proposal, agent="b-gent")
        if decision.approved:
            print("Approved via judgment")

        # With bypass token
        token = ledger.mint_bypass("b-gent", "trust_gate", cost=0.1)
        decision = await gate.evaluate(proposal, agent="b-gent", bypass_token=token)
        if decision.bypassed:
            print(f"Approved via bypass, spent {decision.capital_spent}")

        # With JudgeAgent (LLM-based evaluation)
        from agents.t.judge import JudgeAgent, JudgmentCriteria
        from runtime.openrouter import OpenRouterRuntime

        judge = JudgeAgent(JudgmentCriteria())
        runtime = OpenRouterRuntime(api_key="...")
        gate_with_judge = TrustGate(
            capital_ledger=ledger,
            judge_agent=judge,
            runtime=runtime,
        )
        decision = await gate_with_judge.evaluate(proposal, agent="b-gent")
    """

    capital_ledger: EventSourcedLedger
    cost_function: CostFactor = field(default_factory=lambda: BYPASS_COST)

    # Optional JudgeAgent integration
    judge_agent: Optional["JudgeAgent[Any, Any]"] = None
    runtime: Optional["Runtime"] = None

    # Thresholds
    judgment_threshold: float = 0.8  # Score needed for standard approval
    risk_threshold: float = 0.3  # Max risk for standard approval
    llm_risk_threshold: float = 0.5  # Risk level that triggers LLM evaluation

    # Rewards
    good_proposal_reward: float = 0.02  # Capital earned for good proposals

    async def evaluate(
        self,
        proposal: Proposal,
        agent: str,
        bypass_token: BypassToken | None = None,
        judgment_score: float | None = None,
    ) -> TrustDecision:
        """
        Evaluate a proposal and decide whether to approve.

        Args:
            proposal: The proposal to evaluate
            agent: Agent ID making the proposal
            bypass_token: Optional bypass token (OCap capability)
            judgment_score: Pre-computed judgment score (0.0-1.0)
                           If None, uses a simple heuristic

        Returns:
            TrustDecision with approval status and capital changes
        """
        # Get or compute judgment score
        if judgment_score is None:
            judgment_score = await self._compute_judgment(proposal)

        # Build cost context for algebraic computation
        ctx = CostContext(
            risk=proposal.risk,
            judgment_score=judgment_score,
            resources_ok=True,  # Could integrate with resource checker
        )

        # Standard path: all checks must pass
        if (
            judgment_score >= self.judgment_threshold
            and proposal.risk <= self.risk_threshold
        ):
            # Good proposal → credit agent
            self.capital_ledger.credit(
                agent,
                self.good_proposal_reward,
                "good_proposal",
                proposal_action=proposal.action,
            )
            return TrustDecision(
                approved=True,
                bypassed=False,
                capital_earned=self.good_proposal_reward,
                judgment_score=judgment_score,
                reason="Approved: judgment passed",
            )

        # Fool's Bypass: agent presents token
        if bypass_token is not None:
            return self._evaluate_bypass(bypass_token, judgment_score, ctx)

        # Denied: return cost to bypass
        bypass_cost = self.cost_function(ctx)
        return TrustDecision(
            approved=False,
            bypassed=False,
            bypass_cost=bypass_cost,
            judgment_score=judgment_score,
            reason=f"Denied: judgment={judgment_score:.2f} < {self.judgment_threshold}, "
            f"risk={proposal.risk:.2f}. Bypass available for {bypass_cost:.3f} capital.",
        )

    def _evaluate_bypass(
        self,
        token: BypassToken,
        judgment_score: float,
        ctx: CostContext,
    ) -> TrustDecision:
        """
        Evaluate a bypass attempt with a token.

        OCap Pattern: We check the TOKEN, not the agent's identity.
        """
        # Verify token validity
        if not token.is_valid():
            return TrustDecision(
                approved=False,
                bypassed=False,
                bypass_cost=self.cost_function(ctx),
                judgment_score=judgment_score,
                reason="Bypass denied: token expired or invalid",
            )

        # Verify token is for this gate
        if token.check_name != "trust_gate":
            return TrustDecision(
                approved=False,
                bypassed=False,
                bypass_cost=self.cost_function(ctx),
                judgment_score=judgment_score,
                reason=f"Bypass denied: token is for '{token.check_name}', not 'trust_gate'",
            )

        # Token valid → approve with bypass
        # Note: Cost was already deducted when token was minted
        return TrustDecision(
            approved=True,
            bypassed=True,
            capital_spent=token.cost,
            judgment_score=judgment_score,
            reason=f"Approved via bypass (cost: {token.cost:.3f})",
        )

    async def _compute_judgment(self, proposal: Proposal) -> float:
        """
        Compute judgment score for a proposal.

        Uses JudgeAgent when available and conditions are met:
        1. judge_agent and runtime are configured
        2. Proposal risk exceeds llm_risk_threshold (high stakes)

        Falls back to heuristic when:
        - JudgeAgent not configured
        - Low-risk proposal (heuristic is sufficient)
        - LLM call fails (graceful degradation)
        """
        # Decide whether to use LLM-based evaluation
        use_llm = (
            self.judge_agent is not None
            and self.runtime is not None
            and proposal.risk > self.llm_risk_threshold
        )

        if use_llm:
            try:
                return await self._compute_judgment_llm(proposal)
            except Exception as e:
                # Graceful degradation: fall back to heuristic
                logger.warning(f"JudgeAgent failed, falling back to heuristic: {e}")

        return self._compute_judgment_heuristic(proposal)

    async def _compute_judgment_llm(self, proposal: Proposal) -> float:
        """
        Use JudgeAgent for LLM-based semantic evaluation.

        Maps Proposal to (intent, output) pair for JudgeAgent evaluation.
        """
        assert self.judge_agent is not None
        assert self.runtime is not None

        # Construct intent from proposal
        intent = f"Agent '{proposal.agent}' wants to: {proposal.action}"

        # Construct output from proposal diff and context
        output_parts = []
        if proposal.diff:
            output_parts.append(f"Code changes:\n{proposal.diff}")
        if proposal.context:
            output_parts.append(f"Context:\n{json.dumps(proposal.context, indent=2)}")
        output = "\n\n".join(output_parts) if output_parts else "(no details provided)"

        # Call JudgeAgent
        result = await self.judge_agent.execute_async((intent, output), self.runtime)

        # Use weighted_score as judgment score
        logger.debug(
            f"JudgeAgent evaluation: correctness={result.correctness:.2f}, "
            f"safety={result.safety:.2f}, weighted={result.weighted_score:.2f}"
        )
        return result.weighted_score

    def _compute_judgment_heuristic(self, proposal: Proposal) -> float:
        """
        Simple heuristic for low-stakes evaluation.

        Used when:
        - JudgeAgent not configured
        - Low-risk proposals (risk <= llm_risk_threshold)
        - LLM call fails (fallback)
        """
        score = 0.5  # Base score

        # Bonus for having context
        if proposal.context:
            score += 0.1

        # Bonus for having diff
        if proposal.diff:
            score += 0.1

        # Penalty for high risk
        score -= proposal.risk * 0.3

        # Clamp to [0, 1]
        return max(0.0, min(1.0, score))

    def compute_bypass_cost(
        self,
        risk: float,
        judgment_score: float,
        resources_ok: bool = True,
    ) -> float:
        """
        Compute the cost to bypass the gate.

        Uses algebraic cost composition:
        BYPASS_COST = BASE_COST + 0.1 * RISK_PREMIUM + 0.1 * JUDGMENT_DEFICIT + RESOURCE_PENALTY

        Args:
            risk: Risk level (0.0-1.0)
            judgment_score: Current judgment score (0.0-1.0)
            resources_ok: Whether resource constraints are satisfied

        Returns:
            Cost in capital units
        """
        ctx = CostContext(
            risk=risk,
            judgment_score=judgment_score,
            resources_ok=resources_ok,
        )
        return self.cost_function(ctx)


# === Convenience Functions ===


def create_trust_gate(
    ledger: EventSourcedLedger | None = None,
    judgment_threshold: float = 0.8,
    risk_threshold: float = 0.3,
    good_proposal_reward: float = 0.02,
    judge_agent: Optional["JudgeAgent[Any, Any]"] = None,
    runtime: Optional["Runtime"] = None,
    llm_risk_threshold: float = 0.5,
) -> TrustGate:
    """
    Create a TrustGate with default or custom configuration.

    Args:
        ledger: Capital ledger (creates new one if None)
        judgment_threshold: Score needed for standard approval
        risk_threshold: Max risk for standard approval
        good_proposal_reward: Capital earned for good proposals
        judge_agent: Optional JudgeAgent for LLM-based evaluation
        runtime: Optional Runtime for JudgeAgent execution
        llm_risk_threshold: Risk level that triggers LLM evaluation (default: 0.5)

    Returns:
        Configured TrustGate

    Example (with JudgeAgent):
        from agents.t.judge import JudgeAgent, JudgmentCriteria
        from runtime.openrouter import OpenRouterRuntime

        judge = JudgeAgent(JudgmentCriteria(correctness=1.0, safety=1.0, style=0.3))
        runtime = OpenRouterRuntime(api_key=os.getenv("OPENROUTER_API_KEY"))

        gate = create_trust_gate(
            judge_agent=judge,
            runtime=runtime,
            llm_risk_threshold=0.3,  # Use LLM for any proposal with risk > 0.3
        )
    """
    return TrustGate(
        capital_ledger=ledger or EventSourcedLedger(),
        judgment_threshold=judgment_threshold,
        risk_threshold=risk_threshold,
        good_proposal_reward=good_proposal_reward,
        judge_agent=judge_agent,
        runtime=runtime,
        llm_risk_threshold=llm_risk_threshold,
    )
