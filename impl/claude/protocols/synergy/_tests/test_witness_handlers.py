"""
Tests for Witness synergy handlers.

Tests both WitnessToBrainHandler and WitnessToGardenHandler.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pytest

from protocols.synergy.events import (
    Jewel,
    SynergyEvent,
    SynergyEventType,
    create_witness_git_commit_event,
    create_witness_thought_event,
)
from protocols.synergy.handlers import WitnessToBrainHandler, WitnessToGardenHandler

# =============================================================================
# WitnessToBrainHandler Tests
# =============================================================================


class TestWitnessToBrainHandler:
    """Tests for WitnessToBrainHandler."""

    @pytest.fixture
    def handler(self) -> WitnessToBrainHandler:
        """Create handler with auto_capture=False for testing."""
        return WitnessToBrainHandler(auto_capture=False)

    @pytest.mark.asyncio
    async def test_handler_name(self, handler: WitnessToBrainHandler) -> None:
        """Handler should have correct name."""
        assert handler.name == "WitnessToBrainHandler"

    @pytest.mark.asyncio
    async def test_supported_events(self, handler: WitnessToBrainHandler) -> None:
        """Handler should support thought and git commit events."""
        assert SynergyEventType.WITNESS_THOUGHT_CAPTURED in handler.SUPPORTED_EVENTS
        assert SynergyEventType.WITNESS_GIT_COMMIT in handler.SUPPORTED_EVENTS

    @pytest.mark.asyncio
    async def test_handles_thought_captured(self, handler: WitnessToBrainHandler) -> None:
        """Handler should process thought captured events."""
        event = create_witness_thought_event(
            thought_id="thought-123",
            content="Noticed interesting pattern in codebase",
            source="git",
            tags=["pattern", "observation"],
            confidence=0.9,
        )

        result = await handler.handle(event)

        assert result.success
        assert "thought" in result.message.lower() or "dry run" in result.message.lower()
        assert result.metadata.get("source") == "git"

    @pytest.mark.asyncio
    async def test_handles_git_commit(self, handler: WitnessToBrainHandler) -> None:
        """Handler should process git commit events (significant commits)."""
        event = create_witness_git_commit_event(
            commit_hash="abc123def456",
            author_email="dev@example.com",
            message="feat: Add witness cross-jewel integration",
            files_changed=10,
            insertions=200,
            deletions=50,
        )

        result = await handler.handle(event)

        assert result.success
        # Significant commit (>50 changes) should be captured
        assert "commit" in result.message.lower() or "dry run" in result.message.lower()

    @pytest.mark.asyncio
    async def test_skips_low_confidence_thoughts(self, handler: WitnessToBrainHandler) -> None:
        """Handler should skip thoughts with confidence < 0.5."""
        event = create_witness_thought_event(
            thought_id="thought-low",
            content="Maybe something happened",
            source="unknown",
            tags=[],
            confidence=0.3,  # Below 0.5 threshold
        )

        result = await handler.handle(event)

        assert result.success  # Skip is still successful
        assert "skipped" in result.message.lower() or "low confidence" in result.message.lower()

    @pytest.mark.asyncio
    async def test_skips_minor_commits(self, handler: WitnessToBrainHandler) -> None:
        """Handler should skip minor commits (few changes)."""
        event = create_witness_git_commit_event(
            commit_hash="tiny123",
            author_email="dev@example.com",
            message="fix: typo",
            files_changed=1,
            insertions=2,
            deletions=2,
        )

        result = await handler.handle(event)

        assert result.success  # Skip is still successful
        assert "skipped" in result.message.lower() or "minor" in result.message.lower()

    @pytest.mark.asyncio
    async def test_skips_unsupported_events(self, handler: WitnessToBrainHandler) -> None:
        """Handler should skip unsupported event types."""
        event = SynergyEvent(
            source_jewel=Jewel.WITNESS,
            target_jewel=Jewel.BRAIN,
            event_type=SynergyEventType.WITNESS_DAEMON_STARTED,  # Not in SUPPORTED_EVENTS
            source_id="daemon-1",
            payload={"pid": 123},
        )

        result = await handler.handle(event)

        assert result.success
        assert "skipped" in result.message.lower() or "not handling" in result.message.lower()


# =============================================================================
# WitnessToGardenHandler Tests
# =============================================================================


class TestWitnessToGardenHandler:
    """Tests for WitnessToGardenHandler."""

    @pytest.fixture
    def handler(self) -> WitnessToGardenHandler:
        """Create handler with auto_update=False for testing."""
        return WitnessToGardenHandler(auto_update=False)

    @pytest.mark.asyncio
    async def test_handler_name(self, handler: WitnessToGardenHandler) -> None:
        """Handler should have correct name."""
        assert handler.name == "WitnessToGardenHandler"

    @pytest.mark.asyncio
    async def test_supported_events(self, handler: WitnessToGardenHandler) -> None:
        """Handler should support git commit events."""
        assert SynergyEventType.WITNESS_GIT_COMMIT in handler.SUPPORTED_EVENTS

    @pytest.mark.asyncio
    async def test_extracts_explicit_plot_link(self, handler: WitnessToGardenHandler) -> None:
        """Handler should extract explicit [plot:...] tags."""
        event = create_witness_git_commit_event(
            commit_hash="abc123",
            author_email="dev@example.com",
            message="feat: [witness] Add cross-jewel handlers",
            files_changed=5,
            insertions=100,
            deletions=20,
        )

        result = await handler.handle(event)

        assert result.success
        assert "witness" in str(result.metadata.get("linked_plots", []))

    @pytest.mark.asyncio
    async def test_extracts_plan_reference(self, handler: WitnessToGardenHandler) -> None:
        """Handler should extract plan file references."""
        event = create_witness_git_commit_event(
            commit_hash="def456",
            author_email="dev@example.com",
            message="docs: Update plans/witness-phase2.md with progress",
            files_changed=3,
            insertions=50,
            deletions=10,
        )

        result = await handler.handle(event)

        assert result.success
        # Should extract "witness" from "witness-phase2"
        linked = result.metadata.get("linked_plots", [])
        assert "witness" in linked or len(linked) > 0

    @pytest.mark.asyncio
    async def test_extracts_crown_jewel_keywords(self, handler: WitnessToGardenHandler) -> None:
        """Handler should extract Crown Jewel keywords."""
        event = create_witness_git_commit_event(
            commit_hash="ghi789",
            author_email="dev@example.com",
            message="feat: Brain integration for witness thoughts",
            files_changed=4,
            insertions=80,
            deletions=15,
        )

        result = await handler.handle(event)

        assert result.success
        linked = result.metadata.get("linked_plots", [])
        # Should find both "brain" and "witness"
        assert "brain" in linked or "witness" in linked

    @pytest.mark.asyncio
    async def test_skips_no_plot_links(self, handler: WitnessToGardenHandler) -> None:
        """Handler should skip commits with no plot links."""
        event = create_witness_git_commit_event(
            commit_hash="jkl012",
            author_email="dev@example.com",
            message="chore: Update dependencies",
            files_changed=2,
            insertions=30,
            deletions=30,
        )

        result = await handler.handle(event)

        assert result.success
        assert "skipped" in result.message.lower() or "no plot" in result.message.lower()

    @pytest.mark.asyncio
    async def test_calculates_progress_delta(self, handler: WitnessToGardenHandler) -> None:
        """Handler should calculate reasonable progress delta."""
        # Test the internal calculation method
        delta = handler._calculate_progress_delta(
            files_changed=10,
            insertions=200,
            deletions=50,
        )

        # Should be between 1% and 10%
        assert 0.01 <= delta <= 0.10

    @pytest.mark.asyncio
    async def test_progress_delta_caps_at_ten_percent(
        self, handler: WitnessToGardenHandler
    ) -> None:
        """Progress delta should cap at 10%."""
        delta = handler._calculate_progress_delta(
            files_changed=100,
            insertions=10000,
            deletions=5000,
        )

        assert delta <= 0.10

    @pytest.mark.asyncio
    async def test_skips_unsupported_events(self, handler: WitnessToGardenHandler) -> None:
        """Handler should skip unsupported event types."""
        event = SynergyEvent(
            source_jewel=Jewel.WITNESS,
            target_jewel=Jewel.GARDENER,
            event_type=SynergyEventType.WITNESS_THOUGHT_CAPTURED,  # Not in SUPPORTED_EVENTS
            source_id="thought-1",
            payload={"content": "test"},
        )

        result = await handler.handle(event)

        assert result.success
        assert "skipped" in result.message.lower() or "not handling" in result.message.lower()


# =============================================================================
# Integration Tests
# =============================================================================


class TestWitnessHandlerIntegration:
    """Integration tests for witness handlers with bus."""

    @pytest.mark.asyncio
    async def test_handlers_implement_protocol(self) -> None:
        """Both handlers should implement SynergyHandler protocol."""
        brain_handler = WitnessToBrainHandler(auto_capture=False)
        garden_handler = WitnessToGardenHandler(auto_update=False)

        # Protocol requires name property
        assert hasattr(brain_handler, "name")
        assert hasattr(garden_handler, "name")
        assert isinstance(brain_handler.name, str)
        assert isinstance(garden_handler.name, str)

        # Protocol requires async handle method
        assert hasattr(brain_handler, "handle")
        assert hasattr(garden_handler, "handle")

    @pytest.mark.asyncio
    async def test_handlers_graceful_degradation(self) -> None:
        """Handlers should gracefully handle missing dependencies."""
        # With auto_capture=False, handlers log but don't fail
        brain_handler = WitnessToBrainHandler(auto_capture=False)
        garden_handler = WitnessToGardenHandler(auto_update=False)

        thought_event = create_witness_thought_event(
            thought_id="test-1",
            content="Test thought",
            source="test",
            tags=["test"],
            confidence=0.9,
        )

        commit_event = create_witness_git_commit_event(
            commit_hash="test123",
            author_email="test@example.com",
            message="test: [witness] Test commit",
            files_changed=5,
            insertions=100,
            deletions=10,
        )

        # Both should succeed (dry run mode)
        brain_result = await brain_handler.handle(thought_event)
        garden_result = await garden_handler.handle(commit_event)

        assert brain_result.success
        assert garden_result.success
