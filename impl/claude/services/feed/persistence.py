"""
Feed Feedback Persistence: Database layer for user interaction tracking.

Provides async CRUD operations for feed interactions and engagement stats.

Philosophy:
    "The system adapts to the user, not the user to the system."
    (Linear Adaptation principle)

Storage pattern:
- Append-only interaction log (feed_interactions table)
- Pre-computed aggregate stats (feed_engagement_stats table)
- Incremental updates using INSERT ... ON CONFLICT

See: services/feed/feedback.py (in-memory MVP)
See: models/feed_feedback.py (database schema)
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from models.feed_feedback import FeedEngagementStats, FeedInteraction
from services.feed.feedback import FeedbackAction

logger = logging.getLogger(__name__)


class FeedFeedbackPersistence:
    """
    Persistent storage for feed feedback interactions.

    Provides:
    - Recording user interactions (view, engage, dismiss)
    - Retrieving interaction history
    - Computing aggregate engagement stats
    - Analytics queries
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        """
        Initialize feed feedback persistence.

        Args:
            session_factory: SQLAlchemy async session factory
        """
        self._session_factory = session_factory

    async def record_interaction(
        self,
        user_id: str,
        kblock_id: str,
        action: FeedbackAction,
        dwell_time_ms: int | None = None,
        interaction_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Record a user interaction with a K-Block.

        Args:
            user_id: User identifier
            kblock_id: K-Block identifier
            action: Type of interaction (view, engage, dismiss, contradict)
            dwell_time_ms: Time spent viewing (for view actions)
            interaction_type: Specific type (e.g., "edit", "comment" for engage)
            metadata: Additional context (JSON-serializable)

        Returns:
            Interaction ID
        """
        interaction_id = str(uuid4())

        async with self._session_factory() as session:
            # Create interaction record
            interaction = FeedInteraction(
                id=interaction_id,
                user_id=user_id,
                kblock_id=kblock_id,
                action=action.value,
                dwell_time_ms=dwell_time_ms,
                interaction_type=interaction_type,
                interaction_metadata=json.dumps(metadata) if metadata else None,
            )

            session.add(interaction)

            # Update aggregate stats (upsert pattern)
            await self._update_engagement_stats(
                session=session,
                kblock_id=kblock_id,
                action=action,
                timestamp=datetime.now(),
                dwell_time_ms=dwell_time_ms,
            )

            await session.commit()

            logger.debug(
                f"Recorded {action.value} interaction: user={user_id}, kblock={kblock_id}"
            )

            return interaction_id

    async def _update_engagement_stats(
        self,
        session: AsyncSession,
        kblock_id: str,
        action: FeedbackAction,
        timestamp: datetime,
        dwell_time_ms: int | None = None,
    ) -> None:
        """
        Update aggregate engagement stats for a K-Block.

        Uses INSERT ... ON CONFLICT for efficient upserts.

        Args:
            session: Database session
            kblock_id: K-Block identifier
            action: Type of interaction
            timestamp: When interaction occurred
            dwell_time_ms: Dwell time for view actions
        """
        # Determine which counter to increment
        increment_fields: dict[str, Any] = {}

        if action == FeedbackAction.VIEW:
            increment_fields["view_count"] = FeedEngagementStats.view_count + 1
            increment_fields["last_viewed_at"] = timestamp
        elif action == FeedbackAction.ENGAGE:
            increment_fields["engage_count"] = FeedEngagementStats.engage_count + 1
            increment_fields["last_engaged_at"] = timestamp
        elif action == FeedbackAction.DISMISS:
            increment_fields["dismiss_count"] = FeedEngagementStats.dismiss_count + 1

        # Try to update existing record
        stmt = (
            update(FeedEngagementStats)
            .where(FeedEngagementStats.kblock_id == kblock_id)
            .values(**increment_fields)
            .returning(FeedEngagementStats.kblock_id)
        )

        result = await session.execute(stmt)
        updated = result.scalar_one_or_none()

        # If no existing record, create one
        if updated is None:
            initial_values = {
                "kblock_id": kblock_id,
                "view_count": 1 if action == FeedbackAction.VIEW else 0,
                "engage_count": 1 if action == FeedbackAction.ENGAGE else 0,
                "dismiss_count": 1 if action == FeedbackAction.DISMISS else 0,
                "attention_score": 0.0,
                "unique_viewers": 0,
                "unique_engagers": 0,
            }

            if action == FeedbackAction.VIEW:
                initial_values["last_viewed_at"] = timestamp
            elif action == FeedbackAction.ENGAGE:
                initial_values["last_engaged_at"] = timestamp

            stats = FeedEngagementStats(**initial_values)
            session.add(stats)

        # Recompute attention score
        await self._recompute_attention_score(session, kblock_id)

    async def _recompute_attention_score(
        self, session: AsyncSession, kblock_id: str
    ) -> None:
        """
        Recompute attention score for a K-Block.

        Formula: (engagements * 2 + views * 0.5 - dismissals) / (total + 1)
        Normalized to [0, 1] range.

        Args:
            session: Database session
            kblock_id: K-Block identifier
        """
        # Fetch current stats
        stmt = select(FeedEngagementStats).where(
            FeedEngagementStats.kblock_id == kblock_id
        )
        result = await session.execute(stmt)
        stats = result.scalar_one_or_none()

        if stats is None:
            return

        # Compute score
        views = stats.view_count
        engagements = stats.engage_count
        dismissals = stats.dismiss_count

        total = views + engagements + dismissals
        if total == 0:
            score = 0.0
        else:
            raw_score = (engagements * 2.0 + views * 0.5 - dismissals) / (total + 1)
            score = max(0.0, min(1.0, raw_score / 2.0))

        # Update score
        update_stmt = (
            update(FeedEngagementStats)
            .where(FeedEngagementStats.kblock_id == kblock_id)
            .values(attention_score=score)
        )
        await session.execute(update_stmt)

    async def get_attention_score(self, user_id: str, kblock_id: str) -> float:
        """
        Get attention score for a K-Block (user-specific in future, global for now).

        Args:
            user_id: User identifier
            kblock_id: K-Block identifier

        Returns:
            Attention score (0.0 to 1.0)
        """
        async with self._session_factory() as session:
            stmt = select(FeedEngagementStats.attention_score).where(
                FeedEngagementStats.kblock_id == kblock_id
            )
            result = await session.execute(stmt)
            score = result.scalar_one_or_none()

            return score or 0.0

    async def get_interaction_stats(
        self, user_id: str, kblock_id: str
    ) -> dict[str, int]:
        """
        Get raw interaction counts for a K-Block.

        Args:
            user_id: User identifier (for future per-user stats)
            kblock_id: K-Block identifier

        Returns:
            Dictionary with views, engagements, dismissals counts
        """
        async with self._session_factory() as session:
            stmt = select(FeedEngagementStats).where(
                FeedEngagementStats.kblock_id == kblock_id
            )
            result = await session.execute(stmt)
            stats = result.scalar_one_or_none()

            if stats is None:
                return {"views": 0, "engagements": 0, "dismissals": 0}

            return {
                "views": stats.view_count,
                "engagements": stats.engage_count,
                "dismissals": stats.dismiss_count,
            }

    async def get_analytics(
        self,
        limit: int = 20,
        min_interactions: int = 1,
    ) -> dict[str, Any]:
        """
        Get feed engagement analytics.

        Returns:
            Analytics data including:
            - Most engaged K-Blocks
            - Average dwell time
            - Total interaction counts
            - Temporal trends
        """
        async with self._session_factory() as session:
            # Most engaged K-Blocks
            top_kblocks_stmt = (
                select(FeedEngagementStats)
                .where(
                    (
                        FeedEngagementStats.view_count
                        + FeedEngagementStats.engage_count
                        + FeedEngagementStats.dismiss_count
                    )
                    >= min_interactions
                )
                .order_by(FeedEngagementStats.attention_score.desc())
                .limit(limit)
            )
            top_result = await session.execute(top_kblocks_stmt)
            top_kblocks = top_result.scalars().all()

            # Global stats
            totals_stmt = select(
                func.sum(FeedEngagementStats.view_count).label("total_views"),
                func.sum(FeedEngagementStats.engage_count).label("total_engages"),
                func.sum(FeedEngagementStats.dismiss_count).label("total_dismissals"),
                func.avg(FeedEngagementStats.avg_dwell_time_sec).label(
                    "avg_dwell_time"
                ),
            )
            totals_result = await session.execute(totals_stmt)
            totals = totals_result.one()

            # Recent activity (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            recent_stmt = select(func.count(FeedInteraction.id)).where(
                FeedInteraction.created_at >= yesterday
            )
            recent_result = await session.execute(recent_stmt)
            recent_count = recent_result.scalar() or 0

            return {
                "most_engaged_kblocks": [
                    {
                        "kblock_id": kb.kblock_id,
                        "attention_score": kb.attention_score,
                        "view_count": kb.view_count,
                        "engage_count": kb.engage_count,
                        "dismiss_count": kb.dismiss_count,
                        "last_engaged_at": (
                            kb.last_engaged_at.isoformat()
                            if kb.last_engaged_at
                            else None
                        ),
                    }
                    for kb in top_kblocks
                ],
                "totals": {
                    "views": int(totals.total_views or 0),
                    "engagements": int(totals.total_engages or 0),
                    "dismissals": int(totals.total_dismissals or 0),
                    "avg_dwell_time_sec": float(totals.avg_dwell_time or 0.0),
                },
                "recent_activity": {
                    "interactions_24h": recent_count,
                },
            }


__all__ = ["FeedFeedbackPersistence"]
