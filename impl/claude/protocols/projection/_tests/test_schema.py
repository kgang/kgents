"""Tests for projection schema types."""

from datetime import datetime, timedelta

import pytest

from protocols.projection.schema import (
    CacheMeta,
    ErrorInfo,
    RefusalInfo,
    StreamMeta,
    UIHint,
    WidgetEnvelope,
    WidgetMeta,
    WidgetStatus,
)

# =============================================================================
# WidgetStatus Tests
# =============================================================================


class TestWidgetStatus:
    """Tests for WidgetStatus enum."""

    def test_all_statuses_exist(self) -> None:
        """Verify all expected statuses are defined."""
        expected = {"IDLE", "LOADING", "STREAMING", "DONE", "ERROR", "REFUSAL", "STALE"}
        actual = {s.name for s in WidgetStatus}
        assert actual == expected

    def test_status_values_are_unique(self) -> None:
        """Verify all status values are unique."""
        values = [s.value for s in WidgetStatus]
        assert len(values) == len(set(values))


# =============================================================================
# CacheMeta Tests
# =============================================================================


class TestCacheMeta:
    """Tests for CacheMeta dataclass."""

    def test_defaults(self) -> None:
        """Test default values."""
        cache = CacheMeta()
        assert cache.is_cached is False
        assert cache.cached_at is None
        assert cache.ttl_seconds is None
        assert cache.cache_key is None
        assert cache.deterministic is True

    def test_is_stale_when_not_cached(self) -> None:
        """Non-cached data is never stale."""
        cache = CacheMeta(is_cached=False, cached_at=datetime.now(), ttl_seconds=60)
        assert cache.is_stale is False

    def test_is_stale_when_no_cached_at(self) -> None:
        """Data without timestamp is not stale."""
        cache = CacheMeta(is_cached=True, cached_at=None, ttl_seconds=60)
        assert cache.is_stale is False

    def test_is_stale_when_no_ttl(self) -> None:
        """Data without TTL is not stale."""
        cache = CacheMeta(is_cached=True, cached_at=datetime.now(), ttl_seconds=None)
        assert cache.is_stale is False

    def test_is_stale_fresh_data(self) -> None:
        """Recently cached data is not stale."""
        cache = CacheMeta(
            is_cached=True,
            cached_at=datetime.now() - timedelta(seconds=30),
            ttl_seconds=60,
        )
        assert cache.is_stale is False

    def test_is_stale_old_data(self) -> None:
        """Old cached data is stale."""
        cache = CacheMeta(
            is_cached=True,
            cached_at=datetime.now() - timedelta(seconds=120),
            ttl_seconds=60,
        )
        assert cache.is_stale is True

    def test_age_seconds_when_cached(self) -> None:
        """Age is calculated correctly for cached data."""
        cached_at = datetime.now() - timedelta(seconds=30)
        cache = CacheMeta(is_cached=True, cached_at=cached_at)
        age = cache.age_seconds
        assert age is not None
        assert 29 < age < 31  # Allow for timing variance

    def test_age_seconds_when_not_cached(self) -> None:
        """Age is None for non-cached data."""
        cache = CacheMeta(is_cached=False)
        assert cache.age_seconds is None


# =============================================================================
# ErrorInfo Tests
# =============================================================================


class TestErrorInfo:
    """Tests for ErrorInfo dataclass."""

    def test_basic_error(self) -> None:
        """Test creating a basic error."""
        error = ErrorInfo(
            category="network",
            code="ECONNREFUSED",
            message="Connection refused",
        )
        assert error.category == "network"
        assert error.code == "ECONNREFUSED"
        assert error.message == "Connection refused"
        assert error.retry_after_seconds is None

    def test_is_retryable_network(self) -> None:
        """Network errors are retryable."""
        error = ErrorInfo(category="network", code="CONN", message="fail")
        assert error.is_retryable is True

    def test_is_retryable_timeout(self) -> None:
        """Timeout errors are retryable."""
        error = ErrorInfo(category="timeout", code="TIMEOUT", message="fail")
        assert error.is_retryable is True

    def test_is_retryable_permission(self) -> None:
        """Permission errors are not retryable."""
        error = ErrorInfo(category="permission", code="FORBIDDEN", message="fail")
        assert error.is_retryable is False

    def test_is_retryable_validation(self) -> None:
        """Validation errors are not retryable."""
        error = ErrorInfo(category="validation", code="INVALID", message="fail")
        assert error.is_retryable is False


# =============================================================================
# RefusalInfo Tests
# =============================================================================


class TestRefusalInfo:
    """Tests for RefusalInfo dataclass."""

    def test_basic_refusal(self) -> None:
        """Test creating a basic refusal."""
        refusal = RefusalInfo(reason="Insufficient permissions")
        assert refusal.reason == "Insufficient permissions"
        assert refusal.consent_required is None
        assert refusal.appeal_to is None
        assert refusal.override_cost is None

    def test_refusal_with_consent(self) -> None:
        """Test refusal requiring consent."""
        refusal = RefusalInfo(
            reason="This action requires confirmation",
            consent_required="DELETE_DATA",
            appeal_to="self.soul.appeal",
            override_cost=10.0,
        )
        assert refusal.consent_required == "DELETE_DATA"
        assert refusal.appeal_to == "self.soul.appeal"
        assert refusal.override_cost == 10.0


# =============================================================================
# StreamMeta Tests
# =============================================================================


class TestStreamMeta:
    """Tests for StreamMeta dataclass."""

    def test_defaults(self) -> None:
        """Test default values."""
        stream = StreamMeta()
        assert stream.total_expected is None
        assert stream.received == 0
        assert stream.started_at is None
        assert stream.last_chunk_at is None

    def test_progress_indeterminate(self) -> None:
        """Progress is -1 when total is unknown."""
        stream = StreamMeta(total_expected=None, received=50)
        assert stream.progress == -1.0
        assert stream.is_indeterminate is True

    def test_progress_zero_total(self) -> None:
        """Progress is -1 when total is zero."""
        stream = StreamMeta(total_expected=0, received=0)
        assert stream.progress == -1.0

    def test_progress_partial(self) -> None:
        """Progress is calculated correctly."""
        stream = StreamMeta(total_expected=100, received=25)
        assert stream.progress == 0.25
        assert stream.is_indeterminate is False

    def test_progress_complete(self) -> None:
        """Progress caps at 1.0."""
        stream = StreamMeta(total_expected=100, received=150)
        assert stream.progress == 1.0

    def test_with_received(self) -> None:
        """with_received creates new instance."""
        original = StreamMeta(total_expected=100, received=0, started_at=datetime.now())
        updated = original.with_received(50)
        assert updated.received == 50
        assert updated.total_expected == 100
        assert updated.started_at == original.started_at
        assert updated.last_chunk_at is not None
        # Original is unchanged
        assert original.received == 0


# =============================================================================
# WidgetMeta Tests
# =============================================================================


class TestWidgetMeta:
    """Tests for WidgetMeta dataclass."""

    def test_defaults(self) -> None:
        """Test default values."""
        meta = WidgetMeta()
        assert meta.status == WidgetStatus.IDLE
        assert meta.cache is None
        assert meta.error is None
        assert meta.refusal is None
        assert meta.stream is None
        assert meta.ui_hint is None

    def test_is_loading_states(self) -> None:
        """Test is_loading for various states."""
        assert WidgetMeta(status=WidgetStatus.LOADING).is_loading is True
        assert WidgetMeta(status=WidgetStatus.STREAMING).is_loading is True
        assert WidgetMeta(status=WidgetStatus.IDLE).is_loading is False
        assert WidgetMeta(status=WidgetStatus.DONE).is_loading is False

    def test_show_cached_badge_fresh(self) -> None:
        """Fresh cached data doesn't show badge."""
        cache = CacheMeta(
            is_cached=True,
            cached_at=datetime.now() - timedelta(seconds=30),
            ttl_seconds=60,
        )
        meta = WidgetMeta(status=WidgetStatus.DONE, cache=cache)
        assert meta.show_cached_badge is False

    def test_show_cached_badge_stale(self) -> None:
        """Stale cached data shows badge."""
        cache = CacheMeta(
            is_cached=True,
            cached_at=datetime.now() - timedelta(seconds=120),
            ttl_seconds=60,
        )
        meta = WidgetMeta(status=WidgetStatus.STALE, cache=cache)
        assert meta.show_cached_badge is True

    def test_has_error(self) -> None:
        """Test has_error property."""
        error = ErrorInfo(category="network", code="ERR", message="fail")
        meta = WidgetMeta(status=WidgetStatus.ERROR, error=error)
        assert meta.has_error is True

        # Status must match
        meta_no_status = WidgetMeta(status=WidgetStatus.DONE, error=error)
        assert meta_no_status.has_error is False

    def test_has_refusal(self) -> None:
        """Test has_refusal property."""
        refusal = RefusalInfo(reason="Denied")
        meta = WidgetMeta(status=WidgetStatus.REFUSAL, refusal=refusal)
        assert meta.has_refusal is True

        # Status must match
        meta_no_status = WidgetMeta(status=WidgetStatus.DONE, refusal=refusal)
        assert meta_no_status.has_refusal is False

    def test_factory_idle(self) -> None:
        """Test idle factory."""
        meta = WidgetMeta.idle()
        assert meta.status == WidgetStatus.IDLE

    def test_factory_loading(self) -> None:
        """Test loading factory."""
        meta = WidgetMeta.loading()
        assert meta.status == WidgetStatus.LOADING

    def test_factory_streaming(self) -> None:
        """Test streaming factory."""
        stream = StreamMeta(total_expected=100)
        meta = WidgetMeta.streaming(stream)
        assert meta.status == WidgetStatus.STREAMING
        assert meta.stream == stream

    def test_factory_done(self) -> None:
        """Test done factory."""
        meta = WidgetMeta.done()
        assert meta.status == WidgetStatus.DONE

    def test_factory_done_stale(self) -> None:
        """Test done factory with stale cache becomes STALE."""
        cache = CacheMeta(
            is_cached=True,
            cached_at=datetime.now() - timedelta(seconds=120),
            ttl_seconds=60,
        )
        meta = WidgetMeta.done(cache)
        assert meta.status == WidgetStatus.STALE

    def test_factory_with_error(self) -> None:
        """Test with_error factory."""
        error = ErrorInfo(category="network", code="ERR", message="fail")
        meta = WidgetMeta.with_error(error)
        assert meta.status == WidgetStatus.ERROR
        assert meta.error == error

    def test_factory_with_refusal(self) -> None:
        """Test with_refusal factory."""
        refusal = RefusalInfo(reason="Denied")
        meta = WidgetMeta.with_refusal(refusal)
        assert meta.status == WidgetStatus.REFUSAL
        assert meta.refusal == refusal


# =============================================================================
# WidgetEnvelope Tests
# =============================================================================


class TestWidgetEnvelope:
    """Tests for WidgetEnvelope dataclass."""

    def test_basic_envelope(self) -> None:
        """Test creating a basic envelope."""
        data = {"name": "Alice", "score": 42}
        envelope = WidgetEnvelope(data=data)
        assert envelope.data == data
        assert envelope.meta.status == WidgetStatus.IDLE
        assert envelope.source_path is None

    def test_envelope_with_meta(self) -> None:
        """Test envelope with metadata."""
        data = "Hello"
        meta = WidgetMeta.done()
        envelope = WidgetEnvelope(
            data=data,
            meta=meta,
            source_path="world.town.manifest",
            observer_archetype="developer",
        )
        assert envelope.data == data
        assert envelope.meta.status == WidgetStatus.DONE
        assert envelope.source_path == "world.town.manifest"
        assert envelope.observer_archetype == "developer"

    def test_with_meta(self) -> None:
        """Test with_meta creates new instance."""
        original = WidgetEnvelope(data="test", meta=WidgetMeta.idle())
        updated = original.with_meta(WidgetMeta.loading())
        assert updated.meta.status == WidgetStatus.LOADING
        assert updated.data == "test"
        # Original unchanged
        assert original.meta.status == WidgetStatus.IDLE

    def test_with_status(self) -> None:
        """Test with_status creates new instance."""
        original = WidgetEnvelope(data="test", meta=WidgetMeta.idle())
        updated = original.with_status(WidgetStatus.DONE)
        assert updated.meta.status == WidgetStatus.DONE
        # Original unchanged
        assert original.meta.status == WidgetStatus.IDLE

    def test_to_dict_basic(self) -> None:
        """Test to_dict with basic envelope."""
        envelope = WidgetEnvelope(data={"key": "value"}, meta=WidgetMeta.done())
        result = envelope.to_dict()
        assert result["data"] == {"key": "value"}
        assert result["meta"]["status"] == "done"
        assert "cache" not in result["meta"]
        assert "error" not in result["meta"]

    def test_to_dict_with_cache(self) -> None:
        """Test to_dict includes cache when present."""
        cache = CacheMeta(
            is_cached=True,
            cached_at=datetime(2024, 1, 1, 12, 0, 0),
            ttl_seconds=300,
            cache_key="test-key",
        )
        meta = WidgetMeta(status=WidgetStatus.DONE, cache=cache)
        envelope = WidgetEnvelope(data="test", meta=meta)
        result = envelope.to_dict()

        assert "cache" in result["meta"]
        assert result["meta"]["cache"]["isCached"] is True
        assert result["meta"]["cache"]["ttlSeconds"] == 300
        assert result["meta"]["cache"]["cacheKey"] == "test-key"

    def test_to_dict_with_error(self) -> None:
        """Test to_dict includes error when present."""
        error = ErrorInfo(
            category="network",
            code="ECONNREFUSED",
            message="Connection refused",
            retry_after_seconds=5,
        )
        meta = WidgetMeta.with_error(error)
        envelope = WidgetEnvelope(data=None, meta=meta)
        result = envelope.to_dict()

        assert "error" in result["meta"]
        assert result["meta"]["error"]["category"] == "network"
        assert result["meta"]["error"]["code"] == "ECONNREFUSED"
        assert result["meta"]["error"]["retryAfterSeconds"] == 5

    def test_to_dict_with_refusal(self) -> None:
        """Test to_dict includes refusal when present."""
        refusal = RefusalInfo(
            reason="Access denied",
            consent_required="ADMIN_CONSENT",
            appeal_to="self.soul.appeal",
        )
        meta = WidgetMeta.with_refusal(refusal)
        envelope = WidgetEnvelope(data=None, meta=meta)
        result = envelope.to_dict()

        assert "refusal" in result["meta"]
        assert result["meta"]["refusal"]["reason"] == "Access denied"
        assert result["meta"]["refusal"]["consentRequired"] == "ADMIN_CONSENT"

    def test_to_dict_with_stream(self) -> None:
        """Test to_dict includes stream when present."""
        stream = StreamMeta(
            total_expected=100,
            received=50,
            started_at=datetime(2024, 1, 1, 12, 0, 0),
        )
        meta = WidgetMeta.streaming(stream)
        envelope = WidgetEnvelope(data="partial", meta=meta)
        result = envelope.to_dict()

        assert "stream" in result["meta"]
        assert result["meta"]["stream"]["totalExpected"] == 100
        assert result["meta"]["stream"]["received"] == 50

    def test_to_dict_with_provenance(self) -> None:
        """Test to_dict includes provenance fields."""
        envelope = WidgetEnvelope(
            data="test",
            meta=WidgetMeta.done(),
            source_path="world.town.manifest",
            observer_archetype="developer",
        )
        result = envelope.to_dict()

        assert result["sourcePath"] == "world.town.manifest"
        assert result["observerArchetype"] == "developer"


# =============================================================================
# Round-trip Serialization Tests
# =============================================================================


class TestSerialization:
    """Test JSON serialization round-trips."""

    def test_envelope_to_dict_all_fields(self) -> None:
        """Test that to_dict captures all fields."""
        cache = CacheMeta(
            is_cached=True,
            cached_at=datetime(2024, 1, 1, 12, 0, 0),
            ttl_seconds=300,
            cache_key="key",
            deterministic=True,
        )
        stream = StreamMeta(
            total_expected=100,
            received=50,
            started_at=datetime(2024, 1, 1, 12, 0, 0),
            last_chunk_at=datetime(2024, 1, 1, 12, 1, 0),
        )
        error = ErrorInfo(
            category="network",
            code="ERR",
            message="msg",
            retry_after_seconds=10,
            fallback_action="retry",
            trace_id="trace-123",
        )
        refusal = RefusalInfo(
            reason="denied",
            consent_required="consent",
            appeal_to="appeal",
            override_cost=5.0,
        )

        # Test with cache
        envelope = WidgetEnvelope(
            data={"test": "data"},
            meta=WidgetMeta(status=WidgetStatus.DONE, cache=cache),
            source_path="test.path",
            observer_archetype="tester",
        )
        result = envelope.to_dict()
        assert result["meta"]["cache"]["deterministic"] is True

        # Test with error
        envelope_err = WidgetEnvelope(
            data=None,
            meta=WidgetMeta(status=WidgetStatus.ERROR, error=error),
        )
        result_err = envelope_err.to_dict()
        assert result_err["meta"]["error"]["traceId"] == "trace-123"

        # Test with refusal
        envelope_ref = WidgetEnvelope(
            data=None,
            meta=WidgetMeta(status=WidgetStatus.REFUSAL, refusal=refusal),
        )
        result_ref = envelope_ref.to_dict()
        assert result_ref["meta"]["refusal"]["overrideCost"] == 5.0

        # Test with stream
        envelope_stream = WidgetEnvelope(
            data="partial",
            meta=WidgetMeta(status=WidgetStatus.STREAMING, stream=stream),
        )
        result_stream = envelope_stream.to_dict()
        assert result_stream["meta"]["stream"]["lastChunkAt"] is not None
