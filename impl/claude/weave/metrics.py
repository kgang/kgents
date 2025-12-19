"""
Compression Metrics for Turn-gents Hypothesis Validation.

This module tracks compression metrics to validate the Turn-gents H1 hypothesis:
> "Context computed via CausalCone projection is <50% the size of
>  equivalent linear ContextWindow for multi-agent interactions."

Usage:
    from weave.metrics import log_compression, get_metrics

    # Log a compression event
    log_compression(agent_id="K-gent", full_tokens=1000, cone_tokens=400)

    # Get aggregated metrics
    metrics = get_metrics()
    print(f"H1 passed: {metrics.h1_passed}")  # True if avg compression >= 50%

The metrics are designed to be:
1. Lightweight: Minimal overhead per event
2. Aggregatable: Can compute session and lifetime stats
3. Observable: Can be exported to dashboard/OTEL
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

# Global compression event log (in-memory for now)
_compression_events: list["CompressionEvent"] = []


@dataclass
class CompressionEvent:
    """
    A single compression measurement event.

    Records the difference between full context and causal cone context
    for a specific agent at a specific time.
    """

    timestamp: float
    agent_id: str
    full_tokens: int  # Size of full linear context
    cone_tokens: int  # Size of causal cone context
    compression_ratio: float  # 1.0 - (cone/full)


@dataclass
class CompressionMetrics:
    """
    Aggregated compression metrics for H1 validation.

    The key metric is h1_passed: whether average compression >= 50%.
    This validates the Turn-gents hypothesis that CausalCone projection
    provides significant context reduction.
    """

    total_events: int
    avg_compression: float  # Average compression ratio (0.0 - 1.0)
    total_tokens_saved: int  # Total tokens saved across all events
    h1_passed: bool  # True if avg_compression >= 0.5

    # Per-agent breakdowns
    by_agent: dict[str, "AgentCompressionStats"] = field(default_factory=dict)


@dataclass
class AgentCompressionStats:
    """Compression statistics for a single agent."""

    agent_id: str
    event_count: int
    avg_compression: float
    total_full_tokens: int
    total_cone_tokens: int
    tokens_saved: int

    @property
    def compression_pct(self) -> int:
        """Compression ratio as integer percentage."""
        return int(self.avg_compression * 100)


def log_compression(agent_id: str, full_tokens: int, cone_tokens: int) -> None:
    """
    Log a compression measurement event.

    Call this after computing a causal cone for an agent to track
    how much context was saved compared to full linear history.

    Args:
        agent_id: The agent whose context was computed
        full_tokens: Size of full linear context (estimated token count)
        cone_tokens: Size of causal cone context (estimated token count)
    """
    if full_tokens <= 0:
        return  # Can't compute ratio for empty context

    ratio = 1.0 - (cone_tokens / full_tokens) if full_tokens > 0 else 0.0
    ratio = max(0.0, min(1.0, ratio))  # Clamp to [0, 1]

    event = CompressionEvent(
        timestamp=time.time(),
        agent_id=agent_id,
        full_tokens=full_tokens,
        cone_tokens=cone_tokens,
        compression_ratio=ratio,
    )
    _compression_events.append(event)


def get_metrics() -> CompressionMetrics:
    """
    Get aggregated compression metrics.

    Returns metrics including:
    - Total events logged
    - Average compression ratio
    - Total tokens saved
    - H1 passed (True if avg compression >= 50%)
    - Per-agent breakdown

    Returns empty metrics if no events logged.
    """
    if not _compression_events:
        return CompressionMetrics(
            total_events=0,
            avg_compression=0.0,
            total_tokens_saved=0,
            h1_passed=False,
            by_agent={},
        )

    # Compute aggregates
    total_saved = sum(e.full_tokens - e.cone_tokens for e in _compression_events)
    avg_ratio = sum(e.compression_ratio for e in _compression_events) / len(_compression_events)

    # Per-agent breakdown
    agent_events: dict[str, list[CompressionEvent]] = {}
    for event in _compression_events:
        agent_events.setdefault(event.agent_id, []).append(event)

    by_agent: dict[str, AgentCompressionStats] = {}
    for agent_id, events in agent_events.items():
        total_full = sum(e.full_tokens for e in events)
        total_cone = sum(e.cone_tokens for e in events)
        agent_avg = sum(e.compression_ratio for e in events) / len(events)

        by_agent[agent_id] = AgentCompressionStats(
            agent_id=agent_id,
            event_count=len(events),
            avg_compression=agent_avg,
            total_full_tokens=total_full,
            total_cone_tokens=total_cone,
            tokens_saved=total_full - total_cone,
        )

    return CompressionMetrics(
        total_events=len(_compression_events),
        avg_compression=avg_ratio,
        total_tokens_saved=total_saved,
        h1_passed=avg_ratio >= 0.5,
        by_agent=by_agent,
    )


def reset_metrics() -> None:
    """
    Reset all compression metrics.

    Use this at the start of a new test session or benchmark run.
    """
    global _compression_events
    _compression_events = []


def get_events() -> list[CompressionEvent]:
    """
    Get all raw compression events.

    Useful for detailed analysis or export.
    """
    return _compression_events.copy()


def estimate_tokens(text_or_events: Any, chars_per_token: int = 4) -> int:
    """
    Estimate token count from text or event list.

    This is a rough estimate based on average characters per token.
    Real token counting would require a tokenizer.

    Args:
        text_or_events: String or list of events
        chars_per_token: Average characters per token (default: 4)

    Returns:
        Estimated token count
    """
    if isinstance(text_or_events, str):
        return len(text_or_events) // chars_per_token
    elif isinstance(text_or_events, list):
        # Estimate ~100 chars per event
        return (len(text_or_events) * 100) // chars_per_token
    else:
        return 0


__all__ = [
    "CompressionEvent",
    "CompressionMetrics",
    "AgentCompressionStats",
    "log_compression",
    "get_metrics",
    "reset_metrics",
    "get_events",
    "estimate_tokens",
]
