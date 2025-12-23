"""
Tests for proxy handle types.

AD-015: Proxy Handles & Transparent Batch Processes
"""

from datetime import datetime, timedelta

import pytest

from services.proxy.types import (
    HandleStatus,
    ProxyHandle,
    ProxyHandleEvent,
    SourceType,
)

# =============================================================================
# HandleStatus Tests
# =============================================================================


class TestHandleStatus:
    """Tests for HandleStatus enum."""

    def test_all_statuses_exist(self) -> None:
        """All expected statuses should exist."""
        assert HandleStatus.EMPTY == "empty"
        assert HandleStatus.COMPUTING == "computing"
        assert HandleStatus.FRESH == "fresh"
        assert HandleStatus.STALE == "stale"
        assert HandleStatus.ERROR == "error"

    def test_string_value(self) -> None:
        """Status should be usable as string via .value."""
        # Note: str(HandleStatus.FRESH) returns "HandleStatus.FRESH"
        # Use .value to get the underlying string
        assert HandleStatus.FRESH.value == "fresh"
        assert HandleStatus.FRESH == "fresh"  # Comparison works due to str inheritance


# =============================================================================
# SourceType Tests
# =============================================================================


class TestSourceType:
    """Tests for SourceType enum."""

    def test_all_source_types_exist(self) -> None:
        """All expected source types should exist."""
        assert SourceType.SPEC_CORPUS == "spec_corpus"
        assert SourceType.WITNESS_GRAPH == "witness_graph"
        assert SourceType.CODEBASE_GRAPH == "codebase_graph"
        assert SourceType.TOWN_SNAPSHOT == "town_snapshot"
        assert SourceType.MEMORY_CRYSTALS == "memory_crystals"
        assert SourceType.CUSTOM == "custom"

    def test_custom_extension_point(self) -> None:
        """CUSTOM type should allow extension."""
        assert SourceType.CUSTOM.value == "custom"


# =============================================================================
# ProxyHandle Tests
# =============================================================================


class TestProxyHandleCreation:
    """Tests for ProxyHandle creation."""

    def test_requires_human_label(self) -> None:
        """Law 4: human_label is required (no anonymous debris)."""
        with pytest.raises(ValueError, match="human_label is required"):
            ProxyHandle(human_label="")

    def test_creates_with_valid_label(self) -> None:
        """Should create handle with valid human_label."""
        handle = ProxyHandle(human_label="Test handle")
        assert handle.human_label == "Test handle"
        assert handle.handle_id  # UUID generated
        assert handle.status == HandleStatus.EMPTY

    def test_defaults(self) -> None:
        """Should have sensible defaults."""
        handle = ProxyHandle(human_label="Test handle")
        assert handle.source_type == SourceType.CUSTOM
        assert handle.status == HandleStatus.EMPTY
        assert handle.data is None
        assert handle.error is None
        assert handle.computed_by == "system"
        assert handle.computation_count == 0
        assert handle.access_count == 0

    def test_custom_ttl(self) -> None:
        """Should accept custom TTL."""
        ttl = timedelta(hours=2)
        handle = ProxyHandle(
            human_label="Test handle",
            ttl=ttl,
            status=HandleStatus.FRESH,
        )
        assert handle.ttl == ttl


class TestProxyHandleStatus:
    """Tests for ProxyHandle status methods."""

    def test_is_fresh_when_fresh_and_not_expired(self) -> None:
        """is_fresh() should return True for FRESH status within TTL."""
        handle = ProxyHandle(
            human_label="Test",
            status=HandleStatus.FRESH,
            data="test data",
        )
        assert handle.is_fresh() is True

    def test_is_fresh_false_when_expired(self) -> None:
        """is_fresh() should return False when TTL expired."""
        handle = ProxyHandle(
            human_label="Test",
            status=HandleStatus.FRESH,
            ttl=timedelta(seconds=-1),  # Already expired
            data="test data",
        )
        assert handle.is_fresh() is False

    def test_is_fresh_false_when_not_fresh_status(self) -> None:
        """is_fresh() should return False for non-FRESH status."""
        for status in [
            HandleStatus.EMPTY,
            HandleStatus.COMPUTING,
            HandleStatus.STALE,
            HandleStatus.ERROR,
        ]:
            handle = ProxyHandle(
                human_label="Test",
                status=status,
            )
            assert handle.is_fresh() is False, f"Expected False for {status}"

    def test_is_stale_when_stale_status(self) -> None:
        """is_stale() should return True for STALE status."""
        handle = ProxyHandle(
            human_label="Test",
            status=HandleStatus.STALE,
        )
        assert handle.is_stale() is True

    def test_is_stale_when_fresh_but_expired(self) -> None:
        """is_stale() should return True when FRESH but TTL expired."""
        handle = ProxyHandle(
            human_label="Test",
            status=HandleStatus.FRESH,
            ttl=timedelta(seconds=-1),  # Already expired
        )
        assert handle.is_stale() is True

    def test_is_computing(self) -> None:
        """is_computing() should detect COMPUTING status."""
        handle = ProxyHandle(
            human_label="Test",
            status=HandleStatus.COMPUTING,
        )
        assert handle.is_computing() is True

        handle.status = HandleStatus.FRESH
        assert handle.is_computing() is False

    def test_is_error(self) -> None:
        """is_error() should detect ERROR status."""
        handle = ProxyHandle(
            human_label="Test",
            status=HandleStatus.ERROR,
            error="Something went wrong",
        )
        assert handle.is_error() is True


class TestProxyHandleAccess:
    """Tests for ProxyHandle access tracking."""

    def test_access_increments_count(self) -> None:
        """access() should increment access_count."""
        handle = ProxyHandle(human_label="Test")
        assert handle.access_count == 0

        handle.access()
        assert handle.access_count == 1

        handle.access()
        assert handle.access_count == 2

    def test_access_updates_last_accessed(self) -> None:
        """access() should update last_accessed timestamp."""
        handle = ProxyHandle(human_label="Test")
        old_accessed = handle.last_accessed

        # Small sleep to ensure timestamp difference
        import time

        time.sleep(0.01)

        handle.access()
        assert handle.last_accessed > old_accessed


class TestProxyHandleProperties:
    """Tests for ProxyHandle computed properties."""

    def test_age(self) -> None:
        """age property should return time since creation."""
        handle = ProxyHandle(human_label="Test")

        # Age should be very small (just created)
        assert handle.age.total_seconds() < 1.0

    def test_time_until_expiration(self) -> None:
        """time_until_expiration should return remaining TTL."""
        handle = ProxyHandle(
            human_label="Test",
            status=HandleStatus.FRESH,
            ttl=timedelta(minutes=5),
        )

        remaining = handle.time_until_expiration
        assert remaining is not None
        # Should be close to 5 minutes
        assert 4.9 * 60 < remaining.total_seconds() < 5.0 * 60

    def test_time_until_expiration_none_when_no_expiry(self) -> None:
        """time_until_expiration should return None when expires_at is None."""
        handle = ProxyHandle(human_label="Test")
        handle.expires_at = None
        assert handle.time_until_expiration is None


class TestProxyHandleSerialization:
    """Tests for ProxyHandle serialization."""

    def test_to_dict(self) -> None:
        """to_dict() should produce serializable dict."""
        handle = ProxyHandle(
            human_label="Test handle",
            source_type=SourceType.SPEC_CORPUS,
            status=HandleStatus.FRESH,
            data={"key": "value"},
            computed_by="test_suite",
            computation_duration=1.5,
            computation_count=3,
        )

        d = handle.to_dict()

        assert d["human_label"] == "Test handle"
        assert d["source_type"] == "spec_corpus"
        assert d["status"] == "fresh"
        assert d["data"] == {"key": "value"}
        assert d["computed_by"] == "test_suite"
        assert d["computation_duration"] == 1.5
        assert d["computation_count"] == 3
        assert d["handle_id"] == handle.handle_id

    def test_from_dict(self) -> None:
        """from_dict() should reconstruct handle."""
        original = ProxyHandle(
            human_label="Test handle",
            source_type=SourceType.SPEC_CORPUS,
            status=HandleStatus.FRESH,
            data={"key": "value"},
        )

        d = original.to_dict()
        restored = ProxyHandle.from_dict(d)

        assert restored.human_label == original.human_label
        assert restored.source_type == original.source_type
        assert restored.status == original.status
        assert restored.data == original.data
        assert restored.handle_id == original.handle_id

    def test_roundtrip(self) -> None:
        """to_dict -> from_dict should preserve data."""
        handle = ProxyHandle(
            human_label="Roundtrip test",
            source_type=SourceType.WITNESS_GRAPH,
            status=HandleStatus.STALE,
            data=[1, 2, 3],
            error=None,
            computed_by="roundtrip_test",
            computation_duration=2.5,
            computation_count=5,
        )

        restored = ProxyHandle.from_dict(handle.to_dict())

        # Compare all significant fields
        assert restored.human_label == handle.human_label
        assert restored.source_type == handle.source_type
        assert restored.status == handle.status
        assert restored.data == handle.data
        assert restored.computed_by == handle.computed_by
        assert restored.computation_duration == handle.computation_duration
        assert restored.computation_count == handle.computation_count


# =============================================================================
# ProxyHandleEvent Tests
# =============================================================================


class TestProxyHandleEvent:
    """Tests for ProxyHandleEvent."""

    def test_creation(self) -> None:
        """Should create event with all fields."""
        event = ProxyHandleEvent(
            event_type="computation_started",
            source_type=SourceType.SPEC_CORPUS,
            handle_id="abc-123",
            details={"force": True},
        )

        assert event.event_type == "computation_started"
        assert event.source_type == SourceType.SPEC_CORPUS
        assert event.handle_id == "abc-123"
        assert event.details == {"force": True}
        assert isinstance(event.timestamp, datetime)

    def test_to_dict(self) -> None:
        """to_dict() should produce serializable dict."""
        event = ProxyHandleEvent(
            event_type="computation_completed",
            source_type=SourceType.SPEC_CORPUS,
            handle_id="abc-123",
            details={"duration": 1.5},
        )

        d = event.to_dict()

        assert d["event_type"] == "computation_completed"
        assert d["source_type"] == "spec_corpus"
        assert d["handle_id"] == "abc-123"
        assert d["details"] == {"duration": 1.5}
        assert "timestamp" in d

    def test_all_event_types(self) -> None:
        """All event types should be creatable."""
        event_types = [
            "computation_started",
            "computation_completed",
            "computation_failed",
            "handle_accessed",
            "handle_stale",
            "handle_invalidated",
            "handle_deleted",
        ]

        for event_type in event_types:
            event = ProxyHandleEvent(
                event_type=event_type,  # type: ignore
                source_type=SourceType.CUSTOM,
                handle_id=None,
            )
            assert event.event_type == event_type
