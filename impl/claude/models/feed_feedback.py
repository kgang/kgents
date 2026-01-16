"""
Feed Feedback Models: PostgreSQL persistence for user interactions with K-Blocks.

This module defines SQLAlchemy models for tracking user engagement with feed items,
enabling the ranking algorithm to improve over time through learning.

The models support:
- User interactions (view, engage, dismiss, dwell time)
- Temporal tracking (when interactions occurred)
- Engagement analytics (aggregate statistics)

AGENTESE: self.data.table.feed_feedback.*
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class FeedInteraction(TimestampMixin, Base):
    """
    Single user interaction with a K-Block in the feed.

    Tracks atomic interactions like views, clicks, edits, dismissals.
    Used by AttentionTracker to compute personalized attention scores.

    Storage pattern:
    - High write volume (one row per interaction)
    - Time-series data (indexed by timestamp for analytics)
    - User-scoped queries (indexed by user_id + kblock_id)
    """

    __tablename__ = "feed_interactions"

    # Identity
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Who
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # What
    kblock_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # How (interaction type)
    action: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # "view", "engage", "dismiss", "contradict"

    # When (timestamp from TimestampMixin provides created_at)

    # Duration (for view events)
    dwell_time_ms: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # Milliseconds spent viewing

    # Context
    interaction_type: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )  # "edit", "comment", "link", "copy" for engage actions
    interaction_metadata: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )  # JSON metadata (e.g., {"contradicts": "kblock_id"})

    # Indexes for common queries
    __table_args__ = (
        # User's interactions with a specific K-Block
        Index("idx_user_kblock", "user_id", "kblock_id"),
        # Recent interactions for a user (feed personalization)
        Index("idx_user_timestamp", "user_id", "created_at"),
        # K-Block engagement metrics
        Index("idx_kblock_action", "kblock_id", "action"),
        # Temporal analytics
        Index("idx_timestamp", "created_at"),
    )


class FeedEngagementStats(TimestampMixin, Base):
    """
    Aggregate engagement statistics for a K-Block.

    Pre-computed stats to avoid expensive aggregation queries.
    Updated incrementally as interactions occur.

    Storage pattern:
    - One row per K-Block
    - Updated on each interaction (using ON CONFLICT)
    - Fast reads for ranking algorithm
    """

    __tablename__ = "feed_engagement_stats"

    # Identity (K-Block ID)
    kblock_id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # Engagement counts
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    engage_count: Mapped[int] = mapped_column(Integer, default=0)
    dismiss_count: Mapped[int] = mapped_column(Integer, default=0)

    # Engagement scores (derived)
    attention_score: Mapped[float] = mapped_column(
        Float, default=0.0
    )  # (engagements * 2 + views * 0.5 - dismissals) / total

    # Temporal signals
    last_viewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_engaged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Average dwell time (in seconds)
    avg_dwell_time_sec: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Unique users who interacted
    unique_viewers: Mapped[int] = mapped_column(Integer, default=0)
    unique_engagers: Mapped[int] = mapped_column(Integer, default=0)

    # Indexes
    __table_args__ = (
        # Find most engaged K-Blocks
        Index("idx_attention_score", "attention_score"),
        # Find recently engaged K-Blocks
        Index("idx_last_engaged", "last_engaged_at"),
    )
