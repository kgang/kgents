"""
Sovereign Analyzer: Async analysis worker for ingested entities.

> *"Analysis is automatic. Placeholders are automatic. Trust the flow."*

This module implements the core analysis workflow:

    analyze(path) ──► 1. Check if already analyzed (skip unless force)
                      2. Set status = ANALYZING, emit ANALYSIS_STARTED
                      3. Get entity content from store
                      4. Discover references via extract_edges()
                      5. Check which refs don't exist → placeholder_paths
                      6. Create placeholders for missing (fully automatic)
                      7. Create witness mark
                      8. Set status = ANALYZED, emit ANALYSIS_COMPLETED
                      On error: Set status = FAILED, emit ANALYSIS_FAILED

Teaching:
    gotcha: Placeholders are created with minimal metadata.
            They're sovereign entities, but marked as placeholders.

    gotcha: Analysis is idempotent. Running twice on same content
            produces same refs, but only creates placeholders once.

See: spec/protocols/inbound-sovereignty.md
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from .analysis import AnalysisResult, AnalysisState, AnalysisStatus
from .ingest import extract_edges
from .store import SovereignStore

if TYPE_CHECKING:
    from services.witness.bus import WitnessSynergyBus
    from services.witness.persistence import WitnessPersistence

logger = logging.getLogger(__name__)


# =============================================================================
# SovereignAnalyzer
# =============================================================================


class SovereignAnalyzer:
    """
    Analyzes ingested entities to discover references and create placeholders.

    The analyzer:
    1. Extracts edges from content (using existing extract_edges())
    2. Identifies references that don't yet exist
    3. Creates placeholder entities for missing references
    4. Records analysis state in overlay
    5. Emits witness events for tracking

    Example:
        >>> analyzer = SovereignAnalyzer(store, witness, bus)
        >>> result = await analyzer.analyze("spec/protocols/k-block.md")
        >>> print(f"Found {result.ref_count} refs, created {result.placeholder_count} placeholders")
    """

    def __init__(
        self,
        store: SovereignStore,
        witness: "WitnessPersistence | None" = None,
        bus: "WitnessSynergyBus | None" = None,
    ) -> None:
        """
        Initialize the analyzer.

        Args:
            store: The sovereign store
            witness: Optional witness persistence (for marks)
            bus: Optional synergy bus (for events)
        """
        self.store = store
        self.witness = witness
        self.bus = bus

    async def analyze(
        self,
        path: str,
        force: bool = False,
        author: str = "system",
    ) -> AnalysisResult:
        """
        Analyze an entity.

        Full workflow:
        1. Check if already analyzed (skip if not force)
        2. Set status = ANALYZING
        3. Get entity content
        4. Extract edges (references)
        5. Identify missing references
        6. Create placeholders for missing
        7. Create witness mark
        8. Set status = ANALYZED
        9. Emit events

        Args:
            path: Entity path to analyze
            force: Force re-analysis even if already analyzed
            author: Who is requesting the analysis

        Returns:
            AnalysisResult with discovered refs and placeholders
        """
        # 1. Check if already analyzed
        if not force:
            existing_state = await self.store.get_analysis_state(path)
            if existing_state and existing_state.is_complete:
                logger.debug(
                    f"Entity {path} already analyzed (status={existing_state.status.value})"
                )
                return AnalysisResult(
                    path=path,
                    status=existing_state.status,
                    discovered_refs=existing_state.discovered_refs,
                    placeholder_paths=existing_state.placeholder_paths,
                    analysis_mark_id=existing_state.analysis_mark_id,
                )

        # 2. Set status = ANALYZING
        analyzing_state = AnalysisState(
            status=AnalysisStatus.ANALYZING,
            started_at=datetime.now(UTC).isoformat(),
        )
        await self.store.set_analysis_state(path, analyzing_state)

        # Emit ANALYSIS_STARTED event
        if self.bus:
            from services.witness.bus import WitnessTopics

            await self.bus.publish(
                WitnessTopics.SOVEREIGN_ANALYSIS_STARTED,
                {
                    "path": path,
                    "started_at": analyzing_state.started_at,
                    "analyzer": analyzing_state.analyzer,
                },
            )

        try:
            # 3. Get entity content
            entity = await self.store.get_current(path)
            if not entity:
                raise ValueError(f"Entity not found: {path}")

            # 4. Discover references via extract_edges()
            edges = extract_edges(entity.content, path)
            discovered_refs = list({edge.target for edge in edges})

            logger.debug(f"Discovered {len(discovered_refs)} unique refs in {path}")

            # 5. Check which refs don't exist → placeholder_paths
            placeholder_paths = []
            for ref in discovered_refs:
                # Check if ref exists in store
                if not await self.store.exists(ref):
                    placeholder_paths.append(ref)

            logger.debug(f"Found {len(placeholder_paths)} missing refs in {path}")

            # 6. Create placeholders for missing (fully automatic)
            for placeholder_path in placeholder_paths:
                await self._create_placeholder(placeholder_path, source_path=path, author=author)

            # 7. Create witness mark
            mark_id = await self._create_analysis_mark(
                path,
                ref_count=len(discovered_refs),
                placeholder_count=len(placeholder_paths),
                author=author,
            )

            # 8. Set status = ANALYZED
            completed_state = AnalysisState(
                status=AnalysisStatus.ANALYZED,
                started_at=analyzing_state.started_at,
                completed_at=datetime.now(UTC).isoformat(),
                analyzer=analyzing_state.analyzer,
                analysis_mark_id=mark_id,
                discovered_refs=discovered_refs,
                placeholder_paths=placeholder_paths,
            )
            await self.store.set_analysis_state(path, completed_state)

            # 9. Emit ANALYSIS_COMPLETED event
            if self.bus:
                from services.witness.bus import WitnessTopics

                await self.bus.publish(
                    WitnessTopics.SOVEREIGN_ANALYSIS_COMPLETED,
                    {
                        "path": path,
                        "completed_at": completed_state.completed_at,
                        "ref_count": len(discovered_refs),
                        "placeholder_count": len(placeholder_paths),
                        "analysis_mark_id": mark_id,
                    },
                )

            logger.info(
                f"Analysis complete for {path}: {len(discovered_refs)} refs, "
                f"{len(placeholder_paths)} placeholders created"
            )

            return AnalysisResult(
                path=path,
                status=AnalysisStatus.ANALYZED,
                discovered_refs=discovered_refs,
                placeholder_paths=placeholder_paths,
                analysis_mark_id=mark_id,
            )

        except Exception as e:
            # On error: Set status = FAILED, emit ANALYSIS_FAILED
            logger.error(f"Analysis failed for {path}: {e}")

            failed_state = AnalysisState(
                status=AnalysisStatus.FAILED,
                started_at=analyzing_state.started_at,
                completed_at=datetime.now(UTC).isoformat(),
                error=str(e),
            )
            await self.store.set_analysis_state(path, failed_state)

            # Emit ANALYSIS_FAILED event
            if self.bus:
                from services.witness.bus import WitnessTopics

                await self.bus.publish(
                    WitnessTopics.SOVEREIGN_ANALYSIS_FAILED,
                    {
                        "path": path,
                        "error": str(e),
                        "completed_at": failed_state.completed_at,
                    },
                )

            return AnalysisResult(
                path=path,
                status=AnalysisStatus.FAILED,
                error=str(e),
            )

    async def _create_placeholder(
        self,
        placeholder_path: str,
        source_path: str,
        author: str,
    ) -> None:
        """
        Create a placeholder entity for a missing reference.

        Placeholders are sovereign entities with minimal content.
        They're marked in metadata so they can be identified later.

        Args:
            placeholder_path: Path for the placeholder
            source_path: Path of entity that references this
            author: Who is creating the placeholder
        """
        # Create minimal placeholder content
        placeholder_content = f"""# {placeholder_path}

> *Placeholder created by sovereign analysis*

This entity does not yet exist in the source repository.
It was referenced by: `{source_path}`

Status: **PLACEHOLDER**

When the actual content is ingested, this placeholder will be replaced.
"""

        # Store as version 1
        mark_id = await self._create_placeholder_mark(
            placeholder_path,
            source_path=source_path,
            author=author,
        )

        await self.store.store_version(
            path=placeholder_path,
            content=placeholder_content.encode("utf-8"),
            ingest_mark=mark_id,
            metadata={
                "source": f"placeholder:{source_path}",
                "is_placeholder": True,
                "created_from": source_path,
            },
        )

        # Set analysis state as PENDING for placeholder
        # (it can be analyzed later if needed)
        placeholder_state = AnalysisState(status=AnalysisStatus.PENDING)
        await self.store.set_analysis_state(placeholder_path, placeholder_state)

        # Emit PLACEHOLDER_CREATED event
        if self.bus:
            from services.witness.bus import WitnessTopics

            await self.bus.publish(
                WitnessTopics.SOVEREIGN_PLACEHOLDER_CREATED,
                {
                    "path": placeholder_path,
                    "source_path": source_path,
                    "mark_id": mark_id,
                },
            )

        logger.info(f"Created placeholder: {placeholder_path} (referenced by {source_path})")

    async def _create_analysis_mark(
        self,
        path: str,
        ref_count: int,
        placeholder_count: int,
        author: str,
    ) -> str:
        """
        Create witness mark for analysis completion.

        Returns mark ID (or placeholder if no witness).
        """
        if self.witness is None:
            import uuid

            return f"unwitnessed-{uuid.uuid4().hex[:12]}"

        result = await self.witness.save_mark(
            action=f"sovereign.analysis: {path}",
            reasoning=(
                f"Analyzed entity: discovered {ref_count} refs, "
                f"created {placeholder_count} placeholders"
            ),
            principles=["composable"],  # Analysis enables composition
            tags=[
                "analysis",
                "sovereign",
                f"refs:{ref_count}",
                f"placeholders:{placeholder_count}",
            ],
            author=author,
        )

        return result.mark_id

    async def _create_placeholder_mark(
        self,
        placeholder_path: str,
        source_path: str,
        author: str,
    ) -> str:
        """
        Create witness mark for placeholder creation.

        Returns mark ID (or placeholder if no witness).
        """
        if self.witness is None:
            import uuid

            return f"unwitnessed-{uuid.uuid4().hex[:12]}"

        result = await self.witness.save_mark(
            action=f"sovereign.placeholder: {placeholder_path}",
            reasoning=f"Referenced by {source_path} but not yet ingested",
            principles=["composable"],
            tags=[
                "placeholder",
                "sovereign",
                f"source:{source_path}",
            ],
            author=author,
        )

        return result.mark_id


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "SovereignAnalyzer",
]
