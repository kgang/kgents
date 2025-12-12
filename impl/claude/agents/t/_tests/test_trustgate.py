"""
Tests for TrustGate: Capital-Backed Trust Gate with Fool's Bypass

Tests verify:
1. Standard approval path (good judgment → approve + credit)
2. Standard denial path (bad judgment → deny + return bypass cost)
3. Bypass approval path (token → approve, cost already deducted)
4. Token validation (expired, wrong gate)
5. Algebraic cost computation
6. OCap pattern (token-based, not identity-based)
"""

from __future__ import annotations

from datetime import timedelta

import pytest
from agents.t.trustgate import (
    Proposal,
    TrustDecision,
    TrustGate,
    create_trust_gate,
)
from shared.capital import BypassToken, EventSourcedLedger
from shared.costs import CostContext, CostFactor, constant_cost

# === Fixtures ===


@pytest.fixture
def ledger() -> EventSourcedLedger:
    """Fresh ledger per test."""
    return EventSourcedLedger()


@pytest.fixture
def funded_ledger() -> EventSourcedLedger:
    """Ledger with test agent funded."""
    ledger = EventSourcedLedger()
    ledger.credit("test-agent", 0.5, "test_setup")
    return ledger


@pytest.fixture
def gate(ledger: EventSourcedLedger) -> TrustGate:
    """Default TrustGate."""
    return TrustGate(capital_ledger=ledger)


@pytest.fixture
def funded_gate(funded_ledger: EventSourcedLedger) -> TrustGate:
    """TrustGate with funded agent."""
    return TrustGate(capital_ledger=funded_ledger)


@pytest.fixture
def good_proposal() -> Proposal:
    """Proposal that should pass standard judgment."""
    return Proposal(
        agent="test-agent",
        action="fix typo in README",
        diff="- Hello Wrold\n+ Hello World",
        context={"file": "README.md"},
        risk=0.1,  # Low risk
    )


@pytest.fixture
def risky_proposal() -> Proposal:
    """Proposal that should fail standard judgment."""
    return Proposal(
        agent="test-agent",
        action="delete production database",
        diff="DROP TABLE users;",
        context={},
        risk=0.9,  # High risk
    )


# === Standard Approval Tests ===


class TestStandardApproval:
    """Tests for standard approval path."""

    @pytest.mark.asyncio
    async def test_approve_good_proposal(
        self, gate: TrustGate, good_proposal: Proposal
    ) -> None:
        """Good proposal with high judgment score is approved."""
        decision = await gate.evaluate(
            good_proposal,
            agent="test-agent",
            judgment_score=0.9,  # Above threshold
        )

        assert decision.approved is True
        assert decision.bypassed is False
        assert decision.capital_earned > 0
        assert "judgment passed" in decision.reason

    @pytest.mark.asyncio
    async def test_approve_credits_agent(
        self, gate: TrustGate, good_proposal: Proposal
    ) -> None:
        """Approved proposal credits the agent."""
        initial_balance = gate.capital_ledger.balance("test-agent")

        await gate.evaluate(
            good_proposal,
            agent="test-agent",
            judgment_score=0.9,
        )

        new_balance = gate.capital_ledger.balance("test-agent")
        assert new_balance > initial_balance

    @pytest.mark.asyncio
    async def test_approve_records_event(
        self, gate: TrustGate, good_proposal: Proposal
    ) -> None:
        """Approved proposal creates CREDIT event."""
        await gate.evaluate(
            good_proposal,
            agent="test-agent",
            judgment_score=0.9,
        )

        events = gate.capital_ledger.witness("test-agent")
        assert len(events) == 1
        assert events[0].event_type == "CREDIT"
        assert events[0].metadata.get("reason") == "good_proposal"


# === Standard Denial Tests ===


class TestStandardDenial:
    """Tests for standard denial path."""

    @pytest.mark.asyncio
    async def test_deny_risky_proposal(
        self, gate: TrustGate, risky_proposal: Proposal
    ) -> None:
        """Risky proposal with low judgment score is denied."""
        decision = await gate.evaluate(
            risky_proposal,
            agent="test-agent",
            judgment_score=0.3,  # Below threshold
        )

        assert decision.approved is False
        assert decision.bypassed is False
        assert decision.bypass_cost is not None
        assert decision.bypass_cost > 0

    @pytest.mark.asyncio
    async def test_deny_returns_bypass_cost(
        self, gate: TrustGate, risky_proposal: Proposal
    ) -> None:
        """Denied proposal includes bypass cost."""
        decision = await gate.evaluate(
            risky_proposal,
            agent="test-agent",
            judgment_score=0.3,
        )

        assert decision.bypass_cost is not None
        # Bypass cost should be positive
        assert decision.bypass_cost > 0

    @pytest.mark.asyncio
    async def test_deny_no_capital_change(
        self, funded_gate: TrustGate, risky_proposal: Proposal
    ) -> None:
        """Denied proposal doesn't change capital (no credit or debit)."""
        initial_balance = funded_gate.capital_ledger.balance("test-agent")

        await funded_gate.evaluate(
            risky_proposal,
            agent="test-agent",
            judgment_score=0.3,
        )

        # Balance unchanged (denial doesn't cost anything)
        assert funded_gate.capital_ledger.balance("test-agent") == initial_balance


# === Bypass Approval Tests ===


class TestBypassApproval:
    """Tests for bypass approval path (Fool's Bypass)."""

    @pytest.mark.asyncio
    async def test_bypass_with_valid_token(
        self, funded_gate: TrustGate, risky_proposal: Proposal
    ) -> None:
        """Valid bypass token approves risky proposal."""
        # Mint bypass token
        token = funded_gate.capital_ledger.mint_bypass(
            "test-agent", "trust_gate", cost=0.1
        )
        assert token is not None

        decision = await funded_gate.evaluate(
            risky_proposal,
            agent="test-agent",
            bypass_token=token,
            judgment_score=0.3,  # Would fail standard path
        )

        assert decision.approved is True
        assert decision.bypassed is True
        assert decision.capital_spent == 0.1

    @pytest.mark.asyncio
    async def test_bypass_token_already_deducted(
        self, funded_gate: TrustGate, risky_proposal: Proposal
    ) -> None:
        """Bypass cost is deducted when token is minted, not on use."""
        initial_balance = funded_gate.capital_ledger.balance("test-agent")

        # Mint token (deducts cost)
        token = funded_gate.capital_ledger.mint_bypass(
            "test-agent", "trust_gate", cost=0.1
        )
        assert token is not None

        after_mint = funded_gate.capital_ledger.balance("test-agent")
        assert after_mint == initial_balance - 0.1

        # Use token (no additional deduction)
        await funded_gate.evaluate(
            risky_proposal,
            agent="test-agent",
            bypass_token=token,
            judgment_score=0.3,
        )

        after_use = funded_gate.capital_ledger.balance("test-agent")
        assert after_use == after_mint  # No change on use

    @pytest.mark.asyncio
    async def test_bypass_reason_includes_cost(
        self, funded_gate: TrustGate, risky_proposal: Proposal
    ) -> None:
        """Bypass decision includes cost in reason."""
        token = funded_gate.capital_ledger.mint_bypass(
            "test-agent", "trust_gate", cost=0.15
        )
        assert token is not None

        decision = await funded_gate.evaluate(
            risky_proposal,
            agent="test-agent",
            bypass_token=token,
            judgment_score=0.3,
        )

        assert "0.15" in decision.reason or "bypass" in decision.reason.lower()


# === Token Validation Tests ===


class TestTokenValidation:
    """Tests for bypass token validation."""

    @pytest.mark.asyncio
    async def test_reject_expired_token(
        self, funded_gate: TrustGate, risky_proposal: Proposal
    ) -> None:
        """Expired token is rejected."""
        # Create already-expired token
        from datetime import UTC, datetime

        now = datetime.now(UTC)
        expired_token = BypassToken(
            agent="test-agent",
            check_name="trust_gate",
            granted_at=now - timedelta(hours=2),
            expires_at=now - timedelta(hours=1),  # Expired
            cost=0.1,
            correlation_id="test-expired",
        )

        decision = await funded_gate.evaluate(
            risky_proposal,
            agent="test-agent",
            bypass_token=expired_token,
            judgment_score=0.3,
        )

        assert decision.approved is False
        assert (
            "expired" in decision.reason.lower() or "invalid" in decision.reason.lower()
        )

    @pytest.mark.asyncio
    async def test_reject_wrong_gate_token(
        self, funded_gate: TrustGate, risky_proposal: Proposal
    ) -> None:
        """Token for different gate is rejected."""
        # Mint token for different gate
        token = funded_gate.capital_ledger.mint_bypass(
            "test-agent",
            "other_gate",
            cost=0.1,  # Wrong gate
        )
        assert token is not None

        decision = await funded_gate.evaluate(
            risky_proposal,
            agent="test-agent",
            bypass_token=token,
            judgment_score=0.3,
        )

        assert decision.approved is False
        assert "other_gate" in decision.reason

    @pytest.mark.asyncio
    async def test_reject_insufficient_capital_for_token(
        self, gate: TrustGate, risky_proposal: Proposal
    ) -> None:
        """Cannot mint token without sufficient capital."""
        # Agent has only initial_capital (0.5)
        token = gate.capital_ledger.mint_bypass(
            "poor-agent",
            "trust_gate",
            cost=1.0,  # More than available
        )
        assert token is None  # Cannot mint


# === Algebraic Cost Tests ===


class TestAlgebraicCost:
    """Tests for algebraic cost computation."""

    def test_compute_bypass_cost(self, gate: TrustGate) -> None:
        """Bypass cost is computed algebraically."""
        cost = gate.compute_bypass_cost(
            risk=0.5,
            judgment_score=0.5,
            resources_ok=True,
        )
        assert cost > 0

    def test_high_risk_increases_cost(self, gate: TrustGate) -> None:
        """Higher risk increases bypass cost."""
        low_risk_cost = gate.compute_bypass_cost(
            risk=0.1, judgment_score=0.5, resources_ok=True
        )
        high_risk_cost = gate.compute_bypass_cost(
            risk=0.9, judgment_score=0.5, resources_ok=True
        )
        assert high_risk_cost > low_risk_cost

    def test_low_judgment_increases_cost(self, gate: TrustGate) -> None:
        """Lower judgment score increases bypass cost."""
        high_judgment_cost = gate.compute_bypass_cost(
            risk=0.5, judgment_score=0.9, resources_ok=True
        )
        low_judgment_cost = gate.compute_bypass_cost(
            risk=0.5, judgment_score=0.3, resources_ok=True
        )
        assert low_judgment_cost > high_judgment_cost

    def test_custom_cost_function(self, ledger: EventSourcedLedger) -> None:
        """Gate accepts custom cost function."""
        custom_cost = constant_cost(0.5, "fixed")
        gate = TrustGate(
            capital_ledger=ledger,
            cost_function=custom_cost,
        )

        cost = gate.compute_bypass_cost(
            risk=0.9,  # High risk ignored
            judgment_score=0.1,  # Low judgment ignored
            resources_ok=False,  # Resource penalty ignored
        )
        assert cost == 0.5  # Always 0.5


# === Factory Function Tests ===


class TestCreateTrustGate:
    """Tests for create_trust_gate factory."""

    def test_create_with_defaults(self) -> None:
        """Factory creates gate with defaults."""
        gate = create_trust_gate()

        assert gate.capital_ledger is not None
        assert gate.judgment_threshold == 0.8
        assert gate.risk_threshold == 0.3

    def test_create_with_custom_thresholds(self) -> None:
        """Factory accepts custom thresholds."""
        gate = create_trust_gate(
            judgment_threshold=0.9,
            risk_threshold=0.1,
            good_proposal_reward=0.05,
        )

        assert gate.judgment_threshold == 0.9
        assert gate.risk_threshold == 0.1
        assert gate.good_proposal_reward == 0.05

    def test_create_with_existing_ledger(
        self, funded_ledger: EventSourcedLedger
    ) -> None:
        """Factory accepts existing ledger."""
        gate = create_trust_gate(ledger=funded_ledger)

        assert gate.capital_ledger is funded_ledger
        # Verify funded agent exists
        assert gate.capital_ledger.balance("test-agent") > 0


# === OCap Pattern Tests ===


class TestOCapPattern:
    """Tests verifying OCap pattern adherence."""

    @pytest.mark.asyncio
    async def test_token_is_capability(
        self, funded_gate: TrustGate, risky_proposal: Proposal
    ) -> None:
        """Token IS the capability, not agent identity."""
        # Agent A mints token
        token = funded_gate.capital_ledger.mint_bypass(
            "agent-a", "trust_gate", cost=0.1
        )
        assert token is not None

        # Token can be used (token.agent matches, but we don't check caller)
        # In real OCap, whoever holds the token can use it
        decision = await funded_gate.evaluate(
            risky_proposal,
            agent="agent-a",  # Must match token.agent in our impl
            bypass_token=token,
            judgment_score=0.3,
        )

        assert decision.approved is True
        assert decision.bypassed is True

    @pytest.mark.asyncio
    async def test_no_token_means_no_bypass(
        self, funded_gate: TrustGate, risky_proposal: Proposal
    ) -> None:
        """Without token, bypass is unavailable."""
        decision = await funded_gate.evaluate(
            risky_proposal,
            agent="test-agent",
            bypass_token=None,  # No token
            judgment_score=0.3,
        )

        assert decision.approved is False
        assert decision.bypass_cost is not None  # Can get cost to acquire token


# === Integration Tests ===


class TestIntegration:
    """Integration tests with full flow."""

    @pytest.mark.asyncio
    async def test_full_bypass_flow(self, funded_gate: TrustGate) -> None:
        """Test complete bypass flow: deny → mint token → approve."""
        proposal = Proposal(
            agent="test-agent",
            action="risky operation",
            risk=0.8,
        )

        # Step 1: Initial evaluation denied
        decision1 = await funded_gate.evaluate(
            proposal,
            agent="test-agent",
            judgment_score=0.3,
        )
        assert decision1.approved is False
        bypass_cost = decision1.bypass_cost
        assert bypass_cost is not None

        # Step 2: Mint bypass token
        token = funded_gate.capital_ledger.mint_bypass(
            "test-agent", "trust_gate", cost=bypass_cost
        )
        assert token is not None

        # Step 3: Re-evaluate with token
        decision2 = await funded_gate.evaluate(
            proposal,
            agent="test-agent",
            bypass_token=token,
            judgment_score=0.3,
        )
        assert decision2.approved is True
        assert decision2.bypassed is True

    @pytest.mark.asyncio
    async def test_capital_accumulation(self, gate: TrustGate) -> None:
        """Good proposals accumulate capital over time."""
        agent = "good-agent"

        # Submit multiple good proposals
        for i in range(5):
            proposal = Proposal(
                agent=agent,
                action=f"good action {i}",
                risk=0.1,
            )
            await gate.evaluate(
                proposal,
                agent=agent,
                judgment_score=0.9,
            )

        # Agent should have accumulated capital
        balance = gate.capital_ledger.balance(agent)
        expected = gate.capital_ledger.initial_capital + (5 * gate.good_proposal_reward)
        assert abs(balance - expected) < 0.001


# === JudgeAgent Integration Tests ===


class TestJudgeAgentIntegration:
    """Tests for JudgeAgent integration."""

    @pytest.mark.asyncio
    async def test_heuristic_used_without_judge(
        self, gate: TrustGate, good_proposal: Proposal
    ) -> None:
        """Without JudgeAgent, heuristic is used."""
        # Gate has no judge_agent configured
        assert gate.judge_agent is None

        # Should use heuristic
        decision = await gate.evaluate(
            good_proposal,
            agent="test-agent",
        )

        # Heuristic gives ~0.7 for good_proposal (0.5 + 0.1 + 0.1 - 0.03)
        assert decision.judgment_score is not None
        assert 0.6 < decision.judgment_score < 0.8

    @pytest.mark.asyncio
    async def test_heuristic_used_for_low_risk(
        self, ledger: EventSourcedLedger
    ) -> None:
        """Low-risk proposals use heuristic even with JudgeAgent."""
        from unittest.mock import AsyncMock, MagicMock

        # Create mock JudgeAgent and Runtime
        mock_judge = MagicMock()
        mock_runtime = MagicMock()

        gate = TrustGate(
            capital_ledger=ledger,
            judge_agent=mock_judge,
            runtime=mock_runtime,
            llm_risk_threshold=0.5,  # Only use LLM for risk > 0.5
        )

        low_risk_proposal = Proposal(
            agent="test-agent",
            action="fix typo",
            risk=0.1,  # Below llm_risk_threshold
        )

        decision = await gate.evaluate(
            low_risk_proposal,
            agent="test-agent",
        )

        # JudgeAgent should NOT be called for low-risk
        mock_judge.execute_async.assert_not_called()
        assert decision.judgment_score is not None

    @pytest.mark.asyncio
    async def test_judge_called_for_high_risk(self, ledger: EventSourcedLedger) -> None:
        """High-risk proposals use JudgeAgent when available."""
        from dataclasses import dataclass
        from unittest.mock import AsyncMock, MagicMock

        # Create a mock JudgmentResult
        @dataclass
        class MockJudgmentResult:
            correctness: float = 0.9
            safety: float = 0.8
            style: float = 0.7
            weighted_score: float = 0.85
            explanation: str = "Good proposal"

        mock_judge = MagicMock()
        mock_judge.execute_async = AsyncMock(return_value=MockJudgmentResult())

        mock_runtime = MagicMock()

        gate = TrustGate(
            capital_ledger=ledger,
            judge_agent=mock_judge,
            runtime=mock_runtime,
            llm_risk_threshold=0.5,
        )

        high_risk_proposal = Proposal(
            agent="test-agent",
            action="delete database",
            diff="DROP TABLE users;",
            context={"dangerous": True},
            risk=0.8,  # Above llm_risk_threshold
        )

        decision = await gate.evaluate(
            high_risk_proposal,
            agent="test-agent",
        )

        # JudgeAgent SHOULD be called for high-risk
        mock_judge.execute_async.assert_called_once()
        # Judgment score should be from JudgeAgent
        assert decision.judgment_score == 0.85

    @pytest.mark.asyncio
    async def test_fallback_on_judge_failure(self, ledger: EventSourcedLedger) -> None:
        """Falls back to heuristic when JudgeAgent fails."""
        from unittest.mock import AsyncMock, MagicMock

        mock_judge = MagicMock()
        mock_judge.execute_async = AsyncMock(side_effect=Exception("LLM API error"))

        mock_runtime = MagicMock()

        gate = TrustGate(
            capital_ledger=ledger,
            judge_agent=mock_judge,
            runtime=mock_runtime,
            llm_risk_threshold=0.5,
        )

        high_risk_proposal = Proposal(
            agent="test-agent",
            action="risky action",
            risk=0.8,
        )

        # Should not raise, should fall back to heuristic
        decision = await gate.evaluate(
            high_risk_proposal,
            agent="test-agent",
        )

        # JudgeAgent was called but failed
        mock_judge.execute_async.assert_called_once()
        # Should have fallen back to heuristic
        assert decision.judgment_score is not None
        # Heuristic gives ~0.26 for high-risk (0.5 - 0.24)
        assert 0.2 < decision.judgment_score < 0.4

    @pytest.mark.asyncio
    async def test_create_trust_gate_with_judge(self) -> None:
        """create_trust_gate accepts JudgeAgent and Runtime."""
        from unittest.mock import MagicMock

        mock_judge = MagicMock()
        mock_runtime = MagicMock()

        gate = create_trust_gate(
            judge_agent=mock_judge,
            runtime=mock_runtime,
            llm_risk_threshold=0.3,
        )

        assert gate.judge_agent is mock_judge
        assert gate.runtime is mock_runtime
        assert gate.llm_risk_threshold == 0.3
