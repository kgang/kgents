"""
Forest Section: Read current focus from Forest Protocol.

The Forest Section reads from plans/_forest.md and extracts:
- Summary statistics (total plans, active, complete)
- Active trees with progress
- Current focus based on most recently touched plans

This is a "soft" section (rigidity ~0.4) because it changes
based on project activity.

See: spec/protocols/forest-protocol.md
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ..section_base import NPhase, Section, estimate_tokens, run_sync
from ..soft_section import MergeStrategy, SoftSection
from ..sources.base import SectionSource, SourcePriority, SourceResult, TemplateSource
from ..sources.file_source import FileSource

if TYPE_CHECKING:
    from ..compiler import CompilationContext

logger = logging.getLogger(__name__)


# =============================================================================
# Forest Source: Extract focus from _forest.md
# =============================================================================


@dataclass
class ForestSource(SectionSource):
    """
    Source that extracts current focus from plans/_forest.md.

    Parses the forest health file to extract:
    - Summary statistics
    - Top active trees (most recently touched)
    - Current focus intent
    """

    name: str = "forest:file"
    priority: SourcePriority = SourcePriority.FILE
    rigidity: float = 0.4  # Soft - changes frequently
    max_active_trees: int = 5  # Top N most active trees to show

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Read and parse forest health file."""
        traces = ["ForestSource: Looking for _forest.md"]

        # Resolve forest path
        forest_path = context.forest_path
        if forest_path is None:
            traces.append("No forest path in context")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        forest_file = forest_path / "_forest.md"
        traces.append(f"Forest file: {forest_file}")

        if not forest_file.exists():
            traces.append("Forest file not found")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                source_path=forest_file,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        # Read and parse
        try:
            raw_content = forest_file.read_text(encoding="utf-8")
            traces.append(f"Read {len(raw_content)} chars from _forest.md")
        except OSError as e:
            traces.append(f"Error reading forest file: {e}")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                source_path=forest_file,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        # Extract summary and active trees
        summary = self._extract_summary(raw_content, traces)
        active_trees = self._extract_active_trees(raw_content, traces)

        # Apply focus intent filter if provided
        if context.focus_intent and active_trees:
            traces.append(f"Filtering by focus intent: {context.focus_intent}")
            active_trees = self._filter_by_intent(active_trees, context.focus_intent, traces)

        # Build section content
        content = self._build_content(summary, active_trees, traces)
        traces.append(f"Built content: {len(content)} chars")

        return SourceResult(
            content=content,
            success=True,
            source_name=self.name,
            source_path=forest_file,
            reasoning_trace=tuple(traces),
            rigidity=self.rigidity,
        )

    def _extract_summary(self, content: str, traces: list[str]) -> dict[str, str]:
        """Extract summary statistics from forest file."""
        summary: dict[str, str] = {}

        # Look for summary section lines like "- **Total Plans**: 59"
        patterns = [
            (r"\*\*Total Plans\*\*:\s*(\d+)", "total"),
            (r"\*\*Active\*\*:\s*(\d+)", "active"),
            (r"\*\*Complete\*\*:\s*(\d+)", "complete"),
            (r"\*\*Blocked\*\*:\s*(\d+)", "blocked"),
            (r"\*\*Average Progress\*\*:\s*(\d+%)", "progress"),
        ]

        for pattern, key in patterns:
            match = re.search(pattern, content)
            if match:
                summary[key] = match.group(1)

        traces.append(f"Extracted summary: {len(summary)} fields")
        return summary

    def _extract_active_trees(self, content: str, traces: list[str]) -> list[dict[str, str]]:
        """Extract active trees from the Active Trees table."""
        trees: list[dict[str, str]] = []

        # Find the Active Trees section
        active_section_match = re.search(
            r"## Active Trees\s*\n\s*\|.*?\|\s*\n\s*\|[-\s|]+\|\s*\n((?:\|.*?\|\s*\n)+)",
            content,
            re.DOTALL,
        )

        if not active_section_match:
            traces.append("Active Trees section not found")
            return trees

        table_content = active_section_match.group(1)

        # Parse table rows
        # Format: | Plan | Progress | Last Touched | Status | Notes |
        row_pattern = (
            r"\|\s*([^|]+)\s*\|\s*(\d+%)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]*)\s*\|"
        )

        for match in re.finditer(row_pattern, table_content):
            plan, progress, last_touched, status, notes = match.groups()
            trees.append(
                {
                    "plan": plan.strip(),
                    "progress": progress.strip(),
                    "last_touched": last_touched.strip(),
                    "status": status.strip(),
                    "notes": notes.strip()[:50],  # Truncate notes
                }
            )

        traces.append(f"Extracted {len(trees)} active trees")

        # Sort by last_touched (most recent first) and take top N
        # Date format is YYYY-MM-DD
        try:
            trees.sort(key=lambda t: t["last_touched"], reverse=True)
        except Exception:
            pass  # Keep original order if sorting fails

        return trees[: self.max_active_trees]

    def _filter_by_intent(
        self,
        trees: list[dict[str, str]],
        intent: str,
        traces: list[str],
    ) -> list[dict[str, str]]:
        """Filter trees by focus intent keyword."""
        intent_lower = intent.lower()
        filtered = [
            t
            for t in trees
            if intent_lower in t["plan"].lower() or intent_lower in t.get("notes", "").lower()
        ]
        traces.append(f"Filtered to {len(filtered)} trees matching intent")
        return filtered if filtered else trees  # Fall back to all if no matches

    def _build_content(
        self,
        summary: dict[str, str],
        trees: list[dict[str, str]],
        traces: list[str],
    ) -> str:
        """Build the section content from extracted data."""
        lines = ["## Current Focus (Forest Protocol)"]
        lines.append("")

        # Summary line
        if summary:
            parts = []
            if "active" in summary:
                parts.append(f"{summary['active']} active")
            if "complete" in summary:
                parts.append(f"{summary['complete']} complete")
            if "progress" in summary:
                parts.append(f"{summary['progress']} avg")
            if parts:
                lines.append(f"**Forest Health**: {', '.join(parts)}")
                lines.append("")

        # Active trees table
        if trees:
            lines.append("### Active Plans")
            lines.append("")
            lines.append("| Plan | Progress | Status |")
            lines.append("|------|----------|--------|")
            for tree in trees:
                plan_name = tree["plan"].split("/")[-1]  # Just the filename
                lines.append(f"| {plan_name} | {tree['progress']} | {tree['status']} |")
            lines.append("")
        else:
            lines.append("*No active plans found.*")
            lines.append("")

        return "\n".join(lines)


# =============================================================================
# Forest Section Compiler
# =============================================================================


class ForestSectionCompiler:
    """
    Compile the Forest section.

    Uses SoftSection with ForestSource and a template fallback.
    Rigidity is ~0.4 (fairly soft) since this changes frequently.
    """

    FALLBACK_CONTENT = """## Current Focus (Forest Protocol)

*Forest health data unavailable. Run `kgents forest manifest` to generate.*
"""

    @property
    def name(self) -> str:
        return "forest"

    @property
    def required(self) -> bool:
        return False  # Optional - omit if forest data unavailable

    @property
    def phases(self) -> frozenset[NPhase]:
        return frozenset()  # Relevant to all phases

    def compile(self, context: "CompilationContext") -> Section:
        """
        Compile forest section synchronously.

        Uses run_sync() for safe async execution from sync context.
        This handles event loop detection properly for both CLI
        and async framework usage (Wave 3 P1 fix).
        """
        soft = self._create_soft_section()
        result = run_sync(soft.crystallize(context))
        return result.section.with_reasoning(result.reasoning_trace)

    def _create_soft_section(self) -> SoftSection:
        """Create the SoftSection with sources."""
        from ..sources.base import FallbackSource

        return SoftSection(
            name=self.name,
            sources=[
                ForestSource(),
                # Use FallbackSource (priority=0) so ForestSource is tried first
                FallbackSource(
                    name=f"{self.name}:fallback",
                    fallback_message=self.FALLBACK_CONTENT,
                ),
            ],
            merge_strategy=MergeStrategy.FIRST_WINS,
            required=self.required,
            default_rigidity=0.4,
        )

    def estimate_tokens(self) -> int:
        """Estimate token cost for budget planning."""
        return 200  # Forest section is typically compact


# =============================================================================
# Utility: Create SoftSection for Forest
# =============================================================================


def create_forest_soft_section() -> SoftSection:
    """
    Create a SoftSection for the Forest section.

    Useful for direct async usage outside the compiler.
    """
    from ..sources.base import FallbackSource

    return SoftSection(
        name="forest",
        sources=[
            ForestSource(),
            # Use FallbackSource (priority=0) so ForestSource is tried first
            FallbackSource(
                name="forest:fallback",
                fallback_message=ForestSectionCompiler.FALLBACK_CONTENT,
            ),
        ],
        merge_strategy=MergeStrategy.FIRST_WINS,
        required=False,
        default_rigidity=0.4,
    )


__all__ = [
    "ForestSource",
    "ForestSectionCompiler",
    "create_forest_soft_section",
]
