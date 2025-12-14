"""
Tests for usage metering.

Tests:
- Request tracking
- Token usage tracking
- Rate limiting
- Daily/monthly quota enforcement
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from protocols.api.metering import (
    UsageStats,
    check_rate_limit,
    check_token_quota,
    clear_usage_stats,
    get_usage_stats,
    record_request,
    reset_daily_stats,
)


@pytest.fixture
def clean_usage() -> None:
    """Clean usage stats before each test."""
    clear_usage_stats()


class TestUsageStats:
    """Tests for UsageStats dataclass."""

    def test_usage_stats_creation(self) -> None:
        """Test UsageStats creation."""
        stats = UsageStats(user_id="test_user")

        assert stats.user_id == "test_user"
        assert stats.requests_today == 0
        assert stats.tokens_today == 0
        assert stats.tokens_month == 0
        assert stats.last_request is None
        assert stats.first_request_today is None
        assert stats.endpoints_hit == {}


class TestUsageTracking:
    """Tests for usage tracking."""

    def test_get_usage_stats_new_user(self, clean_usage: None) -> None:
        """Test getting stats for new user creates entry."""
        stats = get_usage_stats("new_user")

        assert stats.user_id == "new_user"
        assert stats.requests_today == 0

    def test_get_usage_stats_existing_user(self, clean_usage: None) -> None:
        """Test getting stats for existing user."""
        # Create initial stats
        stats1 = get_usage_stats("user_1")
        stats1.requests_today = 5

        # Get again
        stats2 = get_usage_stats("user_1")

        assert stats2.user_id == "user_1"
        assert stats2.requests_today == 5
        assert stats1 is stats2  # Same object

    def test_record_request_basic(self, clean_usage: None) -> None:
        """Test recording a basic request."""
        record_request("user_1", "/v1/soul/dialogue", tokens_used=100)

        stats = get_usage_stats("user_1")

        assert stats.requests_today == 1
        assert stats.tokens_today == 100
        assert stats.tokens_month == 100
        assert stats.last_request is not None
        assert stats.first_request_today is not None
        assert stats.endpoints_hit["/v1/soul/dialogue"] == 1

    def test_record_multiple_requests(self, clean_usage: None) -> None:
        """Test recording multiple requests."""
        record_request("user_1", "/v1/soul/dialogue", tokens_used=100)
        record_request("user_1", "/v1/soul/dialogue", tokens_used=150)
        record_request("user_1", "/v1/soul/governance", tokens_used=50)

        stats = get_usage_stats("user_1")

        assert stats.requests_today == 3
        assert stats.tokens_today == 300
        assert stats.tokens_month == 300
        assert stats.endpoints_hit["/v1/soul/dialogue"] == 2
        assert stats.endpoints_hit["/v1/soul/governance"] == 1

    def test_record_request_multiple_users(self, clean_usage: None) -> None:
        """Test recording requests for multiple users."""
        record_request("user_1", "/v1/soul/dialogue", tokens_used=100)
        record_request("user_2", "/v1/soul/dialogue", tokens_used=200)

        stats1 = get_usage_stats("user_1")
        stats2 = get_usage_stats("user_2")

        assert stats1.tokens_today == 100
        assert stats2.tokens_today == 200


class TestDailyReset:
    """Tests for daily statistics reset."""

    def test_reset_daily_stats(self, clean_usage: None) -> None:
        """Test resetting daily stats."""
        # Set up some stats
        record_request("user_1", "/v1/soul/dialogue", tokens_used=100)

        stats = get_usage_stats("user_1")
        assert stats.requests_today == 1
        assert stats.tokens_today == 100
        monthly_before = stats.tokens_month

        # Reset daily
        reset_daily_stats("user_1")

        # Check reset
        assert stats.requests_today == 0
        assert stats.tokens_today == 0
        assert stats.first_request_today is None
        # Monthly should NOT reset
        assert stats.tokens_month == monthly_before

    def test_automatic_daily_reset(self, clean_usage: None) -> None:
        """Test automatic daily reset on new day."""
        # Record request
        record_request("user_1", "/v1/soul/dialogue", tokens_used=100)

        stats = get_usage_stats("user_1")
        assert stats.requests_today == 1

        # Simulate new day by manipulating first_request_today
        stats.first_request_today = datetime.now() - timedelta(days=1)

        # Record another request
        record_request("user_1", "/v1/soul/dialogue", tokens_used=50)

        # Should have reset daily count
        stats = get_usage_stats("user_1")
        assert stats.requests_today == 1  # Reset and then incremented
        assert stats.tokens_today == 50  # Reset and then incremented
        assert stats.tokens_month == 150  # NOT reset


class TestRateLimiting:
    """Tests for rate limit checking."""

    def test_check_rate_limit_under_limit(self, clean_usage: None) -> None:
        """Test rate limit check when under limit."""
        record_request("user_1", "/test", tokens_used=0)

        allowed, error = check_rate_limit("user_1", rate_limit=100)

        assert allowed is True
        assert error is None

    def test_check_rate_limit_at_limit(self, clean_usage: None) -> None:
        """Test rate limit check at exact limit.

        With the pre-record pattern (record BEFORE check), at exactly 10 requests
        with limit 10, the 10th request is still allowed. The 11th is denied.
        """
        # Record up to limit
        for _ in range(10):
            record_request("user_1", "/test", tokens_used=0)

        # At exactly 10 requests, the limit allows it (we're AT the limit, not OVER)
        allowed, error = check_rate_limit("user_1", rate_limit=10)

        assert allowed is True  # 10 <= 10, so allowed
        assert error is None

        # Record one more (11th request)
        record_request("user_1", "/test", tokens_used=0)
        allowed, error = check_rate_limit("user_1", rate_limit=10)

        # Now we're over the limit
        assert allowed is False
        assert error is not None
        assert "Rate limit" in error

    def test_check_rate_limit_over_limit(self, clean_usage: None) -> None:
        """Test rate limit check when over limit."""
        # Record beyond limit
        for _ in range(15):
            record_request("user_1", "/test", tokens_used=0)

        allowed, error = check_rate_limit("user_1", rate_limit=10)

        assert allowed is False
        assert error is not None

    def test_check_rate_limit_new_user(self, clean_usage: None) -> None:
        """Test rate limit check for new user."""
        allowed, error = check_rate_limit("new_user", rate_limit=100)

        assert allowed is True
        assert error is None


class TestTokenQuota:
    """Tests for token quota checking."""

    def test_check_token_quota_unlimited(self, clean_usage: None) -> None:
        """Test token quota with unlimited (0) limit."""
        record_request("user_1", "/test", tokens_used=1000000)

        allowed, error = check_token_quota("user_1", monthly_limit=0)

        assert allowed is True
        assert error is None

    def test_check_token_quota_under_limit(self, clean_usage: None) -> None:
        """Test token quota when under limit."""
        record_request("user_1", "/test", tokens_used=5000)

        allowed, error = check_token_quota(
            "user_1", monthly_limit=10000, tokens_needed=1000
        )

        assert allowed is True
        assert error is None

    def test_check_token_quota_would_exceed(self, clean_usage: None) -> None:
        """Test token quota when request would exceed."""
        record_request("user_1", "/test", tokens_used=9500)

        allowed, error = check_token_quota(
            "user_1", monthly_limit=10000, tokens_needed=1000
        )

        assert allowed is False
        assert error is not None
        assert "quota exceeded" in error.lower()

    def test_check_token_quota_already_exceeded(self, clean_usage: None) -> None:
        """Test token quota when already exceeded."""
        record_request("user_1", "/test", tokens_used=11000)

        allowed, error = check_token_quota("user_1", monthly_limit=10000)

        assert allowed is False
        assert error is not None

    def test_check_token_quota_new_user(self, clean_usage: None) -> None:
        """Test token quota for new user."""
        allowed, error = check_token_quota("new_user", monthly_limit=10000)

        assert allowed is True
        assert error is None


class TestUsageStatistics:
    """Tests for usage statistics collection."""

    def test_get_all_usage_stats_empty(self, clean_usage: None) -> None:
        """Test getting all stats when empty."""
        from protocols.api.metering import get_all_usage_stats

        stats = get_all_usage_stats()

        assert stats == {}

    def test_get_all_usage_stats_multiple_users(self, clean_usage: None) -> None:
        """Test getting all stats with multiple users."""
        from protocols.api.metering import get_all_usage_stats

        record_request("user_1", "/test", tokens_used=100)
        record_request("user_2", "/test", tokens_used=200)

        stats = get_all_usage_stats()

        assert len(stats) == 2
        assert stats["user_1"]["tokens_today"] == 100
        assert stats["user_2"]["tokens_today"] == 200

    def test_usage_stats_serialization(self, clean_usage: None) -> None:
        """Test usage stats are properly serializable."""
        from protocols.api.metering import get_all_usage_stats

        record_request("user_1", "/test", tokens_used=100)

        stats = get_all_usage_stats()

        # Should be JSON-serializable
        import json

        json_str = json.dumps(stats)
        assert json_str is not None

        # Deserialize and verify
        data = json.loads(json_str)
        assert data["user_1"]["tokens_today"] == 100


class TestEndpointTracking:
    """Tests for endpoint-specific tracking."""

    def test_track_multiple_endpoints(self, clean_usage: None) -> None:
        """Test tracking different endpoints."""
        record_request("user_1", "/v1/soul/dialogue", tokens_used=100)
        record_request("user_1", "/v1/soul/governance", tokens_used=50)
        record_request("user_1", "/v1/soul/dialogue", tokens_used=100)

        stats = get_usage_stats("user_1")

        assert stats.endpoints_hit["/v1/soul/dialogue"] == 2
        assert stats.endpoints_hit["/v1/soul/governance"] == 1

    def test_endpoint_tracking_with_query_params(self, clean_usage: None) -> None:
        """Test endpoint tracking treats query params separately."""
        record_request("user_1", "/v1/soul/dialogue?mode=reflect", tokens_used=100)
        record_request("user_1", "/v1/soul/dialogue?mode=advise", tokens_used=100)

        stats = get_usage_stats("user_1")

        # These are tracked as different endpoints
        assert len(stats.endpoints_hit) == 2
