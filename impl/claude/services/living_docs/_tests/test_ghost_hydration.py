"""
Tests for Ghost Hydration (Memory-First Docs Phase 4).

These tests verify the hydrate_with_ghosts() method that surfaces
ancestral wisdom from deleted code during task hydration.

Laws tested:
1. Ghost Hydration Law: Hydration MUST surface wisdom from extinct code when relevant
2. Graceful Degradation: If brain unavailable, returns basic context
3. Keyword Matching: Ghosts are surfaced based on keyword match

See: spec/protocols/memory-first-docs.md, plans/memory-first-docs-execution.md
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.living_docs.hydrator import (
    HydrationContext,
    Hydrator,
    hydrate_context,
)


# =============================================================================
# Mock Fixtures
# =============================================================================


@dataclass
class MockTeachingCrystal:
    """Mock TeachingCrystal for testing."""

    id: str = "tc-123"
    insight: str = "Validate dialogue input before processing"
    severity: str = "critical"
    source_module: str = "services.town.dialogue"
    source_symbol: str = "DialogueService.process"
    died_at: datetime | None = None
    successor_module: str | None = None

    @property
    def is_alive(self) -> bool:
        return self.died_at is None

    @property
    def is_ancestor(self) -> bool:
        return self.died_at is not None


@dataclass
class MockExtinctionEvent:
    """Mock ExtinctionEvent for testing."""

    id: str = "ext-12345-abc"
    reason: str = "Crown Jewel Cleanup"
    commit: str = "abc12345"
    deleted_paths: list[str] | None = None
    decision_doc: str | None = None

    def __post_init__(self) -> None:
        if self.deleted_paths is None:
            self.deleted_paths = ["services/town/"]


@dataclass
class MockGhostWisdom:
    """Mock GhostWisdom for testing."""

    teaching: MockTeachingCrystal
    extinction_event: MockExtinctionEvent | None
    successor: str | None


@pytest.fixture
def mock_brain():
    """Create a mock BrainPersistence with ghost wisdom."""
    brain = MagicMock()

    # Create some test ghost wisdom
    ghost_teaching = MockTeachingCrystal(
        insight="Always validate dialogue input before processing",
        severity="critical",
        source_module="services.town.dialogue",
        source_symbol="DialogueService.validate",
        died_at=datetime.now(UTC),
    )

    ghost_event = MockExtinctionEvent(
        reason="Crown Jewel Cleanup - AD-009",
        commit="12209627",
    )

    ghost = MockGhostWisdom(
        teaching=ghost_teaching,
        extinction_event=ghost_event,
        successor="services.brain.conversation",
    )

    # Configure mock
    brain.get_extinct_wisdom = AsyncMock(return_value=[ghost])

    return brain


@pytest.fixture
def mock_brain_empty():
    """Create a mock BrainPersistence with no ghost wisdom."""
    brain = MagicMock()
    brain.get_extinct_wisdom = AsyncMock(return_value=[])
    return brain


# =============================================================================
# Test: hydrate_with_ghosts
# =============================================================================


class TestHydrateWithGhosts:
    """Tests for Hydrator.hydrate_with_ghosts() behavior."""

    @pytest.mark.asyncio
    async def test_ghosts_included_when_relevant(self, mock_brain):
        """hydrate_with_ghosts() includes ghost wisdom when task matches."""
        hydrator = Hydrator()

        # Task mentions dialogue/town
        context = await hydrator.hydrate_with_ghosts("implement town dialogue", mock_brain)

        # Should have called get_extinct_wisdom with keywords
        mock_brain.get_extinct_wisdom.assert_called_once()

        # Should have ancestral wisdom
        assert len(context.ancestral_wisdom) > 0

    @pytest.mark.asyncio
    async def test_ghosts_in_context_output(self, mock_brain):
        """hydrate_with_ghosts() includes ghosts in context structure."""
        hydrator = Hydrator()

        context = await hydrator.hydrate_with_ghosts("validate dialogue", mock_brain)

        # Verify ghost is present
        assert len(context.ancestral_wisdom) == 1
        ghost = context.ancestral_wisdom[0]
        assert ghost.teaching.insight == "Always validate dialogue input before processing"
        assert ghost.successor == "services.brain.conversation"

    @pytest.mark.asyncio
    async def test_no_ghosts_when_empty(self, mock_brain_empty):
        """hydrate_with_ghosts() gracefully handles no ghost wisdom."""
        hydrator = Hydrator()

        context = await hydrator.hydrate_with_ghosts("random unrelated task", mock_brain_empty)

        assert len(context.ancestral_wisdom) == 0
        assert len(context.extinct_modules) == 0

    @pytest.mark.asyncio
    async def test_extinct_modules_populated(self, mock_brain):
        """hydrate_with_ghosts() populates extinct_modules list."""
        hydrator = Hydrator()

        context = await hydrator.hydrate_with_ghosts("dialogue validation", mock_brain)

        # Should have the extinct module
        assert "services.town.dialogue" in context.extinct_modules

    @pytest.mark.asyncio
    async def test_graceful_degradation_on_error(self):
        """hydrate_with_ghosts() degrades gracefully if brain fails."""
        hydrator = Hydrator()

        # Create a brain that throws
        failing_brain = MagicMock()
        failing_brain.get_extinct_wisdom = AsyncMock(side_effect=Exception("DB error"))

        # Should not raise, just return basic context
        context = await hydrator.hydrate_with_ghosts("some task", failing_brain)

        # Basic context should still be valid
        assert context.task == "some task"
        assert len(context.ancestral_wisdom) == 0


# =============================================================================
# Test: to_markdown with ghosts
# =============================================================================


class TestHydrationContextWithGhosts:
    """Tests for HydrationContext.to_markdown() with ancestral wisdom."""

    def test_markdown_includes_ancestral_wisdom(self):
        """to_markdown() includes ancestral wisdom section when present."""
        ghost_teaching = MockTeachingCrystal(
            insight="Town pattern: use message queues",
            severity="warning",
            source_module="services.town.messaging",
            source_symbol="MessageBus.send",
            died_at=datetime.now(UTC),
        )

        ghost = MockGhostWisdom(
            teaching=ghost_teaching,
            extinction_event=MockExtinctionEvent(reason="Cleanup"),
            successor=None,
        )

        context = HydrationContext(
            task="implement messaging",
            ancestral_wisdom=[ghost],
            extinct_modules=["services.town.messaging"],
        )

        markdown = context.to_markdown()

        # Should have ancestral wisdom section
        assert "Ancestral Wisdom" in markdown
        assert "Town pattern: use message queues" in markdown
        assert "services.town.messaging" in markdown

    def test_markdown_shows_successor(self):
        """to_markdown() shows successor when module was replaced."""
        ghost_teaching = MockTeachingCrystal(
            insight="Chat gotcha",
            source_module="services.chat.handler",
            source_symbol="ChatHandler.process",
            died_at=datetime.now(UTC),
        )

        ghost = MockGhostWisdom(
            teaching=ghost_teaching,
            extinction_event=MockExtinctionEvent(reason="Migration"),
            successor="services.brain.conversation",
        )

        context = HydrationContext(
            task="implement chat",
            ancestral_wisdom=[ghost],
        )

        markdown = context.to_markdown()

        assert "services.brain.conversation" in markdown

    def test_markdown_groups_by_module(self):
        """to_markdown() groups ghosts by source module."""
        ghost1 = MockGhostWisdom(
            teaching=MockTeachingCrystal(
                insight="Gotcha 1",
                source_module="services.town.a",
                source_symbol="A.method",
                died_at=datetime.now(UTC),
            ),
            extinction_event=MockExtinctionEvent(),
            successor=None,
        )

        ghost2 = MockGhostWisdom(
            teaching=MockTeachingCrystal(
                insight="Gotcha 2",
                source_module="services.town.a",
                source_symbol="A.other",
                died_at=datetime.now(UTC),
            ),
            extinction_event=MockExtinctionEvent(),
            successor=None,
        )

        context = HydrationContext(
            task="test",
            ancestral_wisdom=[ghost1, ghost2],
        )

        markdown = context.to_markdown()

        # Module should appear once as a header
        assert markdown.count("### `services.town.a`") == 1
        # Both gotchas should be present
        assert "Gotcha 1" in markdown
        assert "Gotcha 2" in markdown


# =============================================================================
# Test: to_dict with ghosts
# =============================================================================


class TestHydrationContextDictWithGhosts:
    """Tests for HydrationContext.to_dict() with ancestral wisdom."""

    def test_dict_includes_ancestral_wisdom(self):
        """to_dict() includes ancestral_wisdom field."""
        ghost = MockGhostWisdom(
            teaching=MockTeachingCrystal(
                insight="Test insight",
                severity="critical",
                source_module="services.test",
                source_symbol="Test.method",
                died_at=datetime.now(UTC),
            ),
            extinction_event=MockExtinctionEvent(reason="Test"),
            successor="services.new",
        )

        context = HydrationContext(
            task="test",
            ancestral_wisdom=[ghost],
            extinct_modules=["services.test"],
        )

        d = context.to_dict()

        assert "ancestral_wisdom" in d
        assert len(d["ancestral_wisdom"]) == 1
        assert d["ancestral_wisdom"][0]["insight"] == "Test insight"
        assert d["ancestral_wisdom"][0]["successor"] == "services.new"
        assert d["ancestral_wisdom"][0]["extinction_reason"] == "Test"

    def test_dict_includes_extinct_modules(self):
        """to_dict() includes extinct_modules field."""
        context = HydrationContext(
            task="test",
            extinct_modules=["services.a", "services.b"],
        )

        d = context.to_dict()

        assert "extinct_modules" in d
        assert d["extinct_modules"] == ["services.a", "services.b"]


__all__ = [
    "TestHydrateWithGhosts",
    "TestHydrationContextWithGhosts",
    "TestHydrationContextDictWithGhosts",
]
