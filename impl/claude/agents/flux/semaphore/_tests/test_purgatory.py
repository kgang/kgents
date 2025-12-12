"""Tests for Purgatory."""

import pickle

import pytest
from agents.flux.semaphore import Purgatory, SemaphoreReason, SemaphoreToken


class TestPurgatorySave:
    """Test Purgatory.save() method."""

    @pytest.mark.asyncio
    async def test_save_stores_token_by_id(self) -> None:
        """save() stores token by ID."""
        purgatory = Purgatory()
        token = SemaphoreToken[str](id="sem-test1234")

        await purgatory.save(token)

        assert purgatory.get("sem-test1234") is token

    @pytest.mark.asyncio
    async def test_save_multiple_tokens(self) -> None:
        """Can save multiple tokens."""
        purgatory = Purgatory()
        token1 = SemaphoreToken[str](id="sem-aaaaaaaa")
        token2 = SemaphoreToken[str](id="sem-bbbbbbbb")

        await purgatory.save(token1)
        await purgatory.save(token2)

        assert purgatory.get("sem-aaaaaaaa") is token1
        assert purgatory.get("sem-bbbbbbbb") is token2

    @pytest.mark.asyncio
    async def test_save_overwrites_same_id(self) -> None:
        """Saving token with same ID overwrites previous."""
        purgatory = Purgatory()
        token1 = SemaphoreToken[str](id="sem-test1234", prompt="First")
        token2 = SemaphoreToken[str](id="sem-test1234", prompt="Second")

        await purgatory.save(token1)
        await purgatory.save(token2)

        assert purgatory.get("sem-test1234") is token2


class TestPurgatoryListPending:
    """Test Purgatory.list_pending() method."""

    @pytest.mark.asyncio
    async def test_list_pending_returns_only_pending(self) -> None:
        """list_pending() returns only pending tokens."""
        purgatory = Purgatory()

        pending_token = SemaphoreToken[str](id="sem-pending1")
        await purgatory.save(pending_token)

        resolved_token = SemaphoreToken[str](id="sem-resolved")
        await purgatory.save(resolved_token)
        await purgatory.resolve("sem-resolved", "input")

        cancelled_token = SemaphoreToken[str](id="sem-cancel1")
        await purgatory.save(cancelled_token)
        await purgatory.cancel("sem-cancel1")

        pending = purgatory.list_pending()
        assert len(pending) == 1
        assert pending[0].id == "sem-pending1"

    @pytest.mark.asyncio
    async def test_list_pending_empty_initially(self) -> None:
        """list_pending() returns empty list for new purgatory."""
        purgatory = Purgatory()
        assert purgatory.list_pending() == []


class TestPurgatoryResolve:
    """Test Purgatory.resolve() method."""

    @pytest.mark.asyncio
    async def test_resolve_marks_token_resolved(self) -> None:
        """resolve() marks token as resolved."""
        purgatory = Purgatory()
        token = SemaphoreToken[str](id="sem-test1234")
        await purgatory.save(token)

        await purgatory.resolve("sem-test1234", "Approve")

        assert token.is_resolved is True
        assert token.is_pending is False

    @pytest.mark.asyncio
    async def test_resolve_returns_reentry_context(self) -> None:
        """resolve() returns ReentryContext."""
        purgatory = Purgatory()
        token = SemaphoreToken[str](
            id="sem-test1234",
            frozen_state=b"state",
            original_event="event",
        )
        await purgatory.save(token)

        reentry = await purgatory.resolve("sem-test1234", "Approve")

        assert reentry is not None
        assert reentry.token_id == "sem-test1234"
        assert reentry.frozen_state == b"state"
        assert reentry.human_input == "Approve"
        assert reentry.original_event == "event"

    @pytest.mark.asyncio
    async def test_resolve_returns_none_for_already_resolved(self) -> None:
        """resolve() returns None for already-resolved token."""
        purgatory = Purgatory()
        token = SemaphoreToken[str](id="sem-test1234")
        await purgatory.save(token)

        await purgatory.resolve("sem-test1234", "First")
        result = await purgatory.resolve("sem-test1234", "Second")

        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_returns_none_for_unknown_id(self) -> None:
        """resolve() returns None for unknown ID."""
        purgatory = Purgatory()
        result = await purgatory.resolve("sem-nonexistent", "input")
        assert result is None

    @pytest.mark.asyncio
    async def test_resolve_returns_none_for_cancelled(self) -> None:
        """resolve() returns None for cancelled token."""
        purgatory = Purgatory()
        token = SemaphoreToken[str](id="sem-test1234")
        await purgatory.save(token)

        await purgatory.cancel("sem-test1234")
        result = await purgatory.resolve("sem-test1234", "input")

        assert result is None


class TestPurgatoryCancel:
    """Test Purgatory.cancel() method."""

    @pytest.mark.asyncio
    async def test_cancel_marks_token_cancelled(self) -> None:
        """cancel() marks token as cancelled."""
        purgatory = Purgatory()
        token = SemaphoreToken[str](id="sem-test1234")
        await purgatory.save(token)

        await purgatory.cancel("sem-test1234")

        assert token.is_cancelled is True
        assert token.is_pending is False

    @pytest.mark.asyncio
    async def test_cancel_returns_true_on_success(self) -> None:
        """cancel() returns True if successfully cancelled."""
        purgatory = Purgatory()
        token = SemaphoreToken[str](id="sem-test1234")
        await purgatory.save(token)

        result = await purgatory.cancel("sem-test1234")
        assert result is True

    @pytest.mark.asyncio
    async def test_cancel_returns_false_for_already_resolved(self) -> None:
        """cancel() returns False for already-resolved token."""
        purgatory = Purgatory()
        token = SemaphoreToken[str](id="sem-test1234")
        await purgatory.save(token)

        await purgatory.resolve("sem-test1234", "input")
        result = await purgatory.cancel("sem-test1234")

        assert result is False

    @pytest.mark.asyncio
    async def test_cancel_returns_false_for_unknown_id(self) -> None:
        """cancel() returns False for unknown ID."""
        purgatory = Purgatory()
        result = await purgatory.cancel("sem-nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_cancel_returns_false_for_already_cancelled(self) -> None:
        """cancel() returns False for already-cancelled token."""
        purgatory = Purgatory()
        token = SemaphoreToken[str](id="sem-test1234")
        await purgatory.save(token)

        await purgatory.cancel("sem-test1234")
        result = await purgatory.cancel("sem-test1234")

        assert result is False


class TestPurgatoryGet:
    """Test Purgatory.get() method."""

    @pytest.mark.asyncio
    async def test_get_returns_token_regardless_of_state(self) -> None:
        """get() returns token regardless of state."""
        purgatory = Purgatory()

        # Pending
        pending = SemaphoreToken[str](id="sem-pending1")
        await purgatory.save(pending)
        assert purgatory.get("sem-pending1") is pending

        # Resolved
        resolved = SemaphoreToken[str](id="sem-resolved")
        await purgatory.save(resolved)
        await purgatory.resolve("sem-resolved", "input")
        assert purgatory.get("sem-resolved") is resolved

        # Cancelled
        cancelled = SemaphoreToken[str](id="sem-cancel1")
        await purgatory.save(cancelled)
        await purgatory.cancel("sem-cancel1")
        assert purgatory.get("sem-cancel1") is cancelled

    def test_get_returns_none_for_unknown(self) -> None:
        """get() returns None for unknown ID."""
        purgatory = Purgatory()
        assert purgatory.get("sem-nonexistent") is None


class TestPurgatoryListAll:
    """Test Purgatory.list_all() method."""

    @pytest.mark.asyncio
    async def test_list_all_returns_all_tokens(self) -> None:
        """list_all() returns all tokens regardless of state."""
        purgatory = Purgatory()

        token1 = SemaphoreToken[str](id="sem-pending1")
        await purgatory.save(token1)

        token2 = SemaphoreToken[str](id="sem-resolved")
        await purgatory.save(token2)
        await purgatory.resolve("sem-resolved", "input")

        token3 = SemaphoreToken[str](id="sem-cancel1")
        await purgatory.save(token3)
        await purgatory.cancel("sem-cancel1")

        all_tokens = purgatory.list_all()
        assert len(all_tokens) == 3

    def test_list_all_empty_initially(self) -> None:
        """list_all() returns empty list for new purgatory."""
        purgatory = Purgatory()
        assert purgatory.list_all() == []


class TestPurgatoryClear:
    """Test Purgatory.clear() method."""

    @pytest.mark.asyncio
    async def test_clear_removes_all_tokens(self) -> None:
        """clear() removes all tokens."""
        purgatory = Purgatory()

        await purgatory.save(SemaphoreToken[str](id="sem-token1"))
        await purgatory.save(SemaphoreToken[str](id="sem-token2"))
        await purgatory.save(SemaphoreToken[str](id="sem-token3"))

        purgatory.clear()

        assert purgatory.list_all() == []
        assert purgatory.list_pending() == []


class TestPurgatoryRecover:
    """Test Purgatory.recover() method."""

    @pytest.mark.asyncio
    async def test_recover_returns_empty_without_memory(self) -> None:
        """recover() returns empty list without D-gent memory (Phase 1)."""
        purgatory = Purgatory()

        # Save some tokens
        await purgatory.save(SemaphoreToken[str](id="sem-token1"))
        await purgatory.save(SemaphoreToken[str](id="sem-token2"))

        # Simulate "new" purgatory (Phase 1: no persistence)
        new_purgatory = Purgatory()
        recovered = await new_purgatory.recover()

        # Phase 1: no recovery without D-gent
        assert recovered == []


class TestPurgatoryIntegration:
    """Integration tests for full round-trip."""

    @pytest.mark.asyncio
    async def test_round_trip(self) -> None:
        """Full round-trip: create -> save -> resolve -> reentry."""
        purgatory = Purgatory()

        # Simulate agent state at ejection
        agent_state = {"partial_result": "halfway there", "step": 3}
        frozen = pickle.dumps(agent_state)

        # Create token
        token = SemaphoreToken[str](
            reason=SemaphoreReason.APPROVAL_NEEDED,
            frozen_state=frozen,
            original_event="delete_records",
            prompt="Delete 47 records?",
            options=["Approve", "Reject", "Review"],
            severity="critical",
        )

        # Eject to purgatory
        await purgatory.save(token)
        assert len(purgatory.list_pending()) == 1

        # Human resolves
        reentry = await purgatory.resolve(token.id, "Approve")

        assert reentry is not None
        assert reentry.token_id == token.id
        assert reentry.human_input == "Approve"
        assert reentry.original_event == "delete_records"

        # Restore agent state
        restored = pickle.loads(reentry.frozen_state)
        assert restored["partial_result"] == "halfway there"
        assert restored["step"] == 3

        # Token no longer pending
        assert len(purgatory.list_pending()) == 0
        assert token.is_resolved

    @pytest.mark.asyncio
    async def test_multiple_concurrent_semaphores(self) -> None:
        """Multiple semaphores can be pending simultaneously."""
        purgatory = Purgatory()

        # Create multiple tokens
        tokens = [
            SemaphoreToken[str](
                id=f"sem-token{i:04d}",
                prompt=f"Question {i}?",
            )
            for i in range(5)
        ]

        # Save all
        for token in tokens:
            await purgatory.save(token)

        assert len(purgatory.list_pending()) == 5

        # Resolve some, cancel some
        await purgatory.resolve("sem-token0000", "A")
        await purgatory.resolve("sem-token0001", "B")
        await purgatory.cancel("sem-token0002")

        assert len(purgatory.list_pending()) == 2
        assert len(purgatory.list_all()) == 5

        # Remaining pending tokens
        pending_ids = [t.id for t in purgatory.list_pending()]
        assert "sem-token0003" in pending_ids
        assert "sem-token0004" in pending_ids

    @pytest.mark.asyncio
    async def test_reentry_context_preserves_complex_state(self) -> None:
        """ReentryContext correctly preserves complex frozen state."""
        purgatory = Purgatory()

        # Complex state with nested dicts/lists (not custom classes, which can't pickle)
        agent_state = {
            "step": 7,
            "results": [1, 2, 3],
            "nested": {"inner_value": 42, "items": ["a", "b"]},
            "metadata": {"key": "value"},
            "tuple_data": (1, 2, 3),
        }
        frozen = pickle.dumps(agent_state)

        token = SemaphoreToken[dict[str, str]](
            frozen_state=frozen,
            original_event={"type": "complex", "data": [1, 2]},
        )
        await purgatory.save(token)

        reentry = await purgatory.resolve(token.id, {"choice": "option1"})
        assert reentry is not None

        # Verify complex state restoration
        restored = pickle.loads(reentry.frozen_state)
        assert restored["step"] == 7
        assert restored["results"] == [1, 2, 3]
        assert restored["nested"]["inner_value"] == 42
        assert restored["nested"]["items"] == ["a", "b"]
        assert restored["metadata"]["key"] == "value"
        assert restored["tuple_data"] == (1, 2, 3)

        # Verify human input preserved
        assert reentry.human_input == {"choice": "option1"}

        # Verify original event preserved
        assert reentry.original_event["type"] == "complex"
        assert reentry.original_event["data"] == [1, 2]
