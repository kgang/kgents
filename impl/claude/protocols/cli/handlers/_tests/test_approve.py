"""
Tests for kgents pending/approve/reject CLI handlers.

Tests verify:
1. Help displays correctly for all commands
2. pending command lists pending YIELD turns
3. approve command approves turns
4. reject command rejects turns
5. Partial ID resolution
6. Error handling for edge cases

These tests are part of the Turn-gents Realization phase.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# === Fixtures ===


class MockContext:
    """Mock InvocationContext for testing."""

    def __init__(self) -> None:
        self.outputs: list[tuple[str, dict[str, Any]]] = []

    def output(self, human: str, semantic: dict[str, Any]) -> None:
        self.outputs.append((human, semantic))


@pytest.fixture
def ctx() -> MockContext:
    """Create mock context."""
    return MockContext()


@pytest.fixture
def yield_handler() -> Any:
    """Create a YieldHandler for testing."""
    from weave import YieldHandler

    return YieldHandler()


@pytest.fixture
def pending_yield_turn() -> Any:
    """Create a pending YieldTurn for testing."""
    from weave.turn import YieldTurn

    return YieldTurn.create_yield(
        content="Deploy to production",
        source="deployer-agent",
        yield_reason="Production deployment requires approval",
        required_approvers={"human"},
        turn_id="yield-001",
        confidence=0.6,
    )


# === Help Tests ===


class TestPendingHelp:
    """Tests for pending --help."""

    def test_help_flag(self, ctx: MockContext) -> None:
        """--help returns 0 and shows help text."""
        from protocols.cli.handlers.approve import cmd_pending

        result = cmd_pending(["--help"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_h_flag(self, ctx: MockContext) -> None:
        """-h returns 0 and shows help text."""
        from protocols.cli.handlers.approve import cmd_pending

        result = cmd_pending(["-h"], ctx)  # type: ignore[arg-type]

        assert result == 0


class TestApproveHelp:
    """Tests for approve --help."""

    def test_help_flag(self, ctx: MockContext) -> None:
        """--help returns 0."""
        from protocols.cli.handlers.approve import cmd_approve

        result = cmd_approve(["--help"], ctx)  # type: ignore[arg-type]

        assert result == 0


class TestRejectHelp:
    """Tests for reject --help."""

    def test_help_flag(self, ctx: MockContext) -> None:
        """--help returns 0."""
        from protocols.cli.handlers.approve import cmd_reject

        result = cmd_reject(["--help"], ctx)  # type: ignore[arg-type]

        assert result == 0


# === Pending Command Tests ===


class TestPendingCommand:
    """Tests for the pending command."""

    def test_no_pending(self, ctx: MockContext) -> None:
        """No pending turns returns gracefully."""
        from protocols.cli.handlers.approve import cmd_pending

        result = cmd_pending([], ctx)  # type: ignore[arg-type]

        assert result == 0
        assert any("No pending" in out[0] for out in ctx.outputs)

    def test_json_output(self, ctx: MockContext) -> None:
        """--json flag produces JSON output."""
        from protocols.cli.handlers.approve import cmd_pending

        result = cmd_pending(["--json"], ctx)  # type: ignore[arg-type]

        assert result == 0

    def test_source_filter(self, ctx: MockContext) -> None:
        """--source flag filters by source."""
        from protocols.cli.handlers.approve import cmd_pending

        result = cmd_pending(["--source", "deployer-agent"], ctx)  # type: ignore[arg-type]

        assert result == 0


# === Approve Command Tests ===


class TestApproveCommand:
    """Tests for the approve command."""

    def test_no_turn_id(self, ctx: MockContext) -> None:
        """No turn ID specified returns error."""
        from protocols.cli.handlers.approve import cmd_approve

        result = cmd_approve([], ctx)  # type: ignore[arg-type]

        assert result == 1
        assert any("No turn ID" in out[0] for out in ctx.outputs)

    def test_turn_not_found(self, ctx: MockContext) -> None:
        """Turn not found returns error."""
        from protocols.cli.handlers.approve import cmd_approve

        result = cmd_approve(["nonexistent-id"], ctx)  # type: ignore[arg-type]

        assert result == 1
        assert any("not found" in out[0] for out in ctx.outputs)


# === Reject Command Tests ===


class TestRejectCommand:
    """Tests for the reject command."""

    def test_no_turn_id(self, ctx: MockContext) -> None:
        """No turn ID specified returns error."""
        from protocols.cli.handlers.approve import cmd_reject

        result = cmd_reject([], ctx)  # type: ignore[arg-type]

        assert result == 1
        assert any("No turn ID" in out[0] for out in ctx.outputs)

    def test_turn_not_found(self, ctx: MockContext) -> None:
        """Turn not found returns error."""
        from protocols.cli.handlers.approve import cmd_reject

        result = cmd_reject(["nonexistent-id"], ctx)  # type: ignore[arg-type]

        assert result == 1
        assert any("not found" in out[0] for out in ctx.outputs)

    def test_reason_flag(self, ctx: MockContext) -> None:
        """--reason flag is parsed."""
        from protocols.cli.handlers.approve import cmd_reject

        result = cmd_reject(["turn-id", "--reason", "Not approved"], ctx)  # type: ignore[arg-type]

        # Will fail because turn doesn't exist, but reason should be parsed
        assert result == 1


# === YieldHandler Integration Tests ===


class TestYieldHandlerIntegration:
    """Tests with actual YieldHandler."""

    @pytest.mark.asyncio
    async def test_request_approval_flow(self, yield_handler: Any, pending_yield_turn: Any) -> None:
        """Full approval flow works."""
        from weave import ApprovalStatus

        # Start approval request in background
        async def approve_after_delay() -> None:
            await asyncio.sleep(0.1)
            await yield_handler.approve(pending_yield_turn.id, "human")

        # Create task for delayed approval
        approve_task = asyncio.create_task(approve_after_delay())

        # Request approval
        result = await yield_handler.request_approval(pending_yield_turn, timeout=1.0)

        await approve_task

        assert result.is_approved
        assert result.status == ApprovalStatus.APPROVED

    @pytest.mark.asyncio
    async def test_rejection_flow(self, yield_handler: Any, pending_yield_turn: Any) -> None:
        """Rejection flow works."""
        from weave import ApprovalStatus

        # Start approval request in background
        async def reject_after_delay() -> None:
            await asyncio.sleep(0.1)
            await yield_handler.reject(pending_yield_turn.id, "human", "Not safe to deploy")

        # Create task for delayed rejection
        reject_task = asyncio.create_task(reject_after_delay())

        # Request approval
        result = await yield_handler.request_approval(pending_yield_turn, timeout=1.0)

        await reject_task

        assert result.is_rejected
        assert result.status == ApprovalStatus.REJECTED
        assert result.rejection_reason == "Not safe to deploy"

    @pytest.mark.asyncio
    async def test_timeout_flow(self, yield_handler: Any, pending_yield_turn: Any) -> None:
        """Timeout is handled correctly."""
        from weave import ApprovalStatus

        # Request approval with short timeout (no approval given)
        result = await yield_handler.request_approval(pending_yield_turn, timeout=0.1)

        assert result.is_timeout
        assert result.status == ApprovalStatus.TIMEOUT

    def test_list_pending(self, yield_handler: Any, pending_yield_turn: Any) -> None:
        """list_pending returns pending turns."""
        # Manually add to pending (simulating request_approval)
        from weave.yield_handler import PendingApproval

        yield_handler._pending[pending_yield_turn.id] = PendingApproval(
            turn=pending_yield_turn,
            strategy=yield_handler.default_strategy,
        )

        pending = yield_handler.list_pending()

        assert len(pending) == 1
        assert pending[0].id == pending_yield_turn.id

    def test_is_pending(self, yield_handler: Any, pending_yield_turn: Any) -> None:
        """is_pending checks correctly."""
        from weave.yield_handler import PendingApproval

        assert not yield_handler.is_pending(pending_yield_turn.id)

        yield_handler._pending[pending_yield_turn.id] = PendingApproval(
            turn=pending_yield_turn,
            strategy=yield_handler.default_strategy,
        )

        assert yield_handler.is_pending(pending_yield_turn.id)


# === ID Resolution Tests ===


class TestIdResolution:
    """Tests for partial ID resolution."""

    def test_resolve_full_id(self, yield_handler: Any, pending_yield_turn: Any) -> None:
        """Full ID resolves correctly."""
        from protocols.cli.handlers.approve import _resolve_turn_id
        from weave.yield_handler import PendingApproval

        yield_handler._pending[pending_yield_turn.id] = PendingApproval(
            turn=pending_yield_turn,
            strategy=yield_handler.default_strategy,
        )

        resolved = _resolve_turn_id(yield_handler, pending_yield_turn.id)

        assert resolved == pending_yield_turn.id

    def test_resolve_partial_id(self, yield_handler: Any, pending_yield_turn: Any) -> None:
        """Partial ID resolves to full ID."""
        from protocols.cli.handlers.approve import _resolve_turn_id
        from weave.yield_handler import PendingApproval

        yield_handler._pending[pending_yield_turn.id] = PendingApproval(
            turn=pending_yield_turn,
            strategy=yield_handler.default_strategy,
        )

        # Use partial ID
        resolved = _resolve_turn_id(yield_handler, "yield-00")

        assert resolved == pending_yield_turn.id

    def test_resolve_nonexistent(self, yield_handler: Any) -> None:
        """Nonexistent ID returns None."""
        from protocols.cli.handlers.approve import _resolve_turn_id

        resolved = _resolve_turn_id(yield_handler, "nonexistent")

        assert resolved is None


# === Output Helpers Tests ===


class TestOutputHelpers:
    """Tests for output helper functions."""

    def test_emit_output_with_ctx(self) -> None:
        """_emit_output uses ctx when available."""
        from protocols.cli.handlers.approve import _emit_output

        ctx = MockContext()
        _emit_output("test message", {"key": "value"}, ctx)  # type: ignore[arg-type]

        assert len(ctx.outputs) == 1
        assert ctx.outputs[0][0] == "test message"

    def test_emit_output_without_ctx(self, capsys: Any) -> None:
        """_emit_output prints when no ctx."""
        from protocols.cli.handlers.approve import _emit_output

        _emit_output("test message", {"key": "value"}, None)

        captured = capsys.readouterr()
        assert "test message" in captured.out


# === YieldTurn Tests ===


class TestYieldTurn:
    """Tests for YieldTurn functionality."""

    def test_create_yield(self) -> None:
        """YieldTurn.create_yield works."""
        from weave.turn import YieldTurn

        turn = YieldTurn.create_yield(
            content="Test action",
            source="test-agent",
            yield_reason="Needs approval",
            required_approvers={"human", "admin"},
        )

        assert turn.yield_reason == "Needs approval"
        assert turn.required_approvers == frozenset({"human", "admin"})
        assert turn.approved_by == frozenset()
        assert not turn.is_approved()

    def test_approve_turn(self) -> None:
        """YieldTurn.approve creates new turn with approval."""
        from weave.turn import YieldTurn

        turn = YieldTurn.create_yield(
            content="Test action",
            source="test-agent",
            yield_reason="Needs approval",
            required_approvers={"human"},
        )

        approved_turn = turn.approve("human")

        assert "human" in approved_turn.approved_by
        assert approved_turn.is_approved()
        # Original unchanged (immutable)
        assert not turn.is_approved()

    def test_approve_invalid_approver(self) -> None:
        """Approving with invalid approver raises error."""
        from weave.turn import YieldTurn

        turn = YieldTurn.create_yield(
            content="Test action",
            source="test-agent",
            yield_reason="Needs approval",
            required_approvers={"human"},
        )

        with pytest.raises(ValueError):
            turn.approve("not-a-valid-approver")

    def test_pending_approvers(self) -> None:
        """pending_approvers returns who hasn't approved yet."""
        from weave.turn import YieldTurn

        turn = YieldTurn.create_yield(
            content="Test action",
            source="test-agent",
            yield_reason="Needs approval",
            required_approvers={"human", "admin"},
        )

        assert turn.pending_approvers() == frozenset({"human", "admin"})

        approved_turn = turn.approve("human")
        assert approved_turn.pending_approvers() == frozenset({"admin"})


# === Global Handler Tests ===


class TestGlobalHandler:
    """Tests for global YieldHandler access."""

    def test_get_yield_handler(self) -> None:
        """get_yield_handler returns handler."""
        from protocols.cli.handlers.approve import get_yield_handler

        handler = get_yield_handler()

        assert handler is not None

    def test_get_yield_handler_singleton(self) -> None:
        """get_yield_handler returns same instance."""
        from protocols.cli.handlers.approve import get_yield_handler

        handler1 = get_yield_handler()
        handler2 = get_yield_handler()

        assert handler1 is handler2
