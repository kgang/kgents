"""
InspectionService: Universal Inspection for Any System Element.

This service provides deep inspection capabilities for the Self-Reflective OS,
enabling examination of any element in the system:
- Files (Python modules, specs, plans)
- K-Blocks (Constitutional and codebase)
- Witness marks and crystals

Philosophy:
    "Inspection is introspection. The system that sees itself can trust itself."

AGENTESE Paths:
- self.inspect.file      - Inspect a file with full context
- self.inspect.kblock    - Inspect a K-Block with derivation chain
- self.inspect.quick     - Lightweight inspection for quick lookups

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- All transports collapse to logos.invoke(path, observer, ...)

See: plans/self-reflective-os/
See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================


class DriftStatus(str, Enum):
    """Status of spec/impl drift for an element."""

    COHERENT = "coherent"  # No drift detected
    MINOR_DRIFT = "minor_drift"  # Small divergence
    MAJOR_DRIFT = "major_drift"  # Significant divergence
    ORPHAN = "orphan"  # No derivation to axioms
    UNKNOWN = "unknown"  # Status cannot be determined


@dataclass(frozen=True)
class FileHistory:
    """Git history for a file."""

    file_path: str
    last_commit_hash: str
    last_commit_date: datetime
    last_commit_author: str
    last_commit_message: str
    total_commits: int
    contributors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "file_path": self.file_path,
            "last_commit_hash": self.last_commit_hash,
            "last_commit_date": self.last_commit_date.isoformat(),
            "last_commit_author": self.last_commit_author,
            "last_commit_message": self.last_commit_message,
            "total_commits": self.total_commits,
            "contributors": list(self.contributors),
        }


@dataclass(frozen=True)
class DerivationStep:
    """A single step in the derivation chain."""

    kblock_id: str
    kblock_title: str
    layer: int
    layer_name: str
    galois_loss: float
    derives_from: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "kblock_id": self.kblock_id,
            "kblock_title": self.kblock_title,
            "layer": self.layer,
            "layer_name": self.layer_name,
            "galois_loss": self.galois_loss,
            "derives_from": list(self.derives_from),
        }


@dataclass(frozen=True)
class DerivationChain:
    """Complete derivation chain from element to axioms."""

    target_id: str
    target_path: str
    steps: tuple[DerivationStep, ...] = ()
    reaches_axiom: bool = False
    total_galois_loss: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "target_id": self.target_id,
            "target_path": self.target_path,
            "steps": [s.to_dict() for s in self.steps],
            "reaches_axiom": self.reaches_axiom,
            "total_galois_loss": self.total_galois_loss,
            "depth": len(self.steps),
        }

    def to_text(self) -> str:
        """Format as human-readable text."""
        lines = [
            f"Derivation Chain: {self.target_path}",
            f"Reaches Axiom: {'Yes' if self.reaches_axiom else 'No'}",
            f"Total Galois Loss: {self.total_galois_loss:.4f}",
            "",
        ]
        for i, step in enumerate(self.steps):
            indent = "  " * i
            lines.append(f"{indent}-> {step.kblock_id} (L{step.layer}: {step.layer_name})")
        return "\n".join(lines)


@dataclass(frozen=True)
class QuickInspection:
    """Lightweight inspection result."""

    identifier: str
    kind: str  # 'file', 'kblock', 'mark', 'crystal'
    exists: bool
    summary: str
    layer: int | None = None
    layer_name: str | None = None
    galois_loss: float | None = None
    drift_status: DriftStatus | None = None
    tags: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "identifier": self.identifier,
            "kind": self.kind,
            "exists": self.exists,
            "summary": self.summary,
            "layer": self.layer,
            "layer_name": self.layer_name,
            "galois_loss": self.galois_loss,
            "drift_status": self.drift_status.value if self.drift_status else None,
            "tags": list(self.tags),
        }


@dataclass(frozen=True)
class InspectionResult:
    """
    Full inspection of any element in the system.

    This is the comprehensive result of inspecting a file, K-Block,
    or other system element, including all related metadata.
    """

    kblock_id: str
    path: str
    layer: int
    layer_name: str
    content_summary: str
    derivation_chain: DerivationChain
    related_witnesses: tuple[dict[str, Any], ...] = ()
    related_decisions: tuple[dict[str, Any], ...] = ()
    git_info: FileHistory | None = None
    drift_status: DriftStatus | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "kblock_id": self.kblock_id,
            "path": self.path,
            "layer": self.layer,
            "layer_name": self.layer_name,
            "content_summary": self.content_summary,
            "derivation_chain": self.derivation_chain.to_dict(),
            "related_witnesses": list(self.related_witnesses),
            "related_decisions": list(self.related_decisions),
            "git_info": self.git_info.to_dict() if self.git_info else None,
            "drift_status": self.drift_status.value if self.drift_status else None,
            "metadata": self.metadata,
        }

    def to_text(self) -> str:
        """Format as human-readable text."""
        lines = [
            f"Inspection: {self.path}",
            "=" * 60,
            f"K-Block ID: {self.kblock_id}",
            f"Layer: L{self.layer} ({self.layer_name})",
            f"Drift Status: {self.drift_status.value if self.drift_status else 'unknown'}",
            "",
            "Summary:",
            self.content_summary[:500] + "..."
            if len(self.content_summary) > 500
            else self.content_summary,
            "",
            self.derivation_chain.to_text(),
            "",
        ]

        if self.git_info:
            lines.extend(
                [
                    "Git Info:",
                    f"  Last Commit: {self.git_info.last_commit_hash[:8]}",
                    f"  Author: {self.git_info.last_commit_author}",
                    f"  Date: {self.git_info.last_commit_date.isoformat()}",
                    f"  Message: {self.git_info.last_commit_message[:60]}",
                    "",
                ]
            )

        if self.related_witnesses:
            lines.extend(
                [
                    f"Related Witnesses ({len(self.related_witnesses)}):",
                ]
            )
            for w in self.related_witnesses[:5]:
                lines.append(f"  - {w.get('id', 'unknown')}: {w.get('summary', '')[:50]}")

        return "\n".join(lines)


# =============================================================================
# Layer Names
# =============================================================================

LAYER_NAMES = {
    0: "Axioms",
    1: "Kernel",
    2: "Principles",
    3: "Architecture",
    4: "Specification",
    5: "Implementation",
}


def get_layer_name(layer: int) -> str:
    """Get human-readable name for a layer."""
    return LAYER_NAMES.get(layer, f"L{layer}")


# =============================================================================
# InspectionService
# =============================================================================


class InspectionService:
    """
    Universal inspection for any system element.

    This service provides deep inspection capabilities by composing
    from existing services:
    - SelfReflectionService for Constitutional K-Blocks
    - CodebaseScanner for module K-Blocks
    - WitnessTimelineService for related witnesses
    - DriftService for drift analysis

    Example:
        service = InspectionService()

        # Inspect a file
        result = await service.inspect_file("services/witness/mark.py")

        # Inspect a K-Block
        result = await service.inspect_kblock("COMPOSABLE")

        # Quick inspection
        quick = await service.quick_inspect("ASHC")
    """

    def __init__(
        self,
        reflection_service: Any | None = None,
        codebase_scanner: Any | None = None,
        timeline_service: Any | None = None,
        drift_service: Any | None = None,
    ) -> None:
        """
        Initialize InspectionService.

        Args:
            reflection_service: SelfReflectionService instance
            codebase_scanner: CodebaseScanner instance
            timeline_service: WitnessTimelineService instance
            drift_service: DriftService instance
        """
        self._reflection_service = reflection_service
        self._codebase_scanner = codebase_scanner
        self._timeline_service = timeline_service
        self._drift_service = drift_service

    def _get_reflection_service(self) -> Any:
        """Lazy-load SelfReflectionService."""
        if self._reflection_service is None:
            try:
                from services.self.reflection_service import get_reflection_service

                self._reflection_service = get_reflection_service()
            except ImportError:
                logger.warning("SelfReflectionService not available")
        return self._reflection_service

    def _get_codebase_scanner(self) -> Any:
        """Lazy-load CodebaseScanner."""
        if self._codebase_scanner is None:
            try:
                from services.self.scanner import CodebaseScanner

                self._codebase_scanner = CodebaseScanner()
            except ImportError:
                logger.warning("CodebaseScanner not available")
        return self._codebase_scanner

    def _get_timeline_service(self) -> Any:
        """Lazy-load WitnessTimelineService."""
        if self._timeline_service is None:
            try:
                from services.self.witness_timeline_service import get_witness_timeline_service

                self._timeline_service = get_witness_timeline_service()
            except ImportError:
                logger.warning("WitnessTimelineService not available")
        return self._timeline_service

    def _get_drift_service(self) -> Any:
        """Lazy-load DriftService."""
        if self._drift_service is None:
            try:
                from services.self.drift_service import get_drift_service

                self._drift_service = get_drift_service()
            except ImportError:
                logger.warning("DriftService not available")
        return self._drift_service

    # =========================================================================
    # Unified Inspection
    # =========================================================================

    async def inspect(self, identifier: str) -> InspectionResult:
        """
        Inspect any system element by identifier.

        Auto-detects the type of element and routes to appropriate handler:
        - File paths (ending in .py, .md, etc.) -> inspect_file
        - K-Block IDs (uppercase, no extension) -> inspect_kblock
        - Mark IDs (mark-...) -> inspect via timeline

        Args:
            identifier: File path, K-Block ID, or mark ID

        Returns:
            Full InspectionResult for the element
        """
        # Detect type and route
        if identifier.startswith("mark-"):
            return await self._inspect_mark(identifier)
        elif identifier.startswith("crystal-"):
            return await self._inspect_crystal(identifier)
        elif "." in identifier or "/" in identifier:
            # Looks like a file path
            return await self.inspect_file(identifier)
        else:
            # Assume K-Block ID
            return await self.inspect_kblock(identifier)

    async def inspect_file(self, path: str) -> InspectionResult:
        """
        Inspect a file with full context.

        Args:
            path: File path (absolute or relative to project root)

        Returns:
            InspectionResult with file analysis, K-Block, git info, and witnesses
        """
        # Determine K-Block ID from path
        kblock_id = self._path_to_kblock_id(path)

        # Get content summary
        content_summary = await self._get_file_summary(path)

        # Determine layer from path
        layer, layer_name = self._infer_layer_from_path(path)

        # Build derivation chain
        derivation_chain = await self._build_derivation_chain(kblock_id, path)

        # Get related witnesses
        related_witnesses = await self._get_related_witnesses(path)

        # Get git info
        git_info = await self._get_git_info(path)

        # Get drift status
        drift_status = await self._get_drift_status(kblock_id)

        return InspectionResult(
            kblock_id=kblock_id,
            path=path,
            layer=layer,
            layer_name=layer_name,
            content_summary=content_summary,
            derivation_chain=derivation_chain,
            related_witnesses=tuple(related_witnesses),
            related_decisions=(),  # TODO: Add decision lookup
            git_info=git_info,
            drift_status=drift_status,
            metadata={
                "inspected_at": datetime.now(timezone.utc).isoformat(),
                "inspection_type": "file",
            },
        )

    async def inspect_kblock(self, kblock_id: str) -> InspectionResult:
        """
        Inspect a K-Block with derivation chain.

        Args:
            kblock_id: K-Block identifier (e.g., "COMPOSABLE", "ASHC")

        Returns:
            InspectionResult with K-Block details and derivation
        """
        reflection_service = self._get_reflection_service()

        # Try to get K-Block from reflection service
        kblock = None
        path = kblock_id
        layer = 3
        layer_name = "Architecture"
        content_summary = f"K-Block: {kblock_id}"

        if reflection_service:
            try:
                inspection = await reflection_service.inspect(kblock_id)
                if inspection:
                    path = kblock_id
                    layer = inspection.kblock.layer
                    layer_name = get_layer_name(layer)
                    content_summary = inspection.kblock.content or f"K-Block: {kblock_id}"
            except Exception as e:
                logger.warning(f"Error inspecting K-Block {kblock_id}: {e}")

        # Build derivation chain
        derivation_chain = await self._build_derivation_chain(kblock_id, path)

        # Get drift status
        drift_status = await self._get_drift_status(kblock_id)

        return InspectionResult(
            kblock_id=kblock_id,
            path=path,
            layer=layer,
            layer_name=layer_name,
            content_summary=content_summary,
            derivation_chain=derivation_chain,
            related_witnesses=(),
            related_decisions=(),
            git_info=None,
            drift_status=drift_status,
            metadata={
                "inspected_at": datetime.now(timezone.utc).isoformat(),
                "inspection_type": "kblock",
            },
        )

    async def quick_inspect(self, identifier: str) -> QuickInspection:
        """
        Lightweight inspection for quick lookups.

        Args:
            identifier: File path, K-Block ID, or mark ID

        Returns:
            QuickInspection with basic information
        """
        # Detect type
        if identifier.startswith("mark-"):
            kind = "mark"
        elif identifier.startswith("crystal-"):
            kind = "crystal"
        elif "." in identifier or "/" in identifier:
            kind = "file"
        else:
            kind = "kblock"

        # Quick checks based on type
        exists = True
        summary = ""
        layer = None
        layer_name = None
        galois_loss = None
        drift_status = None
        tags: tuple[str, ...] = ()

        if kind == "file":
            path = Path(identifier)
            exists = path.exists() if path.is_absolute() else True  # Assume exists if relative
            summary = f"File: {identifier}"
            layer, layer_name = self._infer_layer_from_path(identifier)

        elif kind == "kblock":
            reflection_service = self._get_reflection_service()
            if reflection_service:
                try:
                    inspection = await reflection_service.inspect(identifier)
                    if inspection:
                        exists = True
                        summary = inspection.kblock.title or identifier
                        layer = inspection.kblock.layer
                        layer_name = get_layer_name(layer)
                        galois_loss = inspection.kblock.galois_loss
                        tags = tuple(inspection.kblock.tags) if inspection.kblock.tags else ()
                    else:
                        exists = False
                        summary = f"K-Block not found: {identifier}"
                except Exception:
                    exists = False
                    summary = f"Error inspecting: {identifier}"
            else:
                summary = f"K-Block: {identifier}"

        elif kind == "mark":
            timeline_service = self._get_timeline_service()
            if timeline_service:
                try:
                    mark_store = timeline_service._get_mark_store()
                    from services.witness.mark import MarkId

                    mark = mark_store.get(MarkId(identifier))
                    if mark:
                        exists = True
                        summary = mark.response.content[:100] if mark.response.content else "Mark"
                        tags = mark.tags
                    else:
                        exists = False
                        summary = f"Mark not found: {identifier}"
                except Exception:
                    exists = False
                    summary = f"Error inspecting mark: {identifier}"
            else:
                summary = f"Mark: {identifier}"

        elif kind == "crystal":
            timeline_service = self._get_timeline_service()
            if timeline_service:
                try:
                    crystal_store = timeline_service._get_crystal_store()
                    from services.witness.crystal import CrystalId

                    crystal = crystal_store.get(CrystalId(identifier))
                    if crystal:
                        exists = True
                        summary = crystal.insight[:100] if crystal.insight else "Crystal"
                        layer = crystal.level.value
                        layer_name = crystal.level.name
                    else:
                        exists = False
                        summary = f"Crystal not found: {identifier}"
                except Exception:
                    exists = False
                    summary = f"Error inspecting crystal: {identifier}"
            else:
                summary = f"Crystal: {identifier}"

        return QuickInspection(
            identifier=identifier,
            kind=kind,
            exists=exists,
            summary=summary,
            layer=layer,
            layer_name=layer_name,
            galois_loss=galois_loss,
            drift_status=drift_status,
            tags=tags,
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _path_to_kblock_id(self, path: str) -> str:
        """Convert a file path to a K-Block ID."""
        # Remove extension and convert to uppercase identifier
        import hashlib

        path_hash = hashlib.sha256(path.encode()).hexdigest()[:12]
        return f"mkb_{path_hash}"

    def _infer_layer_from_path(self, path: str) -> tuple[int, str]:
        """Infer the layer from a file path."""
        path_lower = path.lower()

        if "bootstrap" in path_lower or "axiom" in path_lower:
            return 0, "Axioms"
        elif "kernel" in path_lower:
            return 1, "Kernel"
        elif "principle" in path_lower or "constitution" in path_lower:
            return 2, "Principles"
        elif "agents/" in path_lower or "protocols/" in path_lower:
            return 3, "Architecture"
        elif "spec/" in path_lower:
            return 4, "Specification"
        else:
            return 5, "Implementation"

    async def _get_file_summary(self, path: str) -> str:
        """Get a summary of a file's content."""
        try:
            full_path = Path(path)
            if not full_path.is_absolute():
                # Try relative to project root
                import os

                project_root = os.environ.get(
                    "KGENTS_PROJECT_ROOT", "/Users/kentgang/git/kgents/impl/claude"
                )
                full_path = Path(project_root) / path

            if full_path.exists():
                content = full_path.read_text()
                # Return docstring or first 500 chars
                if content.startswith('"""'):
                    end = content.find('"""', 3)
                    if end > 0:
                        return content[3:end].strip()
                return content[:500]
            return f"File not found: {path}"
        except Exception as e:
            return f"Error reading file: {e}"

    async def _build_derivation_chain(self, kblock_id: str, path: str) -> DerivationChain:
        """Build derivation chain for an element."""
        steps: list[DerivationStep] = []
        reaches_axiom = False
        total_loss = 0.0

        reflection_service = self._get_reflection_service()
        if reflection_service:
            try:
                chain = await reflection_service.get_derivation_chain(kblock_id)
                if chain and chain.steps:
                    for step in chain.steps:
                        steps.append(
                            DerivationStep(
                                kblock_id=step.kblock_id,
                                kblock_title=step.title,
                                layer=step.layer,
                                layer_name=get_layer_name(step.layer),
                                galois_loss=step.galois_loss,
                                derives_from=tuple(step.derives_from) if step.derives_from else (),
                            )
                        )
                        total_loss += step.galois_loss
                    reaches_axiom = chain.reaches_axiom
            except Exception as e:
                logger.warning(f"Error building derivation chain: {e}")

        return DerivationChain(
            target_id=kblock_id,
            target_path=path,
            steps=tuple(steps),
            reaches_axiom=reaches_axiom,
            total_galois_loss=total_loss,
        )

    async def _get_related_witnesses(self, path: str) -> list[dict[str, Any]]:
        """Get witness marks related to a file."""
        timeline_service = self._get_timeline_service()
        if timeline_service:
            try:
                marks: list[dict[str, Any]] = await timeline_service.get_marks_for_file(
                    path, limit=20
                )
                return marks
            except Exception as e:
                logger.warning(f"Error getting related witnesses: {e}")
        return []

    async def _get_git_info(self, path: str) -> FileHistory | None:
        """Get git history for a file."""
        try:
            import os
            import subprocess

            project_root = os.environ.get(
                "KGENTS_PROJECT_ROOT", "/Users/kentgang/git/kgents/impl/claude"
            )

            # Get last commit info
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%ai|%an|%s", "--", path],
                capture_output=True,
                text=True,
                cwd=project_root,
            )

            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split("|", 3)
                if len(parts) >= 4:
                    commit_hash, commit_date, author, message = parts

                    # Get total commits
                    count_result = subprocess.run(
                        ["git", "rev-list", "--count", "HEAD", "--", path],
                        capture_output=True,
                        text=True,
                        cwd=project_root,
                    )
                    total_commits = (
                        int(count_result.stdout.strip()) if count_result.returncode == 0 else 0
                    )

                    return FileHistory(
                        file_path=path,
                        last_commit_hash=commit_hash,
                        last_commit_date=datetime.fromisoformat(
                            commit_date.replace(" ", "T").replace(" +", "+")
                        ),
                        last_commit_author=author,
                        last_commit_message=message,
                        total_commits=total_commits,
                    )
        except Exception as e:
            logger.warning(f"Error getting git info for {path}: {e}")
        return None

    async def _get_drift_status(self, kblock_id: str) -> DriftStatus:
        """Get drift status for a K-Block."""
        drift_service = self._get_drift_service()
        if drift_service:
            try:
                orphans = (
                    await drift_service.get_orphans()
                    if hasattr(drift_service, "get_orphans")
                    else []
                )
                if kblock_id in orphans:
                    return DriftStatus.ORPHAN
                return DriftStatus.COHERENT
            except Exception as e:
                logger.warning(f"Error getting drift status: {e}")
        return DriftStatus.UNKNOWN

    async def _inspect_mark(self, mark_id: str) -> InspectionResult:
        """Inspect a witness mark."""
        timeline_service = self._get_timeline_service()

        content_summary = f"Mark: {mark_id}"
        related_witnesses: list[dict[str, Any]] = []

        if timeline_service:
            try:
                mark_store = timeline_service._get_mark_store()
                from services.witness.mark import MarkId

                mark = mark_store.get(MarkId(mark_id))
                if mark:
                    content_summary = (
                        mark.response.content[:500]
                        if mark.response.content
                        else f"Mark from {mark.origin}"
                    )
                    related_witnesses = [timeline_service._mark_to_dict(mark)]
            except Exception as e:
                logger.warning(f"Error inspecting mark: {e}")

        return InspectionResult(
            kblock_id=mark_id,
            path=mark_id,
            layer=5,
            layer_name="Implementation",
            content_summary=content_summary,
            derivation_chain=DerivationChain(target_id=mark_id, target_path=mark_id),
            related_witnesses=tuple(related_witnesses),
            related_decisions=(),
            git_info=None,
            drift_status=DriftStatus.UNKNOWN,
            metadata={
                "inspected_at": datetime.now(timezone.utc).isoformat(),
                "inspection_type": "mark",
            },
        )

    async def _inspect_crystal(self, crystal_id: str) -> InspectionResult:
        """Inspect a witness crystal."""
        timeline_service = self._get_timeline_service()

        content_summary = f"Crystal: {crystal_id}"
        layer = 0
        layer_name = "SESSION"

        if timeline_service:
            try:
                crystal_store = timeline_service._get_crystal_store()
                from services.witness.crystal import CrystalId

                crystal = crystal_store.get(CrystalId(crystal_id))
                if crystal:
                    content_summary = (
                        crystal.insight[:500]
                        if crystal.insight
                        else f"Crystal at {crystal.level.name}"
                    )
                    layer = crystal.level.value
                    layer_name = crystal.level.name
            except Exception as e:
                logger.warning(f"Error inspecting crystal: {e}")

        return InspectionResult(
            kblock_id=crystal_id,
            path=crystal_id,
            layer=layer,
            layer_name=layer_name,
            content_summary=content_summary,
            derivation_chain=DerivationChain(target_id=crystal_id, target_path=crystal_id),
            related_witnesses=(),
            related_decisions=(),
            git_info=None,
            drift_status=DriftStatus.UNKNOWN,
            metadata={
                "inspected_at": datetime.now(timezone.utc).isoformat(),
                "inspection_type": "crystal",
            },
        )


# =============================================================================
# Factory Functions
# =============================================================================

_global_service: InspectionService | None = None


def get_inspection_service() -> InspectionService:
    """Get the global inspection service (singleton)."""
    global _global_service
    if _global_service is None:
        _global_service = InspectionService()
    return _global_service


def create_inspection_service(
    reflection_service: Any | None = None,
    codebase_scanner: Any | None = None,
    timeline_service: Any | None = None,
    drift_service: Any | None = None,
) -> InspectionService:
    """
    Create a new inspection service with dependencies.

    Args:
        reflection_service: SelfReflectionService instance
        codebase_scanner: CodebaseScanner instance
        timeline_service: WitnessTimelineService instance
        drift_service: DriftService instance

    Returns:
        New InspectionService instance
    """
    return InspectionService(
        reflection_service=reflection_service,
        codebase_scanner=codebase_scanner,
        timeline_service=timeline_service,
        drift_service=drift_service,
    )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Enums
    "DriftStatus",
    # Data Models
    "FileHistory",
    "DerivationStep",
    "DerivationChain",
    "QuickInspection",
    "InspectionResult",
    # Helper
    "get_layer_name",
    "LAYER_NAMES",
    # Service
    "InspectionService",
    # Factory
    "get_inspection_service",
    "create_inspection_service",
]
