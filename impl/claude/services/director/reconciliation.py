"""
Ghost Reconciliation Service: Zero-Seed Integration for Document Merging.

> *"The file is a lie. There is only the graph."*

When a ghost document (placeholder) meets its "real" counterpart, we have
a dialectical situation:
- THESIS: The ghost (what we expected)
- ANTITHESIS: The upload (what arrived)
- SYNTHESIS: The merged result (Zero-Seed mediated)

This service handles the reconciliation process, using Zero-Seed's
justification framework to make principled merge decisions.

Teaching:
    gotcha: Simple replacements don't need Zero-Seed. Only merge scenarios
            where both ghost and upload have content require dialectical synthesis.

    gotcha: The reconciliation result includes provenance marks — every merge
            decision is traced.

See: spec/protocols/document-director.md (Ghost Reconciliation section)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from .types import (
    GhostMetadata,
    GhostOrigin,
    ReconciliationRequest,
    ReconciliationResult,
    ReconciliationStrategy,
)

if TYPE_CHECKING:
    from services.witness.persistence import WitnessPersistence
    from services.zero_seed.core import NodeId

logger = logging.getLogger(__name__)


# =============================================================================
# Merge Conflict Types
# =============================================================================


@dataclass
class MergeConflict:
    """
    A conflict discovered during document merge.

    Conflicts arise when ghost and upload have incompatible content in
    the same semantic region. Zero-Seed helps resolve these by:
    1. Identifying the conflict
    2. Evaluating both sides by evidence tier
    3. Proposing a synthesis (if possible)
    """

    region: str  # e.g., "header", "section:Overview", "line:42"
    ghost_content: str
    upload_content: str
    resolution: str  # What was decided
    reasoning: str  # Why


@dataclass
class MergeReport:
    """
    Full report of a merge operation.

    This is the detailed record of what happened during reconciliation,
    suitable for witness marking and audit trails.
    """

    ghost_path: str
    strategy: ReconciliationStrategy
    conflicts: list[MergeConflict]
    ghost_lines_kept: int
    upload_lines_kept: int
    merged_lines: int  # Lines that combined both sources
    timestamp: str

    @property
    def had_conflicts(self) -> bool:
        return len(self.conflicts) > 0

    def to_summary(self) -> str:
        """Human-readable summary for witness marks."""
        if not self.had_conflicts:
            return f"Clean merge: {self.upload_lines_kept} lines from upload, {self.ghost_lines_kept} from ghost"
        return (
            f"Resolved {len(self.conflicts)} conflicts: "
            f"{self.upload_lines_kept} from upload, {self.ghost_lines_kept} from ghost, "
            f"{self.merged_lines} merged"
        )


# =============================================================================
# Reconciliation Service
# =============================================================================


class GhostReconciliationService:
    """
    Service for reconciling ghost documents with uploaded content.

    Strategies:
    - REPLACE: Discard ghost, use upload (fast path)
    - MERGE_UPLOADED_WINS: Merge, conflicts resolved by upload
    - MERGE_GHOST_WINS: Merge, conflicts resolved by ghost
    - INTERACTIVE: Not handled here — returns conflict list for UI

    Philosophy:
        "Every reconciliation is a dialectical synthesis witnessed by marks."
    """

    def __init__(
        self,
        witness: "WitnessPersistence | None" = None,
    ) -> None:
        self.witness = witness

    async def reconcile(
        self,
        request: ReconciliationRequest,
        author: str = "system",
    ) -> ReconciliationResult:
        """
        Reconcile a ghost with uploaded content.

        Args:
            request: The reconciliation request
            author: Who is performing the reconciliation

        Returns:
            ReconciliationResult with final content and metadata
        """
        logger.info(
            f"Reconciling ghost {request.ghost_path} with strategy {request.strategy.value}"
        )

        # Fast path: REPLACE strategy just uses upload content
        if request.strategy == ReconciliationStrategy.REPLACE:
            return await self._handle_replace(request, author)

        # Check if merge is actually needed
        if not request.needs_merge():
            # Ghost was empty or upload is empty — treat as replace
            return await self._handle_replace(request, author)

        # Full merge path
        return await self._handle_merge(request, author)

    async def _handle_replace(
        self,
        request: ReconciliationRequest,
        author: str,
    ) -> ReconciliationResult:
        """Handle simple replacement (no merge needed)."""
        mark_id = None

        if self.witness:
            mark = await self.witness.save_mark(
                action=f"Reconciled ghost: {request.ghost_path} (replaced)",
                reasoning="Ghost replaced with uploaded content, no merge needed",
                tags=[
                    "reconciliation",
                    "ghost-replaced",
                    f"path:{request.ghost_path}",
                ],
                author=author,
            )
            mark_id = mark.mark_id

        return ReconciliationResult(
            path=request.ghost_path,
            final_content=request.uploaded_content,
            strategy_used=ReconciliationStrategy.REPLACE,
            had_conflicts=False,
            conflict_summary="",
            mark_id=mark_id,
        )

    async def _handle_merge(
        self,
        request: ReconciliationRequest,
        author: str,
    ) -> ReconciliationResult:
        """
        Handle full merge with conflict resolution.

        This is where Zero-Seed integration happens. We use a structural
        merge approach that:
        1. Parses both documents into sections
        2. Matches sections by heading/structure
        3. Merges matching sections, identifying conflicts
        4. Resolves conflicts using the strategy
        """
        ghost_sections = self._parse_sections(request.ghost_content)
        upload_sections = self._parse_sections(request.uploaded_content)

        # Track merge results
        conflicts: list[MergeConflict] = []
        ghost_lines_kept = 0
        upload_lines_kept = 0
        merged_lines = 0

        # Build merged content
        merged_sections: list[str] = []

        # Use upload as base (its structure wins)
        for section_name, upload_content in upload_sections.items():
            if section_name in ghost_sections:
                ghost_content = ghost_sections[section_name]

                if ghost_content == upload_content:
                    # Identical — no conflict
                    merged_sections.append(upload_content)
                    upload_lines_kept += len(upload_content.split("\n"))
                else:
                    # Conflict — resolve based on strategy
                    resolved, conflict = self._resolve_conflict(
                        section_name,
                        ghost_content,
                        upload_content,
                        request.strategy,
                    )
                    merged_sections.append(resolved)
                    if conflict:
                        conflicts.append(conflict)
                    # Count appropriately
                    if request.strategy == ReconciliationStrategy.MERGE_UPLOADED_WINS:
                        upload_lines_kept += len(resolved.split("\n"))
                    elif request.strategy == ReconciliationStrategy.MERGE_GHOST_WINS:
                        ghost_lines_kept += len(resolved.split("\n"))
                    else:
                        merged_lines += len(resolved.split("\n"))
            else:
                # Section only in upload — keep it
                merged_sections.append(upload_content)
                upload_lines_kept += len(upload_content.split("\n"))

        # Add ghost-only sections at the end (if strategy favors ghost)
        if request.strategy in (
            ReconciliationStrategy.MERGE_GHOST_WINS,
            ReconciliationStrategy.INTERACTIVE,
        ):
            for section_name, ghost_content in ghost_sections.items():
                if section_name not in upload_sections:
                    merged_sections.append(f"\n<!-- Preserved from ghost -->\n{ghost_content}")
                    ghost_lines_kept += len(ghost_content.split("\n"))

        final_content = "\n\n".join(merged_sections)

        # Create merge report
        report = MergeReport(
            ghost_path=request.ghost_path,
            strategy=request.strategy,
            conflicts=conflicts,
            ghost_lines_kept=ghost_lines_kept,
            upload_lines_kept=upload_lines_kept,
            merged_lines=merged_lines,
            timestamp=datetime.now(UTC).isoformat(),
        )

        # Create witness mark
        mark_id = None
        if self.witness:
            mark = await self.witness.save_mark(
                action=f"Reconciled ghost: {request.ghost_path} (merged)",
                reasoning=report.to_summary(),
                tags=[
                    "reconciliation",
                    "ghost-merged",
                    f"path:{request.ghost_path}",
                    f"strategy:{request.strategy.value}",
                    f"conflicts:{len(conflicts)}",
                ],
                author=author,
            )
            mark_id = mark.mark_id

        return ReconciliationResult(
            path=request.ghost_path,
            final_content=final_content,
            strategy_used=request.strategy,
            had_conflicts=report.had_conflicts,
            conflict_summary=report.to_summary(),
            mark_id=mark_id,
        )

    def _parse_sections(self, content: str) -> dict[str, str]:
        """
        Parse markdown content into sections by heading.

        This is a simplified parser. For real Zero-Seed integration,
        we would use the full spec parser from services/living_spec.
        """
        sections: dict[str, str] = {}
        current_section = "preamble"
        current_lines: list[str] = []

        for line in content.split("\n"):
            if line.startswith("#"):
                # Save previous section
                if current_lines:
                    sections[current_section] = "\n".join(current_lines)
                # Start new section
                current_section = line.strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        # Save final section
        if current_lines:
            sections[current_section] = "\n".join(current_lines)

        return sections

    def _resolve_conflict(
        self,
        section: str,
        ghost_content: str,
        upload_content: str,
        strategy: ReconciliationStrategy,
    ) -> tuple[str, MergeConflict | None]:
        """
        Resolve a conflict between ghost and upload content.

        Returns:
            (resolved_content, conflict_record)
        """
        if strategy == ReconciliationStrategy.MERGE_UPLOADED_WINS:
            return upload_content, MergeConflict(
                region=section,
                ghost_content=ghost_content[:100] + "..."
                if len(ghost_content) > 100
                else ghost_content,
                upload_content=upload_content[:100] + "..."
                if len(upload_content) > 100
                else upload_content,
                resolution="Used upload content",
                reasoning="Strategy MERGE_UPLOADED_WINS: upload takes precedence",
            )
        elif strategy == ReconciliationStrategy.MERGE_GHOST_WINS:
            return ghost_content, MergeConflict(
                region=section,
                ghost_content=ghost_content[:100] + "..."
                if len(ghost_content) > 100
                else ghost_content,
                upload_content=upload_content[:100] + "..."
                if len(upload_content) > 100
                else upload_content,
                resolution="Used ghost content",
                reasoning="Strategy MERGE_GHOST_WINS: ghost takes precedence",
            )
        else:
            # INTERACTIVE or unknown — default to upload but mark conflict
            return upload_content, MergeConflict(
                region=section,
                ghost_content=ghost_content[:100] + "..."
                if len(ghost_content) > 100
                else ghost_content,
                upload_content=upload_content[:100] + "..."
                if len(upload_content) > 100
                else upload_content,
                resolution="Used upload content (default)",
                reasoning="Interactive strategy fell back to upload",
            )


# =============================================================================
# Factory Function
# =============================================================================


def create_reconciliation_service(
    witness: "WitnessPersistence | None" = None,
) -> GhostReconciliationService:
    """Create a GhostReconciliationService with optional witness integration."""
    return GhostReconciliationService(witness=witness)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "GhostReconciliationService",
    "MergeConflict",
    "MergeReport",
    "create_reconciliation_service",
]
