"""
Tests for Explorer adapters.

Verifies that adapters correctly convert DB models to UnifiedEvent.
"""

from datetime import UTC, datetime

import pytest

from services.explorer.adapters import (
    CrystalAdapter,
    EvidenceAdapter,
    LemmaAdapter,
    MarkAdapter,
    TeachingAdapter,
    TrailAdapter,
    get_adapter,
    get_all_adapters,
)
from services.explorer.contracts import EntityType, UnifiedEvent


class TestAdapterRegistry:
    """Test adapter registry functions."""

    def test_get_adapter_returns_correct_type(self) -> None:
        """Each entity type returns the correct adapter."""
        assert isinstance(get_adapter(EntityType.MARK), MarkAdapter)
        assert isinstance(get_adapter(EntityType.CRYSTAL), CrystalAdapter)
        assert isinstance(get_adapter(EntityType.TRAIL), TrailAdapter)
        assert isinstance(get_adapter(EntityType.EVIDENCE), EvidenceAdapter)
        assert isinstance(get_adapter(EntityType.TEACHING), TeachingAdapter)
        assert isinstance(get_adapter(EntityType.LEMMA), LemmaAdapter)

    def test_get_all_adapters_returns_six(self) -> None:
        """All six adapters are returned."""
        adapters = get_all_adapters()
        assert len(adapters) == 6

    def test_all_adapters_have_entity_type(self) -> None:
        """Each adapter has an entity_type property."""
        for adapter in get_all_adapters():
            assert adapter.entity_type in EntityType


class TestMarkAdapter:
    """Test MarkAdapter conversion."""

    def test_converts_mock_mark(self) -> None:
        """MarkAdapter converts a mock mark to UnifiedEvent."""

        # Create a mock WitnessMark
        class MockMark:
            id = "mark-123"
            action = "Fixed the bug in auth flow"
            reasoning = "Security vulnerability discovered"
            principles = ["composable", "ethical"]
            tags = ["security", "auth"]
            author = "kent"
            session_id = "session-456"
            parent_mark_id = None
            created_at = datetime.now(UTC)

        adapter = MarkAdapter()
        event = adapter.to_unified_event(MockMark())

        assert event.id == "mark-123"
        assert event.type == EntityType.MARK
        assert "Fixed the bug" in event.title
        assert event.metadata["type"] == "mark"
        assert event.metadata["author"] == "kent"
        assert "composable" in event.metadata["principles"]


class TestCrystalAdapter:
    """Test CrystalAdapter conversion."""

    def test_converts_mock_crystal(self) -> None:
        """CrystalAdapter converts a mock crystal to UnifiedEvent."""

        class MockCrystal:
            id = "crystal-456"
            summary = "AGENTESE paths are verbs, not nouns"
            content_hash = "abc123"
            tags = ["agentese", "insight"]
            access_count = 42
            last_accessed = None
            source_type = "capture"
            source_ref = None
            datum_id = None
            created_at = datetime.now(UTC)

        adapter = CrystalAdapter()
        event = adapter.to_unified_event(MockCrystal())

        assert event.id == "crystal-456"
        assert event.type == EntityType.CRYSTAL
        assert "AGENTESE" in event.title
        assert event.metadata["type"] == "crystal"
        assert event.metadata["access_count"] == 42


class TestTrailAdapter:
    """Test TrailAdapter conversion."""

    def test_converts_mock_trail(self) -> None:
        """TrailAdapter converts a mock trail to UnifiedEvent."""

        class MockTrail:
            id = "trail-789"
            name = "Exploring auth implementation"
            topics = ["auth", "security"]
            steps = [1, 2, 3]  # Mock steps
            commitments = []
            forked_from_id = None
            is_active = True
            created_at = datetime.now(UTC)

        adapter = TrailAdapter()
        event = adapter.to_unified_event(MockTrail())

        assert event.id == "trail-789"
        assert event.type == EntityType.TRAIL
        assert "auth" in event.title.lower()
        assert event.metadata["type"] == "trail"
        assert event.metadata["step_count"] == 3


class TestUnifiedEventSerialization:
    """Test UnifiedEvent serialization."""

    def test_to_dict_serializes_correctly(self) -> None:
        """UnifiedEvent.to_dict() produces valid JSON-serializable dict."""
        event = UnifiedEvent(
            id="test-123",
            type=EntityType.MARK,
            title="Test event",
            summary="A test event",
            timestamp=datetime.now(UTC).isoformat(),
            metadata={"type": "mark", "author": "kent"},
        )

        d = event.to_dict()

        assert d["id"] == "test-123"
        assert d["type"] == "mark"
        assert d["title"] == "Test event"
        assert d["metadata"]["author"] == "kent"
