"""
AGENTESE Nodes for Crystal Compression and Export.

time.crystal.* paths for crystal operations:
- time.crystal.manifest  - View crystal status
- time.crystal.compress  - Compress trace to crystal
- time.crystal.export    - Export crystal as artifact
- time.crystal.honest    - Show what was dropped

Philosophy:
    "Turn your day into proof of intention."
    "The crystal is honest about what was lost."

See: spec/protocols/witness-crystallization.md
See: pilots/trail-to-crystal-daily-lab.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from protocols.agentese.contract import Contract, Response as ContractResponse
from protocols.agentese.node import BaseLogosNode, BasicRendering, Renderable
from protocols.agentese.registry import node

from .crystal import Crystal, CrystalLevel
from .crystal_compression import (
    CompressionResult,
    CrystalCompressor,
    get_crystal_compressor,
)
from .crystal_export import (
    CrystalExporter,
    ExportedCrystal,
    get_crystal_exporter,
)
from .crystal_store import CrystalStore, get_crystal_store
from .trace_store import MarkStore, get_mark_store

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.agentese.node import Observer

logger = logging.getLogger("kgents.witness.crystal_nodes")


# =============================================================================
# Contracts
# =============================================================================


@dataclass
class CrystalManifestResponse:
    """Response for time.crystal.manifest."""

    today_mark_count: int
    today_crystal_count: int
    compression_available: bool
    last_crystal_date: str | None
    last_coherence: float | None


@dataclass
class CompressRequest:
    """Request for time.crystal.compress."""

    date: str | None = None  # ISO date, defaults to today
    max_ratio: float = 0.10  # Target compression ratio


@dataclass
class CompressResponse:
    """Response for time.crystal.compress."""

    success: bool
    crystal_id: str | None
    compression_ratio: float
    preserved_count: int
    dropped_count: int
    causal_chain_summary: str
    honest_disclosure: str
    meets_target: bool
    quality_tier: str


@dataclass
class ExportRequest:
    """Request for time.crystal.export."""

    crystal_id: str | None = None  # Specific crystal, defaults to latest
    format: str = "markdown"  # "markdown", "image", "url"
    date: str | None = None  # ISO date for date-based lookup


@dataclass
class ExportResponse:
    """Response for time.crystal.export."""

    success: bool
    format: str
    content: str | None  # For markdown
    path: str | None  # For image
    url: str | None  # For url


@dataclass
class HonestRequest:
    """Request for time.crystal.honest."""

    crystal_id: str | None = None  # Specific crystal
    date: str | None = None  # ISO date


@dataclass
class HonestResponse:
    """Response for time.crystal.honest showing what was dropped."""

    crystal_id: str | None
    dropped_count: int
    dropped_reasons: list[dict[str, Any]]
    honest_gaps: list[dict[str, Any]]
    warm_disclosure: str
    galois_loss: float
    quality_tier: str


# =============================================================================
# AGENTESE Node
# =============================================================================


@node(
    "time.crystal",
    description="Crystal Compression - Turn your day into proof of intention",
    contracts={
        "manifest": ContractResponse(CrystalManifestResponse),
        "compress": Contract(CompressRequest, CompressResponse),
        "export": Contract(ExportRequest, ExportResponse),
        "honest": Contract(HonestRequest, HonestResponse),
    },
    examples=[
        ("manifest", {}, "Get crystal status"),
        ("compress", {}, "Compress today's marks to crystal"),
        ("compress", {"max_ratio": 0.05}, "Aggressive compression"),
        ("export", {"format": "markdown"}, "Export latest crystal as markdown"),
        ("export", {"format": "image"}, "Export as shareable image"),
        ("honest", {}, "Show what was dropped in latest crystal"),
    ],
)
class TimeCrystalNode(BaseLogosNode):
    """
    AGENTESE node for Crystal Compression operations.

    Exposes crystal compression and export through the universal protocol.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Key Operations:
    - compress: Compress marks to crystal with <10% ratio target
    - export: Export crystal as shareable artifact
    - honest: Show what was dropped (Amendment G compliance)

    Example:
        # Via AGENTESE gateway
        POST /agentese/time/crystal/compress
        {"max_ratio": 0.10}

        # Via Logos directly
        await logos.invoke("time.crystal.compress", observer)

        # Via CLI
        kgents time crystal compress
    """

    def __init__(
        self,
        mark_store: MarkStore | None = None,
        crystal_store: CrystalStore | None = None,
        compressor: CrystalCompressor | None = None,
        exporter: CrystalExporter | None = None,
    ) -> None:
        """
        Initialize TimeCrystalNode.

        Args:
            mark_store: The mark store (optional)
            crystal_store: The crystal store (optional)
            compressor: The crystal compressor (optional)
            exporter: The crystal exporter (optional)
        """
        self._mark_store = mark_store
        self._crystal_store = crystal_store
        self._compressor = compressor
        self._exporter = exporter

        # Cache for latest compression result (for honesty queries)
        self._last_compression: CompressionResult | None = None

    @property
    def mark_store(self) -> MarkStore:
        """Get the mark store."""
        if self._mark_store is None:
            self._mark_store = get_mark_store()
        return self._mark_store

    @property
    def crystal_store(self) -> CrystalStore:
        """Get the crystal store."""
        if self._crystal_store is None:
            self._crystal_store = get_crystal_store()
        return self._crystal_store

    @property
    def compressor(self) -> CrystalCompressor:
        """Get the crystal compressor."""
        if self._compressor is None:
            self._compressor = get_crystal_compressor()
        return self._compressor

    @property
    def exporter(self) -> CrystalExporter:
        """Get the crystal exporter."""
        if self._exporter is None:
            self._exporter = get_crystal_exporter()
        return self._exporter

    @property
    def handle(self) -> str:
        return "time.crystal"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Return archetype-specific affordances."""
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access for developers and operators
        if archetype_lower in (
            "developer",
            "operator",
            "admin",
            "system",
            "architect",
            "researcher",
        ):
            return ("manifest", "compress", "export", "honest")

        # Newcomers can view but not compress
        if archetype_lower in ("newcomer", "casual", "reviewer"):
            return ("manifest", "export", "honest")

        # Guest: minimal
        return ("manifest",)

    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest crystal status to observer.

        AGENTESE: time.crystal.manifest
        """
        today = date.today()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())

        # Count today's marks
        today_marks = [m for m in self.mark_store.all() if start <= m.timestamp <= end]

        # Count crystals for today
        today_crystals = [
            c for c in self.crystal_store.all() if c.time_range and c.time_range[0].date() == today
        ]

        # Get last crystal info
        all_crystals = list(self.crystal_store.all())
        last_crystal = max(all_crystals, key=lambda c: c.crystallized_at) if all_crystals else None

        return BasicRendering(
            summary=f"Crystal status: {len(today_marks)} marks today, {len(today_crystals)} crystals",
            content=(
                f"Marks available for compression: {len(today_marks)}\n"
                f"Compression available: {len(today_marks) >= 3}\n"
                f"Last crystal: {last_crystal.crystallized_at.date() if last_crystal else 'None'}"
            ),
            metadata={
                "today_mark_count": len(today_marks),
                "today_crystal_count": len(today_crystals),
                "compression_available": len(today_marks) >= 3,
                "last_crystal_date": (
                    last_crystal.crystallized_at.date().isoformat() if last_crystal else None
                ),
                "last_coherence": last_crystal.confidence if last_crystal else None,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Observer | Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to handlers."""
        if aspect == "compress":
            return await self._handle_compress(kwargs)
        elif aspect == "export":
            return await self._handle_export(kwargs)
        elif aspect == "honest":
            return await self._handle_honest(kwargs)
        else:
            return {"error": f"Unknown aspect: {aspect}"}

    async def _handle_compress(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle compress aspect - compress marks to crystal."""
        date_str = kwargs.get("date")
        max_ratio = kwargs.get("max_ratio", 0.10)

        # Parse date
        target_date = date.today()
        if date_str:
            try:
                target_date = date.fromisoformat(date_str)
            except ValueError:
                return {"error": f"Invalid date format: {date_str}. Use ISO format (YYYY-MM-DD)"}

        # Get marks for date
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date, datetime.max.time())

        marks = [m for m in self.mark_store.all() if start <= m.timestamp <= end]

        if len(marks) < 3:
            return {
                "success": False,
                "crystal_id": None,
                "compression_ratio": 0.0,
                "preserved_count": 0,
                "dropped_count": 0,
                "causal_chain_summary": "",
                "honest_disclosure": "Not enough marks to compress (need at least 3).",
                "meets_target": False,
                "quality_tier": "needs_work",
            }

        # Compress
        try:
            result = await self.compressor.compress(
                marks=marks,
                max_ratio=max_ratio,
                session_id=f"day-{target_date.isoformat()}",
            )

            # Store the crystal
            self.crystal_store.append(result.crystal)

            # Cache for honesty queries
            self._last_compression = result

            return {
                "success": True,
                "crystal_id": str(result.crystal.id),
                "compression_ratio": result.compression_ratio,
                "preserved_count": result.preserved_count,
                "dropped_count": result.dropped_count,
                "causal_chain_summary": result.chain_summary,
                "honest_disclosure": result.honesty.warm_disclosure,
                "meets_target": result.meets_target,
                "quality_tier": result.quality_tier,
            }
        except Exception as e:
            logger.error(f"Compression failed: {e}")
            return {
                "success": False,
                "crystal_id": None,
                "compression_ratio": 0.0,
                "preserved_count": 0,
                "dropped_count": 0,
                "causal_chain_summary": "",
                "honest_disclosure": f"Compression failed: {e}",
                "meets_target": False,
                "quality_tier": "error",
            }

    async def _handle_export(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle export aspect - export crystal as artifact."""
        crystal_id = kwargs.get("crystal_id")
        format_str = kwargs.get("format", "markdown")
        date_str = kwargs.get("date")

        # Validate format
        if format_str not in ("markdown", "image", "url"):
            return {
                "success": False,
                "format": format_str,
                "content": None,
                "path": None,
                "url": None,
                "error": f"Invalid format: {format_str}. Valid: markdown, image, url",
            }

        # Find crystal
        crystal: Crystal | None = None

        if crystal_id:
            crystal = self.crystal_store.get(crystal_id)
        elif date_str:
            target_date = date.fromisoformat(date_str)
            for c in self.crystal_store.all():
                if c.time_range and c.time_range[0].date() == target_date:
                    crystal = c
                    break
        else:
            # Get latest
            all_crystals = list(self.crystal_store.all())
            if all_crystals:
                crystal = max(all_crystals, key=lambda c: c.crystallized_at)

        if not crystal:
            return {
                "success": False,
                "format": format_str,
                "content": None,
                "path": None,
                "url": None,
                "error": "No crystal found",
            }

        # Export based on format
        try:
            if format_str == "markdown":
                content = await self.exporter.export_as_markdown(crystal, self._last_compression)
                return {
                    "success": True,
                    "format": format_str,
                    "content": content,
                    "path": None,
                    "url": None,
                }
            elif format_str == "image":
                path = await self.exporter.export_as_image(
                    crystal, compression_result=self._last_compression
                )
                return {
                    "success": True,
                    "format": format_str,
                    "content": None,
                    "path": str(path),
                    "url": None,
                }
            elif format_str == "url":
                url = await self.exporter.export_as_url(crystal, self._last_compression)
                return {
                    "success": True,
                    "format": format_str,
                    "content": None,
                    "path": None,
                    "url": url,
                }
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return {
                "success": False,
                "format": format_str,
                "content": None,
                "path": None,
                "url": None,
                "error": str(e),
            }

        return {"success": False, "format": format_str, "error": "Unexpected state"}

    async def _handle_honest(self, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Handle honest aspect - show what was dropped."""
        crystal_id = kwargs.get("crystal_id")
        date_str = kwargs.get("date")

        # If we have a cached compression result, use it
        if self._last_compression:
            return {
                "crystal_id": str(self._last_compression.crystal.id),
                "dropped_count": self._last_compression.dropped_count,
                "dropped_reasons": [r.to_dict() for r in self._last_compression.dropped_reasons],
                "honest_gaps": [g.to_dict() for g in self._last_compression.honest_gaps],
                "warm_disclosure": self._last_compression.honesty.warm_disclosure,
                "galois_loss": self._last_compression.honesty.galois_loss,
                "quality_tier": self._last_compression.honesty.quality_tier,
            }

        # Otherwise, get from crystal metadata
        crystal: Crystal | None = None

        if crystal_id:
            crystal = self.crystal_store.get(crystal_id)
        elif date_str:
            target_date = date.fromisoformat(date_str)
            for c in self.crystal_store.all():
                if c.time_range and c.time_range[0].date() == target_date:
                    crystal = c
                    break
        else:
            # Get latest
            all_crystals = list(self.crystal_store.all())
            if all_crystals:
                crystal = max(all_crystals, key=lambda c: c.crystallized_at)

        if not crystal:
            return {
                "crystal_id": None,
                "dropped_count": 0,
                "dropped_reasons": [],
                "honest_gaps": [],
                "warm_disclosure": "No crystal found to analyze.",
                "galois_loss": 0.0,
                "quality_tier": "unknown",
            }

        # Build response from crystal metadata
        return {
            "crystal_id": str(crystal.id),
            "dropped_count": 0,  # Not available without compression result
            "dropped_reasons": [],
            "honest_gaps": [],
            "warm_disclosure": (
                f"This crystal was created with {crystal.confidence:.0%} confidence. "
                f"It preserves {crystal.source_count} source marks."
            ),
            "galois_loss": 1.0 - crystal.confidence,
            "quality_tier": (
                "excellent"
                if crystal.confidence > 0.9
                else "good"
                if crystal.confidence > 0.7
                else "moderate"
            ),
        }


# =============================================================================
# Factory Functions
# =============================================================================


_node: TimeCrystalNode | None = None


def get_time_crystal_node() -> TimeCrystalNode:
    """Get the singleton TimeCrystalNode instance."""
    global _node
    if _node is None:
        _node = TimeCrystalNode()
    return _node


def reset_time_crystal_node() -> None:
    """Reset the singleton (for testing)."""
    global _node
    _node = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Contracts
    "CrystalManifestResponse",
    "CompressRequest",
    "CompressResponse",
    "ExportRequest",
    "ExportResponse",
    "HonestRequest",
    "HonestResponse",
    # Node
    "TimeCrystalNode",
    "get_time_crystal_node",
    "reset_time_crystal_node",
]
