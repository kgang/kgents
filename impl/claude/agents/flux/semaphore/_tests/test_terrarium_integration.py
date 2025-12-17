"""
Tests for FluxAgent + Terrarium Integration (Phase 5).

These tests verify:
1. FluxAgent emits SemaphoreEvent to Mirror when semaphore ejected
2. FluxAgent emits resolution event when ReentryContext processed
3. Mirror attachment/detachment works correctly
4. Purgatory attachment/detachment works correctly
5. End-to-end flow: eject → observe → resolve → complete
"""

from __future__ import annotations

import asyncio
import pickle
from dataclasses import dataclass
from typing import Any

import pytest
from agents.flux.terrarium_events import EventType, SemaphoreEvent
from agents.flux.mirror import HolographicBuffer

from ...agent import FluxAgent
from ...config import FluxConfig
from ..flux_integration import create_reentry_perturbation
from ..mixin import SemaphoreMixin, is_semaphore_token
from ..purgatory import Purgatory
from ..reason import SemaphoreReason
from ..reentry import ReentryContext
from ..token import SemaphoreToken

# === Test Fixtures ===


@dataclass
class ReviewState:
    """Test state for review agent."""

    document_id: str
    partial_review: str


class ReviewAgent(SemaphoreMixin[str, str, ReviewState]):
    """Agent that yields semaphore for document review."""

    name: str = "ReviewAgent"

    async def invoke(self, doc: str) -> str | SemaphoreToken[str]:
        """Review document, yield for sensitive content."""
        if "sensitive" in doc.lower():
            state = ReviewState(
                document_id=f"doc-{hash(doc) % 10000}",
                partial_review=f"needs-review:{doc[:20]}",
            )
            return self.create_semaphore(
                reason=SemaphoreReason.APPROVAL_NEEDED,
                state=state,
                original_event=doc,
                prompt="Review sensitive document?",
                options=["Approve", "Reject", "Escalate"],
                severity="warning",
            )
        return f"reviewed:{doc}"

    async def resume(
        self,
        frozen_state: bytes,
        human_input: Any,
    ) -> str:
        """Complete review after human decision."""
        state = self.restore_state(frozen_state)
        if human_input == "Approve":
            return f"approved:{state.document_id}:{state.partial_review}"
        elif human_input == "Reject":
            return f"rejected:{state.document_id}"
        else:
            return f"escalated:{state.document_id}"


async def async_iter(items: list[Any]) -> Any:
    """Create async iterator from list."""
    for item in items:
        yield item


# === Test Mirror Attachment ===


class TestMirrorAttachment:
    """Test mirror attachment to FluxAgent."""

    def test_attach_mirror(self) -> None:
        """Can attach mirror to FluxAgent."""
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(inner=agent)  # type: ignore[arg-type]
        buffer = HolographicBuffer()

        result = flux.attach_mirror(buffer)

        assert result is flux  # Returns self for chaining
        assert flux.mirror is buffer

    def test_detach_mirror(self) -> None:
        """Can detach mirror from FluxAgent."""
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(inner=agent)  # type: ignore[arg-type]
        buffer = HolographicBuffer()

        flux.attach_mirror(buffer)
        detached = flux.detach_mirror()

        assert detached is buffer
        assert flux.mirror is None

    def test_detach_returns_none_when_no_mirror(self) -> None:
        """Detach returns None when no mirror attached."""
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(inner=agent)  # type: ignore[arg-type]

        assert flux.detach_mirror() is None


# === Test Purgatory Attachment ===


class TestPurgatoryAttachment:
    """Test purgatory attachment to FluxAgent."""

    def test_attach_purgatory(self) -> None:
        """Can attach purgatory to FluxAgent."""
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(inner=agent)  # type: ignore[arg-type]
        purgatory = Purgatory()

        result = flux.attach_purgatory(purgatory)

        assert result is flux
        assert flux.purgatory is purgatory

    def test_detach_purgatory(self) -> None:
        """Can detach purgatory from FluxAgent."""
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(inner=agent)  # type: ignore[arg-type]
        purgatory = Purgatory()

        flux.attach_purgatory(purgatory)
        detached = flux.detach_purgatory()

        assert detached is purgatory
        assert flux.purgatory is None


# === Test Semaphore Ejection with Mirror ===


class TestSemaphoreEjectionWithMirror:
    """Test semaphore ejection emits to mirror."""

    @pytest.mark.asyncio
    async def test_emits_semaphore_event_on_ejection(self) -> None:
        """SemaphoreEvent is emitted to mirror when semaphore ejected."""
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(inner=agent)  # type: ignore[arg-type]
        buffer = HolographicBuffer()
        purgatory = Purgatory()

        flux.attach_mirror(buffer).attach_purgatory(purgatory)

        # Process event that triggers semaphore
        results: list[str] = []
        async for result in flux.start(async_iter(["This is sensitive data"])):
            results.append(result)

        # No results emitted (semaphore blocked it)
        assert len(results) == 0

        # Token was ejected to purgatory
        assert len(purgatory.list_pending()) == 1

        # Event was emitted to mirror
        assert buffer.events_reflected >= 1
        snapshot = buffer.get_snapshot()

        # Find the semaphore ejected event
        semaphore_events = [
            e for e in snapshot if e.get("type") == EventType.SEMAPHORE_EJECTED.value
        ]
        assert len(semaphore_events) >= 1

        event = semaphore_events[0]
        assert "data" in event
        assert event["data"]["prompt"] == "Review sensitive document?"
        assert event["data"]["severity"] == "warning"
        assert "Approve" in event["data"]["options"]

    @pytest.mark.asyncio
    async def test_normal_processing_continues_after_semaphore(self) -> None:
        """Stream continues processing after semaphore ejection."""
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(inner=agent)  # type: ignore[arg-type]
        buffer = HolographicBuffer()
        purgatory = Purgatory()

        flux.attach_mirror(buffer).attach_purgatory(purgatory)

        # Process mix of normal and sensitive documents
        docs = ["normal doc 1", "sensitive doc", "normal doc 2"]
        results: list[str] = []

        async for result in flux.start(async_iter(docs)):
            results.append(result)

        # Normal docs processed, sensitive doc blocked
        assert len(results) == 2
        assert results[0] == "reviewed:normal doc 1"
        assert results[1] == "reviewed:normal doc 2"

        # One token in purgatory
        assert len(purgatory.list_pending()) == 1


# === Test Semaphore Resolution with Mirror ===


class TestSemaphoreResolutionWithMirror:
    """Test semaphore resolution emits to mirror."""

    @pytest.mark.asyncio
    async def test_emits_resolution_event_direct(self) -> None:
        """Resolution event is emitted when _emit_semaphore_resolved called."""
        # This test directly tests the emission function without flux complexity
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(inner=agent)  # type: ignore[arg-type]
        buffer = HolographicBuffer()

        flux.attach_mirror(buffer)

        # Create a mock reentry context
        reentry = ReentryContext(
            token_id="test-token",
            frozen_state=b"state",
            human_input="Approve",
            original_event="test",
        )

        # Directly call the resolution emission
        await flux._emit_semaphore_resolved(reentry)

        # Check event was emitted
        snapshot = buffer.get_snapshot()
        resolution_events = [
            e for e in snapshot if e.get("type") == EventType.SEMAPHORE_RESOLVED.value
        ]
        assert len(resolution_events) == 1
        assert resolution_events[0]["data"]["token_id"] == "test-token"
        assert resolution_events[0]["data"]["resolved"] is True

    @pytest.mark.asyncio
    async def test_resolution_event_content(self) -> None:
        """Resolution event has correct content."""
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(inner=agent)  # type: ignore[arg-type]
        buffer = HolographicBuffer()

        flux.attach_mirror(buffer)

        reentry = ReentryContext(
            token_id="sem-12345",
            frozen_state=b"frozen",
            human_input="Reject",
            original_event="doc",
        )

        await flux._emit_semaphore_resolved(reentry)

        snapshot = buffer.get_snapshot()
        event = snapshot[0]

        assert event["type"] == EventType.SEMAPHORE_RESOLVED.value
        assert event["agent_id"] == flux.id
        assert event["data"]["token_id"] == "sem-12345"


# === Test End-to-End Flow ===


class TestEndToEndFlow:
    """Test complete semaphore flow with Terrarium."""

    @pytest.mark.asyncio
    async def test_ejection_event_contains_token_data(self) -> None:
        """Ejection event contains complete token data."""
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(
            inner=agent,  # type: ignore[arg-type]
            config=FluxConfig(entropy_budget=100.0),
        )
        buffer = HolographicBuffer()
        purgatory = Purgatory()

        flux.attach_mirror(buffer).attach_purgatory(purgatory)

        # Process sensitive document
        results: list[str] = []
        async for result in flux.start(async_iter(["sensitive doc"])):
            results.append(result)

        # Verify ejection event content
        snapshot = buffer.get_snapshot()
        ejection_events = [
            e for e in snapshot if e.get("type") == EventType.SEMAPHORE_EJECTED.value
        ]
        assert len(ejection_events) == 1

        event = ejection_events[0]
        assert event["agent_id"] == flux.id
        assert "data" in event
        assert "token_id" in event["data"]
        assert event["data"]["prompt"] == "Review sensitive document?"
        assert "Approve" in event["data"]["options"]
        assert event["data"]["severity"] == "warning"
        assert event["data"]["context"]["reason"] == "approval_needed"

    @pytest.mark.asyncio
    async def test_purgatory_stores_ejected_token(self) -> None:
        """Ejected token is stored in Purgatory for resolution."""
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(inner=agent)  # type: ignore[arg-type]
        purgatory = Purgatory()

        flux.attach_purgatory(purgatory)

        # Process sensitive document
        async for _ in flux.start(async_iter(["sensitive doc"])):
            pass

        # Token should be in purgatory
        pending = purgatory.list_pending()
        assert len(pending) == 1

        token = pending[0]
        assert token.prompt == "Review sensitive document?"
        assert token.reason.value == "approval_needed"

    @pytest.mark.asyncio
    async def test_multiple_documents_processed_correctly(self) -> None:
        """Normal docs processed, sensitive docs ejected."""
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(inner=agent)  # type: ignore[arg-type]
        buffer = HolographicBuffer()
        purgatory = Purgatory()

        flux.attach_mirror(buffer).attach_purgatory(purgatory)

        # Process mix of documents
        docs = ["normal 1", "sensitive doc", "normal 2", "another sensitive"]
        results: list[str] = []

        async for result in flux.start(async_iter(docs)):
            results.append(result)

        # Normal docs should be processed
        assert len(results) == 2
        assert "reviewed:normal 1" in results
        assert "reviewed:normal 2" in results

        # Sensitive docs should be in purgatory
        assert len(purgatory.list_pending()) == 2

        # Mirror should have ejection events
        ejection_events = [
            e
            for e in buffer.get_snapshot()
            if e.get("type") == EventType.SEMAPHORE_EJECTED.value
        ]
        assert len(ejection_events) == 2


# === Test Without Mirror (Graceful Degradation) ===


class TestWithoutMirror:
    """Test semaphore handling works without mirror."""

    @pytest.mark.asyncio
    async def test_semaphore_works_without_mirror(self) -> None:
        """Semaphore handling works even without mirror attached."""
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(inner=agent)  # type: ignore[arg-type]
        purgatory = Purgatory()

        # Only attach purgatory, no mirror
        flux.attach_purgatory(purgatory)

        results: list[str] = []
        async for result in flux.start(async_iter(["sensitive doc", "normal doc"])):
            results.append(result)

        # Normal doc processed
        assert len(results) == 1
        assert results[0] == "reviewed:normal doc"

        # Sensitive doc in purgatory
        assert len(purgatory.list_pending()) == 1


class TestWithoutPurgatory:
    """Test behavior when no purgatory attached."""

    @pytest.mark.asyncio
    async def test_semaphore_still_detected_without_purgatory(self) -> None:
        """Semaphore is detected but not persisted without purgatory."""
        agent = ReviewAgent()
        flux: FluxAgent[str, str] = FluxAgent(inner=agent)  # type: ignore[arg-type]
        buffer = HolographicBuffer()

        # Only attach mirror, no purgatory
        flux.attach_mirror(buffer)

        results: list[str] = []
        async for result in flux.start(async_iter(["sensitive doc", "normal doc"])):
            results.append(result)

        # Normal doc processed, sensitive skipped (no purgatory)
        assert len(results) == 1

        # Event still emitted to mirror
        snapshot = buffer.get_snapshot()
        semaphore_events = [
            e for e in snapshot if e.get("type") == EventType.SEMAPHORE_EJECTED.value
        ]
        assert len(semaphore_events) >= 1
