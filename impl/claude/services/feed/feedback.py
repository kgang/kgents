"""
Feed Feedback: User interaction tracking for personalization.

"The user creates feedback systems WITH the feed. This is recursive and powerful."

This module implements:
- FeedbackAction: Enum of user actions (view, engage, dismiss, contradict)
- FeedbackEvent: Timestamped user interaction with K-Block
- AttentionTracker: In-memory attention tracking (for MVP)
- FeedbackSystem: Orchestrates feedback loop

Philosophy:
    The system adapts to user wants and needs.
    The system does NOT change behavior against user will.
    (Linear Adaptation principle)
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Protocol

from services.k_block.core.kblock import KBlock

# =============================================================================
# Feedback Actions
# =============================================================================


class FeedbackAction(Enum):
    """
    User actions that provide feedback to the feed algorithm.

    Actions:
    - VIEW: Passive attention (user saw the K-Block)
    - ENGAGE: Active interaction (edit, comment, link, copy)
    - DISMISS: Negative signal (user actively dismissed/hid)
    - CONTRADICT: User marked contradiction (special case of engage)
    """

    VIEW = "view"
    ENGAGE = "engage"
    DISMISS = "dismiss"
    CONTRADICT = "contradict"


# =============================================================================
# Feedback Event
# =============================================================================


@dataclass(frozen=True)
class FeedbackEvent:
    """
    A timestamped user interaction with a K-Block.

    Immutable record of feedback for analysis and learning.
    """

    user_id: str
    kblock_id: str
    action: FeedbackAction
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: "dict[str, str]" = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "user_id": self.user_id,
            "kblock_id": self.kblock_id,
            "action": self.action.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


# =============================================================================
# Attention Tracker Protocol
# =============================================================================


class AttentionTrackerProtocol(Protocol):
    """
    Protocol for attention tracking implementations.

    Allows swapping between in-memory (MVP) and persistent (production).
    """

    async def record_view(self, user_id: str, kblock_id: str) -> None:
        """Record a view (passive attention)."""
        ...

    async def record_engagement(self, user_id: str, kblock_id: str) -> None:
        """Record an engagement (active interaction)."""
        ...

    async def record_dismissal(self, user_id: str, kblock_id: str) -> None:
        """Record a dismissal (negative signal)."""
        ...

    async def get_attention_score(self, user_id: str, kblock_id: str) -> float:
        """Get attention score for a K-Block (0.0 to 1.0)."""
        ...

    async def get_stats(self, user_id: str, kblock_id: str) -> dict[str, int]:
        """Get raw attention stats."""
        ...


# =============================================================================
# In-Memory Attention Tracker (MVP)
# =============================================================================


class InMemoryAttentionTracker:
    """
    In-memory attention tracking for MVP.

    Tracks views, engagements, and dismissals per user per K-Block.
    Computes attention scores on the fly.

    NOTE: This is an in-memory implementation. For production,
    use PersistentAttentionTracker with database backend.
    """

    def __init__(self) -> None:
        # (user_id, kblock_id) -> {views, engagements, dismissals}
        self._attention: dict[tuple[str, str], dict[str, int]] = defaultdict(
            lambda: {"views": 0, "engagements": 0, "dismissals": 0}
        )

    async def record_view(self, user_id: str, kblock_id: str) -> None:
        """Record a view (passive attention)."""
        key = (user_id, kblock_id)
        self._attention[key]["views"] += 1

    async def record_engagement(self, user_id: str, kblock_id: str) -> None:
        """Record an engagement (active interaction)."""
        key = (user_id, kblock_id)
        self._attention[key]["engagements"] += 1

    async def record_dismissal(self, user_id: str, kblock_id: str) -> None:
        """Record a dismissal (negative signal)."""
        key = (user_id, kblock_id)
        self._attention[key]["dismissals"] += 1

    async def get_attention_score(self, user_id: str, kblock_id: str) -> float:
        """
        Get attention score for a K-Block (0.0 to 1.0).

        Formula: (engagements * 2 + views * 0.5 - dismissals) / (total + 1)
        Normalized to [0, 1] range.
        """
        key = (user_id, kblock_id)
        attention = self._attention[key]

        views = attention["views"]
        engagements = attention["engagements"]
        dismissals = attention["dismissals"]

        total = views + engagements + dismissals
        if total == 0:
            return 0.0

        raw_score = (engagements * 2.0 + views * 0.5 - dismissals) / (total + 1)
        # Normalize to [0, 1]
        return max(0.0, min(1.0, raw_score / 2.0))

    async def get_stats(self, user_id: str, kblock_id: str) -> dict[str, int]:
        """Get raw attention stats."""
        key = (user_id, kblock_id)
        return dict(self._attention[key])


# =============================================================================
# Persistent Attention Tracker
# =============================================================================


class PersistentAttentionTracker:
    """
    Database-backed attention tracking.

    Persists all interactions to PostgreSQL for:
    - Cross-session tracking
    - Analytics
    - ML training data

    Uses FeedFeedbackPersistence for storage.
    """

    def __init__(self, persistence: "FeedFeedbackPersistence") -> None:
        """
        Initialize persistent tracker.

        Args:
            persistence: Feed feedback persistence layer
        """
        from services.feed.persistence import FeedFeedbackPersistence

        self._persistence: FeedFeedbackPersistence = persistence

    async def record_view(self, user_id: str, kblock_id: str) -> None:
        """Record a view (passive attention)."""
        await self._persistence.record_interaction(
            user_id=user_id,
            kblock_id=kblock_id,
            action=FeedbackAction.VIEW,
        )

    async def record_engagement(self, user_id: str, kblock_id: str) -> None:
        """Record an engagement (active interaction)."""
        await self._persistence.record_interaction(
            user_id=user_id,
            kblock_id=kblock_id,
            action=FeedbackAction.ENGAGE,
        )

    async def record_dismissal(self, user_id: str, kblock_id: str) -> None:
        """Record a dismissal (negative signal)."""
        await self._persistence.record_interaction(
            user_id=user_id,
            kblock_id=kblock_id,
            action=FeedbackAction.DISMISS,
        )

    async def get_attention_score(self, user_id: str, kblock_id: str) -> float:
        """Get attention score from database."""
        return await self._persistence.get_attention_score(user_id, kblock_id)

    async def get_stats(self, user_id: str, kblock_id: str) -> dict[str, int]:
        """Get raw attention stats from database."""
        return await self._persistence.get_interaction_stats(user_id, kblock_id)


# Alias for backward compatibility
AttentionTracker = InMemoryAttentionTracker


# =============================================================================
# Feedback System
# =============================================================================


class FeedbackSystem:
    """
    Orchestrates the feed-feedback loop.

    When users interact with K-Blocks in a feed:
    1. Record the interaction (FeedbackEvent)
    2. Update attention tracking
    3. Trigger callbacks (if configured)
    4. Learn preferences for future ranking

    This is the recursive power of feeds: users create feedback systems WITH feeds.

    Personal Feed Creation:
    The createPersonalFeed() method analyzes user interaction history to create
    a personalized Feed with adjusted ranking weights based on engagement patterns.
    """

    def __init__(self, attention_tracker: AttentionTracker | None = None) -> None:
        self.attention_tracker = attention_tracker or AttentionTracker()
        self._events: list[FeedbackEvent] = []
        # Track dismissed K-Blocks for filtering
        self._dismissed: dict[str, set[str]] = {}  # user_id -> set of kblock_ids

    async def on_view(self, user_id: str, kblock: KBlock) -> None:
        """User viewed a K-Block (passive attention)."""
        event = FeedbackEvent(
            user_id=user_id,
            kblock_id=kblock.id,
            action=FeedbackAction.VIEW,
        )
        self._events.append(event)
        await self.attention_tracker.record_view(user_id, kblock.id)

    async def on_engage(self, user_id: str, kblock: KBlock, action_type: str = "edit") -> None:
        """User engaged with a K-Block (active interaction)."""
        event = FeedbackEvent(
            user_id=user_id,
            kblock_id=kblock.id,
            action=FeedbackAction.ENGAGE,
            metadata={"action_type": action_type},
        )
        self._events.append(event)
        await self.attention_tracker.record_engagement(user_id, kblock.id)

    async def on_dismiss(self, user_id: str, kblock: KBlock) -> None:
        """User dismissed a K-Block (negative signal)."""
        event = FeedbackEvent(
            user_id=user_id,
            kblock_id=kblock.id,
            action=FeedbackAction.DISMISS,
        )
        self._events.append(event)
        await self.attention_tracker.record_dismissal(user_id, kblock.id)

        # Track dismissed K-Blocks for filtering
        if user_id not in self._dismissed:
            self._dismissed[user_id] = set()
        self._dismissed[user_id].add(kblock.id)

    async def on_contradict(self, user_id: str, kblock1: KBlock, kblock2: KBlock) -> None:
        """User marked a contradiction between two K-Blocks."""
        # Record both as engagements (special case)
        event1 = FeedbackEvent(
            user_id=user_id,
            kblock_id=kblock1.id,
            action=FeedbackAction.CONTRADICT,
            metadata={"contradicts": kblock2.id},
        )
        event2 = FeedbackEvent(
            user_id=user_id,
            kblock_id=kblock2.id,
            action=FeedbackAction.CONTRADICT,
            metadata={"contradicts": kblock1.id},
        )
        self._events.extend([event1, event2])

        await self.attention_tracker.record_engagement(user_id, kblock1.id)
        await self.attention_tracker.record_engagement(user_id, kblock2.id)

    async def get_events(
        self,
        user_id: str | None = None,
        kblock_id: str | None = None,
        action: FeedbackAction | None = None,
        limit: int = 100,
    ) -> list[FeedbackEvent]:
        """
        Get feedback events with optional filtering.

        Args:
            user_id: Filter by user
            kblock_id: Filter by K-Block
            action: Filter by action type
            limit: Maximum number of events to return

        Returns:
            List of feedback events (most recent first)
        """
        filtered = self._events

        if user_id:
            filtered = [e for e in filtered if e.user_id == user_id]

        if kblock_id:
            filtered = [e for e in filtered if e.kblock_id == kblock_id]

        if action:
            filtered = [e for e in filtered if e.action == action]

        # Sort by timestamp descending (most recent first)
        filtered.sort(key=lambda e: e.timestamp, reverse=True)

        return filtered[:limit]

    async def get_user_stats(self, user_id: str) -> dict[str, int]:
        """
        Get aggregate interaction stats for a user.

        Returns:
            Dictionary with total views, engagements, dismissals, contradictions
        """
        user_events = [e for e in self._events if e.user_id == user_id]

        return {
            "views": sum(1 for e in user_events if e.action == FeedbackAction.VIEW),
            "engagements": sum(1 for e in user_events if e.action == FeedbackAction.ENGAGE),
            "dismissals": sum(1 for e in user_events if e.action == FeedbackAction.DISMISS),
            "contradictions": sum(1 for e in user_events if e.action == FeedbackAction.CONTRADICT),
            "total": len(user_events),
        }

    async def get_dismissed_kblocks(self, user_id: str) -> set[str]:
        """
        Get the set of K-Block IDs that the user has dismissed.

        Used by createPersonalFeed to filter out dismissed items.
        """
        return self._dismissed.get(user_id, set())

    async def create_personal_feed(
        self,
        user_id: str,
        base_feed_id: str = "cosmos",
        name: str | None = None,
    ):
        """
        Create a personalized feed based on user interaction history.

        This implements the adaptive ranking algorithm:
        1. Start with base feed configuration
        2. Adjust weights based on user engagement patterns
        3. Add filter to exclude dismissed K-Blocks

        The algorithm learns from:
        - High engagement rate = increase attention_weight
        - Many contradictions = increase coherence_weight
        - Frequent dismissals = decrease recency_weight (less spam)

        Args:
            user_id: User identifier for personalization
            base_feed_id: Starting feed configuration (default: cosmos)
            name: Custom name for personal feed (default: "{base} for {user}")

        Returns:
            Personalized Feed instance with adjusted weights

        Philosophy:
            "The system adapts to user wants and needs.
             The system does NOT change behavior against user will."
            (Linear Adaptation principle)
        """
        from .config import get_feed_config
        from .core import Feed, FeedFilter, FeedRanking, FeedSource
        from .defaults import get_default_feed

        config = get_feed_config()

        # Get base feed or default to cosmos
        base_feed = get_default_feed(base_feed_id)
        if base_feed is None:
            cosmos = get_default_feed("cosmos")
            assert cosmos is not None, "COSMOS_FEED should always exist"
            base_feed = cosmos

        # Get user stats
        stats = await self.get_user_stats(user_id)
        total = stats["total"]

        # If insufficient interactions, return base feed with default weights
        if total < config.min_interactions_for_personalization:
            return Feed(
                id=f"personal_{user_id}_{base_feed_id}",
                name=name or f"{base_feed.name} (Personal)",
                description=f"Personalized feed for {user_id} (collecting data: {total}/{config.min_interactions_for_personalization} interactions)",
                sources=base_feed.sources,
                filters=base_feed.filters,
                ranking=FeedRanking(
                    attention_weight=config.attention_weight,
                    principles_weight=config.principles_weight,
                    recency_weight=config.recency_weight,
                    coherence_weight=config.coherence_weight,
                ),
            )

        # Calculate engagement rate (engagements / views)
        engagement_rate = stats["engagements"] / max(stats["views"], 1)

        # Calculate dismissal rate (dismissals / total interactions)
        dismissal_rate = stats["dismissals"] / max(total, 1)

        # Calculate contradiction rate
        contradiction_rate = stats["contradictions"] / max(total, 1)

        # Adjust weights based on patterns
        # Start with config defaults
        attention_w = config.attention_weight
        principles_w = config.principles_weight
        recency_w = config.recency_weight
        coherence_w = config.coherence_weight

        # High engagement = user responds to attention-based ranking
        if engagement_rate > 0.3:
            attention_w *= 1.2
            principles_w *= 0.9

        # Many contradictions = user values coherence
        if contradiction_rate > 0.1:
            coherence_w *= 1.3
            recency_w *= 0.8

        # High dismissal rate = reduce spam (less recency bias)
        if dismissal_rate > 0.2:
            recency_w *= 0.7
            coherence_w *= 1.1

        # Normalize weights to sum to 1.0
        total_weight = attention_w + principles_w + recency_w + coherence_w
        attention_w /= total_weight
        principles_w /= total_weight
        recency_w /= total_weight
        coherence_w /= total_weight

        # Build filters including dismissed K-Blocks
        dismissed = await self.get_dismissed_kblocks(user_id)
        filters = list(base_feed.filters)

        if dismissed:
            # Add custom filter to exclude dismissed K-Blocks
            filters.append(
                FeedFilter(
                    field="custom",
                    operator="eq",
                    value=lambda kb, d=dismissed: kb.id not in d,
                )
            )

        return Feed(
            id=f"personal_{user_id}_{base_feed_id}",
            name=name or f"{base_feed.name} (Personal)",
            description=f"Personalized feed for {user_id} based on {total} interactions",
            sources=base_feed.sources,
            filters=tuple(filters),
            ranking=FeedRanking(
                attention_weight=attention_w,
                principles_weight=principles_w,
                recency_weight=recency_w,
                coherence_weight=coherence_w,
            ),
        )


__all__ = [
    "FeedbackAction",
    "FeedbackEvent",
    "AttentionTrackerProtocol",
    "InMemoryAttentionTracker",
    "PersistentAttentionTracker",
    "AttentionTracker",  # Alias for backward compatibility
    "FeedbackSystem",
]
