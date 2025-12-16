"""
Atelier Gestalt Integration: Code analysis for artifacts.

Wave 2: Extensions - Atelier uses Gestalt for code analysis.

When a builder creates a code artifact in the Atelier, this module
provides Gestalt-powered analysis of the code's health metrics.

This enables:
- Real-time code quality feedback during creation
- Health grades displayed in artifact cards
- Drift detection for created code
- Architecture alignment suggestions

Usage:
    from agents.atelier.gestalt_integration import (
        analyze_artifact_code,
        GestaltArtifactAnalysis,
    )

    # Analyze code from an artifact
    analysis = await analyze_artifact_code(
        code="class MyService:\\n    ...",
        language="python",
    )

    print(f"Health: {analysis.grade} ({analysis.score:.0%})")
    print(f"Issues: {len(analysis.issues)}")
"""

from __future__ import annotations

import asyncio
import logging
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.atelier.artisan import Piece
    from protocols.gestalt.analysis import Module, ModuleHealth

logger = logging.getLogger(__name__)


# =============================================================================
# Analysis Result Types
# =============================================================================


@dataclass(frozen=True)
class CodeIssue:
    """A code quality issue detected by Gestalt."""

    severity: str  # "error", "warning", "info"
    category: str  # "coupling", "cohesion", "drift", "complexity"
    message: str
    line: int | None = None
    suggestion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "severity": self.severity,
            "category": self.category,
            "message": self.message,
            "line": self.line,
            "suggestion": self.suggestion,
        }


@dataclass
class GestaltArtifactAnalysis:
    """
    Result of analyzing an artifact's code with Gestalt.

    This provides:
    - Health grade (A+ to F)
    - Overall score (0.0 to 1.0)
    - Detailed metrics (coupling, cohesion, complexity, drift)
    - Detected issues with suggestions
    """

    # Core metrics
    grade: str = "?"
    score: float = 0.0

    # Detailed metrics (0.0 to 1.0, higher is worse for negatives)
    coupling: float = 0.0  # How tangled with other code
    cohesion: float = 1.0  # How focused (higher is better)
    complexity: float = 0.0  # Cyclomatic complexity normalized
    drift: float = 0.0  # Governance violations

    # Lines of code
    lines_of_code: int = 0

    # Detected issues
    issues: list[CodeIssue] = field(default_factory=list)

    # Raw module data (for advanced usage)
    raw_module: "Module | None" = None

    @property
    def is_healthy(self) -> bool:
        """Check if the code is considered healthy (B+ or better)."""
        return self.grade in ("A+", "A", "A-", "B+", "B")

    @property
    def needs_attention(self) -> bool:
        """Check if the code needs attention (C or worse)."""
        return self.grade in ("C+", "C", "C-", "D+", "D", "D-", "F")

    def to_dict(self) -> dict[str, Any]:
        return {
            "grade": self.grade,
            "score": round(self.score, 2),
            "coupling": round(self.coupling, 2),
            "cohesion": round(self.cohesion, 2),
            "complexity": round(self.complexity, 2),
            "drift": round(self.drift, 2),
            "lines_of_code": self.lines_of_code,
            "is_healthy": self.is_healthy,
            "needs_attention": self.needs_attention,
            "issues": [i.to_dict() for i in self.issues],
        }

    def to_cli(self) -> str:
        """Format for CLI display."""
        lines = [
            f"Health Grade: {self.grade} ({self.score:.0%})",
            f"  Coupling:   {self._bar(self.coupling)} ({self.coupling:.0%})",
            f"  Cohesion:   {self._bar(self.cohesion)} ({self.cohesion:.0%})",
            f"  Complexity: {self._bar(self.complexity)} ({self.complexity:.0%})",
            f"  Drift:      {self._bar(self.drift)} ({self.drift:.0%})",
            f"  LOC:        {self.lines_of_code}",
        ]

        if self.issues:
            lines.append("")
            lines.append(f"Issues ({len(self.issues)}):")
            for issue in self.issues[:5]:
                marker = "!" if issue.severity == "error" else "~"
                lines.append(f"  {marker} {issue.message}")
                if issue.suggestion:
                    lines.append(f"    Suggestion: {issue.suggestion}")

        return "\n".join(lines)

    def _bar(self, value: float, width: int = 10) -> str:
        """Create a progress bar for a metric."""
        filled = int(value * width)
        return "█" * filled + "░" * (width - filled)


# =============================================================================
# Analysis Functions
# =============================================================================


async def analyze_artifact_code(
    code: str,
    language: str = "python",
    filename: str | None = None,
) -> GestaltArtifactAnalysis:
    """
    Analyze code from an artifact using Gestalt.

    This creates a temporary file with the code and runs Gestalt's
    module analysis on it.

    Args:
        code: The source code to analyze
        language: Programming language ("python" or "typescript")
        filename: Optional filename hint for better analysis

    Returns:
        GestaltArtifactAnalysis with health metrics and issues
    """
    if not code.strip():
        return GestaltArtifactAnalysis(
            grade="?",
            score=0.0,
            issues=[
                CodeIssue(
                    severity="info",
                    category="empty",
                    message="No code to analyze",
                )
            ],
        )

    # Determine file extension
    ext = ".py" if language == "python" else ".ts"
    # Note: filename parameter reserved for future use (e.g., module name hints)
    _ = filename  # Acknowledge parameter

    try:
        # Create temporary file for analysis
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=ext,
            delete=False,
        ) as f:
            f.write(code)
            temp_path = Path(f.name)

        # Run Gestalt analysis
        analysis = await _analyze_file(temp_path, language)

        # Clean up
        temp_path.unlink()

        return analysis

    except Exception as e:
        logger.error(f"Gestalt analysis failed: {e}")
        return GestaltArtifactAnalysis(
            grade="?",
            score=0.0,
            issues=[
                CodeIssue(
                    severity="error",
                    category="analysis",
                    message=f"Analysis failed: {e}",
                )
            ],
        )


async def _analyze_file(
    file_path: Path,
    language: str,
) -> GestaltArtifactAnalysis:
    """Analyze a single file using Gestalt's analysis engine."""
    from protocols.gestalt.analysis import (
        ModuleHealth,
        analyze_module_health,
        detect_language,
        scan_file,
    )

    # Count lines
    lines_of_code = len(file_path.read_text().splitlines())

    # Scan the file to get module info
    modules = scan_file(file_path, language)
    if not modules:
        # File didn't produce any modules (maybe empty or unparseable)
        return GestaltArtifactAnalysis(
            grade="?",
            score=0.0,
            lines_of_code=lines_of_code,
            issues=[
                CodeIssue(
                    severity="warning",
                    category="parsing",
                    message="Could not parse file",
                )
            ],
        )

    # Get first module (for single-file artifacts)
    module = modules[0]

    # Analyze health
    health = analyze_module_health(module)

    # Collect issues
    issues: list[CodeIssue] = []

    # High coupling warning
    if health.coupling > 0.7:
        issues.append(
            CodeIssue(
                severity="warning",
                category="coupling",
                message=f"High coupling ({health.coupling:.0%})",
                suggestion="Consider breaking into smaller, more focused modules",
            )
        )

    # Low cohesion warning
    if health.cohesion < 0.4:
        issues.append(
            CodeIssue(
                severity="warning",
                category="cohesion",
                message=f"Low cohesion ({health.cohesion:.0%})",
                suggestion="Related functions should be grouped together",
            )
        )

    # High complexity warning
    if health.complexity > 0.6:
        issues.append(
            CodeIssue(
                severity="warning",
                category="complexity",
                message=f"High complexity ({health.complexity:.0%})",
                suggestion="Consider extracting helper functions",
            )
        )

    # Drift issues
    if health.drift > 0.3:
        issues.append(
            CodeIssue(
                severity="info",
                category="drift",
                message=f"Some drift detected ({health.drift:.0%})",
                suggestion="Review architectural alignment",
            )
        )

    return GestaltArtifactAnalysis(
        grade=health.grade,
        score=health.overall_health,
        coupling=health.coupling,
        cohesion=health.cohesion,
        complexity=health.complexity,
        drift=health.drift,
        lines_of_code=lines_of_code,
        issues=issues,
        raw_module=module,
    )


async def analyze_piece(piece: "Piece") -> GestaltArtifactAnalysis | None:
    """
    Analyze an Atelier piece if it contains code.

    This inspects the piece's content and form to determine if
    it's analyzable code, then runs Gestalt analysis.

    Args:
        piece: An Atelier Piece object

    Returns:
        GestaltArtifactAnalysis if the piece contains code, None otherwise
    """
    # Check if piece contains code
    code_forms = {"code", "script", "module", "component", "function", "class"}
    if piece.form.lower() not in code_forms:
        return None

    # Get code content
    code = piece.content if hasattr(piece, "content") else None
    if not code:
        return None

    # Detect language from piece metadata or guess
    language = "python"  # Default
    if hasattr(piece, "metadata"):
        language = piece.metadata.get("language", "python")

    return await analyze_artifact_code(code, language)


# =============================================================================
# Synergy Integration
# =============================================================================


async def emit_artifact_analysis_complete(
    piece_id: str,
    analysis: GestaltArtifactAnalysis,
    session_id: str,
) -> None:
    """
    Emit a synergy event when artifact analysis completes.

    This can trigger:
    - UI updates showing health grade
    - Brain capture of analysis results
    - Suggestions surfacing

    Args:
        piece_id: The analyzed piece ID
        analysis: The analysis results
        session_id: The Atelier session
    """
    from protocols.synergy import get_synergy_bus
    from protocols.synergy.events import SynergyEvent, SynergyEventType

    event = SynergyEvent(
        source_jewel="atelier",
        target_jewel="gestalt",
        event_type=SynergyEventType.ANALYSIS_COMPLETE,
        source_id=piece_id,
        payload={
            "type": "artifact_analysis",
            "grade": analysis.grade,
            "score": analysis.score,
            "coupling": analysis.coupling,
            "cohesion": analysis.cohesion,
            "complexity": analysis.complexity,
            "drift": analysis.drift,
            "lines_of_code": analysis.lines_of_code,
            "issue_count": len(analysis.issues),
            "session_id": session_id,
        },
    )

    bus = get_synergy_bus()
    await bus.emit(event)


# =============================================================================
# UI Widget Integration
# =============================================================================


def create_health_badge_props(analysis: GestaltArtifactAnalysis) -> dict[str, Any]:
    """
    Create props for a health badge component.

    Usage in React:
        <HealthBadge {...createHealthBadgeProps(analysis)} />

    Returns:
        Props dict with grade, color, score, tooltip
    """
    grade_colors = {
        "A+": "emerald",
        "A": "emerald",
        "A-": "green",
        "B+": "green",
        "B": "lime",
        "B-": "lime",
        "C+": "yellow",
        "C": "amber",
        "C-": "amber",
        "D+": "orange",
        "D": "orange",
        "D-": "red",
        "F": "red",
        "?": "gray",
    }

    tooltip_parts = [
        f"Score: {analysis.score:.0%}",
        f"Coupling: {analysis.coupling:.0%}",
        f"Cohesion: {analysis.cohesion:.0%}",
        f"Complexity: {analysis.complexity:.0%}",
    ]
    if analysis.issues:
        tooltip_parts.append(f"Issues: {len(analysis.issues)}")

    return {
        "grade": analysis.grade,
        "color": grade_colors.get(analysis.grade, "gray"),
        "score": analysis.score,
        "isHealthy": analysis.is_healthy,
        "needsAttention": analysis.needs_attention,
        "tooltip": " | ".join(tooltip_parts),
        "issues": [i.to_dict() for i in analysis.issues[:3]],
    }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Types
    "CodeIssue",
    "GestaltArtifactAnalysis",
    # Analysis functions
    "analyze_artifact_code",
    "analyze_piece",
    # Synergy
    "emit_artifact_analysis_complete",
    # UI helpers
    "create_health_badge_props",
]
