"""
Entity Adapters: Convert DB models to UnifiedEvent.

> *"The file is a lie. There is only the graph."*

Each adapter converts a specific DB model to the UnifiedEvent shape:
- MarkAdapter: WitnessMark → UnifiedEvent
- CrystalAdapter: Crystal → UnifiedEvent
- TrailAdapter: TrailRow → UnifiedEvent
- EvidenceAdapter: TraceWitness|VerificationGraph|CategoricalViolation → UnifiedEvent
- TeachingAdapter: TeachingCrystal → UnifiedEvent
- LemmaAdapter: VerifiedLemmaModel → UnifiedEvent

The Adapter Protocol:
- to_unified_event(row) → UnifiedEvent
- list_recent(session, limit, offset) → list[UnifiedEvent]
- count(session) → int

Teaching:
    gotcha: Evidence is three subtypes in one adapter. Use EvidenceSubtype discriminator.
    gotcha: TrailRow has computed evidence_strength from max commitment level.
    gotcha: TeachingCrystal.is_alive is a property, not a column.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import TYPE_CHECKING, Any, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .contracts import (
    CrystalMetadata,
    EntityType,
    EvidenceMetadata,
    LemmaMetadata,
    MarkMetadata,
    StreamFilters,
    TeachingMetadata,
    TrailMetadata,
    UnifiedEvent,
)

if TYPE_CHECKING:
    from models.ashc import VerifiedLemmaModel
    from models.brain import Crystal, TeachingCrystal
    from models.trail import TrailRow
    from models.verification import (
        CategoricalViolation,
        TraceWitness,
        VerificationGraph,
    )
    from models.witness import WitnessMark

logger = logging.getLogger(__name__)


# =============================================================================
# Timestamp Helper
# =============================================================================


def _safe_timestamp(value: Any) -> str:
    """
    Safely convert a timestamp to ISO format string.

    Handles: datetime, string, None, and other types gracefully.
    """
    if value is None:
        return datetime.utcnow().isoformat()
    if isinstance(value, str):
        return value  # Already a string
    if hasattr(value, "isoformat"):
        return str(value.isoformat())
    return str(value)


T = TypeVar("T")


# =============================================================================
# Base Adapter Protocol
# =============================================================================


class EntityAdapter(ABC):
    """
    Base adapter protocol for converting DB models to UnifiedEvent.

    Each adapter must implement:
    - entity_type: The EntityType this adapter handles
    - to_unified_event(): Convert single row to UnifiedEvent
    - list_recent(): Query recent rows and convert
    - count(): Get total count for this entity type
    """

    @property
    @abstractmethod
    def entity_type(self) -> EntityType:
        """The entity type this adapter handles."""
        ...

    @abstractmethod
    def to_unified_event(self, row: Any) -> UnifiedEvent:
        """Convert a single DB row to UnifiedEvent."""
        ...

    @abstractmethod
    async def list_recent(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Query recent rows and convert to UnifiedEvents."""
        ...

    @abstractmethod
    async def count(
        self,
        session: AsyncSession,
        filters: StreamFilters | None = None,
    ) -> int:
        """Get total count for this entity type."""
        ...


# =============================================================================
# Mark Adapter
# =============================================================================


class MarkAdapter(EntityAdapter):
    """Convert WitnessMark to UnifiedEvent."""

    @property
    def entity_type(self) -> EntityType:
        return EntityType.MARK

    def to_unified_event(self, row: WitnessMark) -> UnifiedEvent:
        """Convert WitnessMark to UnifiedEvent."""
        # Build metadata
        metadata = MarkMetadata(
            type="mark",
            action=row.action,
            reasoning=row.reasoning,
            principles=list(row.principles) if row.principles else [],
            tags=list(row.tags) if row.tags else [],
            author=row.author or "kent",
            session_id=row.session_id,
            parent_mark_id=row.parent_mark_id,
        )

        # Build title from action (truncate if long)
        title = row.action[:80] + "..." if len(row.action) > 80 else row.action

        # Build summary from reasoning or principles
        if row.reasoning:
            summary = row.reasoning[:120] + "..." if len(row.reasoning) > 120 else row.reasoning
        elif row.principles:
            summary = f"Honors: {', '.join(row.principles[:3])}"
        else:
            summary = f"By {row.author or 'kent'}"

        return UnifiedEvent(
            id=row.id,
            type=EntityType.MARK,
            title=title,
            summary=summary,
            timestamp=_safe_timestamp(row.created_at),
            metadata=metadata.__dict__,
        )

    async def list_recent(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Query recent marks and convert."""
        from models.witness import WitnessMark

        stmt = select(WitnessMark).order_by(WitnessMark.created_at.desc())

        # Apply filters
        if filters:
            if filters.author:
                stmt = stmt.where(WitnessMark.author == filters.author)
            if filters.date_start:
                stmt = stmt.where(WitnessMark.created_at >= filters.date_start)
            if filters.date_end:
                stmt = stmt.where(WitnessMark.created_at <= filters.date_end)
            if filters.tags:
                # JSON array contains any of the tags
                for tag in filters.tags:
                    stmt = stmt.where(WitnessMark.tags.contains([tag]))

        stmt = stmt.offset(offset).limit(limit)

        result = await session.execute(stmt)
        rows = result.scalars().all()

        return [self.to_unified_event(row) for row in rows]

    async def count(
        self,
        session: AsyncSession,
        filters: StreamFilters | None = None,
    ) -> int:
        """Get total mark count."""
        from models.witness import WitnessMark

        stmt = select(func.count()).select_from(WitnessMark)

        if filters:
            if filters.author:
                stmt = stmt.where(WitnessMark.author == filters.author)
            if filters.date_start:
                stmt = stmt.where(WitnessMark.created_at >= filters.date_start)
            if filters.date_end:
                stmt = stmt.where(WitnessMark.created_at <= filters.date_end)

        result = await session.execute(stmt)
        return result.scalar() or 0


# =============================================================================
# Crystal Adapter
# =============================================================================


class CrystalAdapter(EntityAdapter):
    """Convert Crystal to UnifiedEvent."""

    @property
    def entity_type(self) -> EntityType:
        return EntityType.CRYSTAL

    def to_unified_event(self, row: Crystal) -> UnifiedEvent:
        """Convert Crystal to UnifiedEvent."""
        metadata = CrystalMetadata(
            type="crystal",
            content_hash=row.content_hash or "",
            tags=list(row.tags) if row.tags else [],
            access_count=row.access_count or 0,
            last_accessed=_safe_timestamp(row.last_accessed) if row.last_accessed else None,
            source_type=row.source_type,
            source_ref=row.source_ref,
            datum_id=row.datum_id,
        )

        # Title is summary (truncated)
        title = row.summary[:80] + "..." if len(row.summary) > 80 else row.summary

        # Summary includes access info and tags
        parts = []
        if row.access_count:
            parts.append(f"Accessed {row.access_count}x")
        if row.tags:
            parts.append(f"Tags: {', '.join(row.tags[:3])}")
        summary = " | ".join(parts) if parts else "Crystallized knowledge"

        return UnifiedEvent(
            id=row.id,
            type=EntityType.CRYSTAL,
            title=title,
            summary=summary,
            timestamp=_safe_timestamp(row.created_at),
            metadata=metadata.__dict__,
        )

    async def list_recent(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Query recent crystals and convert."""
        from models.brain import Crystal

        stmt = select(Crystal).order_by(Crystal.created_at.desc())

        if filters:
            if filters.date_start:
                stmt = stmt.where(Crystal.created_at >= filters.date_start)
            if filters.date_end:
                stmt = stmt.where(Crystal.created_at <= filters.date_end)
            if filters.tags:
                for tag in filters.tags:
                    stmt = stmt.where(Crystal.tags.contains([tag]))

        stmt = stmt.offset(offset).limit(limit)

        result = await session.execute(stmt)
        rows = result.scalars().all()

        return [self.to_unified_event(row) for row in rows]

    async def count(
        self,
        session: AsyncSession,
        filters: StreamFilters | None = None,
    ) -> int:
        """Get total crystal count."""
        from models.brain import Crystal

        stmt = select(func.count()).select_from(Crystal)

        if filters:
            if filters.date_start:
                stmt = stmt.where(Crystal.created_at >= filters.date_start)
            if filters.date_end:
                stmt = stmt.where(Crystal.created_at <= filters.date_end)

        result = await session.execute(stmt)
        return result.scalar() or 0


# =============================================================================
# Trail Adapter
# =============================================================================


class TrailAdapter(EntityAdapter):
    """Convert TrailRow to UnifiedEvent."""

    @property
    def entity_type(self) -> EntityType:
        return EntityType.TRAIL

    def _compute_evidence_strength(self, row: TrailRow) -> str:
        """Compute evidence strength from commitments."""
        # Check if there are any commitments loaded
        if hasattr(row, "commitments") and row.commitments:
            levels = [c.level for c in row.commitments]
            if "definitive" in levels:
                return "definitive"
            if "strong" in levels:
                return "strong"
            if "moderate" in levels:
                return "moderate"
        return "weak"

    def to_unified_event(self, row: TrailRow) -> UnifiedEvent:
        """Convert TrailRow to UnifiedEvent."""
        step_count = len(row.steps) if hasattr(row, "steps") and row.steps else 0

        metadata = TrailMetadata(
            type="trail",
            name=row.name,
            step_count=step_count,
            topics=list(row.topics) if row.topics else [],
            evidence_strength=self._compute_evidence_strength(row),
            forked_from_id=row.forked_from_id,
            is_active=row.is_active if hasattr(row, "is_active") else True,
        )

        # Title is trail name
        title = row.name

        # Summary includes step count and topics
        parts = [f"{step_count} steps"]
        if row.topics:
            parts.append(f"Topics: {', '.join(row.topics[:2])}")
        summary = " | ".join(parts)

        return UnifiedEvent(
            id=row.id,
            type=EntityType.TRAIL,
            title=title,
            summary=summary,
            timestamp=_safe_timestamp(row.created_at),
            metadata=metadata.__dict__,
        )

    async def list_recent(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Query recent trails and convert."""
        from models.trail import TrailRow

        stmt = select(TrailRow).order_by(TrailRow.created_at.desc())

        if filters:
            if filters.date_start:
                stmt = stmt.where(TrailRow.created_at >= filters.date_start)
            if filters.date_end:
                stmt = stmt.where(TrailRow.created_at <= filters.date_end)

        stmt = stmt.offset(offset).limit(limit)

        result = await session.execute(stmt)
        rows = result.scalars().all()

        return [self.to_unified_event(row) for row in rows]

    async def count(
        self,
        session: AsyncSession,
        filters: StreamFilters | None = None,
    ) -> int:
        """Get total trail count."""
        from models.trail import TrailRow

        stmt = select(func.count()).select_from(TrailRow)

        if filters:
            if filters.date_start:
                stmt = stmt.where(TrailRow.created_at >= filters.date_start)
            if filters.date_end:
                stmt = stmt.where(TrailRow.created_at <= filters.date_end)

        result = await session.execute(stmt)
        return result.scalar() or 0


# =============================================================================
# Evidence Adapter (handles 3 subtypes)
# =============================================================================


class EvidenceAdapter(EntityAdapter):
    """Convert TraceWitness, VerificationGraph, or CategoricalViolation to UnifiedEvent."""

    @property
    def entity_type(self) -> EntityType:
        return EntityType.EVIDENCE

    def _convert_trace_witness(self, row: TraceWitness) -> UnifiedEvent:
        """Convert TraceWitness to UnifiedEvent."""
        metadata = EvidenceMetadata(
            type="evidence",
            subtype="trace_witness",
            agent_path=row.agent_path,
            status=row.verification_status.value
            if hasattr(row.verification_status, "value")
            else str(row.verification_status),
            violation_type=None,
            is_resolved=None,
        )

        title = f"Trace: {row.agent_path}" if row.agent_path else "Trace Witness"
        summary = f"Status: {metadata.status}"

        return UnifiedEvent(
            id=row.id,
            type=EntityType.EVIDENCE,
            title=title,
            summary=summary,
            timestamp=_safe_timestamp(row.created_at),
            metadata=metadata.__dict__,
        )

    def _convert_verification_graph(self, row: VerificationGraph) -> UnifiedEvent:
        """Convert VerificationGraph to UnifiedEvent."""
        metadata = EvidenceMetadata(
            type="evidence",
            subtype="verification_graph",
            agent_path=None,
            status=row.status.value if hasattr(row.status, "value") else str(row.status),
            violation_type=None,
            is_resolved=None,
        )

        title = row.name if row.name else "Verification Graph"
        node_count = row.node_count if hasattr(row, "node_count") else 0
        edge_count = row.edge_count if hasattr(row, "edge_count") else 0
        summary = f"{node_count} nodes, {edge_count} edges | Status: {metadata.status}"

        return UnifiedEvent(
            id=row.id,
            type=EntityType.EVIDENCE,
            title=title,
            summary=summary,
            timestamp=_safe_timestamp(row.created_at),
            metadata=metadata.__dict__,
        )

    def _convert_categorical_violation(self, row: CategoricalViolation) -> UnifiedEvent:
        """Convert CategoricalViolation to UnifiedEvent."""
        violation_type = (
            row.violation_type.value
            if hasattr(row.violation_type, "value")
            else str(row.violation_type)
        )

        metadata = EvidenceMetadata(
            type="evidence",
            subtype="categorical_violation",
            agent_path=None,
            status="success" if row.is_resolved else "failure",
            violation_type=violation_type,
            is_resolved=row.is_resolved,
        )

        title = f"Violation: {violation_type}"
        summary = row.law_description[:80] if row.law_description else "Categorical law violation"

        return UnifiedEvent(
            id=row.id,
            type=EntityType.EVIDENCE,
            title=title,
            summary=summary,
            timestamp=_safe_timestamp(row.created_at),
            metadata=metadata.__dict__,
        )

    def to_unified_event(self, row: Any) -> UnifiedEvent:
        """Convert evidence row to UnifiedEvent (dispatches by type)."""
        from models.verification import (
            CategoricalViolation,
            TraceWitness,
            VerificationGraph,
        )

        if isinstance(row, TraceWitness):
            return self._convert_trace_witness(row)
        elif isinstance(row, VerificationGraph):
            return self._convert_verification_graph(row)
        elif isinstance(row, CategoricalViolation):
            return self._convert_categorical_violation(row)
        else:
            # Fallback
            return UnifiedEvent(
                id=getattr(row, "id", "unknown"),
                type=EntityType.EVIDENCE,
                title="Unknown Evidence",
                summary="Unknown evidence type",
                timestamp=datetime.utcnow().isoformat(),
                metadata={"type": "evidence", "subtype": "unknown"},
            )

    async def list_recent(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Query recent evidence from all three tables and merge."""
        from models.verification import (
            CategoricalViolation,
            TraceWitness,
            VerificationGraph,
        )

        events: list[UnifiedEvent] = []

        # Query each table with limit/3 (rough distribution)
        per_table_limit = max(limit // 3, 10)

        # TraceWitness
        tw_stmt = (
            select(TraceWitness).order_by(TraceWitness.created_at.desc()).limit(per_table_limit)
        )
        tw_result = await session.execute(tw_stmt)
        for tw_row in tw_result.scalars().all():
            events.append(self._convert_trace_witness(tw_row))

        # VerificationGraph
        vg_stmt = (
            select(VerificationGraph)
            .order_by(VerificationGraph.created_at.desc())
            .limit(per_table_limit)
        )
        vg_result = await session.execute(vg_stmt)
        for vg_row in vg_result.scalars().all():
            events.append(self._convert_verification_graph(vg_row))

        # CategoricalViolation
        cv_stmt = (
            select(CategoricalViolation)
            .order_by(CategoricalViolation.created_at.desc())
            .limit(per_table_limit)
        )
        cv_result = await session.execute(cv_stmt)
        for cv_row in cv_result.scalars().all():
            events.append(self._convert_categorical_violation(cv_row))

        # Sort by timestamp descending and apply limit
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return events[offset : offset + limit]

    async def count(
        self,
        session: AsyncSession,
        filters: StreamFilters | None = None,
    ) -> int:
        """Get total evidence count (all three tables)."""
        from models.verification import (
            CategoricalViolation,
            TraceWitness,
            VerificationGraph,
        )

        total = 0

        for model in [TraceWitness, VerificationGraph, CategoricalViolation]:
            stmt = select(func.count()).select_from(model)
            result = await session.execute(stmt)
            total += result.scalar() or 0

        return total


# =============================================================================
# Teaching Adapter
# =============================================================================


class TeachingAdapter(EntityAdapter):
    """Convert TeachingCrystal to UnifiedEvent."""

    @property
    def entity_type(self) -> EntityType:
        return EntityType.TEACHING

    def to_unified_event(self, row: TeachingCrystal) -> UnifiedEvent:
        """Convert TeachingCrystal to UnifiedEvent."""
        # is_alive is a property on the model
        is_alive = row.died_at is None

        metadata = TeachingMetadata(
            type="teaching",
            insight=row.insight,
            severity=row.severity or "info",
            source_module=row.source_module or "",
            source_symbol=row.source_symbol or "",
            is_alive=is_alive,
            died_at=_safe_timestamp(row.died_at) if row.died_at else None,
            successor_module=row.successor_module,
            extinction_id=None,  # Would need join to get this
        )

        # Title is insight (truncated)
        title = row.insight[:80] + "..." if len(row.insight) > 80 else row.insight

        # Summary includes severity and source
        parts = [f"[{row.severity or 'info'}]"]
        if row.source_module:
            parts.append(f"from {row.source_module}")
        if not is_alive:
            parts.append("(extinct)")
        summary = " ".join(parts)

        return UnifiedEvent(
            id=row.id,
            type=EntityType.TEACHING,
            title=title,
            summary=summary,
            timestamp=_safe_timestamp(row.created_at),
            metadata=metadata.__dict__,
        )

    async def list_recent(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Query recent teachings and convert."""
        from models.brain import TeachingCrystal

        stmt = select(TeachingCrystal).order_by(TeachingCrystal.created_at.desc())

        if filters:
            if filters.date_start:
                stmt = stmt.where(TeachingCrystal.created_at >= filters.date_start)
            if filters.date_end:
                stmt = stmt.where(TeachingCrystal.created_at <= filters.date_end)

        stmt = stmt.offset(offset).limit(limit)

        result = await session.execute(stmt)
        rows = result.scalars().all()

        return [self.to_unified_event(row) for row in rows]

    async def count(
        self,
        session: AsyncSession,
        filters: StreamFilters | None = None,
    ) -> int:
        """Get total teaching count."""
        from models.brain import TeachingCrystal

        stmt = select(func.count()).select_from(TeachingCrystal)

        if filters:
            if filters.date_start:
                stmt = stmt.where(TeachingCrystal.created_at >= filters.date_start)
            if filters.date_end:
                stmt = stmt.where(TeachingCrystal.created_at <= filters.date_end)

        result = await session.execute(stmt)
        return result.scalar() or 0


# =============================================================================
# Lemma Adapter
# =============================================================================


class LemmaAdapter(EntityAdapter):
    """Convert VerifiedLemmaModel to UnifiedEvent."""

    @property
    def entity_type(self) -> EntityType:
        return EntityType.LEMMA

    def to_unified_event(self, row: VerifiedLemmaModel) -> UnifiedEvent:
        """Convert VerifiedLemmaModel to UnifiedEvent."""
        metadata = LemmaMetadata(
            type="lemma",
            statement=row.statement,
            checker=row.checker or "lean4",
            usage_count=row.usage_count or 0,
            obligation_id=row.obligation_id or "",
            dependencies=list(row.dependencies) if row.dependencies else [],
        )

        # Title is statement (truncated)
        title = row.statement[:80] + "..." if len(row.statement) > 80 else row.statement

        # Summary includes checker and usage
        summary = f"Verified by {row.checker} | Used {row.usage_count}x"

        return UnifiedEvent(
            id=row.id,
            type=EntityType.LEMMA,
            title=title,
            summary=summary,
            timestamp=_safe_timestamp(row.created_at),
            metadata=metadata.__dict__,
        )

    async def list_recent(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
        filters: StreamFilters | None = None,
    ) -> list[UnifiedEvent]:
        """Query recent lemmas and convert."""
        from models.ashc import VerifiedLemmaModel

        stmt = select(VerifiedLemmaModel).order_by(VerifiedLemmaModel.created_at.desc())

        if filters:
            if filters.date_start:
                stmt = stmt.where(VerifiedLemmaModel.created_at >= filters.date_start)
            if filters.date_end:
                stmt = stmt.where(VerifiedLemmaModel.created_at <= filters.date_end)

        stmt = stmt.offset(offset).limit(limit)

        result = await session.execute(stmt)
        rows = result.scalars().all()

        return [self.to_unified_event(row) for row in rows]

    async def count(
        self,
        session: AsyncSession,
        filters: StreamFilters | None = None,
    ) -> int:
        """Get total lemma count."""
        from models.ashc import VerifiedLemmaModel

        stmt = select(func.count()).select_from(VerifiedLemmaModel)

        if filters:
            if filters.date_start:
                stmt = stmt.where(VerifiedLemmaModel.created_at >= filters.date_start)
            if filters.date_end:
                stmt = stmt.where(VerifiedLemmaModel.created_at <= filters.date_end)

        result = await session.execute(stmt)
        return result.scalar() or 0


# =============================================================================
# Adapter Registry
# =============================================================================


def get_adapter(entity_type: EntityType) -> EntityAdapter:
    """Get adapter for entity type."""
    adapters: dict[EntityType, EntityAdapter] = {
        EntityType.MARK: MarkAdapter(),
        EntityType.CRYSTAL: CrystalAdapter(),
        EntityType.TRAIL: TrailAdapter(),
        EntityType.EVIDENCE: EvidenceAdapter(),
        EntityType.TEACHING: TeachingAdapter(),
        EntityType.LEMMA: LemmaAdapter(),
    }
    return adapters[entity_type]


def get_all_adapters() -> list[EntityAdapter]:
    """Get all adapters."""
    return [
        MarkAdapter(),
        CrystalAdapter(),
        TrailAdapter(),
        EvidenceAdapter(),
        TeachingAdapter(),
        LemmaAdapter(),
    ]
