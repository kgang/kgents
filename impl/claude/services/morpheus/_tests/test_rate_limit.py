"""
Tests for Morpheus per-observer rate limiting.
"""

import pytest

from services.morpheus import (
    ChatMessage,
    ChatRequest,
    GatewayConfig,
    MorpheusGateway,
    MorpheusPersistence,
    RateLimitError,
    RateLimitState,
)
from services.morpheus.adapters.mock import MockAdapter


@pytest.fixture
def low_limit_config() -> GatewayConfig:
    """Config with very low rate limits for testing."""
    return GatewayConfig(
        rate_limit_rpm=5,
        rate_limit_by_archetype={
            "admin": 10,
            "developer": 5,
            "guest": 2,
        },
    )


@pytest.fixture
def gateway_with_limits(low_limit_config: GatewayConfig) -> MorpheusGateway:
    """Gateway with low rate limits."""
    gateway = MorpheusGateway(config=low_limit_config)
    gateway.register_provider("mock", MockAdapter(), prefix="mock-")
    return gateway


class TestRateLimitState:
    """Tests for RateLimitState tracking."""

    def test_check_and_record_allows_under_limit(self):
        """Requests under limit should be allowed."""
        state = RateLimitState()

        allowed, remaining = state.check_and_record("guest", 5)
        assert allowed is True
        assert remaining == 4

    def test_check_and_record_tracks_multiple(self):
        """Multiple requests should be tracked."""
        state = RateLimitState()

        # First request: remaining = 5 - 1 = 4
        # Second request: remaining = 5 - 2 = 3
        # Third request: remaining = 5 - 3 = 2
        expected_remaining = [4, 3, 2]
        for i in range(3):
            allowed, remaining = state.check_and_record("guest", 5)
            assert allowed is True
            assert remaining == expected_remaining[i]

    def test_check_and_record_blocks_at_limit(self):
        """Requests at limit should be blocked."""
        state = RateLimitState()

        # Use up the limit
        for _ in range(3):
            state.check_and_record("guest", 3)

        # Next should be blocked
        allowed, remaining = state.check_and_record("guest", 3)
        assert allowed is False
        assert remaining == 0

    def test_check_and_record_separate_archetypes(self):
        """Different archetypes should have separate limits."""
        state = RateLimitState()

        # Use up guest limit
        for _ in range(2):
            state.check_and_record("guest", 2)

        # Guest blocked
        allowed, _ = state.check_and_record("guest", 2)
        assert allowed is False

        # Admin still allowed
        allowed, _ = state.check_and_record("admin", 10)
        assert allowed is True

    def test_get_usage_returns_count(self):
        """get_usage should return current request count."""
        state = RateLimitState()

        state.check_and_record("developer", 10)
        state.check_and_record("developer", 10)

        usage = state.get_usage("developer")
        assert usage == 2


class TestRateLimitError:
    """Tests for RateLimitError exception."""

    def test_error_message(self):
        """Error should have informative message."""
        error = RateLimitError("guest", 20)

        assert "guest" in str(error)
        assert "20" in str(error)
        assert error.archetype == "guest"
        assert error.limit == 20
        assert error.retry_after == 60.0


class TestGatewayRateLimiting:
    """Tests for MorpheusGateway rate limiting."""

    async def test_complete_respects_rate_limit(
        self, gateway_with_limits: MorpheusGateway
    ):
        """Completions should respect rate limits."""
        request = ChatRequest(
            model="mock-test",
            messages=[ChatMessage(role="user", content="test")],
        )

        # Guest has limit of 2
        # First two should succeed
        await gateway_with_limits.complete(request, archetype="guest")
        await gateway_with_limits.complete(request, archetype="guest")

        # Third should raise RateLimitError
        with pytest.raises(RateLimitError) as exc_info:
            await gateway_with_limits.complete(request, archetype="guest")

        assert exc_info.value.archetype == "guest"
        assert exc_info.value.limit == 2

    async def test_admin_has_higher_limit(
        self, gateway_with_limits: MorpheusGateway
    ):
        """Admins should have higher rate limits."""
        request = ChatRequest(
            model="mock-test",
            messages=[ChatMessage(role="user", content="test")],
        )

        # Admin has limit of 10 - should handle 5 requests fine
        for _ in range(5):
            await gateway_with_limits.complete(request, archetype="admin")

        # Still under limit
        status = gateway_with_limits.rate_limit_status("admin")
        assert status["remaining"] > 0

    async def test_stream_respects_rate_limit(
        self, gateway_with_limits: MorpheusGateway
    ):
        """Streaming should respect rate limits."""
        request = ChatRequest(
            model="mock-test",
            messages=[ChatMessage(role="user", content="test")],
        )

        # Use up guest limit
        for _ in range(2):
            async for _ in gateway_with_limits.stream(request, archetype="guest"):
                pass

        # Third stream should yield rate limit error
        chunks = []
        async for chunk in gateway_with_limits.stream(request, archetype="guest"):
            chunks.append(chunk)

        # Should have error in content
        assert len(chunks) >= 1
        content = chunks[0].choices[0].delta.content
        assert "Rate limit exceeded" in content

    def test_rate_limit_status(self, gateway_with_limits: MorpheusGateway):
        """rate_limit_status should return correct info."""
        status = gateway_with_limits.rate_limit_status("guest")

        assert status["archetype"] == "guest"
        assert status["limit_rpm"] == 2
        assert status["current_usage"] == 0
        assert status["remaining"] == 2


class TestPersistenceRateLimiting:
    """Tests for MorpheusPersistence rate limiting integration."""

    async def test_persistence_complete_with_rate_limit(self):
        """Persistence should pass archetype for rate limiting."""
        config = GatewayConfig(rate_limit_by_archetype={"guest": 1})
        gateway = MorpheusGateway(config=config)
        gateway.register_provider("mock", MockAdapter(), prefix="mock-")
        persistence = MorpheusPersistence(gateway=gateway, telemetry_enabled=False)

        request = ChatRequest(
            model="mock-test",
            messages=[ChatMessage(role="user", content="test")],
        )

        # First request succeeds
        result = await persistence.complete(request, archetype="guest")
        assert result.response is not None

        # Second request should raise
        with pytest.raises(RateLimitError):
            await persistence.complete(request, archetype="guest")

    def test_persistence_rate_limit_status(self):
        """Persistence should expose rate limit status."""
        config = GatewayConfig(
            rate_limit_by_archetype={"developer": 50},
        )
        gateway = MorpheusGateway(config=config)
        gateway.register_provider("mock", MockAdapter(), prefix="mock-")
        persistence = MorpheusPersistence(gateway=gateway)

        status = persistence.rate_limit_status("developer")

        assert status["archetype"] == "developer"
        assert status["limit_rpm"] == 50
