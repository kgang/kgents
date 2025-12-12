"""
End-to-end integration test for Agent Semaphores.

Tests the full rodizio flow:
1. FluxAgent processes event
2. Agent returns SemaphoreToken (needs approval)
3. Token ejected to DurablePurgatory
4. Stream continues processing other events
5. Human resolves via CLI/AGENTESE
6. ReentryContext injected as perturbation
7. Agent resumes with human input

This test verifies the complete semaphore lifecycle across all components.
"""

from __future__ import annotations

import asyncio
import pickle
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import pytest

from ..durable import DurablePurgatory, create_and_recover_purgatory
from ..flux_integration import (
    REENTRY_PRIORITY,
    create_reentry_perturbation,
    inject_reentry,
    is_reentry_context,
    process_reentry_event,
    process_semaphore_result,
)
from ..mixin import SemaphoreCapable, SemaphoreMixin, is_semaphore_token
from ..purgatory import Purgatory
from ..reason import SemaphoreReason
from ..reentry import ReentryContext
from ..token import SemaphoreToken

# === Test Agent Implementation ===


@dataclass
class ProcessingState:
    """State preserved across semaphore yields."""

    task_id: str
    step: int
    partial_results: list[str]
    metadata: dict[str, Any]


class ApprovalAgent(SemaphoreMixin[str, str, ProcessingState]):
    """
    Test agent that requires approval for certain operations.

    Demonstrates the rodizio pattern:
    - Some operations proceed automatically
    - Some operations yield a semaphore for human approval
    - After approval, processing resumes with context
    """

    name: str = "ApprovalAgent"

    def __init__(self) -> None:
        self.processed_events: list[str] = []
        self.resumed_events: list[tuple[str, Any]] = []

    async def invoke(self, event: str) -> str | SemaphoreToken[str]:
        """
        Process an event, potentially yielding a semaphore.

        Events containing "delete" require approval.
        Events containing "context" require additional info.
        Other events process automatically.
        """
        if "delete" in event.lower():
            # Requires approval
            state = ProcessingState(
                task_id=f"task-{len(self.processed_events)}",
                step=1,
                partial_results=[f"prepared:{event}"],
                metadata={"event": event, "timestamp": datetime.now().isoformat()},
            )
            return self.create_semaphore(
                reason=SemaphoreReason.APPROVAL_NEEDED,
                state=state,
                original_event=event,
                prompt=f"Approve deletion: {event}?",
                options=["Approve", "Reject", "Review"],
                severity="critical",
            )

        if "context" in event.lower():
            # Requires additional context
            state = ProcessingState(
                task_id=f"task-{len(self.processed_events)}",
                step=1,
                partial_results=[f"needs_context:{event}"],
                metadata={"event": event},
            )
            return self.create_semaphore(
                reason=SemaphoreReason.CONTEXT_REQUIRED,
                state=state,
                original_event=event,
                prompt="Which environment should this run in?",
                options=["dev", "staging", "production"],
                severity="warning",
            )

        # Auto-process
        self.processed_events.append(event)
        return f"processed:{event}"

    async def resume(
        self,
        frozen_state: bytes,
        human_input: Any,
    ) -> str:
        """Resume processing after human input."""
        state = self.restore_state(frozen_state)
        event = state.metadata.get("event", "unknown")

        self.resumed_events.append((event, human_input))

        return f"completed:{event}:{human_input}"


# === End-to-End Tests ===


class TestE2EBasicFlow:
    """Basic end-to-end flow tests."""

    @pytest.mark.asyncio
    async def test_auto_process_bypasses_semaphore(self) -> None:
        """Events not requiring approval process automatically."""
        agent = ApprovalAgent()

        result = await agent.invoke("normal event")

        assert not is_semaphore_token(result)
        assert result == "processed:normal event"
        assert "normal event" in agent.processed_events

    @pytest.mark.asyncio
    async def test_approval_flow_creates_semaphore(self) -> None:
        """Events requiring approval create semaphores."""
        agent = ApprovalAgent()

        result = await agent.invoke("delete user records")

        assert is_semaphore_token(result)
        token: SemaphoreToken[str] = result  # type: ignore[assignment]
        assert token.reason == SemaphoreReason.APPROVAL_NEEDED
        assert "delete" in token.prompt.lower()
        assert token.severity == "critical"
        assert len(token.options) == 3

    @pytest.mark.asyncio
    async def test_context_flow_creates_semaphore(self) -> None:
        """Events requiring context create semaphores."""
        agent = ApprovalAgent()

        result = await agent.invoke("deploy with context required")

        assert is_semaphore_token(result)
        token: SemaphoreToken[str] = result  # type: ignore[assignment]
        assert token.reason == SemaphoreReason.CONTEXT_REQUIRED
        assert "environment" in token.prompt.lower()


class TestE2EPurgatoryFlow:
    """Tests for Purgatory ejection and resolution."""

    @pytest.mark.asyncio
    async def test_full_purgatory_roundtrip(self) -> None:
        """Complete flow: invoke -> purgatory -> resolve -> resume."""
        agent = ApprovalAgent()
        purgatory = Purgatory()

        # 1. Agent processes event that requires approval
        result = await agent.invoke("delete important data")
        assert is_semaphore_token(result)
        token: SemaphoreToken[str] = result  # type: ignore[assignment]

        # 2. Eject to purgatory
        await process_semaphore_result(
            token=token,
            purgatory=purgatory,
            original_event="delete important data",
        )
        assert len(purgatory.list_pending()) == 1
        assert purgatory.get(token.id) is token

        # 3. Human resolves
        reentry = await purgatory.resolve(token.id, "Approved by admin")
        assert reentry is not None
        assert reentry.human_input == "Approved by admin"
        assert len(purgatory.list_pending()) == 0

        # 4. Agent resumes with context
        final_result = await process_reentry_event(reentry, agent)  # type: ignore[arg-type]
        assert "completed" in final_result
        assert "Approved by admin" in final_result

        # 5. Verify agent state
        assert len(agent.resumed_events) == 1
        assert agent.resumed_events[0][1] == "Approved by admin"

    @pytest.mark.asyncio
    async def test_multiple_concurrent_semaphores(self) -> None:
        """Multiple events can be in purgatory simultaneously."""
        agent = ApprovalAgent()
        purgatory = Purgatory()

        # Create multiple semaphores
        events = [
            "delete record 1",
            "delete record 2",
            "context needed for operation",
        ]
        tokens: list[SemaphoreToken[str]] = []

        for event in events:
            result = await agent.invoke(event)
            assert is_semaphore_token(result)
            token: SemaphoreToken[str] = result  # type: ignore[assignment]
            tokens.append(token)
            await process_semaphore_result(
                token=token,
                purgatory=purgatory,
                original_event=event,
            )

        # All in purgatory
        assert len(purgatory.list_pending()) == 3

        # Resolve in different order
        await purgatory.resolve(tokens[1].id, "Approved second")
        assert len(purgatory.list_pending()) == 2

        await purgatory.cancel(tokens[0].id)
        assert len(purgatory.list_pending()) == 1

        await purgatory.resolve(tokens[2].id, "staging")
        assert len(purgatory.list_pending()) == 0

    @pytest.mark.asyncio
    async def test_cancelled_token_not_resumable(self) -> None:
        """Cancelled tokens cannot be resolved."""
        agent = ApprovalAgent()
        purgatory = Purgatory()

        result = await agent.invoke("delete everything")
        assert is_semaphore_token(result)
        token: SemaphoreToken[str] = result  # type: ignore[assignment]

        await purgatory.save(token)
        await purgatory.cancel(token.id)

        # Attempting to resolve returns None
        reentry = await purgatory.resolve(token.id, "Too late")
        assert reentry is None
        assert token.is_cancelled


class TestE2EDeadlineHandling:
    """Tests for deadline handling."""

    @pytest.mark.asyncio
    async def test_void_expired_semaphores(self) -> None:
        """Expired semaphores are voided."""
        purgatory = Purgatory()

        # Create token with past deadline
        past_deadline = datetime.now() - timedelta(hours=1)
        expired_token: SemaphoreToken[str] = SemaphoreToken(
            id="sem-expired",
            reason=SemaphoreReason.APPROVAL_NEEDED,
            deadline=past_deadline,
            prompt="Too late?",
        )

        # Create token without deadline
        no_deadline_token: SemaphoreToken[str] = SemaphoreToken(
            id="sem-nodeadline",
            reason=SemaphoreReason.APPROVAL_NEEDED,
            prompt="Anytime?",
        )

        # Create token with future deadline
        future_deadline = datetime.now() + timedelta(hours=1)
        future_token: SemaphoreToken[str] = SemaphoreToken(
            id="sem-future",
            reason=SemaphoreReason.APPROVAL_NEEDED,
            deadline=future_deadline,
            prompt="Still time?",
        )

        await purgatory.save(expired_token)
        await purgatory.save(no_deadline_token)
        await purgatory.save(future_token)

        # Void expired
        voided = await purgatory.void_expired()

        assert len(voided) == 1
        assert voided[0].id == "sem-expired"
        assert expired_token.is_voided
        assert no_deadline_token.is_pending
        assert future_token.is_pending


class TestE2EPerturbationInjection:
    """Tests for perturbation queue injection."""

    @pytest.mark.asyncio
    async def test_reentry_creates_high_priority_perturbation(self) -> None:
        """ReentryContext creates high-priority perturbation."""
        reentry = ReentryContext(
            token_id="sem-test",
            frozen_state=b"state",
            human_input="approved",
            original_event="test",
        )

        perturbation = create_reentry_perturbation(reentry)

        assert perturbation.priority == REENTRY_PRIORITY
        assert perturbation.data is reentry
        assert is_reentry_context(perturbation.data)

    @pytest.mark.asyncio
    async def test_inject_reentry_into_flux(self) -> None:
        """inject_reentry adds perturbation to flux queue."""
        purgatory = Purgatory()
        token: SemaphoreToken[str] = SemaphoreToken(
            id="sem-inject",
            frozen_state=b"state",
        )
        await purgatory.save(token)

        # Mock flux with perturbation queue
        class MockFlux:
            def __init__(self) -> None:
                self._perturbation_queue: asyncio.PriorityQueue[Any] = (
                    asyncio.PriorityQueue()
                )

        flux = MockFlux()

        success = await inject_reentry(
            purgatory=purgatory,
            flux=flux,  # type: ignore[arg-type]
            token_id="sem-inject",
            human_input="approved",
        )

        assert success is True
        assert not flux._perturbation_queue.empty()

        perturbation = await flux._perturbation_queue.get()
        assert isinstance(perturbation.data, ReentryContext)
        assert perturbation.data.human_input == "approved"


class TestE2EStatePreservation:
    """Tests for state preservation across yields."""

    @pytest.mark.asyncio
    async def test_complex_state_preserved(self) -> None:
        """Complex agent state is preserved across semaphore yield."""
        agent = ApprovalAgent()
        purgatory = Purgatory()

        # Process event that creates semaphore
        result = await agent.invoke("delete with context required")
        assert is_semaphore_token(result)
        token: SemaphoreToken[str] = result  # type: ignore[assignment]

        # Verify frozen state can be restored
        state = agent.restore_state(token.frozen_state)
        assert isinstance(state, ProcessingState)
        assert state.step == 1
        assert len(state.partial_results) == 1
        assert "context" in state.partial_results[0]

        # Save to purgatory and resolve
        await purgatory.save(token)
        reentry = await purgatory.resolve(token.id, "staging")
        assert reentry is not None

        # Resume and verify state was used
        final_result = await process_reentry_event(reentry, agent)  # type: ignore[arg-type]
        assert "staging" in final_result

    @pytest.mark.asyncio
    async def test_original_event_preserved(self) -> None:
        """Original event is preserved in reentry context."""
        agent = ApprovalAgent()
        purgatory = Purgatory()

        original_event = "delete user@example.com"
        result = await agent.invoke(original_event)
        assert is_semaphore_token(result)
        token: SemaphoreToken[str] = result  # type: ignore[assignment]

        # Token has original event
        assert token.original_event == original_event

        # After resolution, reentry has original event
        await purgatory.save(token)
        reentry = await purgatory.resolve(token.id, "approved")
        assert reentry is not None
        assert reentry.original_event == original_event


class TestE2EPheromoneSignaling:
    """Tests for pheromone emission during semaphore lifecycle."""

    @pytest.mark.asyncio
    async def test_pheromones_emitted_on_save(self) -> None:
        """Pheromone emitted when token saved to purgatory."""
        emitted: list[tuple[str, dict[str, Any]]] = []

        async def capture_pheromone(signal: str, data: dict[str, Any]) -> None:
            emitted.append((signal, data))

        purgatory = Purgatory(_emit_pheromone=capture_pheromone)
        token: SemaphoreToken[str] = SemaphoreToken(
            id="sem-signal1",
            reason=SemaphoreReason.APPROVAL_NEEDED,
            severity="critical",
        )

        await purgatory.save(token)

        assert len(emitted) == 1
        signal, data = emitted[0]
        assert signal == "purgatory.ejected"
        assert data["token_id"] == "sem-signal1"
        assert data["severity"] == "critical"

    @pytest.mark.asyncio
    async def test_pheromones_emitted_on_resolve(self) -> None:
        """Pheromone emitted when token resolved."""
        emitted: list[tuple[str, dict[str, Any]]] = []

        async def capture_pheromone(signal: str, data: dict[str, Any]) -> None:
            emitted.append((signal, data))

        purgatory = Purgatory(_emit_pheromone=capture_pheromone)
        token: SemaphoreToken[str] = SemaphoreToken(id="sem-signal2")
        await purgatory.save(token)
        emitted.clear()  # Clear save signal

        await purgatory.resolve("sem-signal2", "approved")

        assert len(emitted) == 1
        signal, data = emitted[0]
        assert signal == "purgatory.resolved"
        assert data["token_id"] == "sem-signal2"

    @pytest.mark.asyncio
    async def test_pheromones_emitted_on_void(self) -> None:
        """Pheromone emitted when token voided."""
        emitted: list[tuple[str, dict[str, Any]]] = []

        async def capture_pheromone(signal: str, data: dict[str, Any]) -> None:
            emitted.append((signal, data))

        purgatory = Purgatory(_emit_pheromone=capture_pheromone)
        past_deadline = datetime.now() - timedelta(hours=1)
        token: SemaphoreToken[str] = SemaphoreToken(
            id="sem-signal3",
            deadline=past_deadline,
        )
        await purgatory.save(token)
        emitted.clear()

        await purgatory.void_expired()

        assert len(emitted) == 1
        signal, data = emitted[0]
        assert signal == "purgatory.voided"
        assert data["token_id"] == "sem-signal3"


class TestE2EDurablePurgatory:
    """Tests for DurablePurgatory with persistence."""

    @pytest.mark.asyncio
    async def test_durable_purgatory_basic_operations(self) -> None:
        """DurablePurgatory supports basic operations."""

        # Create with mock memory (in-memory dict)
        class MockMemory:
            def __init__(self) -> None:
                self._data: dict[str, Any] = {}

            async def load(self) -> dict[str, Any] | None:
                return self._data if self._data else None

            async def save(self, data: dict[str, Any]) -> None:
                self._data = data

        memory = MockMemory()
        purgatory = DurablePurgatory(memory=memory)  # type: ignore[arg-type]

        # Save token
        token: SemaphoreToken[str] = SemaphoreToken(
            id="sem-durable1",
            reason=SemaphoreReason.APPROVAL_NEEDED,
        )
        await purgatory.save(token)

        # Verify persisted - DurablePurgatory stores as {"tokens": {...}, "version": 1}
        assert memory._data is not None
        assert "tokens" in memory._data
        assert "sem-durable1" in memory._data["tokens"]

        # Resolve
        reentry = await purgatory.resolve("sem-durable1", "approved")
        assert reentry is not None

    @pytest.mark.asyncio
    async def test_create_and_recover_purgatory(self) -> None:
        """create_and_recover_purgatory creates fresh purgatory."""
        # Without memory, returns in-memory purgatory
        purgatory = await create_and_recover_purgatory(memory=None)

        assert isinstance(purgatory, DurablePurgatory)
        assert len(purgatory.list_pending()) == 0


class TestE2EErrorHandling:
    """Tests for error handling in e2e flows."""

    @pytest.mark.asyncio
    async def test_resume_non_capable_agent_fails(self) -> None:
        """Resuming non-capable agent raises error."""

        class NonCapableAgent:
            name = "NonCapable"

            async def invoke(self, x: str) -> str:
                return x

        agent = NonCapableAgent()
        reentry = ReentryContext(
            token_id="sem-test",
            frozen_state=b"state",
            human_input="test",
            original_event="test",
        )

        with pytest.raises(RuntimeError, match="does not implement resume"):
            await process_reentry_event(reentry, agent)  # type: ignore[arg-type]

    @pytest.mark.asyncio
    async def test_double_resolution_returns_none(self) -> None:
        """Resolving same token twice returns None."""
        purgatory = Purgatory()
        token: SemaphoreToken[str] = SemaphoreToken(id="sem-double")
        await purgatory.save(token)

        first = await purgatory.resolve("sem-double", "first")
        second = await purgatory.resolve("sem-double", "second")

        assert first is not None
        assert second is None

    @pytest.mark.asyncio
    async def test_resolve_unknown_token_returns_none(self) -> None:
        """Resolving unknown token returns None."""
        purgatory = Purgatory()

        result = await purgatory.resolve("sem-nonexistent", "input")

        assert result is None
