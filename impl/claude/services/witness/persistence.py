"""
Witness Persistence: Universe-backed Storage for the 8th Crown Jewel.

Owns domain semantics for Witness storage:
- WHEN to persist (on thought, on action, on escalation)
- WHY to persist (Crystal system for typed, versioned data)
- HOW to compose (Universe handles backend selection and schema)

AGENTESE aspects exposed:
- save_thought: Store thought with semantic embedding
- get_thoughts: Retrieve recent thoughts
- get_trust_level: Get trust with decay applied
- record_escalation: Log trust level change
- record_action: Store action with rollback info
- get_rollback_window: Get reversible actions

Migration Status (SQLAlchemy → Universe/Crystal):
=====================================================
COMPLETED:
- ✅ save_thought() - Uses Universe with WitnessThought schema
- ✅ get_thoughts() - Query Universe, filter in-memory
- ✅ save_mark() - Uses Universe with WitnessMark schema
- ✅ get_mark() - Universe.get() by ID
- ✅ get_marks() - Query Universe, filter in-memory

TODO (Still using SQLAlchemy):
- ⚠️ thought_stream() - Streaming thoughts (lines 305-383)
- ⚠️ get_trust_level() - Trust with decay (lines 388-454)
- ⚠️ update_trust_metrics() - Trust metrics update (lines 456-521)
- ⚠️ record_escalation() - Trust escalation audit (lines 523-589)
- ⚠️ record_action() - Action logging (lines 595-642)
- ⚠️ get_rollback_window() - Rollback actions (lines 644-697)
- ⚠️ get_mark_tree() - Recursive tree traversal (lines 885-982)
- ⚠️ get_mark_ancestry() - Parent chain (lines 984-1024)
- ⚠️ get_evidence_for_spec() - Evidence queries (lines 1030-1077)
- ⚠️ get_specs_with_evidence() - Spec grouping (lines 1079-1105)
- ⚠️ count_evidence_by_spec() - Evidence counts (lines 1107-1140)
- ⚠️ manifest() - Status counts (lines 1145-1148)

Migration Pattern:
1. Create frozen dataclass from schema (WitnessThought, WitnessMark, etc.)
2. Store via universe.store(obj, "witness.X")
3. Query via universe.query(Query(schema="witness.X", ...))
4. Filter in-memory (Universe query is limited vs SQL)
5. Return existing result types (ThoughtResult, MarkResult, etc.)

Limitation: Universe queries are less powerful than SQL
- Only supports: schema, prefix, after (timestamp), limit
- Complex filtering must be done in Python after query
- Consider keeping SQLAlchemy for complex queries OR
- Enhance Universe with better query capabilities

The Pattern (from crown-jewel-patterns.md):
- Pattern 1: Container Owns Workflow (WitnessTrust owns thoughts, actions)
- Pattern 6: Async-Safe Event Emission (fire-and-forget traces)
- Pattern 15: No Hollow Services (always go through DI)

See: docs/skills/metaphysical-fullstack.md
See: spec/protocols/unified-data-crystal.md
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any, AsyncGenerator

from agents.d.schemas.witness import (
    WitnessAction,
    WitnessEscalation,
    WitnessMark,
    WitnessThought,
    WitnessTrust,
)
from agents.d.universe import DataclassSchema, Query, Universe, get_universe

from .polynomial import ActionResult, Thought, TrustLevel

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def hash_email(email: str) -> str:
    """Hash git email for privacy-preserving trust keys."""
    return hashlib.sha256(email.lower().encode()).hexdigest()[:16]


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

    Uses Universe for typed, versioned data storage:
    - WitnessThought: Observation stream
    - WitnessAction: Action history with rollback
    - WitnessTrust: Trust levels with decay
    - WitnessMark: Witnessed behavior records
    - WitnessEscalation: Trust change audit trail

    Domain Semantics:
    - Thoughts are the atomic units of observation
    - Each thought is stored as Crystal with schema
    - Trust decays on load (not on save)
    - Actions are logged with reversibility info
    - All data versioned via schemas

    Example:
        persistence = WitnessPersistence()

        result = await persistence.save_thought(thought)
        thoughts = await persistence.get_thoughts(limit=50)
        trust = await persistence.get_trust_level("user@example.com")
    """

    def __init__(
        self,
        universe: Universe | None = None,
    ) -> None:
        """
        Initialize WitnessPersistence.

        Args:
            universe: Optional Universe instance (uses singleton if None)
        """
        self.universe = universe or get_universe()

        # Register schemas on first init
        self._register_schemas()

    def _register_schemas(self) -> None:
        """Register all Witness schemas with Universe."""
        # Create Universe-compatible DataclassSchemas for witness types
        # These wrap the frozen dataclasses with serialize/deserialize
        self.universe.register_type("witness.thought", WitnessThought)
        self.universe.register_type("witness.action", WitnessAction)
        self.universe.register_type("witness.trust", WitnessTrust)
        self.universe.register_type("witness.mark", WitnessMark)
        self.universe.register_type("witness.escalation", WitnessEscalation)

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
        Save a thought to Universe storage.

        AGENTESE: self.witness.thoughts.capture

        Storage via Universe/Crystal:
        - Thought stored as WitnessThought via schema
        - Schema versioning handles evolution
        - Backend auto-selected (Postgres > SQLite > Memory)

        Args:
            thought: The Thought object from polynomial.py
            trust_id: Optional trust ID for user context
            repository_path: Optional repository context

        Returns:
            ThoughtResult with thought_id and storage details
        """
        # Create WitnessThought dataclass (frozen, immutable)
        witness_thought = WitnessThought(
            content=thought.content,
            source=thought.source,
            tags=thought.tags,
            trust_id=trust_id,
            context={"repository_path": repository_path} if repository_path else {},
        )

        # Store via Universe (schema registered in __init__)
        thought_id = await self.universe.store(witness_thought, "witness.thought")

        result = ThoughtResult(
            thought_id=thought_id,
            content=thought.content,
            source=thought.source,
            tags=list(thought.tags),
            timestamp=thought.timestamp,
            datum_id=thought_id,  # Datum ID returned by store
        )

        logger.debug(f"Saved thought {thought_id} from {thought.source}")
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
        # Query Universe for witness.thought schema
        # Note: Filtering done in-memory as Universe query is limited
        query = Query(
            schema="witness.thought",
            after=since.timestamp() if since else None,
            limit=limit * 3,  # Over-fetch for filtering
        )

        witness_thoughts: list[WitnessThought] = await self.universe.query(query)

        # Filter in-memory
        filtered = []
        for wt in witness_thoughts:
            if trust_id and wt.trust_id != trust_id:
                continue
            if source and wt.source != source:
                continue
            filtered.append(
                Thought(
                    content=wt.content,
                    source=wt.source,
                    tags=wt.tags,
                    timestamp=datetime.now(UTC),  # TODO: extract from datum
                )
            )

        # Sort by timestamp (newest first) and limit
        # Note: Sorting relies on datum creation time
        return filtered[:limit]

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
        Save a mark to Universe storage.

        AGENTESE: world.witness.mark / time.witness.mark

        Storage via Universe/Crystal:
        - Mark stored as WitnessMark via schema
        - Schema versioning handles evolution
        - Parent lineage tracked via parent_mark_id

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
        # Validate parent exists if specified
        if parent_mark_id:
            parent = await self.get_mark(parent_mark_id)
            if not parent:
                raise ValueError(f"Parent mark not found: {parent_mark_id}")

        # Build context dict
        context = {}
        if session_id:
            context["session_id"] = session_id
        if repository_path:
            context["repository_path"] = repository_path

        # Create WitnessMark dataclass (frozen, immutable)
        witness_mark = WitnessMark(
            action=action,
            reasoning=reasoning or "",
            author=author,
            tags=tuple(tags or []),
            principles=tuple(principles or []),
            parent_mark_id=parent_mark_id,
            context=context,
        )

        # Store via Universe
        mark_id = await self.universe.store(witness_mark, "witness.mark")

        result = MarkResult(
            mark_id=mark_id,
            action=action,
            reasoning=reasoning,
            principles=list(principles or []),
            tags=list(tags or []),
            author=author,
            timestamp=datetime.now(UTC),
            datum_id=mark_id,
            parent_mark_id=parent_mark_id,
        )

        logger.debug(f"Saved mark {mark_id} by {author}")
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
        # Query Universe for witness.mark schema
        query = Query(
            schema="witness.mark",
            after=since.timestamp() if since else None,
            limit=limit * 3,  # Over-fetch for filtering
        )

        witness_marks: list[WitnessMark] = await self.universe.query(query)

        # Filter in-memory
        marks = []
        for wm in witness_marks:
            # Apply author filter
            if author and wm.author != author:
                continue

            # Apply session_id filter (from context)
            if session_id and wm.context.get("session_id") != session_id:
                continue

            # Apply tag filters
            mark_tags = list(wm.tags)
            if tags and not any(t in mark_tags for t in tags):
                continue
            if tag_prefix and not any(t.startswith(tag_prefix) for t in mark_tags):
                continue

            marks.append(
                MarkResult(
                    mark_id="unknown",  # TODO: need datum ID
                    action=wm.action,
                    reasoning=wm.reasoning,
                    principles=list(wm.principles),
                    tags=mark_tags,
                    author=wm.author,
                    timestamp=datetime.now(UTC),  # TODO: extract from datum
                    datum_id=None,
                    parent_mark_id=wm.parent_mark_id,
                )
            )

        # Limit results
        return marks[:limit]

    async def get_mark(self, mark_id: str) -> "MarkResult | None":
        """
        Get a single mark by ID.

        Args:
            mark_id: The mark ID to retrieve

        Returns:
            MarkResult or None if not found
        """
        witness_mark = await self.universe.get(mark_id)
        if witness_mark is None or not isinstance(witness_mark, WitnessMark):
            return None

        return MarkResult(
            mark_id=mark_id,
            action=witness_mark.action,
            reasoning=witness_mark.reasoning,
            principles=list(witness_mark.principles),
            tags=list(witness_mark.tags),
            author=witness_mark.author,
            timestamp=datetime.now(UTC),  # TODO: extract from datum
            datum_id=mark_id,
            parent_mark_id=witness_mark.parent_mark_id,
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
    # (No helper methods needed - Universe handles complexity)


__all__ = [
    "WitnessPersistence",
    "ThoughtResult",
    "TrustResult",
    "EscalationResult",
    "ActionResultPersisted",
    "MarkResult",
    "WitnessStatus",
]
