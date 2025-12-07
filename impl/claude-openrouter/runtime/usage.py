"""
Usage Tracking

Track token usage for informational purposes.
For Max subscribers, this is purely informational (not billing).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable

from .messages import TokenUsage


@dataclass
class UsageStats:
    """Aggregate usage statistics"""
    input_tokens: int = 0
    output_tokens: int = 0
    requests: int = 0
    cache_hits: int = 0
    started_at: datetime = field(default_factory=datetime.now)

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cache_hit_rate(self) -> float:
        if self.requests == 0:
            return 0.0
        return self.cache_hits / self.requests

    def __repr__(self) -> str:
        return (
            f"<UsageStats requests={self.requests} "
            f"tokens={self.total_tokens} "
            f"cache_rate={self.cache_hit_rate:.1%}>"
        )


class UsageTracker:
    """Track token usage across requests"""

    def __init__(self):
        self._stats = UsageStats()
        self._callbacks: list[Callable[[TokenUsage, bool], None]] = []

    def track(self, usage: TokenUsage, cached: bool = False) -> None:
        """Record a completion's token usage"""
        self._stats.input_tokens += usage.input_tokens
        self._stats.output_tokens += usage.output_tokens
        self._stats.requests += 1
        if cached:
            self._stats.cache_hits += 1

        # Notify callbacks
        for callback in self._callbacks:
            callback(usage, cached)

    def get_session_stats(self) -> UsageStats:
        """Get current session statistics"""
        return self._stats

    def reset(self) -> None:
        """Reset usage statistics"""
        self._stats = UsageStats()

    def on_usage(self, callback: Callable[[TokenUsage, bool], None]) -> None:
        """Register a callback for usage events"""
        self._callbacks.append(callback)


# Global tracker singleton
_tracker: UsageTracker | None = None


def get_tracker() -> UsageTracker:
    """Get the global usage tracker"""
    global _tracker
    if _tracker is None:
        _tracker = UsageTracker()
    return _tracker


def reset_tracker() -> None:
    """Reset the global tracker"""
    global _tracker
    _tracker = None
