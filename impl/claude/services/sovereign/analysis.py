"""
Analysis State: Track analysis status for sovereign entities.

> *"Every entity deserves analysis. Every analysis reveals references."*

This module defines the state machine for sovereign entity analysis:

    PENDING → ANALYZING → ANALYZED
                ↓
              FAILED

The analysis state is stored in the overlay as `analysis.json` and tracks:
- Current status
- Timestamps (started, completed)
- Analysis results (discovered refs, placeholders created)
- Witness mark linkage

Teaching:
    gotcha: Analysis state is stored in overlay, NOT in metadata.
            Metadata is for versioning, overlay is for derived data.

    gotcha: discovered_refs can point to paths that don't exist yet.
            These become placeholders, created automatically during analysis.

See: spec/protocols/inbound-sovereignty.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

# =============================================================================
# Analysis Status
# =============================================================================


class AnalysisStatus(Enum):
    """Status of entity analysis."""

    PENDING = "pending"  # Ingested, not yet analyzed
    ANALYZING = "analyzing"  # Analysis in progress
    ANALYZED = "analyzed"  # Analysis complete
    FAILED = "failed"  # Analysis failed
    STALE = "stale"  # Deprecated, needs re-analysis


# =============================================================================
# Analysis State
# =============================================================================


@dataclass
class AnalysisState:
    """
    Analysis state for a sovereign entity.

    Stored in overlay/analysis.json for each entity.

    Fields:
        status: Current analysis status
        started_at: When analysis started (ISO timestamp)
        completed_at: When analysis completed (ISO timestamp)
        error: Error message if failed
        analyzer: Analyzer version used (e.g., "structural_v1")
        analysis_mark_id: Witness mark for analysis completion
        discovered_refs: List of paths discovered in content
        placeholder_paths: List of placeholders created for missing refs
    """

    status: AnalysisStatus = AnalysisStatus.PENDING
    started_at: str | None = None
    completed_at: str | None = None
    error: str | None = None
    analyzer: str = "structural_v1"
    analysis_mark_id: str | None = None
    discovered_refs: list[str] = field(default_factory=list)
    placeholder_paths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON storage."""
        return {
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error": self.error,
            "analyzer": self.analyzer,
            "analysis_mark_id": self.analysis_mark_id,
            "discovered_refs": self.discovered_refs,
            "placeholder_paths": self.placeholder_paths,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AnalysisState":
        """Create from dictionary (from JSON storage)."""
        return cls(
            status=AnalysisStatus(data.get("status", "pending")),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            error=data.get("error"),
            analyzer=data.get("analyzer", "structural_v1"),
            analysis_mark_id=data.get("analysis_mark_id"),
            discovered_refs=data.get("discovered_refs", []),
            placeholder_paths=data.get("placeholder_paths", []),
        )

    @property
    def is_complete(self) -> bool:
        """Check if analysis is complete (successful or failed)."""
        return self.status in (AnalysisStatus.ANALYZED, AnalysisStatus.FAILED)

    @property
    def is_successful(self) -> bool:
        """Check if analysis completed successfully."""
        return self.status == AnalysisStatus.ANALYZED

    @property
    def placeholder_count(self) -> int:
        """Number of placeholders created."""
        return len(self.placeholder_paths)

    @property
    def ref_count(self) -> int:
        """Number of references discovered."""
        return len(self.discovered_refs)


# =============================================================================
# Analysis Result
# =============================================================================


@dataclass
class AnalysisResult:
    """
    Result of an analysis operation.

    Returned by SovereignAnalyzer.analyze().

    Fields:
        path: Entity path
        status: Final status
        discovered_refs: List of paths discovered
        placeholder_paths: List of placeholders created
        analysis_mark_id: Witness mark ID
        error: Error message if failed
    """

    path: str
    status: AnalysisStatus
    discovered_refs: list[str] = field(default_factory=list)
    placeholder_paths: list[str] = field(default_factory=list)
    analysis_mark_id: str | None = None
    error: str | None = None

    @property
    def is_successful(self) -> bool:
        """Check if analysis succeeded."""
        return self.status == AnalysisStatus.ANALYZED

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "path": self.path,
            "status": self.status.value,
            "discovered_refs": self.discovered_refs,
            "placeholder_paths": self.placeholder_paths,
            "analysis_mark_id": self.analysis_mark_id,
            "error": self.error,
            "ref_count": len(self.discovered_refs),
            "placeholder_count": len(self.placeholder_paths),
        }


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "AnalysisStatus",
    "AnalysisState",
    "AnalysisResult",
]
