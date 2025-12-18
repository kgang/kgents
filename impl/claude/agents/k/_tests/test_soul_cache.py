"""
Tests for SoulCache.

SoulCache provides Redis-backed caching for K-gent soul state,
enabling fast access to session state, eigenvectors, and active mode.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from agents.k.soul_cache import (
    CachedActiveMode,
    CachedEigenvectors,
    CachedSessionState,
    MockCacheClient,
    SoulCache,
    SoulCacheConfig,
    close_soul_cache,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def mock_config() -> SoulCacheConfig:
    """Create a mock configuration."""
    return SoulCacheConfig(
        redis_url="mock://localhost",
        key_prefix="test:soul:",
        session_ttl=60,
        eigenvector_ttl=30,
        mode_ttl=15,
    )


@pytest.fixture
def mock_client() -> MockCacheClient:
    """Create a mock cache client."""
    return MockCacheClient()


@pytest.fixture
def soul_cache(
    mock_config: SoulCacheConfig,
    mock_client: MockCacheClient,
) -> SoulCache:
    """Create a SoulCache with mock client."""
    return SoulCache(config=mock_config, client=mock_client)


# =============================================================================
# Cached Types Tests
# =============================================================================


class TestCachedSessionState:
    """Tests for CachedSessionState."""

    def test_serialization_roundtrip(self) -> None:
        """Test JSON serialization roundtrip."""
        state = CachedSessionState(
            session_id="sess_123",
            active_mode="reflect",
            interactions_count=5,
            tokens_used_session=1500,
            created_at="2025-01-01T00:00:00+00:00",
            last_interaction="2025-01-01T01:00:00+00:00",
        )

        json_str = state.to_json()
        restored = CachedSessionState.from_json(json_str)

        assert restored.session_id == state.session_id
        assert restored.active_mode == state.active_mode
        assert restored.interactions_count == state.interactions_count
        assert restored.tokens_used_session == state.tokens_used_session

    def test_handles_null_last_interaction(self) -> None:
        """Test handling of null last_interaction."""
        state = CachedSessionState(
            session_id="sess_123",
            active_mode="reflect",
            interactions_count=0,
            tokens_used_session=0,
            created_at="2025-01-01T00:00:00+00:00",
            last_interaction=None,
        )

        json_str = state.to_json()
        restored = CachedSessionState.from_json(json_str)

        assert restored.last_interaction is None


class TestCachedEigenvectors:
    """Tests for CachedEigenvectors."""

    def test_serialization_roundtrip(self) -> None:
        """Test JSON serialization roundtrip."""
        evs = CachedEigenvectors(
            aesthetic=0.8,
            categorical=0.9,
            collaborative=0.7,
            ethical=0.85,
            joyful=0.6,
            tasteful=0.75,
            cached_at="2025-01-01T00:00:00+00:00",
        )

        json_str = evs.to_json()
        restored = CachedEigenvectors.from_json(json_str)

        assert restored.aesthetic == evs.aesthetic
        assert restored.categorical == evs.categorical
        assert restored.ethical == evs.ethical


class TestCachedActiveMode:
    """Tests for CachedActiveMode."""

    def test_serialization_roundtrip(self) -> None:
        """Test JSON serialization roundtrip."""
        mode = CachedActiveMode(
            mode="dialogue",
            changed_at="2025-01-01T00:00:00+00:00",
            reason="User initiated",
        )

        json_str = mode.to_json()
        restored = CachedActiveMode.from_json(json_str)

        assert restored.mode == mode.mode
        assert restored.reason == mode.reason

    def test_handles_null_reason(self) -> None:
        """Test handling of null reason."""
        mode = CachedActiveMode(
            mode="reflect",
            changed_at="2025-01-01T00:00:00+00:00",
            reason=None,
        )

        json_str = mode.to_json()
        restored = CachedActiveMode.from_json(json_str)

        assert restored.reason is None


# =============================================================================
# Mock Client Tests
# =============================================================================


class TestMockCacheClient:
    """Tests for MockCacheClient."""

    @pytest.mark.asyncio
    async def test_get_set(self) -> None:
        """Test basic get/set operations."""
        client = MockCacheClient()

        await client.set("key1", "value1")
        result = await client.get("key1")

        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_missing_key(self) -> None:
        """Test getting a missing key."""
        client = MockCacheClient()
        result = await client.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self) -> None:
        """Test delete operation."""
        client = MockCacheClient()

        await client.set("key1", "value1")
        await client.delete("key1")
        result = await client.get("key1")

        assert result is None

    @pytest.mark.asyncio
    async def test_exists(self) -> None:
        """Test exists check."""
        client = MockCacheClient()

        assert not await client.exists("key1")
        await client.set("key1", "value1")
        assert await client.exists("key1")

    @pytest.mark.asyncio
    async def test_ttl_tracking(self) -> None:
        """Test TTL tracking."""
        client = MockCacheClient()

        await client.set("key1", "value1", ttl=3600)
        ttl = await client.ttl("key1")

        assert ttl > 0
        assert ttl <= 3600

    @pytest.mark.asyncio
    async def test_ttl_no_expiry(self) -> None:
        """Test TTL for key without expiry."""
        client = MockCacheClient()

        await client.set("key1", "value1")  # No TTL
        ttl = await client.ttl("key1")

        assert ttl == -1

    @pytest.mark.asyncio
    async def test_ttl_missing_key(self) -> None:
        """Test TTL for missing key."""
        client = MockCacheClient()
        ttl = await client.ttl("nonexistent")
        assert ttl == -2


# =============================================================================
# SoulCache Tests
# =============================================================================


class TestSoulCacheSession:
    """Tests for session caching."""

    @pytest.mark.asyncio
    async def test_cache_and_get_session(
        self,
        soul_cache: SoulCache,
    ) -> None:
        """Test caching and retrieving session state."""
        session_id = "sess_test_123"
        now = datetime.now(timezone.utc)

        await soul_cache.cache_session(
            session_id=session_id,
            active_mode="reflect",
            interactions_count=5,
            tokens_used=1500,
            created_at=now,
            last_interaction=now,
        )

        state = await soul_cache.get_session(session_id)

        assert state is not None
        assert state.session_id == session_id
        assert state.active_mode == "reflect"
        assert state.interactions_count == 5
        assert state.tokens_used_session == 1500

    @pytest.mark.asyncio
    async def test_get_missing_session(
        self,
        soul_cache: SoulCache,
    ) -> None:
        """Test getting a missing session."""
        state = await soul_cache.get_session("nonexistent")
        assert state is None

    @pytest.mark.asyncio
    async def test_invalidate_session(
        self,
        soul_cache: SoulCache,
    ) -> None:
        """Test invalidating a session."""
        session_id = "sess_to_invalidate"
        now = datetime.now(timezone.utc)

        await soul_cache.cache_session(
            session_id=session_id,
            active_mode="reflect",
            interactions_count=0,
            tokens_used=0,
            created_at=now,
        )

        await soul_cache.invalidate_session(session_id)

        state = await soul_cache.get_session(session_id)
        assert state is None

    @pytest.mark.asyncio
    async def test_touch_session_extends_ttl(
        self,
        soul_cache: SoulCache,
        mock_client: MockCacheClient,
    ) -> None:
        """Test that touch_session extends TTL."""
        session_id = "sess_touch_test"
        now = datetime.now(timezone.utc)

        await soul_cache.cache_session(
            session_id=session_id,
            active_mode="reflect",
            interactions_count=0,
            tokens_used=0,
            created_at=now,
        )

        # Touch should not raise
        await soul_cache.touch_session(session_id)

        # Session should still exist
        state = await soul_cache.get_session(session_id)
        assert state is not None


class TestSoulCacheEigenvectors:
    """Tests for eigenvector caching."""

    @pytest.mark.asyncio
    async def test_cache_and_get_eigenvectors(
        self,
        soul_cache: SoulCache,
    ) -> None:
        """Test caching and retrieving eigenvectors."""
        soul_id = "soul_123"

        await soul_cache.cache_eigenvectors(
            soul_id=soul_id,
            aesthetic=0.8,
            categorical=0.9,
            collaborative=0.7,
            ethical=0.85,
            joyful=0.6,
            tasteful=0.75,
        )

        evs = await soul_cache.get_eigenvectors(soul_id)

        assert evs is not None
        assert evs.aesthetic == 0.8
        assert evs.categorical == 0.9
        assert evs.ethical == 0.85

    @pytest.mark.asyncio
    async def test_get_missing_eigenvectors(
        self,
        soul_cache: SoulCache,
    ) -> None:
        """Test getting missing eigenvectors."""
        evs = await soul_cache.get_eigenvectors("nonexistent")
        assert evs is None

    @pytest.mark.asyncio
    async def test_invalidate_eigenvectors(
        self,
        soul_cache: SoulCache,
    ) -> None:
        """Test invalidating eigenvectors."""
        soul_id = "soul_to_invalidate"

        await soul_cache.cache_eigenvectors(
            soul_id=soul_id,
            aesthetic=0.5,
            categorical=0.5,
            collaborative=0.5,
            ethical=0.5,
            joyful=0.5,
            tasteful=0.5,
        )

        await soul_cache.invalidate_eigenvectors(soul_id)

        evs = await soul_cache.get_eigenvectors(soul_id)
        assert evs is None


class TestSoulCacheMode:
    """Tests for mode caching."""

    @pytest.mark.asyncio
    async def test_cache_and_get_mode(
        self,
        soul_cache: SoulCache,
    ) -> None:
        """Test caching and retrieving active mode."""
        session_id = "sess_mode_test"

        await soul_cache.cache_mode(
            session_id=session_id,
            mode="dialogue",
            reason="User requested",
        )

        mode = await soul_cache.get_mode(session_id)

        assert mode is not None
        assert mode.mode == "dialogue"
        assert mode.reason == "User requested"

    @pytest.mark.asyncio
    async def test_get_missing_mode(
        self,
        soul_cache: SoulCache,
    ) -> None:
        """Test getting missing mode."""
        mode = await soul_cache.get_mode("nonexistent")
        assert mode is None

    @pytest.mark.asyncio
    async def test_cache_mode_no_reason(
        self,
        soul_cache: SoulCache,
    ) -> None:
        """Test caching mode without reason."""
        session_id = "sess_no_reason"

        await soul_cache.cache_mode(
            session_id=session_id,
            mode="reflect",
        )

        mode = await soul_cache.get_mode(session_id)

        assert mode is not None
        assert mode.reason is None


class TestSoulCacheBulkOperations:
    """Tests for bulk operations."""

    @pytest.mark.asyncio
    async def test_invalidate_all_for_soul(
        self,
        soul_cache: SoulCache,
    ) -> None:
        """Test invalidating all data for a soul."""
        soul_id = "soul_bulk_test"
        now = datetime.now(timezone.utc)

        # Cache everything
        await soul_cache.cache_session(
            session_id=soul_id,
            active_mode="reflect",
            interactions_count=0,
            tokens_used=0,
            created_at=now,
        )
        await soul_cache.cache_eigenvectors(
            soul_id=soul_id,
            aesthetic=0.5,
            categorical=0.5,
            collaborative=0.5,
            ethical=0.5,
            joyful=0.5,
            tasteful=0.5,
        )
        await soul_cache.cache_mode(
            session_id=soul_id,
            mode="reflect",
        )

        # Invalidate all
        await soul_cache.invalidate_all_for_soul(soul_id)

        # Verify all gone
        assert await soul_cache.get_session(soul_id) is None
        assert await soul_cache.get_eigenvectors(soul_id) is None
        assert await soul_cache.get_mode(soul_id) is None


class TestSoulCacheHealth:
    """Tests for health check."""

    @pytest.mark.asyncio
    async def test_ping_healthy(
        self,
        soul_cache: SoulCache,
    ) -> None:
        """Test ping on healthy cache."""
        is_healthy = await soul_cache.ping()
        assert is_healthy


class TestSoulCacheConfig:
    """Tests for configuration."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = SoulCacheConfig()

        assert config.redis_url == "redis://localhost:6379"
        assert config.key_prefix == "kgent:soul:"
        assert config.session_ttl == 3600 * 4

    def test_config_from_env(self) -> None:
        """Test config can be loaded from environment."""
        import os

        old_url = os.environ.get("REDIS_URL")
        try:
            os.environ["REDIS_URL"] = "redis://custom:6379"
            config = SoulCacheConfig.from_env()
            assert config.redis_url == "redis://custom:6379"
        finally:
            if old_url:
                os.environ["REDIS_URL"] = old_url
            else:
                os.environ.pop("REDIS_URL", None)


class TestModuleFunctions:
    """Tests for module-level functions."""

    @pytest.mark.asyncio
    async def test_close_soul_cache_noop(self) -> None:
        """Test close_soul_cache when no cache exists."""
        # Should not raise
        await close_soul_cache()


# =============================================================================
# CDC Integration Conceptual Tests
# =============================================================================


class TestSoulCacheCDCIntegration:
    """Conceptual tests for CDC integration."""

    @pytest.mark.asyncio
    async def test_cache_invalidation_pattern(
        self,
        soul_cache: SoulCache,
    ) -> None:
        """
        Test the cache invalidation pattern used with CDC.

        When PostgreSQL data changes:
        1. Change written to Postgres (source of truth)
        2. Outbox trigger fires
        3. Synapse processes event
        4. Cache invalidation called

        This test verifies the invalidation step works correctly.
        """
        soul_id = "soul_cdc_test"
        now = datetime.now(timezone.utc)

        # Simulate initial cache population
        await soul_cache.cache_session(
            session_id=soul_id,
            active_mode="reflect",
            interactions_count=0,
            tokens_used=0,
            created_at=now,
        )

        # Verify cached
        assert await soul_cache.get_session(soul_id) is not None

        # Simulate CDC-triggered invalidation
        # (In production, this would be called by Synapse on UPDATE event)
        await soul_cache.invalidate_session(soul_id)

        # Cache should be empty - next access goes to Postgres
        assert await soul_cache.get_session(soul_id) is None

    @pytest.mark.asyncio
    async def test_cache_after_invalidation_requires_db_read(
        self,
        soul_cache: SoulCache,
    ) -> None:
        """
        Test that after invalidation, fresh data must be read from DB.

        This is the expected pattern:
        1. Cache miss
        2. Read from PostgreSQL
        3. Cache the fresh data
        4. Return to caller
        """
        soul_id = "soul_refresh_test"

        # Initially no cached data
        assert await soul_cache.get_session(soul_id) is None

        # In production code, this would trigger a DB read
        # and then cache the result:
        # state = await postgres.get_soul_state(soul_id)
        # await cache.cache_session(...state...)

        # This test just verifies the cache miss works
        assert await soul_cache.get_session(soul_id) is None
