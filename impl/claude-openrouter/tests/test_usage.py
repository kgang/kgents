"""Tests for runtime/usage.py"""

import pytest

from runtime.usage import (
    UsageStats,
    UsageTracker,
    get_tracker,
    reset_tracker,
)
from runtime.messages import TokenUsage


class TestUsageStats:
    def test_total_tokens(self):
        stats = UsageStats(input_tokens=100, output_tokens=50)
        assert stats.total_tokens == 150

    def test_cache_hit_rate_zero(self):
        stats = UsageStats()
        assert stats.cache_hit_rate == 0.0

    def test_cache_hit_rate(self):
        stats = UsageStats(requests=10, cache_hits=3)
        assert stats.cache_hit_rate == 0.3


class TestUsageTracker:
    def test_track_usage(self):
        tracker = UsageTracker()
        usage = TokenUsage(input_tokens=10, output_tokens=20)

        tracker.track(usage)

        stats = tracker.get_session_stats()
        assert stats.input_tokens == 10
        assert stats.output_tokens == 20
        assert stats.requests == 1
        assert stats.cache_hits == 0

    def test_track_cached(self):
        tracker = UsageTracker()
        usage = TokenUsage(input_tokens=10, output_tokens=20)

        tracker.track(usage, cached=True)

        stats = tracker.get_session_stats()
        assert stats.cache_hits == 1

    def test_accumulate(self):
        tracker = UsageTracker()

        tracker.track(TokenUsage(10, 20))
        tracker.track(TokenUsage(30, 40))

        stats = tracker.get_session_stats()
        assert stats.input_tokens == 40
        assert stats.output_tokens == 60
        assert stats.requests == 2

    def test_reset(self):
        tracker = UsageTracker()
        tracker.track(TokenUsage(10, 20))
        tracker.reset()

        stats = tracker.get_session_stats()
        assert stats.requests == 0

    def test_callback(self):
        tracker = UsageTracker()
        callback_calls = []

        def callback(usage, cached):
            callback_calls.append((usage, cached))

        tracker.on_usage(callback)
        tracker.track(TokenUsage(10, 20), cached=True)

        assert len(callback_calls) == 1
        assert callback_calls[0][1] is True


class TestGetTracker:
    def setup_method(self):
        reset_tracker()

    def test_singleton(self):
        t1 = get_tracker()
        t2 = get_tracker()
        assert t1 is t2
