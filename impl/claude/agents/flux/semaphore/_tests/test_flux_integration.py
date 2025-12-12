"""
Tests for Flux Integration with Semaphores.

Phase 2 tests covering:
1. SemaphoreToken detection in results
2. ReentryContext detection in events
3. Purgatory ejection and injection
4. SemaphoreMixin helpers
5. End-to-end flow
"""

from __future__ import annotations

import asyncio
import pickle
from dataclasses import dataclass
from typing import Any

import pytest

from ..flux_integration import (
    REENTRY_PRIORITY,
    SemaphoreFluxConfig,
    create_reentry_perturbation,
    create_semaphore_flux,
    inject_reentry,
    is_reentry_context,
    process_reentry_event,
    process_semaphore_result,
)
from ..mixin import (
    SemaphoreCapable,
    SemaphoreMixin,
    is_semaphore_capable,
    is_semaphore_token,
)
from ..purgatory import Purgatory
from ..reason import SemaphoreReason
from ..reentry import ReentryContext
from ..token import SemaphoreToken

# === Test Fixtures ===


@dataclass
class MockState:
    """Test state for semaphore tests."""

    partial_result: str
    step: int


class MockSemaphoreAgent(SemaphoreMixin[str, str, MockState]):
    """Mock agent that yields semaphores."""

    name: str = "MockSemaphoreAgent"

    async def invoke(self, input_data: str) -> str | SemaphoreToken[str]:
        """Invoke that may yield a semaphore."""
        if "approve" in input_data.lower():
            state = MockState(partial_result=f"processed:{input_data}", step=1)
            return self.create_semaphore(
                reason=SemaphoreReason.APPROVAL_NEEDED,
                state=state,
                original_event=input_data,
                prompt="Approve this action?",
                options=["Approve", "Reject"],
                severity="warning",
            )
        return f"result:{input_data}"

    async def resume(
        self,
        frozen_state: bytes,
        human_input: Any,
    ) -> str:
        """Resume after human input."""
        state = self.restore_state(frozen_state)
        return f"{state.partial_result}:{human_input}"


# === Test is_semaphore_token ===


class TestIsSemaphoreToken:
    """Test SemaphoreToken detection."""

    def test_detects_semaphore_token(self) -> None:
        """SemaphoreToken is detected."""
        token: SemaphoreToken[Any] = SemaphoreToken(
            reason=SemaphoreReason.CONTEXT_REQUIRED
        )
        assert is_semaphore_token(token) is True

    def test_rejects_string(self) -> None:
        """String is not a SemaphoreToken."""
        assert is_semaphore_token("hello") is False

    def test_rejects_none(self) -> None:
        """None is not a SemaphoreToken."""
        assert is_semaphore_token(None) is False

    def test_rejects_dict(self) -> None:
        """Dict is not a SemaphoreToken."""
        assert is_semaphore_token({"token": "fake"}) is False


# === Test is_reentry_context ===


class TestIsReentryContext:
    """Test ReentryContext detection."""

    def test_detects_reentry_context(self) -> None:
        """ReentryContext is detected."""
        reentry = ReentryContext(
            token_id="sem-test",
            frozen_state=b"state",
            human_input="approve",
            original_event="test",
        )
        assert is_reentry_context(reentry) is True

    def test_rejects_semaphore_token(self) -> None:
        """SemaphoreToken is not a ReentryContext."""
        token: SemaphoreToken[Any] = SemaphoreToken(
            reason=SemaphoreReason.CONTEXT_REQUIRED
        )
        assert is_reentry_context(token) is False

    def test_rejects_string(self) -> None:
        """String is not a ReentryContext."""
        assert is_reentry_context("hello") is False


# === Test is_semaphore_capable ===


class TestIsSemaphoreCapable:
    """Test SemaphoreCapable protocol detection."""

    def test_detects_capable_agent(self) -> None:
        """Agent with resume() is capable."""
        agent = MockSemaphoreAgent()
        assert is_semaphore_capable(agent) is True

    def test_rejects_regular_object(self) -> None:
        """Object without resume() is not capable."""

        class RegularAgent:
            name = "Regular"

            async def invoke(self, x: str) -> str:
                return x

        agent = RegularAgent()
        assert is_semaphore_capable(agent) is False


# === Test SemaphoreMixin ===


class TestSemaphoreMixin:
    """Test SemaphoreMixin helpers."""

    def test_create_semaphore(self) -> None:
        """create_semaphore creates properly configured token."""
        mixin: SemaphoreMixin[str, str, MockState] = MockSemaphoreAgent()
        state = MockState(partial_result="test", step=1)

        token = mixin.create_semaphore(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            state=state,
            original_event="test_event",
            prompt="Approve?",
            options=["Yes", "No"],
            severity="critical",
        )

        assert isinstance(token, SemaphoreToken)
        assert token.reason == SemaphoreReason.APPROVAL_NEEDED
        assert token.prompt == "Approve?"
        assert token.options == ["Yes", "No"]
        assert token.severity == "critical"
        assert token.original_event == "test_event"

    def test_freeze_restore_state(self) -> None:
        """freeze_state and restore_state are inverses."""
        mixin: SemaphoreMixin[str, str, MockState] = MockSemaphoreAgent()
        state = MockState(partial_result="hello", step=42)

        frozen = mixin.freeze_state(state)
        restored = mixin.restore_state(frozen)

        assert restored.partial_result == "hello"
        assert restored.step == 42

    def test_process_reentry(self) -> None:
        """process_reentry extracts state and human_input."""
        mixin: SemaphoreMixin[str, str, MockState] = MockSemaphoreAgent()
        state = MockState(partial_result="data", step=3)
        frozen = mixin.freeze_state(state)

        reentry = ReentryContext(
            token_id="sem-test",
            frozen_state=frozen,
            human_input="approved",
            original_event="event",
        )

        restored_state, human_input = mixin.process_reentry(reentry)

        assert restored_state.partial_result == "data"
        assert restored_state.step == 3
        assert human_input == "approved"


# === Test create_reentry_perturbation ===


class TestCreateReentryPerturbation:
    """Test ReentryContext to Perturbation conversion."""

    def test_creates_perturbation_with_high_priority(self) -> None:
        """Perturbation has high priority."""
        reentry = ReentryContext(
            token_id="sem-test",
            frozen_state=b"state",
            human_input="approve",
            original_event="test",
        )

        perturbation = create_reentry_perturbation(reentry)

        assert perturbation.priority == REENTRY_PRIORITY
        assert perturbation.data is reentry

    def test_perturbation_has_future(self) -> None:
        """Perturbation has a result future."""
        reentry = ReentryContext(
            token_id="sem-test",
            frozen_state=b"state",
            human_input="approve",
            original_event="test",
        )

        perturbation = create_reentry_perturbation(reentry)

        assert perturbation.result_future is not None
        assert not perturbation.result_future.done()


# === Test process_semaphore_result ===


class TestProcessSemaphoreResult:
    """Test semaphore result processing."""

    @pytest.mark.asyncio
    async def test_saves_token_to_purgatory(self) -> None:
        """Token is saved to purgatory."""
        purgatory = Purgatory()
        token: SemaphoreToken[Any] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            frozen_state=b"state",
            prompt="Test?",
        )

        await process_semaphore_result(
            token=token,
            purgatory=purgatory,
            original_event="test_event",
        )

        assert len(purgatory.list_pending()) == 1
        assert purgatory.get(token.id) is token

    @pytest.mark.asyncio
    async def test_enriches_token_with_original_event(self) -> None:
        """Token gets original_event if not set."""
        purgatory = Purgatory()
        token: SemaphoreToken[Any] = SemaphoreToken(
            reason=SemaphoreReason.CONTEXT_REQUIRED,
            frozen_state=b"state",
            original_event=None,  # Not set
        )

        await process_semaphore_result(
            token=token,
            purgatory=purgatory,
            original_event="enriched_event",
        )

        assert token.original_event == "enriched_event"

    @pytest.mark.asyncio
    async def test_preserves_existing_original_event(self) -> None:
        """Token keeps existing original_event."""
        purgatory = Purgatory()
        token: SemaphoreToken[Any] = SemaphoreToken(
            reason=SemaphoreReason.CONTEXT_REQUIRED,
            frozen_state=b"state",
            original_event="original",
        )

        await process_semaphore_result(
            token=token,
            purgatory=purgatory,
            original_event="should_not_override",
        )

        assert token.original_event == "original"


# === Test process_reentry_event ===


class TestProcessReentryEvent:
    """Test reentry event processing."""

    @pytest.mark.asyncio
    async def test_calls_agent_resume(self) -> None:
        """Agent.resume() is called with correct args."""
        agent = MockSemaphoreAgent()
        state = MockState(partial_result="partial", step=2)
        frozen = pickle.dumps(state)

        reentry = ReentryContext(
            token_id="sem-test",
            frozen_state=frozen,
            human_input="approved",
            original_event="test",
        )

        result = await process_reentry_event(reentry, agent)  # type: ignore[arg-type]

        assert result == "partial:approved"

    @pytest.mark.asyncio
    async def test_raises_for_non_capable_agent(self) -> None:
        """RuntimeError for agent without resume()."""

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


# === Test inject_reentry ===


class TestInjectReentry:
    """Test ReentryContext injection into flux."""

    @pytest.mark.asyncio
    async def test_resolves_and_injects(self) -> None:
        """Successfully resolves token and injects perturbation."""
        purgatory = Purgatory()
        token: SemaphoreToken[Any] = SemaphoreToken(
            reason=SemaphoreReason.APPROVAL_NEEDED,
            frozen_state=b"state",
            original_event="test",
        )
        await purgatory.save(token)

        # Create a mock flux with perturbation queue
        class MockFlux:
            def __init__(self) -> None:
                self._perturbation_queue: asyncio.PriorityQueue[Any] = (
                    asyncio.PriorityQueue()
                )

        flux = MockFlux()

        success = await inject_reentry(
            purgatory=purgatory,
            flux=flux,  # type: ignore[arg-type]
            token_id=token.id,
            human_input="approved",
        )

        assert success is True
        assert not flux._perturbation_queue.empty()
        perturbation = await flux._perturbation_queue.get()
        assert isinstance(perturbation.data, ReentryContext)
        assert perturbation.data.human_input == "approved"

    @pytest.mark.asyncio
    async def test_returns_false_for_unknown_token(self) -> None:
        """Returns False for unknown token ID."""
        purgatory = Purgatory()

        class MockFlux:
            def __init__(self) -> None:
                self._perturbation_queue: asyncio.PriorityQueue[Any] = (
                    asyncio.PriorityQueue()
                )

        flux = MockFlux()

        success = await inject_reentry(
            purgatory=purgatory,
            flux=flux,  # type: ignore[arg-type]
            token_id="sem-nonexistent",
            human_input="test",
        )

        assert success is False
        assert flux._perturbation_queue.empty()


# === Test SemaphoreFluxConfig ===


class TestSemaphoreFluxConfig:
    """Test SemaphoreFluxConfig."""

    def test_default_config(self) -> None:
        """Default config has sensible defaults."""
        config = SemaphoreFluxConfig()

        assert isinstance(config.purgatory, Purgatory)
        assert config.reentry_priority == REENTRY_PRIORITY
        assert config.auto_void_on_start is True

    def test_custom_purgatory(self) -> None:
        """Can provide custom purgatory."""
        purgatory = Purgatory()
        config = SemaphoreFluxConfig(purgatory=purgatory)

        assert config.purgatory is purgatory


# === Test End-to-End Flow ===


class TestEndToEndFlow:
    """Test complete semaphore flow."""

    @pytest.mark.asyncio
    async def test_full_roundtrip(self) -> None:
        """Complete flow: invoke → semaphore → purgatory → resolve → resume."""
        # Setup
        agent = MockSemaphoreAgent()
        purgatory = Purgatory()

        # 1. Agent encounters situation needing approval
        result = await agent.invoke("approve this action")

        # 2. Result is a SemaphoreToken
        assert is_semaphore_token(result)
        token: SemaphoreToken[str] = result  # type: ignore[assignment]
        assert token.reason == SemaphoreReason.APPROVAL_NEEDED
        assert token.prompt == "Approve this action?"

        # 3. Eject to Purgatory
        await process_semaphore_result(
            token=token,
            purgatory=purgatory,
            original_event="approve this action",
        )
        assert len(purgatory.list_pending()) == 1

        # 4. Human resolves
        reentry = await purgatory.resolve(token.id, "Approved!")
        assert reentry is not None
        assert len(purgatory.list_pending()) == 0

        # 5. Agent resumes
        final_result = await process_reentry_event(reentry, agent)  # type: ignore[arg-type]
        assert final_result == "processed:approve this action:Approved!"

    @pytest.mark.asyncio
    async def test_normal_invoke_bypasses_semaphore(self) -> None:
        """Normal invoke doesn't create semaphore."""
        agent = MockSemaphoreAgent()

        result = await agent.invoke("normal input")

        assert not is_semaphore_token(result)
        assert result == "result:normal input"
