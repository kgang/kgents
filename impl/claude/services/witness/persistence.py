"""
Witness Persistence: Dual-Track Storage for the 8th Crown Jewel.

Owns domain semantics for Witness storage:
- WHEN to persist (on thought, on action, on escalation)
- WHY to persist (dual-track: fast queries + semantic search)
- HOW to compose (TableAdapter for metadata, D-gent for semantic content)

AGENTESE aspects exposed:
- save_thought: Store thought with semantic embedding
- get_thoughts: Retrieve recent thoughts
- get_trust_level: Get trust with decay applied
- record_escalation: Log trust level change
- record_action: Store action with rollback info
- get_rollback_window: Get reversible actions

Differance Integration:
- save_thought() -> trace with alternatives (defer_embedding, skip_tags)
- record_action() -> trace with alternatives (skip_checkpoint, dry_run)

The Pattern (from crown-jewel-patterns.md):
- Pattern 1: Container Owns Workflow (WitnessTrust owns thoughts, actions)
- Pattern 6: Async-Safe Event Emission (fire-and-forget traces)
- Pattern 15: No Hollow Services (always go through DI)

See: docs/skills/metaphysical-fullstack.md
See: services/brain/persistence.py (reference implementation)
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agents.d import Datum, DgentProtocol, TableAdapter
from agents.differance.alternatives import get_alternatives
from agents.differance.integration import DifferanceIntegration
from models.witness import (
    WitnessAction,
    WitnessEscalation,
    WitnessThought,
    WitnessTrust,
    hash_email,
)

from .polynomial import ActionResult, Thought, TrustLevel

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


# =============================================================================
# Result Dataclasses
# =============================================================================


@dataclass
class ThoughtResult:
    """Result of a thought save operation."""

    thought_id: str
    content: str
    source: str
    tags: list[str]
    timestamp: datetime
    datum_id: str | None = None


@dataclass
class TrustResult:
    """Result of a trust query with decay applied."""

    trust_level: TrustLevel
    raw_level: float
    last_active: datetime
    observation_count: int
    successful_operations: int
    confirmed_suggestions: int
    total_suggestions: int
    acceptance_rate: float
    decay_applied: bool = False


@dataclass
class EscalationResult:
    """Result of an escalation record."""

    escalation_id: int
    from_level: TrustLevel
    to_level: TrustLevel
    reason: str
    timestamp: datetime


@dataclass
class ActionResultPersisted:
    """Result of an action save operation."""

    action_id: str
    action: str
    success: bool
    message: str
    reversible: bool
    git_stash_ref: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WitnessStatus:
    """Witness health status."""

    total_thoughts: int
    total_actions: int
    trust_count: int
    reversible_actions: int
    storage_backend: str


# =============================================================================
# WitnessPersistence Class
# =============================================================================


class WitnessPersistence:
    """
    Persistence layer for Witness Crown Jewel.

    Composes:
    - TableAdapter[WitnessThought]: Fast recency queries
    - TableAdapter[WitnessAction]: Action history with rollback
    - D-gent: Semantic search for thoughts

    Domain Semantics:
    - Thoughts are the atomic units of observation
    - Each thought has queryable metadata AND semantic content
    - Trust decays on load (not on save)
    - Actions are logged with reversibility info

    Example:
        persistence = WitnessPersistence(
            session_factory=session_factory,
            dgent=dgent_router,
        )

        result = await persistence.save_thought(thought)
        thoughts = await persistence.get_thoughts(limit=50)
        trust = await persistence.get_trust_level("user@example.com")
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        dgent: DgentProtocol,
    ) -> None:
        self.session_factory = session_factory
        self.dgent = dgent
        # Differance integration for trace recording
        self._differance = DifferanceIntegration("witness")

    # =========================================================================
    # Thought Operations
    # =========================================================================

    async def save_thought(
        self,
        thought: Thought,
        trust_id: str | None = None,
        repository_path: str | None = None,
    ) -> ThoughtResult:
        """
        Save a thought to dual-track storage.

        AGENTESE: self.witness.thoughts.capture

        Dual-track storage:
        1. Store semantic content in D-gent (for associative search)
        2. Store queryable metadata in SQL (for fast recency queries)

        Args:
            thought: The Thought object from polynomial.py
            trust_id: Optional trust ID for user context
            repository_path: Optional repository context

        Returns:
            ThoughtResult with thought_id and storage details
        """
        thought_id = f"thought-{uuid.uuid4().hex[:12]}"

        # 1. Store semantic content in D-gent
        datum_metadata = {
            "type": "witness_thought",
            "source": thought.source,
            "tags": ",".join(thought.tags),
        }

        datum = Datum(
            id=f"witness-{thought_id}",
            content=thought.content.encode("utf-8"),
            created_at=time.time(),
            causal_parent=None,
            metadata=datum_metadata,
        )

        datum_id = await self.dgent.put(datum)

        # 2. Store queryable metadata in SQL
        async with self.session_factory() as session:
            thought_row = WitnessThought(
                id=thought_id,
                trust_id=trust_id,
                content=thought.content,
                source=thought.source,
                tags=list(thought.tags),
                datum_id=datum_id,
                repository_path=repository_path,
            )
            session.add(thought_row)
            await session.commit()

        result = ThoughtResult(
            thought_id=thought_id,
            content=thought.content,
            source=thought.source,
            tags=list(thought.tags),
            timestamp=thought.timestamp,
            datum_id=datum_id,
        )

        # Fire-and-forget trace recording
        self._record_trace(
            "save_thought",
            (thought.content[:100],),
            thought_id,
            f"Saved thought from {thought.source}",
        )

        return result

    async def get_thoughts(
        self,
        limit: int = 50,
        trust_id: str | None = None,
        source: str | None = None,
        since: datetime | None = None,
    ) -> list[Thought]:
        """
        Get recent thoughts with optional filters.

        AGENTESE: self.witness.thoughts

        Args:
            limit: Maximum thoughts to return (default 50)
            trust_id: Filter by trust ID (user)
            source: Filter by source (git, tests, etc.)
            since: Filter by created_at > since

        Returns:
            List of Thought objects, newest first
        """
        async with self.session_factory() as session:
            stmt = select(WitnessThought).order_by(WitnessThought.created_at.desc())

            if trust_id:
                stmt = stmt.where(WitnessThought.trust_id == trust_id)
            if source:
                stmt = stmt.where(WitnessThought.source == source)
            if since:
                stmt = stmt.where(WitnessThought.created_at > since)

            stmt = stmt.limit(limit)

            result = await session.execute(stmt)
            rows = result.scalars().all()

            return [
                Thought(
                    content=row.content,
                    source=row.source,
                    tags=tuple(row.tags) if row.tags else (),
                    timestamp=row.created_at,
                )
                for row in rows
            ]

    # =========================================================================
    # Trust Operations
    # =========================================================================

    async def get_trust_level(
        self,
        git_email: str,
        repository_path: str | None = None,
        apply_decay: bool = True,
    ) -> TrustResult:
        """
        Get trust level for a user, with decay applied.

        AGENTESE: self.witness.trust

        Trust decays by 0.1 levels per 24h of inactivity.
        Minimum floor: L1 (never drops below L1 after first achievement).

        Args:
            git_email: Git user email
            repository_path: Optional repository context
            apply_decay: Whether to apply decay (default True)

        Returns:
            TrustResult with current trust level and metrics
        """
        email_hash = hash_email(git_email)
        trust_id = f"trust-{email_hash}"

        async with self.session_factory() as session:
            trust = await session.get(WitnessTrust, trust_id)

            if trust is None:
                # Create new trust record at L0
                trust = WitnessTrust(
                    id=trust_id,
                    git_email_hash=email_hash,
                    repository_path=repository_path,
                    trust_level=0,
                    trust_level_raw=0.0,
                )
                session.add(trust)
                await session.commit()
                await session.refresh(trust)

            decay_applied = False
            if apply_decay:
                old_level = trust.trust_level
                trust.apply_decay()
                decay_applied = trust.trust_level != old_level
                if decay_applied:
                    await session.commit()

            # Calculate acceptance rate
            acceptance_rate = (
                trust.confirmed_suggestions / trust.total_suggestions
                if trust.total_suggestions > 0
                else 0.0
            )

            return TrustResult(
                trust_level=TrustLevel(trust.trust_level),
                raw_level=trust.trust_level_raw,
                last_active=trust.last_active,
                observation_count=trust.observation_count,
                successful_operations=trust.successful_operations,
                confirmed_suggestions=trust.confirmed_suggestions,
                total_suggestions=trust.total_suggestions,
                acceptance_rate=acceptance_rate,
                decay_applied=decay_applied,
            )

    async def update_trust_metrics(
        self,
        git_email: str,
        observation_count: int | None = None,
        successful_operations: int | None = None,
        confirmed_suggestion: bool | None = None,
    ) -> TrustResult:
        """
        Update trust metrics for a user.

        Called after polynomial state changes to persist metrics.

        Args:
            git_email: Git user email
            observation_count: New observation count (if changed)
            successful_operations: New successful operations count
            confirmed_suggestion: Whether a suggestion was confirmed

        Returns:
            Updated TrustResult
        """
        email_hash = hash_email(git_email)
        trust_id = f"trust-{email_hash}"

        async with self.session_factory() as session:
            trust = await session.get(WitnessTrust, trust_id)
            if trust is None:
                # Create if not exists
                trust = WitnessTrust(
                    id=trust_id,
                    git_email_hash=email_hash,
                    trust_level=0,
                    trust_level_raw=0.0,
                )
                session.add(trust)

            # Update metrics
            if observation_count is not None:
                trust.observation_count = observation_count
            if successful_operations is not None:
                trust.successful_operations = successful_operations
            if confirmed_suggestion is not None:
                trust.total_suggestions += 1
                if confirmed_suggestion:
                    trust.confirmed_suggestions += 1

            trust.touch()  # Update last_active
            await session.commit()

            acceptance_rate = (
                trust.confirmed_suggestions / trust.total_suggestions
                if trust.total_suggestions > 0
                else 0.0
            )

            return TrustResult(
                trust_level=TrustLevel(trust.trust_level),
                raw_level=trust.trust_level_raw,
                last_active=trust.last_active,
                observation_count=trust.observation_count,
                successful_operations=trust.successful_operations,
                confirmed_suggestions=trust.confirmed_suggestions,
                total_suggestions=trust.total_suggestions,
                acceptance_rate=acceptance_rate,
                decay_applied=False,
            )

    async def record_escalation(
        self,
        git_email: str,
        from_level: TrustLevel,
        to_level: TrustLevel,
        reason: str,
    ) -> EscalationResult:
        """
        Record a trust escalation event.

        AGENTESE: self.witness.trust.escalate

        Args:
            git_email: Git user email
            from_level: Previous trust level
            to_level: New trust level
            reason: Reason for escalation

        Returns:
            EscalationResult with escalation details
        """
        email_hash = hash_email(git_email)
        trust_id = f"trust-{email_hash}"

        async with self.session_factory() as session:
            # Get or create trust record
            trust = await session.get(WitnessTrust, trust_id)
            if trust is None:
                trust = WitnessTrust(
                    id=trust_id,
                    git_email_hash=email_hash,
                    trust_level=to_level.value,
                    trust_level_raw=float(to_level.value),
                )
                session.add(trust)
            else:
                # Update trust level
                trust.trust_level = to_level.value
                trust.trust_level_raw = float(to_level.value)

            # Record escalation
            escalation = WitnessEscalation(
                trust_id=trust_id,
                from_level=from_level.value,
                to_level=to_level.value,
                reason=reason,
                observation_count=trust.observation_count or 0,
                successful_operations=trust.successful_operations or 0,
                confirmed_suggestions=trust.confirmed_suggestions or 0,
                total_suggestions=trust.total_suggestions or 0,
                acceptance_rate=(
                    (trust.confirmed_suggestions or 0) / trust.total_suggestions
                    if trust.total_suggestions and trust.total_suggestions > 0
                    else 0.0
                ),
            )
            session.add(escalation)
            await session.commit()
            await session.refresh(escalation)

            return EscalationResult(
                escalation_id=escalation.id,
                from_level=from_level,
                to_level=to_level,
                reason=reason,
                timestamp=escalation.created_at,
            )

    # =========================================================================
    # Action Operations
    # =========================================================================

    async def record_action(
        self,
        action: ActionResult,
        trust_id: str | None = None,
        repository_path: str | None = None,
        git_stash_ref: str | None = None,
        checkpoint_path: str | None = None,
    ) -> ActionResultPersisted:
        """
        Record an action with rollback info.

        AGENTESE: self.witness.actions.record

        All actions are logged for accountability.
        Reversible actions include rollback info.

        Args:
            action: The ActionResult from polynomial.py
            trust_id: Optional trust ID for user context
            repository_path: Optional repository context
            git_stash_ref: Git stash ref for rollback
            checkpoint_path: File backup path for rollback

        Returns:
            ActionResultPersisted with action details
        """
        async with self.session_factory() as session:
            action_row = WitnessAction(
                id=action.action_id,
                trust_id=trust_id,
                action=action.action,
                target=None,  # Could be extracted from action string
                success=action.success,
                message=action.message,
                reversible=action.reversible,
                inverse_action=action.inverse_action,
                git_stash_ref=git_stash_ref,
                checkpoint_path=checkpoint_path,
                repository_path=repository_path,
            )
            session.add(action_row)
            await session.commit()

        result = ActionResultPersisted(
            action_id=action.action_id,
            action=action.action,
            success=action.success,
            message=action.message,
            reversible=action.reversible,
            git_stash_ref=git_stash_ref,
            timestamp=action.timestamp,
        )

        # Fire-and-forget trace recording
        self._record_trace(
            "record_action",
            (action.action[:100],),
            action.action_id,
            f"Action {'succeeded' if action.success else 'failed'}",
        )

        return result

    async def get_rollback_window(
        self,
        hours: int = 168,  # 7 days
        limit: int = 100,
        reversible_only: bool = True,
    ) -> list[ActionResult]:
        """
        Get actions within the rollback window.

        AGENTESE: self.witness.actions.rollback_window

        Args:
            hours: Window size in hours (default 168 = 7 days)
            limit: Maximum actions to return (default 100)
            reversible_only: Only return reversible actions (default True)

        Returns:
            List of ActionResult objects, newest first
        """
        since = datetime.now(UTC) - timedelta(hours=hours)

        async with self.session_factory() as session:
            stmt = (
                select(WitnessAction)
                .where(WitnessAction.created_at > since)
                .order_by(WitnessAction.created_at.desc())
            )

            if reversible_only:
                stmt = stmt.where(WitnessAction.reversible == True)  # noqa: E712

            stmt = stmt.limit(limit)

            result = await session.execute(stmt)
            rows = result.scalars().all()

            return [
                ActionResult(
                    action_id=row.id,
                    action=row.action,
                    success=row.success,
                    message=row.message,
                    reversible=row.reversible,
                    inverse_action=row.inverse_action,
                    timestamp=row.created_at,
                )
                for row in rows
            ]

    # =========================================================================
    # Status Operations
    # =========================================================================

    async def manifest(self) -> WitnessStatus:
        """
        Get witness health status.

        AGENTESE: self.witness.manifest

        Returns:
            WitnessStatus with counts and health metrics
        """
        async with self.session_factory() as session:
            # Count thoughts
            thought_count = await session.execute(select(func.count()).select_from(WitnessThought))
            total_thoughts = thought_count.scalar() or 0

            # Count actions
            action_count = await session.execute(select(func.count()).select_from(WitnessAction))
            total_actions = action_count.scalar() or 0

            # Count reversible actions
            reversible_count = await session.execute(
                select(func.count())
                .select_from(WitnessAction)
                .where(WitnessAction.reversible == True)  # noqa: E712
            )
            reversible_actions = reversible_count.scalar() or 0

            # Count trust records
            trust_count = await session.execute(select(func.count()).select_from(WitnessTrust))
            total_trust = trust_count.scalar() or 0

        return WitnessStatus(
            total_thoughts=total_thoughts,
            total_actions=total_actions,
            trust_count=total_trust,
            reversible_actions=reversible_actions,
            storage_backend=(
                "postgres" if "postgres" in str(self.session_factory).lower() else "sqlite"
            ),
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _record_trace(
        self,
        operation: str,
        inputs: tuple[str, ...],
        output: str,
        context: str,
    ) -> None:
        """
        Fire-and-forget trace recording via Differance integration.

        Non-blocking: don't await, don't slow down operations.
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(
                self._differance.record(
                    operation=operation,
                    inputs=inputs,
                    output=output,
                    context=context,
                    alternatives=get_alternatives("witness", operation),
                )
            )
        except RuntimeError:
            # No event loop - skip trace (graceful degradation)
            logger.debug(f"No event loop for {operation} trace recording")


__all__ = [
    "WitnessPersistence",
    "ThoughtResult",
    "TrustResult",
    "EscalationResult",
    "ActionResultPersisted",
    "WitnessStatus",
]
