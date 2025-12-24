"""
Analysis Reactor: Auto-triggers LLM analysis on document ingest.

> *"The reactor listens. When a document crosses the membrane, analysis begins."*

This reactor bridges the gap between ingest and analysis:

    SOVEREIGN_INGESTED ──publish──> AnalysisReactor._on_ingested()
                                             │
                                             │ if .md file
                                             ▼
                                    LLM Analyzer (Claude)
                                             │
                                             ├─► SOVEREIGN_ANALYSIS_STARTED
                                             ├─► Update analysis state
                                             ├─► Create witness mark
                                             ├─► Store crystal in overlay
                                             ├─► SOVEREIGN_ANALYSIS_COMPLETED
                                             └─► (or FAILED on error)

The Missing Piece:
    Before this reactor, SOVEREIGN_INGESTED was emitted but nothing listened.
    Now, every markdown document is automatically analyzed upon ingest.

Teaching:
    gotcha: Only .md files are analyzed. Other file types may need different analyzers.

    gotcha: The LLM analyzer (llm_analyzer.py) is optional. If not available,
            analysis is skipped gracefully with a log message.

    gotcha: Error handling is critical. The reactor must NEVER crash on failure.
            Failed analyses set status=FAILED and emit ANALYSIS_FAILED event.

See: spec/protocols/inbound-sovereignty.md
See: plans/claude-document-analysis.md
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Callable

from .analysis import AnalysisResult, AnalysisState, AnalysisStatus
from .store import SovereignStore

if TYPE_CHECKING:
    from services.witness.bus import WitnessSynergyBus
    from services.witness.persistence import WitnessPersistence

logger = logging.getLogger(__name__)


# Type alias for unsubscribe functions
UnsubscribeFunc = Callable[[], None]


# =============================================================================
# Analysis Crystal (placeholder until llm_analyzer.py is implemented)
# =============================================================================


class AnalysisCrystal:
    """
    Result of LLM analysis on a document.

    This is a placeholder dataclass until the full llm_analyzer.py is implemented.
    The real AnalysisCrystal will contain:
    - Discovered references (internal links, external deps)
    - Suggested connections to other documents
    - Extracted concepts and terms
    - Summary and categorization

    For Phase 2, we use structural analysis as a fallback.
    """

    def __init__(
        self,
        path: str,
        refs_found: list[str] | None = None,
        connections_suggested: list[dict[str, Any]] | None = None,
        concepts: list[str] | None = None,
        summary: str | None = None,
        analyzer: str = "structural_v1",
    ) -> None:
        self.path = path
        self.refs_found = refs_found or []
        self.connections_suggested = connections_suggested or []
        self.concepts = concepts or []
        self.summary = summary or ""
        self.analyzer = analyzer
        self.analyzed_at = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "path": self.path,
            "refs_found": self.refs_found,
            "connections_suggested": self.connections_suggested,
            "concepts": self.concepts,
            "summary": self.summary,
            "analyzer": self.analyzer,
            "analyzed_at": self.analyzed_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AnalysisCrystal":
        """Create from dictionary."""
        crystal = cls(
            path=data.get("path", ""),
            refs_found=data.get("refs_found", []),
            connections_suggested=data.get("connections_suggested", []),
            concepts=data.get("concepts", []),
            summary=data.get("summary", ""),
            analyzer=data.get("analyzer", "structural_v1"),
        )
        crystal.analyzed_at = data.get("analyzed_at", datetime.now(UTC).isoformat())
        return crystal


# =============================================================================
# Fallback Structural Analyzer
# =============================================================================


async def analyze_structural(content: str, path: str) -> AnalysisCrystal:
    """
    Fallback structural analysis when LLM is not available.

    Extracts references and structure from markdown using regex patterns.
    This is a simple but effective analysis for Phase 2.

    Args:
        content: The document content
        path: The document path

    Returns:
        AnalysisCrystal with discovered refs
    """
    import re

    refs_found: list[str] = []
    concepts: list[str] = []

    # Extract markdown links
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    for match in link_pattern.finditer(content):
        target = match.group(2)
        if not target.startswith(('http://', 'https://', '#')):
            refs_found.append(target)

    # Extract code block languages (indicators of deps)
    code_pattern = re.compile(r'```(\w+)')
    for match in code_pattern.finditer(content):
        lang = match.group(1)
        if lang and lang not in concepts:
            concepts.append(lang)

    # Extract headings as concepts
    heading_pattern = re.compile(r'^#{1,3}\s+(.+)$', re.MULTILINE)
    for match in heading_pattern.finditer(content):
        heading = match.group(1).strip()
        if heading and len(heading) < 50:  # Reasonable concept length
            concepts.append(heading)

    # Create a basic summary (first non-empty line that isn't a heading)
    summary = ""
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped and not stripped.startswith('#') and not stripped.startswith('```'):
            summary = stripped[:200]  # Cap at 200 chars
            break

    return AnalysisCrystal(
        path=path,
        refs_found=refs_found,
        connections_suggested=[],  # Structural analysis doesn't suggest connections
        concepts=concepts[:20],  # Limit concepts
        summary=summary,
        analyzer="structural_v1",
    )


async def analyze_with_claude(content: str, path: str) -> AnalysisCrystal:
    """
    Analyze document with Claude LLM.

    This function attempts to use the LLM analyzer if available,
    falling back to structural analysis if not.

    Args:
        content: The document content
        path: The document path

    Returns:
        AnalysisCrystal with analysis results
    """
    try:
        # Try to import the LLM analyzer (Phase 1 component)
        # Note: llm_analyzer.py is implemented in Phase 1, not yet available
        from .llm_analyzer import analyze_document  # type: ignore[attr-defined]

        result: AnalysisCrystal = await analyze_document(content, path)
        return result
    except ImportError:
        # LLM analyzer not yet implemented, use structural fallback
        logger.debug(f"LLM analyzer not available, using structural analysis for {path}")
        return await analyze_structural(content, path)
    except Exception as e:
        # Any other error, fall back to structural
        logger.warning(f"LLM analysis failed for {path}, using structural: {e}")
        return await analyze_structural(content, path)


# =============================================================================
# Analysis Reactor
# =============================================================================


class AnalysisReactor:
    """
    Listens to SOVEREIGN_INGESTED and auto-triggers LLM analysis.

    The missing piece: connects ingest -> analysis automatically.

    When a document is ingested:
    1. If it's a .md file, trigger analysis
    2. Update status throughout (ANALYZING -> ANALYZED/FAILED)
    3. Emit events for frontend feedback
    4. Create witness marks for traceability

    Example:
        store = SovereignStore()
        reactor = AnalysisReactor(store, witness, bus)

        # Later: Document ingested...
        # -> reactor receives SOVEREIGN_INGESTED
        # -> emits SOVEREIGN_ANALYSIS_STARTED
        # -> runs Claude analysis
        # -> stores crystal in overlay
        # -> emits SOVEREIGN_ANALYSIS_COMPLETED
    """

    def __init__(
        self,
        store: SovereignStore,
        witness: "WitnessPersistence | None" = None,
        bus: "WitnessSynergyBus | None" = None,
    ) -> None:
        """
        Initialize the analysis reactor.

        Args:
            store: Sovereign store for entity access
            witness: Optional witness for creating marks
            bus: Optional bus for event pub/sub (uses global if None)
        """
        self.store = store
        self.witness = witness
        self._bus = bus
        self._unsubscribe: UnsubscribeFunc | None = None
        self._is_running = False
        self._analysis_count = 0
        self._error_count = 0

        # Auto-subscribe on init
        self._subscribe()

    def _get_bus(self) -> "WitnessSynergyBus | None":
        """Get the bus, using global if not provided."""
        if self._bus is not None:
            return self._bus

        try:
            from services.witness.bus import get_synergy_bus
            return get_synergy_bus()
        except ImportError:
            logger.warning("WitnessSynergyBus not available")
            return None

    def _subscribe(self) -> None:
        """Subscribe to SOVEREIGN_INGESTED events."""
        if self._is_running:
            return

        bus = self._get_bus()
        if bus is None:
            logger.warning("Cannot subscribe: bus not available")
            return

        try:
            from services.witness.bus import WitnessTopics
            self._unsubscribe = bus.subscribe(
                WitnessTopics.SOVEREIGN_INGESTED,
                self._on_ingested,
            )
            self._is_running = True
            logger.info("AnalysisReactor subscribed to SOVEREIGN_INGESTED")
        except Exception as e:
            logger.error(f"Failed to subscribe to SOVEREIGN_INGESTED: {e}")

    async def _on_ingested(self, topic: str, event: dict[str, Any]) -> None:
        """
        Handle SOVEREIGN_INGESTED event.

        Triggers analysis for .md files.

        Args:
            topic: The event topic
            event: The event payload with path, version, etc.
        """
        path = event.get("path", "")

        # Only analyze markdown files
        if not path.endswith(".md"):
            logger.debug(f"Skipping non-markdown file: {path}")
            return

        logger.info(f"Analysis triggered for: {path}")

        try:
            await self._run_analysis(path, event)
        except Exception as e:
            logger.error(f"Analysis failed for {path}: {e}")
            self._error_count += 1
            await self._handle_failure(path, str(e))

    async def _run_analysis(self, path: str, event: dict[str, Any]) -> None:
        """
        Run the full analysis flow.

        1. Set status = ANALYZING
        2. Emit ANALYSIS_STARTED
        3. Get entity content
        4. Run LLM analysis
        5. Create witness mark
        6. Store crystal in overlay
        7. Set status = ANALYZED
        8. Emit ANALYSIS_COMPLETED
        """
        bus = self._get_bus()

        # 1. Set status = ANALYZING
        started_at = datetime.now(UTC).isoformat()
        analyzing_state = AnalysisState(
            status=AnalysisStatus.ANALYZING,
            started_at=started_at,
            analyzer="claude",
        )
        await self.store.set_analysis_state(path, analyzing_state)

        # 2. Emit ANALYSIS_STARTED
        if bus:
            try:
                from services.witness.bus import WitnessTopics
                await bus.publish(
                    WitnessTopics.SOVEREIGN_ANALYSIS_STARTED,
                    {
                        "path": path,
                        "started_at": started_at,
                        "analyzer": "claude",
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to emit ANALYSIS_STARTED: {e}")

        # 3. Get entity content
        entity = await self.store.get_current(path)
        if not entity:
            raise ValueError(f"Entity not found: {path}")

        try:
            content = entity.content.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError(f"Could not decode {path} as UTF-8")

        # 4. Run LLM analysis
        crystal = await analyze_with_claude(content, path)

        # 5. Create witness mark
        mark_id: str | None = None
        if self.witness:
            try:
                mark_result = await self.witness.save_mark(
                    action=f"claude.analysis: {path}",
                    reasoning=(
                        f"LLM analysis found {len(crystal.refs_found)} refs, "
                        f"suggested {len(crystal.connections_suggested)} connections"
                    ),
                    principles=["generative"],
                    author="claude",
                    tags=["analysis:claude", f"path:{path}"],
                )
                mark_id = mark_result.mark_id
            except Exception as e:
                logger.warning(f"Failed to create witness mark: {e}")

        # 6. Store crystal in overlay
        await self.store.store_overlay(path, "analysis_crystal", crystal.to_dict())

        # 7. Set status = ANALYZED
        completed_at = datetime.now(UTC).isoformat()
        analyzed_state = AnalysisState(
            status=AnalysisStatus.ANALYZED,
            started_at=started_at,
            completed_at=completed_at,
            analyzer=crystal.analyzer,
            analysis_mark_id=mark_id,
            discovered_refs=crystal.refs_found,
        )
        await self.store.set_analysis_state(path, analyzed_state)

        self._analysis_count += 1

        # 8. Emit ANALYSIS_COMPLETED
        if bus:
            try:
                from services.witness.bus import WitnessTopics
                await bus.publish(
                    WitnessTopics.SOVEREIGN_ANALYSIS_COMPLETED,
                    {
                        "path": path,
                        "mark_id": mark_id,
                        "refs_found": len(crystal.refs_found),
                        "connections_suggested": len(crystal.connections_suggested),
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to emit ANALYSIS_COMPLETED: {e}")

        logger.info(f"Analysis completed for {path}: {len(crystal.refs_found)} refs found")

    async def _handle_failure(self, path: str, error: str) -> None:
        """
        Handle analysis failure.

        Sets status to FAILED and emits ANALYSIS_FAILED event.
        """
        bus = self._get_bus()

        # Set status = FAILED
        try:
            failed_state = AnalysisState(
                status=AnalysisStatus.FAILED,
                started_at=datetime.now(UTC).isoformat(),
                completed_at=datetime.now(UTC).isoformat(),
                error=error,
            )
            await self.store.set_analysis_state(path, failed_state)
        except Exception as e:
            logger.error(f"Failed to set FAILED state for {path}: {e}")

        # Emit ANALYSIS_FAILED
        if bus:
            try:
                from services.witness.bus import WitnessTopics
                await bus.publish(
                    WitnessTopics.SOVEREIGN_ANALYSIS_FAILED,
                    {
                        "path": path,
                        "error": error,
                    },
                )
            except Exception as e:
                logger.warning(f"Failed to emit ANALYSIS_FAILED: {e}")

    async def analyze(self, path: str, force: bool = False) -> AnalysisCrystal:
        """
        Manually trigger analysis for a path.

        Used by re-analyze button in frontend.

        Args:
            path: The entity path to analyze
            force: If True, analyze even if already analyzed

        Returns:
            AnalysisCrystal with analysis results

        Raises:
            ValueError: If entity not found or already analyzed (and not force)
        """
        # Check if entity exists
        entity = await self.store.get_current(path)
        if not entity:
            raise ValueError(f"Entity not found: {path}")

        # Check if already analyzed (unless force)
        if not force:
            state = await self.store.get_analysis_state(path)
            if state and state.status == AnalysisStatus.ANALYZED:
                # Return existing crystal
                overlay = await self.store.get_overlay(path, "analysis_crystal")
                if overlay:
                    return AnalysisCrystal.from_dict(overlay)

        # Run analysis
        event = {
            "path": path,
            "version": entity.version,
            "edge_count": 0,
            "ingest_mark_id": entity.ingest_mark_id,
        }

        await self._run_analysis(path, event)

        # Return the crystal
        overlay = await self.store.get_overlay(path, "analysis_crystal")
        if overlay:
            return AnalysisCrystal.from_dict(overlay)

        raise ValueError(f"Analysis completed but crystal not found for {path}")

    def shutdown(self) -> None:
        """Unsubscribe from bus and clean up."""
        if self._unsubscribe:
            try:
                self._unsubscribe()
            except Exception as e:
                logger.warning(f"Error during unsubscribe: {e}")

        self._unsubscribe = None
        self._is_running = False
        logger.info("AnalysisReactor shutdown")

    @property
    def stats(self) -> dict[str, Any]:
        """Get reactor statistics."""
        return {
            "is_running": self._is_running,
            "analysis_count": self._analysis_count,
            "error_count": self._error_count,
        }


# =============================================================================
# Factory Function
# =============================================================================


async def create_analysis_reactor(
    store: SovereignStore,
    witness: "WitnessPersistence | None" = None,
) -> AnalysisReactor:
    """
    Create and wire analysis reactor.

    Factory function for app startup.

    Args:
        store: Sovereign store for entity access
        witness: Optional witness for creating marks

    Returns:
        Configured AnalysisReactor instance

    Example:
        store = SovereignStore()
        witness = WitnessPersistence()
        reactor = await create_analysis_reactor(store, witness)

        # Reactor is now listening for SOVEREIGN_INGESTED events
    """
    reactor = AnalysisReactor(store=store, witness=witness)
    return reactor


# =============================================================================
# Global Reactor Instance
# =============================================================================

_reactor: AnalysisReactor | None = None


def get_analysis_reactor() -> AnalysisReactor | None:
    """
    Get the global AnalysisReactor instance.

    Returns None if not initialized. Use create_analysis_reactor() first.
    """
    return _reactor


async def init_analysis_reactor(
    store: SovereignStore,
    witness: "WitnessPersistence | None" = None,
) -> AnalysisReactor:
    """
    Initialize the global AnalysisReactor.

    Should be called once at app startup.
    """
    global _reactor
    if _reactor is not None:
        logger.warning("AnalysisReactor already initialized, shutting down old instance")
        _reactor.shutdown()

    _reactor = await create_analysis_reactor(store, witness)
    return _reactor


def reset_analysis_reactor() -> None:
    """Reset the global reactor (for testing)."""
    global _reactor
    if _reactor is not None:
        _reactor.shutdown()
    _reactor = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Core class
    "AnalysisReactor",
    # Factory
    "create_analysis_reactor",
    # Global instance
    "get_analysis_reactor",
    "init_analysis_reactor",
    "reset_analysis_reactor",
    # Types
    "AnalysisCrystal",
    # Analyzers
    "analyze_with_claude",
    "analyze_structural",
]
