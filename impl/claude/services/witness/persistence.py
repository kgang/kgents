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
from typing import TYPE_CHECKING, Any, AsyncGenerator

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
class MarkResult:
    """Result of a mark save operation."""

    mark_id: str
    action: str
    reasoning: str | None
    principles: list[str]
    tags: list[str]
    author: str
    timestamp: datetime
    datum_id: str | None = None
    parent_mark_id: str | None = None


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

    async def thought_stream(
        self,
        limit: int = 50,
        sources: list[str] | None = None,
        poll_interval: float = 2.0,
    ) -> AsyncGenerator[Thought, None]:
        """
        Stream thoughts in real-time via async generator.

        AGENTESE: self.witness.thoughts.stream (SSE)

        Yields thoughts as they are captured, with polling for new thoughts.
        Initial batch yields most recent thoughts, then polls for new ones.

        Args:
            limit: Maximum thoughts in initial batch (default 50)
            sources: Optional filter by sources (e.g., ['gardener', 'git'])
            poll_interval: Seconds between polls (default 2.0)

        Yields:
            Thought objects as they become available
        """
        last_seen_time: datetime | None = None

        # Initial batch: yield recent thoughts
        initial_thoughts = await self.get_thoughts(limit=limit, source=None)

        # Filter by sources if specified
        if sources:
            initial_thoughts = [t for t in initial_thoughts if t.source in sources]

        # Yield initial batch (oldest first for chronological streaming)
        for thought in reversed(initial_thoughts):
            yield thought
            if thought.timestamp and (last_seen_time is None or thought.timestamp > last_seen_time):
                last_seen_time = thought.timestamp

        # Poll for new thoughts
        while True:
            await asyncio.sleep(poll_interval)

            try:
                new_thoughts = await self.get_thoughts(
                    limit=20,
                    source=None,
                    since=last_seen_time,
                )

                # Filter by sources if specified
                if sources:
                    new_thoughts = [t for t in new_thoughts if t.source in sources]

                # Yield new thoughts (oldest first)
                for thought in reversed(new_thoughts):
                    yield thought
                    if thought.timestamp and (
                        last_seen_time is None or thought.timestamp > last_seen_time
                    ):
                        last_seen_time = thought.timestamp

            except asyncio.CancelledError:
                logger.debug("Thought stream cancelled")
                break
            except Exception as e:
                logger.error(f"Error polling thoughts: {e}")
                # Yield error as special thought
                yield Thought(
                    content=f"[Stream error: {e}]",
                    source="system",
                    tags=("error",),
                    timestamp=datetime.now(UTC),
                )

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
    # Mark Operations (Witness-Fusion UX)
    # =========================================================================

    async def save_mark(
        self,
        action: str,
        reasoning: str | None = None,
        principles: list[str] | None = None,
        tags: list[str] | None = None,
        author: str = "kent",
        session_id: str | None = None,
        repository_path: str | None = None,
        parent_mark_id: str | None = None,
    ) -> "MarkResult":
        """
        Save a mark to dual-track storage.

        AGENTESE: world.witness.mark / time.witness.mark

        Dual-track storage:
        1. Store semantic content in D-gent (for associative search)
        2. Store queryable metadata in SQL (for fast recency queries)

        Args:
            action: What was done
            reasoning: Why (optional but encouraged)
            principles: Which principles honored
            tags: Categorization tags (evidence tags, session tags, etc.)
            author: Who made the mark
            session_id: Optional session context
            repository_path: Optional repository context
            parent_mark_id: Optional parent mark for causal lineage

        Evidence Tags:
            - spec:{path}     — Links mark to a spec
            - evidence:impl   — Implementation evidence declaration
            - evidence:test   — Test evidence declaration
            - evidence:usage  — Usage evidence declaration
            - evidence:run    — Records a test run
            - evidence:pass   — Test passed
            - evidence:fail   — Test failed

        Returns:
            MarkResult with mark_id and storage details
        """
        from models.witness import WitnessMark

        mark_id = f"mark-{uuid.uuid4().hex[:12]}"

        # Validate parent exists if specified
        if parent_mark_id:
            async with self.session_factory() as session:
                parent = await session.get(WitnessMark, parent_mark_id)
                if not parent:
                    raise ValueError(f"Parent mark not found: {parent_mark_id}")

        # 1. Store semantic content in D-gent
        datum_metadata = {
            "type": "witness_mark",
            "author": author,
            "principles": ",".join(principles or []),
            "tags": ",".join(tags or []),
        }

        content_parts = [action]
        if reasoning:
            content_parts.append(f"Reasoning: {reasoning}")
        if principles:
            content_parts.append(f"Principles: {', '.join(principles)}")
        if tags:
            content_parts.append(f"Tags: {', '.join(tags)}")

        datum = Datum(
            id=f"witness-{mark_id}",
            content="\n".join(content_parts).encode("utf-8"),
            created_at=time.time(),
            causal_parent=None,
            metadata=datum_metadata,
        )

        datum_id = await self.dgent.put(datum)

        # 2. Store queryable metadata in SQL
        async with self.session_factory() as session:
            mark_row = WitnessMark(
                id=mark_id,
                action=action,
                reasoning=reasoning,
                principles=list(principles or []),
                tags=list(tags or []),
                author=author,
                session_id=session_id,
                parent_mark_id=parent_mark_id,
                datum_id=datum_id,
                repository_path=repository_path,
            )
            session.add(mark_row)
            await session.commit()

        result = MarkResult(
            mark_id=mark_id,
            action=action,
            reasoning=reasoning,
            principles=list(principles or []),
            tags=list(tags or []),
            author=author,
            timestamp=datetime.now(UTC),
            datum_id=datum_id,
            parent_mark_id=parent_mark_id,
        )

        # Fire-and-forget trace recording
        self._record_trace(
            "save_mark",
            (action[:100],),
            mark_id,
            f"Mark by {author}",
        )

        return result

    async def get_marks(
        self,
        limit: int = 20,
        author: str | None = None,
        session_id: str | None = None,
        since: datetime | None = None,
        tags: list[str] | None = None,
        tag_prefix: str | None = None,
    ) -> list["MarkResult"]:
        """
        Get recent marks with optional filters.

        AGENTESE: world.witness.marks

        Args:
            limit: Maximum marks to return (default 20)
            author: Filter by author
            session_id: Filter by session
            since: Filter by created_at > since
            tags: Filter by exact tag match (any of these tags)
            tag_prefix: Filter by tag prefix (e.g., "spec:" for all spec-related)

        Returns:
            List of MarkResult objects, newest first
        """
        from models.witness import WitnessMark

        async with self.session_factory() as session:
            stmt = select(WitnessMark).order_by(WitnessMark.created_at.desc())

            if author:
                stmt = stmt.where(WitnessMark.author == author)
            if session_id:
                stmt = stmt.where(WitnessMark.session_id == session_id)
            if since:
                stmt = stmt.where(WitnessMark.created_at > since)

            stmt = stmt.limit(limit)

            result = await session.execute(stmt)
            rows = result.scalars().all()

            # Filter by tags in-memory (JSON array filtering varies by DB)
            marks = []
            for row in rows:
                row_tags = list(row.tags) if row.tags else []

                # Apply tag filters
                if tags and not any(t in row_tags for t in tags):
                    continue
                if tag_prefix and not any(t.startswith(tag_prefix) for t in row_tags):
                    continue

                marks.append(
                    MarkResult(
                        mark_id=row.id,
                        action=row.action,
                        reasoning=row.reasoning,
                        principles=list(row.principles) if row.principles else [],
                        tags=row_tags,
                        author=row.author,
                        timestamp=row.created_at,
                        datum_id=row.datum_id,
                        parent_mark_id=row.parent_mark_id,
                    )
                )

            return marks

    async def get_mark(self, mark_id: str) -> "MarkResult | None":
        """
        Get a single mark by ID.

        Args:
            mark_id: The mark ID to retrieve

        Returns:
            MarkResult or None if not found
        """
        from models.witness import WitnessMark

        async with self.session_factory() as session:
            row = await session.get(WitnessMark, mark_id)
            if not row:
                return None

            return MarkResult(
                mark_id=row.id,
                action=row.action,
                reasoning=row.reasoning,
                principles=list(row.principles) if row.principles else [],
                tags=list(row.tags) if row.tags else [],
                author=row.author,
                timestamp=row.created_at,
                datum_id=row.datum_id,
                parent_mark_id=row.parent_mark_id,
            )

    async def get_mark_tree(
        self,
        root_mark_id: str,
        max_depth: int = 10,
    ) -> list["MarkResult"]:
        """
        Get all marks in a causal tree starting from root.

        Traverses children (marks that have this mark as parent) recursively.

        Args:
            root_mark_id: The root mark ID
            max_depth: Maximum depth to traverse (default 10)

        Returns:
            List of MarkResult objects in tree order (root first, then children)
        """
        from models.witness import WitnessMark

        results: list[MarkResult] = []
        visited: set[str] = set()

        async def traverse(mark_id: str, depth: int) -> None:
            if depth > max_depth or mark_id in visited:
                return

            visited.add(mark_id)

            async with self.session_factory() as session:
                # Get the mark itself
                row = await session.get(WitnessMark, mark_id)
                if not row:
                    return

                results.append(
                    MarkResult(
                        mark_id=row.id,
                        action=row.action,
                        reasoning=row.reasoning,
                        principles=list(row.principles) if row.principles else [],
                        tags=list(row.tags) if row.tags else [],
                        author=row.author,
                        timestamp=row.created_at,
                        datum_id=row.datum_id,
                        parent_mark_id=row.parent_mark_id,
                    )
                )

                # Get children (marks that have this as parent)
                stmt = (
                    select(WitnessMark)
                    .where(WitnessMark.parent_mark_id == mark_id)
                    .order_by(WitnessMark.created_at)
                )
                result = await session.execute(stmt)
                children = result.scalars().all()

            # Recursively traverse children
            for child in children:
                await traverse(child.id, depth + 1)

        await traverse(root_mark_id, 0)
        return results

    async def get_mark_ancestry(self, mark_id: str) -> list["MarkResult"]:
        """
        Get ancestors of a mark (parent chain up to root).

        Args:
            mark_id: The mark ID to get ancestry for

        Returns:
            List of MarkResult objects from mark to root (mark first, root last)
        """
        from models.witness import WitnessMark

        results: list[MarkResult] = []
        current_id: str | None = mark_id
        visited: set[str] = set()

        while current_id and current_id not in visited:
            visited.add(current_id)

            async with self.session_factory() as session:
                row = await session.get(WitnessMark, current_id)
                if not row:
                    break

                results.append(
                    MarkResult(
                        mark_id=row.id,
                        action=row.action,
                        reasoning=row.reasoning,
                        principles=list(row.principles) if row.principles else [],
                        tags=list(row.tags) if row.tags else [],
                        author=row.author,
                        timestamp=row.created_at,
                        datum_id=row.datum_id,
                        parent_mark_id=row.parent_mark_id,
                    )
                )

                current_id = row.parent_mark_id

        return results

    # =========================================================================
    # Evidence Operations (Unified Evidence-as-Marks)
    # =========================================================================

    async def get_evidence_for_spec(
        self,
        spec_path: str,
        evidence_type: str | None = None,
        limit: int = 100,
    ) -> list["MarkResult"]:
        """
        Get all evidence marks for a spec.

        Evidence is encoded as marks with specific tags:
        - spec:{path} — Links mark to a spec
        - evidence:impl — Implementation evidence
        - evidence:test — Test evidence
        - evidence:usage — Usage evidence

        Args:
            spec_path: The spec path (e.g., "principles.md" or "spec/principles.md")
            evidence_type: Filter by type ("impl", "test", "usage", or None for all)
            limit: Maximum marks to return

        Returns:
            List of MarkResult objects representing evidence
        """
        # Normalize spec path for matching
        spec_tag = f"spec:{spec_path.replace('spec/', '')}"

        # Query marks with the spec tag
        marks = await self.get_marks(limit=limit * 2, tag_prefix="spec:")

        # Filter to this specific spec
        evidence = []
        for mark in marks:
            if spec_tag not in mark.tags:
                continue

            # Filter by evidence type if specified
            if evidence_type:
                type_tag = f"evidence:{evidence_type}"
                if type_tag not in mark.tags:
                    continue

            evidence.append(mark)

            if len(evidence) >= limit:
                break

        return evidence

    async def get_specs_with_evidence(self, limit: int = 100) -> dict[str, list["MarkResult"]]:
        """
        Get all specs that have evidence marks.

        Returns a mapping of spec paths to their evidence marks.

        Args:
            limit: Maximum total marks to scan

        Returns:
            Dict mapping spec path to list of evidence marks
        """
        # Get all marks with spec: tag prefix
        marks = await self.get_marks(limit=limit, tag_prefix="spec:")

        # Group by spec path
        by_spec: dict[str, list[MarkResult]] = {}
        for mark in marks:
            for tag in mark.tags:
                if tag.startswith("spec:"):
                    spec_path = tag[5:]  # Remove "spec:" prefix
                    if spec_path not in by_spec:
                        by_spec[spec_path] = []
                    by_spec[spec_path].append(mark)
                    break  # Only count once per mark

        return by_spec

    async def count_evidence_by_spec(self) -> dict[str, dict[str, int]]:
        """
        Count evidence by spec and type.

        Returns a nested dict: {spec_path: {evidence_type: count}}

        Example:
            {
                "principles.md": {"impl": 3, "test": 2, "usage": 0},
                "k-block.md": {"impl": 2, "test": 5, "usage": 1},
            }
        """
        marks = await self.get_marks(limit=500, tag_prefix="spec:")

        counts: dict[str, dict[str, int]] = {}
        for mark in marks:
            spec_path = None
            evidence_types = []

            for tag in mark.tags:
                if tag.startswith("spec:"):
                    spec_path = tag[5:]
                elif tag.startswith("evidence:"):
                    evidence_types.append(tag[9:])

            if spec_path:
                if spec_path not in counts:
                    counts[spec_path] = {"impl": 0, "test": 0, "usage": 0}

                for etype in evidence_types:
                    if etype in counts[spec_path]:
                        counts[spec_path][etype] += 1

        return counts

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

        # Detect backend from engine dialect
        try:
            engine = self.session_factory.kw.get("bind")
            if engine and hasattr(engine, "dialect"):
                backend = engine.dialect.name
            else:
                backend = "unknown"
        except Exception:
            backend = "unknown"

        return WitnessStatus(
            total_thoughts=total_thoughts,
            total_actions=total_actions,
            trust_count=total_trust,
            reversible_actions=reversible_actions,
            storage_backend=backend,
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
    "MarkResult",
    "WitnessStatus",
]
