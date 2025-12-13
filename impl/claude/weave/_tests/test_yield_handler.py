"""
Tests for YieldHandler - Phase 5 of Turn-gents Protocol.

Tests cover:
1. YieldHandler approval flow
2. Approval strategies (All, Any, Majority)
3. Rejection handling
4. Timeout handling
5. Multi-party approval
6. Integration with TurnBasedAdapter
7. Soul intercept (should_yield heuristics)
"""

import asyncio

import pytest

from ..turn import TurnType, YieldTurn
from ..yield_handler import (
    ApprovalResult,
    ApprovalStatus,
    ApprovalStrategy,
    PendingApproval,
    YieldHandler,
    compute_risk_score,
    should_yield,
)


class TestApprovalStrategy:
    """Tests for approval strategy enum."""

    def test_three_strategies_exist(self) -> None:
        """All three approval strategies should exist."""
        assert ApprovalStrategy.ALL
        assert ApprovalStrategy.ANY
        assert ApprovalStrategy.MAJORITY

    def test_strategies_are_distinct(self) -> None:
        """Strategies should be distinct values."""
        # Explicit value comparison to satisfy mypy
        assert ApprovalStrategy.ALL.value != ApprovalStrategy.ANY.value
        assert ApprovalStrategy.ANY.value != ApprovalStrategy.MAJORITY.value
        assert ApprovalStrategy.ALL.value != ApprovalStrategy.MAJORITY.value


class TestApprovalStatus:
    """Tests for approval status enum."""

    def test_four_statuses_exist(self) -> None:
        """All four statuses should exist."""
        assert ApprovalStatus.PENDING
        assert ApprovalStatus.APPROVED
        assert ApprovalStatus.REJECTED
        assert ApprovalStatus.TIMEOUT


class TestApprovalResult:
    """Tests for ApprovalResult dataclass."""

    def test_approved_result(self) -> None:
        """Test approved result properties."""
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"approver"},
        )
        result = ApprovalResult(status=ApprovalStatus.APPROVED, turn=turn)

        assert result.is_approved
        assert not result.is_rejected
        assert not result.is_timeout
        assert not result.is_pending

    def test_rejected_result(self) -> None:
        """Test rejected result properties."""
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"approver"},
        )
        result = ApprovalResult(
            status=ApprovalStatus.REJECTED,
            turn=turn,
            rejected_by="reviewer",
            rejection_reason="Not allowed",
        )

        assert not result.is_approved
        assert result.is_rejected
        assert result.rejected_by == "reviewer"
        assert result.rejection_reason == "Not allowed"

    def test_timeout_result(self) -> None:
        """Test timeout result properties."""
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"approver"},
        )
        result = ApprovalResult(
            status=ApprovalStatus.TIMEOUT, turn=turn, timeout_duration=5.0
        )

        assert not result.is_approved
        assert result.is_timeout
        assert result.timeout_duration == 5.0


class TestPendingApproval:
    """Tests for PendingApproval internal state."""

    def test_all_strategy_not_satisfied_initially(self) -> None:
        """ALL strategy requires all approvers."""
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice", "bob"},
        )
        pending = PendingApproval(turn=turn, strategy=ApprovalStrategy.ALL)

        assert not pending.is_satisfied()

    def test_all_strategy_satisfied_after_all_approve(self) -> None:
        """ALL strategy satisfied when all approve."""
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice", "bob"},
        )
        turn = turn.approve("alice")
        turn = turn.approve("bob")

        pending = PendingApproval(turn=turn, strategy=ApprovalStrategy.ALL)
        assert pending.is_satisfied()

    def test_any_strategy_satisfied_after_one(self) -> None:
        """ANY strategy satisfied after first approval."""
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice", "bob"},
        )
        turn = turn.approve("alice")

        pending = PendingApproval(turn=turn, strategy=ApprovalStrategy.ANY)
        assert pending.is_satisfied()

    def test_majority_strategy_needs_half(self) -> None:
        """MAJORITY strategy requires >50%."""
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice", "bob", "charlie"},
        )

        # 1 of 3 not satisfied
        turn1 = turn.approve("alice")
        pending1 = PendingApproval(turn=turn1, strategy=ApprovalStrategy.MAJORITY)
        assert not pending1.is_satisfied()

        # 2 of 3 satisfied
        turn2 = turn1.approve("bob")
        pending2 = PendingApproval(turn=turn2, strategy=ApprovalStrategy.MAJORITY)
        assert pending2.is_satisfied()

    def test_rejection_always_satisfies(self) -> None:
        """Rejection terminates the approval flow."""
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice", "bob"},
        )
        pending = PendingApproval(
            turn=turn,
            strategy=ApprovalStrategy.ALL,
            rejector="alice",
            rejection_reason="No",
        )

        assert pending.is_satisfied()


class TestYieldHandler:
    """Tests for YieldHandler core functionality."""

    @pytest.mark.asyncio
    async def test_immediate_approval_no_approvers(self) -> None:
        """Turn with no approvers is immediately approved."""
        handler = YieldHandler()
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers=set(),
        )

        result = await handler.request_approval(turn)

        assert result.is_approved
        assert result.status == ApprovalStatus.APPROVED

    @pytest.mark.asyncio
    async def test_approval_flow_single_approver(self) -> None:
        """Single approver flow works correctly."""
        handler = YieldHandler()
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice"},
        )

        async def approve_later() -> None:
            await asyncio.sleep(0.01)
            await handler.approve(turn.id, "alice")

        task = asyncio.create_task(approve_later())
        result = await handler.request_approval(turn)
        await task

        assert result.is_approved

    @pytest.mark.asyncio
    async def test_rejection_flow(self) -> None:
        """Rejection terminates approval flow."""
        handler = YieldHandler()
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice"},
        )

        async def reject_later() -> None:
            await asyncio.sleep(0.01)
            await handler.reject(turn.id, "alice", "Not allowed")

        task = asyncio.create_task(reject_later())
        result = await handler.request_approval(turn)
        await task

        assert result.is_rejected
        assert result.rejected_by == "alice"
        assert result.rejection_reason == "Not allowed"

    @pytest.mark.asyncio
    async def test_timeout_flow(self) -> None:
        """Timeout returns timeout status."""
        handler = YieldHandler()
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice"},
        )

        result = await handler.request_approval(turn, timeout=0.01)

        assert result.is_timeout
        assert result.timeout_duration == 0.01

    @pytest.mark.asyncio
    async def test_any_strategy_first_wins(self) -> None:
        """ANY strategy completes after first approval."""
        handler = YieldHandler()
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice", "bob"},
        )

        async def approve_later() -> None:
            await asyncio.sleep(0.01)
            await handler.approve(turn.id, "alice")

        task = asyncio.create_task(approve_later())
        result = await handler.request_approval(turn, strategy=ApprovalStrategy.ANY)
        await task

        assert result.is_approved
        # Only alice approved, not bob
        assert result.turn.approved_by == frozenset({"alice"})

    @pytest.mark.asyncio
    async def test_multi_party_approval(self) -> None:
        """Multiple approvers can approve in sequence."""
        handler = YieldHandler()
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice", "bob", "charlie"},
        )

        async def approve_all() -> None:
            await asyncio.sleep(0.01)
            await handler.approve(turn.id, "alice")
            await asyncio.sleep(0.01)
            await handler.approve(turn.id, "bob")
            await asyncio.sleep(0.01)
            await handler.approve(turn.id, "charlie")

        task = asyncio.create_task(approve_all())
        result = await handler.request_approval(turn)
        await task

        assert result.is_approved
        assert result.turn.approved_by == frozenset({"alice", "bob", "charlie"})

    @pytest.mark.asyncio
    async def test_approve_invalid_turn_returns_false(self) -> None:
        """Approving unknown turn returns False."""
        handler = YieldHandler()

        result = await handler.approve("nonexistent", "alice")
        assert result is False

    @pytest.mark.asyncio
    async def test_reject_invalid_turn_returns_false(self) -> None:
        """Rejecting unknown turn returns False."""
        handler = YieldHandler()

        result = await handler.reject("nonexistent", "alice", "reason")
        assert result is False

    @pytest.mark.asyncio
    async def test_approve_invalid_approver_raises(self) -> None:
        """Approving with invalid approver raises ValueError."""
        handler = YieldHandler()
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice"},
        )

        # Start the approval request in background
        async def try_approve() -> None:
            await asyncio.sleep(0.01)
            with pytest.raises(ValueError):
                await handler.approve(turn.id, "bob")  # bob not in required
            # Then reject to end the test
            await handler.reject(turn.id, "alice", "test")

        task = asyncio.create_task(try_approve())
        await handler.request_approval(turn, timeout=0.1)
        await task

    def test_list_pending(self) -> None:
        """Can list pending approvals."""
        handler = YieldHandler()

        # Initially empty
        assert handler.list_pending() == []

    def test_is_pending(self) -> None:
        """Can check if turn is pending."""
        handler = YieldHandler()

        assert not handler.is_pending("nonexistent")


class TestShouldYield:
    """Tests for should_yield heuristic."""

    def test_low_confidence_action_yields(self) -> None:
        """Low confidence ACTION should yield."""
        assert should_yield(confidence=0.2, yield_threshold=0.3, turn_type="ACTION")

    def test_high_confidence_action_does_not_yield(self) -> None:
        """High confidence ACTION should not yield."""
        assert not should_yield(confidence=0.8, yield_threshold=0.3, turn_type="ACTION")

    def test_speech_never_yields(self) -> None:
        """SPEECH never yields regardless of confidence."""
        assert not should_yield(confidence=0.1, yield_threshold=0.3, turn_type="SPEECH")

    def test_thought_never_yields(self) -> None:
        """THOUGHT never yields regardless of confidence."""
        assert not should_yield(
            confidence=0.1, yield_threshold=0.3, turn_type="THOUGHT"
        )

    def test_boundary_confidence(self) -> None:
        """Boundary confidence exactly at threshold does not yield."""
        assert not should_yield(confidence=0.3, yield_threshold=0.3, turn_type="ACTION")

    def test_just_below_threshold(self) -> None:
        """Just below threshold should yield."""
        assert should_yield(confidence=0.29, yield_threshold=0.3, turn_type="ACTION")


class TestComputeRiskScore:
    """Tests for compute_risk_score function."""

    def test_high_confidence_low_risk(self) -> None:
        """High confidence gives low risk score."""
        score = compute_risk_score(confidence=1.0, entropy_cost=0.0)
        assert score == 0.0

    def test_low_confidence_higher_risk(self) -> None:
        """Low confidence gives higher risk score."""
        score = compute_risk_score(confidence=0.0, entropy_cost=0.0)
        assert score == 1.0

    def test_entropy_cost_increases_risk(self) -> None:
        """Higher entropy cost increases risk."""
        score1 = compute_risk_score(confidence=0.5, entropy_cost=0.0)
        score2 = compute_risk_score(confidence=0.5, entropy_cost=1.0)
        assert score2 > score1

    def test_destructive_doubles_risk(self) -> None:
        """Destructive actions double the risk."""
        score1 = compute_risk_score(confidence=0.5, entropy_cost=0.0)
        score2 = compute_risk_score(
            confidence=0.5, entropy_cost=0.0, is_destructive=True
        )
        assert score2 == score1 * 2.0

    def test_external_effects_increase_risk(self) -> None:
        """External effects increase risk by 50%."""
        score1 = compute_risk_score(confidence=0.5, entropy_cost=0.0)
        score2 = compute_risk_score(
            confidence=0.5, entropy_cost=0.0, has_external_effects=True
        )
        assert score2 == score1 * 1.5

    def test_combined_modifiers(self) -> None:
        """Both modifiers compound."""
        score1 = compute_risk_score(confidence=0.5, entropy_cost=0.0)
        score2 = compute_risk_score(
            confidence=0.5,
            entropy_cost=0.0,
            is_destructive=True,
            has_external_effects=True,
        )
        assert score2 == score1 * 2.0 * 1.5


class TestYieldHandlerCallbacks:
    """Tests for YieldHandler callback mechanism."""

    @pytest.mark.asyncio
    async def test_on_approval_callback(self) -> None:
        """Approval callback is called on approval."""
        handler = YieldHandler()
        callback_called = []

        def on_approve(turn: YieldTurn) -> None:  # type: ignore
            callback_called.append(turn.id)

        handler.on_approval(on_approve)

        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice"},
        )

        async def approve_later() -> None:
            await asyncio.sleep(0.01)
            await handler.approve(turn.id, "alice")

        task = asyncio.create_task(approve_later())
        await handler.request_approval(turn)
        await task

        assert turn.id in callback_called

    @pytest.mark.asyncio
    async def test_on_rejection_callback(self) -> None:
        """Rejection callback is called on rejection."""
        handler = YieldHandler()
        callback_data: list[tuple[str, str, str]] = []

        def on_reject(turn: YieldTurn, rejector: str, reason: str) -> None:  # type: ignore
            callback_data.append((turn.id, rejector, reason))

        handler.on_rejection(on_reject)

        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice"},
        )

        async def reject_later() -> None:
            await asyncio.sleep(0.01)
            await handler.reject(turn.id, "alice", "denied")

        task = asyncio.create_task(reject_later())
        await handler.request_approval(turn)
        await task

        assert len(callback_data) == 1
        assert callback_data[0] == (turn.id, "alice", "denied")

    @pytest.mark.asyncio
    async def test_on_timeout_callback(self) -> None:
        """Timeout callback is called on timeout."""
        handler = YieldHandler()
        callback_called: list[str] = []

        def on_timeout(turn: YieldTurn) -> None:  # type: ignore
            callback_called.append(turn.id)

        handler.on_timeout(on_timeout)

        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice"},
        )

        await handler.request_approval(turn, timeout=0.01)

        assert turn.id in callback_called


class TestMajorityEdgeCases:
    """Edge case tests for majority approval strategy."""

    def test_majority_of_two(self) -> None:
        """Majority of 2 requires 2 (>50% = >1 = 2)."""
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice", "bob"},
        )

        # 1 of 2 not satisfied
        turn1 = turn.approve("alice")
        pending1 = PendingApproval(turn=turn1, strategy=ApprovalStrategy.MAJORITY)
        assert not pending1.is_satisfied()

        # 2 of 2 satisfied
        turn2 = turn1.approve("bob")
        pending2 = PendingApproval(turn=turn2, strategy=ApprovalStrategy.MAJORITY)
        assert pending2.is_satisfied()

    def test_majority_of_one(self) -> None:
        """Majority of 1 requires 1."""
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"alice"},
        )

        turn1 = turn.approve("alice")
        pending = PendingApproval(turn=turn1, strategy=ApprovalStrategy.MAJORITY)
        assert pending.is_satisfied()

    def test_majority_of_four(self) -> None:
        """Majority of 4 requires 3 (>50% = >2 = 3)."""
        turn = YieldTurn.create_yield(
            content="test",
            source="agent",
            yield_reason="test",
            required_approvers={"a", "b", "c", "d"},
        )

        # 2 of 4 not satisfied
        turn2 = turn.approve("a").approve("b")
        pending2 = PendingApproval(turn=turn2, strategy=ApprovalStrategy.MAJORITY)
        assert not pending2.is_satisfied()

        # 3 of 4 satisfied
        turn3 = turn2.approve("c")
        pending3 = PendingApproval(turn=turn3, strategy=ApprovalStrategy.MAJORITY)
        assert pending3.is_satisfied()
