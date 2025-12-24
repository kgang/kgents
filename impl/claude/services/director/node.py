"""
Document Director AGENTESE Node: @node("concept.document")

Exposes Document Director through the universal AGENTESE protocol.

AGENTESE Paths:
- concept.document.manifest   - Director status and statistics
- concept.document.upload     - Upload document (ingest + queue analysis)
- concept.document.analyze    - Trigger/re-trigger analysis
- concept.document.status     - Get document lifecycle status
- concept.document.prompt     - Generate Claude Code execution prompt
- concept.document.capture    - Capture execution results

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- No explicit routes needed
- All transports collapse to logos.invoke(path, observer, ...)

Philosophy:
    "Specs become code. Code becomes evidence. Evidence feeds back to specs."
    "Upload → Analyze → Generate → Execute → Capture → Verify → Loop"

See: spec/protocols/document-director.md
See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from protocols.agentese.affordances import AspectCategory, aspect
from protocols.agentese.contract import Contract, Response
from protocols.agentese.node import (
    BaseLogosNode,
    Observer,
    Renderable,
)
from protocols.agentese.registry import node

from .contracts import (
    AnalyzeRequest,
    AnalyzeResponse,
    CaptureRequest,
    CaptureResponse,
    DirectorManifestResponse,
    PromptRequest,
    PromptResponse,
    StatusRequest,
    StatusResponse,
    UploadRequest,
    UploadResponse,
)
from .types import TestResults

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from services.director.director import DocumentDirector
    from services.sovereign.ingest import Ingestor
    from services.witness.bus import WitnessSynergyBus
    from services.witness.persistence import WitnessPersistence

logger = logging.getLogger(__name__)


# =============================================================================
# Rendering Types
# =============================================================================


@dataclass(frozen=True)
class DirectorManifestRendering:
    """Rendering for director manifest."""

    total_documents: int
    by_status: dict[str, int]
    recent_uploads: list[str]
    recent_analyses: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": "director_manifest",
            "total_documents": self.total_documents,
            "by_status": self.by_status,
            "recent_uploads": self.recent_uploads,
            "recent_analyses": self.recent_analyses,
        }

    def to_text(self) -> str:
        lines = [
            "Document Director Status",
            "========================",
            f"Total Documents: {self.total_documents}",
            "",
            "By Status:",
        ]
        for status, count in self.by_status.items():
            lines.append(f"  {status}: {count}")

        if self.recent_uploads:
            lines.append("")
            lines.append("Recent Uploads:")
            for path in self.recent_uploads:
                lines.append(f"  - {path}")

        return "\n".join(lines)


# =============================================================================
# DocumentDirectorNode
# =============================================================================


@node(
    "concept.document",
    description="Document Director - Lifecycle management for sovereign documents",
    contracts={
        # Perception aspects
        "manifest": Response(DirectorManifestResponse),
        "status": Contract(StatusRequest, StatusResponse),
        # Mutation aspects
        "upload": Contract(UploadRequest, UploadResponse),
        "analyze": Contract(AnalyzeRequest, AnalyzeResponse),
        "prompt": Contract(PromptRequest, PromptResponse),
        "capture": Contract(CaptureRequest, CaptureResponse),
    },
    dependencies=("director", "witness", "bus"),
    examples=[
        ("manifest", {}, "Show director status"),
        ("upload", {"path": "spec/new.md", "content": "# New Spec"}, "Upload document"),
        ("analyze", {"path": "spec/protocols/k-block.md"}, "Analyze document"),
        ("status", {"path": "spec/protocols/k-block.md"}, "Get document status"),
        ("prompt", {"path": "spec/protocols/k-block.md"}, "Generate execution prompt"),
        ("capture", {"path": "spec/new.md", "generated_files": {"impl/new.py": "code"}}, "Capture execution"),
    ],
)
class DocumentDirectorNode(BaseLogosNode):
    """
    AGENTESE node for Document Director.

    Orchestrates the full document lifecycle from spec to implementation.
    All transports (HTTP, WebSocket, CLI) collapse to this interface.

    Example:
        # Via AGENTESE gateway
        POST /agentese/concept/document/upload
        {"path": "spec/my-spec.md", "content": "# My Spec"}

        # Via Logos directly
        await logos.invoke("concept.document.status", observer, path="spec/...")

        # Via CLI
        kg document upload spec/my-spec.md
    """

    def __init__(
        self,
        director: "DocumentDirector",
        witness: "WitnessPersistence",
        bus: "WitnessSynergyBus",
    ) -> None:
        """
        Initialize DocumentDirectorNode.

        Args:
            director: The document director service
            witness: Witness persistence for marks
            bus: Synergy bus for event emission
        """
        self._director = director
        self._witness = witness
        self._bus = bus

    @property
    def handle(self) -> str:
        return "concept.document"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Trust-gated access:
        - developer/operator/cli: Full access
        - architect: Read-only (manifest, status)
        - newcomer/guest: Manifest only
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        # Full access: developers, operators, CLI
        if archetype_lower in ("developer", "operator", "admin", "system", "cli"):
            return (
                "manifest",
                "status",
                "upload",
                "analyze",
                "prompt",
                "capture",
            )

        # Read access: architects, researchers
        if archetype_lower in ("architect", "artist", "researcher", "technical"):
            return ("manifest", "status")

        # Minimal: newcomers, guests
        return ("manifest",)

    @aspect(
        category=AspectCategory.PERCEPTION,
        help="Document director status and statistics",
    )
    async def manifest(self, observer: "Observer | Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Manifest director status.

        AGENTESE: concept.document.manifest

        Note: Currently returns placeholder data. Full implementation would
        query SovereignStore for document counts and statuses.
        """
        # Placeholder implementation - in production would query store
        # The director service doesn't have these methods yet
        return DirectorManifestRendering(
            total_documents=0,
            by_status={},
            recent_uploads=[],
            recent_analyses=[],
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Route aspect invocations to appropriate methods."""

        if aspect == "upload":
            path = kwargs.get("path", "")
            content = kwargs.get("content", "")
            source = kwargs.get("source", "api")

            if not path:
                return {"error": "path required"}
            if not content:
                return {"error": "content required"}

            # Upload via ingestor (director composes ingestor)
            from services.sovereign.types import IngestEvent

            event = IngestEvent.from_content(
                content.encode("utf-8"),
                path,
                source=source,
            )
            ingest_result = await self._director.ingestor.ingest(event, author="api")

            # Emit event
            await self._bus.publish(
                "document.uploaded",
                {
                    "path": path,
                    "version": ingest_result.version,
                    "ingest_mark_id": ingest_result.ingest_mark_id,
                },
            )

            return {
                "path": path,
                "version": ingest_result.version,
                "ingest_mark_id": ingest_result.ingest_mark_id or "",
                "status": "uploaded",
                "analysis_queued": True,  # Would trigger background analysis
            }

        elif aspect == "analyze":
            path = kwargs.get("path", "")
            force = kwargs.get("force", False)

            if not path:
                return {"error": "path required"}

            # Trigger deep analysis
            crystal = await self._director.analyze_deep(path=path, force=force)

            # Emit event
            await self._bus.publish(
                "document.analysis.complete",
                {
                    "path": crystal.entity_path,
                    "status": crystal.status,
                    "claim_count": crystal.claim_count,
                    "ref_count": crystal.ref_count,
                    "placeholder_count": crystal.placeholder_count,
                },
            )

            return {
                "path": crystal.entity_path,
                "status": crystal.status,
                "claim_count": crystal.claim_count,
                "ref_count": crystal.ref_count,
                "placeholder_count": crystal.placeholder_count,
                "analysis_mark_id": None,  # Crystal doesn't track its own mark
                "error": crystal.error,
            }

        elif aspect == "status":
            path = kwargs.get("path", "")

            if not path:
                return {"error": "path required"}

            # Get document status - returns dict
            status_dict = await self._director.get_status(path)

            if not status_dict.get("exists"):
                return {"error": f"Document not found: {path}"}

            return {
                "path": status_dict.get("path", path),
                "status": status_dict.get("analysis_status", "unknown"),
                "version": status_dict.get("version", 0),
                "analysis": status_dict.get("crystal", {}),
                "actions_available": self._compute_actions(status_dict),
            }

        elif aspect == "prompt":
            path = kwargs.get("path", "")

            if not path:
                return {"error": "path required"}

            # Generate execution prompt
            prompt = await self._director.generate_prompt(path)

            # Emit event
            await self._bus.publish(
                "document.prompt.generated",
                {
                    "spec_path": prompt.spec_path,
                    "target_count": len(prompt.targets),
                    "mark_id": prompt.mark_id,
                },
            )

            return {
                "spec_path": prompt.spec_path,
                "targets": prompt.targets,
                "prompt_text": prompt.to_claude_code_task(),
                "mark_id": prompt.mark_id,
            }

        elif aspect == "capture":
            path = kwargs.get("path", "")
            generated_files = kwargs.get("generated_files", {})
            test_passed = kwargs.get("test_passed", False)
            test_output = kwargs.get("test_output")

            if not path:
                return {"error": "path required"}
            if not generated_files:
                return {"error": "generated_files required"}

            # Need to get/create the prompt first
            prompt = await self._director.generate_prompt(path)

            # Build test results
            test_results = TestResults()
            if test_passed:
                for file_path in generated_files:
                    test_results.results[file_path] = {
                        "passed": True,
                        "count": 1,
                        "output": test_output,
                    }

            # Capture execution results
            result = await self._director.capture_execution(
                prompt=prompt,
                generated_files=generated_files,
                test_results=test_results,
                author="api",
            )

            # Emit event
            await self._bus.publish(
                "document.execution.captured",
                {
                    "spec_path": result.spec_path,
                    "captured_count": len(result.captured),
                    "mark_count": len(result.mark_ids),
                },
            )

            # Compute resolved placeholders
            resolved = [p for p in generated_files.keys() if p in prompt.targets]

            return {
                "spec_path": result.spec_path,
                "captured_count": len(result.captured),
                "resolved_placeholders": resolved,
                "evidence_marks": result.mark_ids,
            }

        else:
            return {"error": f"Unknown aspect: {aspect}"}

    def _compute_actions(self, status_dict: dict[str, Any]) -> list[str]:
        """Compute available actions based on document status."""
        actions = []
        analysis_status = status_dict.get("analysis_status", "unknown")
        has_crystal = status_dict.get("has_crystal", False)

        if analysis_status in ("unknown", "pending"):
            actions.append("analyze")
        if analysis_status == "analyzed" and has_crystal:
            actions.extend(["edit", "generate_prompt", "re-analyze"])
        if analysis_status == "stale":
            actions.append("re-analyze")

        return actions


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "DocumentDirectorNode",
    "DirectorManifestRendering",
]
