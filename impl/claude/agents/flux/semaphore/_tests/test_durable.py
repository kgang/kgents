"""
Tests for DurablePurgatory: crash-resistant Purgatory with D-gent backing.

Tests cover:
1. Persistence roundtrip (save → restart → recover)
2. void_expired persists voided tokens
3. Schema version handling
4. Factory functions
"""

from datetime import datetime, timedelta
from typing import Any

import pytest

from agents.d.volatile import VolatileAgent
from agents.flux.semaphore.durable import (
    DEFAULT_STATE,
    DurablePurgatory,
    PurgatoryState,
    create_and_recover_purgatory,
    create_durable_purgatory,
)
from agents.flux.semaphore.reason import SemaphoreReason
from agents.flux.semaphore.token import SemaphoreToken


class TestDurablePurgatoryPersistence:
    """Tests for persistence roundtrip behavior."""

    @pytest.mark.asyncio
    async def test_save_persists_to_memory(self) -> None:
        """save() persists token to D-gent."""
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())
        purgatory = DurablePurgatory(memory=memory)

        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            prompt="Approve this?",
        )

        await purgatory.save(token)

        # Check memory was updated
        state = await memory.load()
        assert token.id in state["tokens"]
        assert state["tokens"][token.id]["prompt"] == "Approve this?"

    @pytest.mark.asyncio
    async def test_recover_loads_tokens_from_memory(self) -> None:
        """recover() loads persisted tokens."""
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())

        # First purgatory saves token
        purgatory1 = DurablePurgatory(memory=memory)
        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.CONTEXT_REQUIRED,
            prompt="Need context",
        )
        await purgatory1.save(token)

        # Simulate restart: new purgatory instance
        purgatory2 = DurablePurgatory(memory=memory)
        recovered = await purgatory2.recover()

        assert len(recovered) == 1
        assert recovered[0].id == token.id
        assert recovered[0].prompt == "Need context"

    @pytest.mark.asyncio
    async def test_persistence_roundtrip_preserves_all_fields(self) -> None:
        """Full roundtrip preserves all token fields."""
        import pickle

        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())
        purgatory1 = DurablePurgatory(memory=memory)

        state = {"step": 5, "partial": "result"}
        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.SENSITIVE_ACTION,
            frozen_state=pickle.dumps(state),
            original_event="test_event",
            prompt="Delete database?",
            options=["Yes", "No", "Cancel"],
            severity="critical",
            deadline=datetime.now() + timedelta(hours=1),
            escalation="admin@example.com",
        )

        await purgatory1.save(token)

        # Simulate restart
        purgatory2 = DurablePurgatory(memory=memory)
        recovered = await purgatory2.recover()

        assert len(recovered) == 1
        r = recovered[0]
        assert r.id == token.id
        assert r.reason == SemaphoreReason.SENSITIVE_ACTION
        assert r.prompt == "Delete database?"
        assert r.options == ["Yes", "No", "Cancel"]
        assert r.severity == "critical"
        assert r.escalation == "admin@example.com"
        assert r.deadline is not None
        # Frozen state preserved
        assert pickle.loads(r.frozen_state) == state

    @pytest.mark.asyncio
    async def test_resolve_persists_state(self) -> None:
        """resolve() persists the resolved state."""
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())
        purgatory1 = DurablePurgatory(memory=memory)

        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            prompt="Approve?",
        )
        await purgatory1.save(token)
        await purgatory1.resolve(token.id, "Approved!")

        # Simulate restart - should see resolved token
        purgatory2 = DurablePurgatory(memory=memory)
        recovered = await purgatory2.recover()

        # Resolved tokens are not "pending"
        assert len(recovered) == 0

        # But the token is still in storage
        all_tokens = purgatory2.list_all()
        assert len(all_tokens) == 1
        assert all_tokens[0].is_resolved is True

    @pytest.mark.asyncio
    async def test_cancel_persists_state(self) -> None:
        """cancel() persists the cancelled state."""
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())
        purgatory1 = DurablePurgatory(memory=memory)

        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.AMBIGUOUS_CHOICE,
            prompt="Which option?",
        )
        await purgatory1.save(token)
        await purgatory1.cancel(token.id)

        # Simulate restart
        purgatory2 = DurablePurgatory(memory=memory)
        recovered = await purgatory2.recover()

        # Cancelled tokens are not "pending"
        assert len(recovered) == 0

        # But the token is still in storage
        all_tokens = purgatory2.list_all()
        assert len(all_tokens) == 1
        assert all_tokens[0].is_cancelled is True


class TestDurablePurgatoryVoidExpired:
    """Tests for void_expired with persistence."""

    @pytest.mark.asyncio
    async def test_void_expired_persists_voided_tokens(self) -> None:
        """void_expired() persists voided state."""
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())
        purgatory1 = DurablePurgatory(memory=memory)

        # Create token with past deadline
        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            deadline=datetime.now() - timedelta(hours=1),  # Past
        )
        await purgatory1.save(token)

        # Void expired
        voided = await purgatory1.void_expired()
        assert len(voided) == 1

        # Simulate restart
        purgatory2 = DurablePurgatory(memory=memory)
        recovered = await purgatory2.recover()

        # Voided tokens are not "pending"
        assert len(recovered) == 0

        # But the token is still in storage
        all_tokens = purgatory2.list_all()
        assert len(all_tokens) == 1
        assert all_tokens[0].is_voided is True

    @pytest.mark.asyncio
    async def test_recover_voids_expired_on_startup(self) -> None:
        """recover() automatically voids expired tokens."""
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())

        # First purgatory saves token with deadline
        purgatory1 = DurablePurgatory(memory=memory)
        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            deadline=datetime.now() - timedelta(hours=1),  # Already past
        )
        # Save directly to memory to simulate saving before expiry
        # (avoid void_expired on first save)
        purgatory1._pending[token.id] = token
        await purgatory1._persist()

        # Simulate restart - recover should void expired
        purgatory2 = DurablePurgatory(memory=memory)
        recovered = await purgatory2.recover()

        # Expired token was voided on recovery
        assert len(recovered) == 0
        all_tokens = purgatory2.list_all()
        assert len(all_tokens) == 1
        assert all_tokens[0].is_voided is True


class TestDurablePurgatorySchemaVersion:
    """Tests for schema version handling."""

    @pytest.mark.asyncio
    async def test_persists_schema_version(self) -> None:
        """Persisted state includes schema version."""
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())
        purgatory = DurablePurgatory(memory=memory)

        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
        )
        await purgatory.save(token)

        state = await memory.load()
        assert state["version"] == 1

    @pytest.mark.asyncio
    async def test_recover_handles_missing_version(self) -> None:
        """recover() handles old state without version."""
        import base64

        # Create state without version field
        old_state: dict[str, Any] = {
            "tokens": {
                "sem-old": {
                    "id": "sem-old",
                    "reason": "approval_needed",
                    "frozen_state": base64.b64encode(b"").decode("utf-8"),
                    "original_event": None,
                    "required_type": None,
                    "deadline": None,
                    "escalation": None,
                    "prompt": "Old token",
                    "options": [],
                    "severity": "info",
                    "created_at": "2025-01-01T12:00:00",
                    "resolved_at": None,
                    "cancelled_at": None,
                    "voided_at": None,
                }
            }
        }

        memory: VolatileAgent[Any] = VolatileAgent(_state=old_state)
        purgatory = DurablePurgatory(memory=memory)  # type: ignore[arg-type]

        # Should recover without error
        recovered = await purgatory.recover()
        assert len(recovered) == 1
        assert recovered[0].id == "sem-old"


class TestDurablePurgatoryPheromones:
    """Tests for pheromone emission during durable operations."""

    @pytest.mark.asyncio
    async def test_save_emits_pheromone(self) -> None:
        """save() emits purgatory.ejected pheromone."""
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())
        signals: list[tuple[str, dict[str, Any]]] = []

        async def capture_signal(name: str, data: dict[str, Any]) -> None:
            signals.append((name, data))

        purgatory = create_durable_purgatory(memory=memory, emit_pheromone=capture_signal)

        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            prompt="Approve?",
        )
        await purgatory.save(token)

        assert len(signals) == 1
        assert signals[0][0] == "purgatory.ejected"
        assert signals[0][1]["token_id"] == token.id

    @pytest.mark.asyncio
    async def test_resolve_emits_pheromone(self) -> None:
        """resolve() emits purgatory.resolved pheromone."""
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())
        signals: list[tuple[str, dict[str, Any]]] = []

        async def capture_signal(name: str, data: dict[str, Any]) -> None:
            signals.append((name, data))

        purgatory = create_durable_purgatory(memory=memory, emit_pheromone=capture_signal)

        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
        )
        await purgatory.save(token)
        signals.clear()

        await purgatory.resolve(token.id, "OK")

        assert len(signals) == 1
        assert signals[0][0] == "purgatory.resolved"
        assert signals[0][1]["token_id"] == token.id

    @pytest.mark.asyncio
    async def test_void_expired_emits_pheromone(self) -> None:
        """void_expired() emits purgatory.voided pheromone."""
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())
        signals: list[tuple[str, dict[str, Any]]] = []

        async def capture_signal(name: str, data: dict[str, Any]) -> None:
            signals.append((name, data))

        purgatory = create_durable_purgatory(memory=memory, emit_pheromone=capture_signal)

        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            deadline=datetime.now() - timedelta(hours=1),
        )
        await purgatory.save(token)
        signals.clear()

        await purgatory.void_expired()

        assert len(signals) == 1
        assert signals[0][0] == "purgatory.voided"
        assert signals[0][1]["token_id"] == token.id


class TestDurablePurgatoryFactories:
    """Tests for factory functions."""

    @pytest.mark.asyncio
    async def test_create_durable_purgatory_without_memory(self) -> None:
        """create_durable_purgatory() works without memory."""
        purgatory = create_durable_purgatory()

        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
        )
        await purgatory.save(token)

        # Works like in-memory purgatory
        assert len(purgatory.list_pending()) == 1

    @pytest.mark.asyncio
    async def test_create_and_recover_purgatory_recovers(self) -> None:
        """create_and_recover_purgatory() recovers state."""
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())

        # First purgatory saves token
        purgatory1 = create_durable_purgatory(memory=memory)
        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
        )
        await purgatory1.save(token)

        # Factory function recovers on creation
        purgatory2 = await create_and_recover_purgatory(memory=memory)

        assert len(purgatory2.list_pending()) == 1
        assert purgatory2.list_pending()[0].id == token.id

    @pytest.mark.asyncio
    async def test_attach_memory_enables_persistence(self) -> None:
        """attach_memory() enables persistence after creation."""
        purgatory = DurablePurgatory()
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())

        # Initially no persistence
        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
        )
        await purgatory.save(token)

        # Memory still empty
        state = await memory.load()
        assert len(state["tokens"]) == 0

        # Attach memory and save again
        purgatory.attach_memory(memory)
        token2: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.CONTEXT_REQUIRED,
        )
        await purgatory.save(token2)

        # Now persisted
        state = await memory.load()
        assert token2.id in state["tokens"]


class TestDurablePurgatoryNoMemory:
    """Tests for behavior without memory attached."""

    @pytest.mark.asyncio
    async def test_recover_returns_empty_without_memory(self) -> None:
        """recover() returns empty list without memory."""
        purgatory = DurablePurgatory()

        recovered = await purgatory.recover()

        assert recovered == []

    @pytest.mark.asyncio
    async def test_operations_work_without_memory(self) -> None:
        """Basic operations work without memory (in-memory only)."""
        purgatory = DurablePurgatory()

        token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
        )

        await purgatory.save(token)
        assert len(purgatory.list_pending()) == 1

        reentry = await purgatory.resolve(token.id, "Done")
        assert reentry is not None
        assert len(purgatory.list_pending()) == 0


class TestDurablePurgatoryIntegration:
    """Integration tests for full workflows."""

    @pytest.mark.asyncio
    async def test_multiple_tokens_roundtrip(self) -> None:
        """Multiple tokens survive restart."""
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())
        purgatory1 = DurablePurgatory(memory=memory)

        tokens = [
            SemaphoreToken[str](
                reason=SemaphoreReason.APPROVAL_NEEDED,
                prompt=f"Token {i}",
            )
            for i in range(5)
        ]

        for token in tokens:
            await purgatory1.save(token)

        # Resolve one, cancel one
        await purgatory1.resolve(tokens[0].id, "OK")
        await purgatory1.cancel(tokens[1].id)

        # Simulate restart
        purgatory2 = DurablePurgatory(memory=memory)
        recovered = await purgatory2.recover()

        # 3 still pending
        assert len(recovered) == 3
        recovered_ids = {t.id for t in recovered}
        assert tokens[0].id not in recovered_ids
        assert tokens[1].id not in recovered_ids

    @pytest.mark.asyncio
    async def test_mixed_states_persist_correctly(self) -> None:
        """All terminal states persist correctly."""
        memory: VolatileAgent[PurgatoryState] = VolatileAgent(_state=DEFAULT_STATE.copy())
        purgatory1 = DurablePurgatory(memory=memory)

        pending_token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            prompt="Still pending",
        )
        resolved_token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            prompt="Will resolve",
        )
        cancelled_token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            prompt="Will cancel",
        )
        voided_token: SemaphoreToken[str] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            prompt="Will void",
            deadline=datetime.now() - timedelta(hours=1),
        )

        for token in [pending_token, resolved_token, cancelled_token, voided_token]:
            await purgatory1.save(token)

        await purgatory1.resolve(resolved_token.id, "OK")
        await purgatory1.cancel(cancelled_token.id)
        await purgatory1.void_expired()

        # Simulate restart
        purgatory2 = DurablePurgatory(memory=memory)
        await purgatory2.recover()

        # Check all states correct
        all_tokens = {t.id: t for t in purgatory2.list_all()}

        assert all_tokens[pending_token.id].is_pending is True
        assert all_tokens[resolved_token.id].is_resolved is True
        assert all_tokens[cancelled_token.id].is_cancelled is True
        assert all_tokens[voided_token.id].is_voided is True
