"""
Tests for ConfirmationManager: L2 Suggestion Confirmation Flow.

Verifies:
- Suggestion submission
- Confirmation flow
- Rejection flow
- Expiration handling
- Metrics tracking
"""

from datetime import datetime, timedelta

import pytest

from services.witness.trust.confirmation import (
    ActionPreview,
    ConfirmationManager,
    ConfirmationResult,
    PendingSuggestion,
    SuggestionStatus,
)

# =============================================================================
# PendingSuggestion Tests
# =============================================================================


class TestPendingSuggestion:
    """Tests for PendingSuggestion."""

    def test_not_expired_when_fresh(self) -> None:
        """Fresh suggestion is not expired."""
        suggestion = PendingSuggestion(
            id="sug-test",
            action="test action",
            target=None,
            rationale="test reason",
            preview=ActionPreview(description="test"),
            confidence=0.8,
            expires_at=datetime.now() + timedelta(hours=1),
        )

        assert not suggestion.is_expired

    def test_expired_when_past_deadline(self) -> None:
        """Suggestion is expired when past deadline."""
        suggestion = PendingSuggestion(
            id="sug-test",
            action="test action",
            target=None,
            rationale="test reason",
            preview=ActionPreview(description="test"),
            confidence=0.8,
            expires_at=datetime.now() - timedelta(hours=1),
        )

        assert suggestion.is_expired

    def test_time_remaining_positive(self) -> None:
        """time_remaining is positive when not expired."""
        suggestion = PendingSuggestion(
            id="sug-test",
            action="test action",
            target=None,
            rationale="test reason",
            preview=ActionPreview(description="test"),
            confidence=0.8,
            expires_at=datetime.now() + timedelta(minutes=30),
        )

        assert suggestion.time_remaining > timedelta(0)

    def test_time_remaining_zero_when_expired(self) -> None:
        """time_remaining is zero when expired."""
        suggestion = PendingSuggestion(
            id="sug-test",
            action="test action",
            target=None,
            rationale="test reason",
            preview=ActionPreview(description="test"),
            confidence=0.8,
            expires_at=datetime.now() - timedelta(hours=1),
        )

        assert suggestion.time_remaining == timedelta(0)

    def test_to_display(self) -> None:
        """to_display formats for human review."""
        suggestion = PendingSuggestion(
            id="sug-test",
            action="git commit -m 'fix'",
            target="src/main.py",
            rationale="Detected uncommitted fix",
            preview=ActionPreview(
                description="Commit changes",
                affected_files=["src/main.py"],
                risk_level="low",
            ),
            confidence=0.85,
        )

        display = suggestion.to_display()

        assert display["id"] == "sug-test"
        assert display["action"] == "git commit -m 'fix'"
        assert display["confidence"] == "85%"
        assert "src/main.py" in display["preview"]["affected_files"]


# =============================================================================
# ConfirmationManager Tests
# =============================================================================


class TestConfirmationManager:
    """Tests for ConfirmationManager."""

    @pytest.fixture
    def manager(self) -> ConfirmationManager:
        """Create a confirmation manager for testing."""
        return ConfirmationManager()

    @pytest.mark.asyncio
    async def test_submit_creates_pending(self, manager: ConfirmationManager) -> None:
        """submit creates a pending suggestion."""
        suggestion = await manager.submit(
            action="git commit -m 'fix'",
            rationale="Detected uncommitted fix",
            confidence=0.85,
        )

        assert suggestion.id.startswith("sug-")
        assert suggestion.status == SuggestionStatus.PENDING
        assert suggestion.action == "git commit -m 'fix'"
        assert manager.total_submitted == 1

    @pytest.mark.asyncio
    async def test_submit_with_target(self, manager: ConfirmationManager) -> None:
        """submit with target parameter."""
        suggestion = await manager.submit(
            action="format",
            target="src/main.py",
            rationale="File needs formatting",
            confidence=0.9,
        )

        assert suggestion.target == "src/main.py"

    @pytest.mark.asyncio
    async def test_submit_with_preview(self, manager: ConfirmationManager) -> None:
        """submit with custom preview."""
        preview = ActionPreview(
            description="Format Python file",
            affected_files=["src/main.py"],
            risk_level="low",
        )

        suggestion = await manager.submit(
            action="format",
            rationale="File needs formatting",
            preview=preview,
        )

        assert suggestion.preview.risk_level == "low"

    @pytest.mark.asyncio
    async def test_confirm_accepts_suggestion(self, manager: ConfirmationManager) -> None:
        """confirm accepts a pending suggestion."""
        suggestion = await manager.submit(
            action="test action",
            rationale="test",
        )

        result = await manager.confirm(suggestion.id)

        assert result.accepted
        assert manager.total_confirmed == 1

    @pytest.mark.asyncio
    async def test_confirm_unknown_suggestion(self, manager: ConfirmationManager) -> None:
        """confirm with unknown ID returns error."""
        result = await manager.confirm("unknown-id")

        assert not result.accepted
        assert result.error == "Suggestion not found"

    @pytest.mark.asyncio
    async def test_confirm_removes_from_pending(self, manager: ConfirmationManager) -> None:
        """confirm removes suggestion from pending."""
        suggestion = await manager.submit(action="test", rationale="test")

        await manager.confirm(suggestion.id)

        assert manager.get_suggestion(suggestion.id) is None

    @pytest.mark.asyncio
    async def test_reject_rejects_suggestion(self, manager: ConfirmationManager) -> None:
        """reject rejects a pending suggestion."""
        suggestion = await manager.submit(action="test", rationale="test")

        result = await manager.reject(suggestion.id, reason="Not needed")

        assert not result.accepted
        assert manager.total_rejected == 1

    @pytest.mark.asyncio
    async def test_reject_unknown_suggestion(self, manager: ConfirmationManager) -> None:
        """reject with unknown ID returns error."""
        result = await manager.reject("unknown-id")

        assert not result.accepted
        assert result.error == "Suggestion not found"

    @pytest.mark.asyncio
    async def test_get_pending_returns_only_pending(self, manager: ConfirmationManager) -> None:
        """get_pending returns only pending suggestions."""
        s1 = await manager.submit(action="test1", rationale="test")
        s2 = await manager.submit(action="test2", rationale="test")

        await manager.confirm(s1.id)

        pending = manager.get_pending()

        assert len(pending) == 1
        assert pending[0].id == s2.id

    @pytest.mark.asyncio
    async def test_acceptance_rate(self, manager: ConfirmationManager) -> None:
        """acceptance_rate calculates correctly."""
        s1 = await manager.submit(action="test1", rationale="test")
        s2 = await manager.submit(action="test2", rationale="test")
        s3 = await manager.submit(action="test3", rationale="test")

        await manager.confirm(s1.id)
        await manager.confirm(s2.id)
        await manager.reject(s3.id)

        assert manager.acceptance_rate == pytest.approx(2 / 3)

    @pytest.mark.asyncio
    async def test_acceptance_rate_empty(self, manager: ConfirmationManager) -> None:
        """acceptance_rate is 0 when no decisions."""
        assert manager.acceptance_rate == 0.0

    @pytest.mark.asyncio
    async def test_stats(self, manager: ConfirmationManager) -> None:
        """stats returns all metrics."""
        s1 = await manager.submit(action="test1", rationale="test")
        await manager.confirm(s1.id)

        stats = manager.stats

        assert stats["total_submitted"] == 1
        assert stats["total_confirmed"] == 1
        assert stats["pending_count"] == 0


class TestConfirmationManagerWithExecution:
    """Tests for ConfirmationManager with execution handler."""

    @pytest.mark.asyncio
    async def test_confirm_executes_action(self) -> None:
        """confirm executes action when handler provided."""
        executed_actions: list[str] = []

        async def execute(action: str) -> tuple[bool, str]:
            executed_actions.append(action)
            return True, "Success"

        manager = ConfirmationManager(execution_handler=execute)

        suggestion = await manager.submit(
            action="git commit -m 'fix'",
            rationale="test",
        )

        result = await manager.confirm(suggestion.id)

        assert result.accepted
        assert result.executed
        assert result.execution_result == "Success"
        assert executed_actions == ["git commit -m 'fix'"]

    @pytest.mark.asyncio
    async def test_confirm_execution_failure(self) -> None:
        """confirm handles execution failure."""

        async def execute(action: str) -> tuple[bool, str]:
            return False, "Execution failed"

        manager = ConfirmationManager(execution_handler=execute)

        suggestion = await manager.submit(action="test", rationale="test")
        result = await manager.confirm(suggestion.id)

        assert result.accepted
        assert not result.executed
        assert result.error == "Execution failed"

    @pytest.mark.asyncio
    async def test_confirm_execution_exception(self) -> None:
        """confirm handles execution exception."""

        async def execute(action: str) -> tuple[bool, str]:
            raise ValueError("Boom!")

        manager = ConfirmationManager(execution_handler=execute)

        suggestion = await manager.submit(action="test", rationale="test")
        result = await manager.confirm(suggestion.id)

        assert result.accepted
        assert not result.executed
        assert "Boom!" in str(result.error)


class TestConfirmationManagerExpiration:
    """Tests for suggestion expiration."""

    @pytest.mark.asyncio
    async def test_confirm_expired_suggestion(self) -> None:
        """confirm fails for expired suggestion."""
        manager = ConfirmationManager(expiration_hours=0)  # Immediately expire

        suggestion = await manager.submit(action="test", rationale="test")
        # Force expiration
        suggestion.expires_at = datetime.now() - timedelta(hours=1)

        result = await manager.confirm(suggestion.id)

        assert not result.accepted
        assert "expired" in str(result.error).lower()
        assert manager.total_expired == 1

    @pytest.mark.asyncio
    async def test_expire_stale(self) -> None:
        """expire_stale expires old suggestions."""
        manager = ConfirmationManager()

        suggestion = await manager.submit(action="test", rationale="test")
        # Force expiration
        suggestion.expires_at = datetime.now() - timedelta(hours=1)

        expired_count = await manager.expire_stale()

        assert expired_count == 1
        assert manager.total_expired == 1
        assert len(manager.get_pending()) == 0

    @pytest.mark.asyncio
    async def test_clear(self) -> None:
        """clear removes all pending suggestions."""
        manager = ConfirmationManager()

        await manager.submit(action="test1", rationale="test")
        await manager.submit(action="test2", rationale="test")

        manager.clear()

        assert len(manager.get_pending()) == 0
