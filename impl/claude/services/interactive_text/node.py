"""
Interactive Text AGENTESE Node.

Registers Interactive Text service with the AGENTESE Universal Gateway.

AGENTESE Paths:
- self.document.manifest - Service status and capabilities
- self.document.parse - Parse markdown to SceneGraph
- self.document.task.toggle - Toggle task checkbox with TraceWitness

The Metaphysical Fullstack Pattern (AD-009):
- The protocol IS the API
- Documents are live control surfaces
- "The text IS the interface"

See: spec/protocols/interactive-text.md

Teaching:
    gotcha: The node depends on "interactive_text_service" in the DI container. If
            this dependency isn't registered in providers.py, the node will be
            SILENTLY SKIPPED during gateway setup. No error, just missing paths.
            (Evidence: test_agentese_path.py::TestAGENTESEPathTokenCreation::test_create_token)

    gotcha: Archetype-based affordances: developer/operator/admin/editor get full
            access (parse + task_toggle). architect/researcher get parse only.
            Everyone else (guest) gets parse only. Case-insensitive matching.
            (Evidence: test_agentese_path.py::TestAGENTESEPathActions::test_right_click_admin_has_edit)

    gotcha: _invoke_aspect returns DICT, not Renderable. The rendering classes
            (ParseRendering, TaskToggleRendering) call .to_dict() immediately.
            This is for JSON serialization compatibility with the API layer.
            (Evidence: test_agentese_path.py::TestAGENTESEPathProjection::test_project_json)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from protocols.agentese.node import BaseLogosNode, Renderable
from protocols.agentese.registry import node

from .service import (
    DocumentManifestResponse,
    InteractiveTextService,
    ParseRequest,
    ParseResponse,
    TaskToggleRequest,
    TaskToggleResponse,
)

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt
    from protocols.agentese.node import AgentMeta, Observer


# =============================================================================
# Rendering Classes (for manifest)
# =============================================================================


@dataclass
class DocumentManifestRendering:
    """Renderable wrapper for document manifest response."""

    response: DocumentManifestResponse

    def to_dict(self) -> dict[str, Any]:
        return self.response.to_dict()

    def to_text(self) -> str:
        return (
            f"Interactive Text Service\n"
            f"Status: {self.response.status}\n"
            f"Token Types: {', '.join(self.response.token_types)}\n"
            f"Features: {', '.join(self.response.features)}"
        )


@dataclass
class ParseRendering:
    """Renderable wrapper for parse response."""

    response: ParseResponse

    def to_dict(self) -> dict[str, Any]:
        return self.response.to_dict()

    def to_text(self) -> str:
        types_str = ", ".join(f"{k}:{v}" for k, v in self.response.token_types.items())
        return f"Parsed {self.response.token_count} tokens: {types_str}"


@dataclass
class TaskToggleRendering:
    """Renderable wrapper for task toggle response."""

    response: TaskToggleResponse

    def to_dict(self) -> dict[str, Any]:
        return self.response.to_dict()

    def to_text(self) -> str:
        if not self.response.success:
            return f"Toggle failed: {self.response.error}"

        state = "checked" if self.response.new_state else "unchecked"
        file_note = " (file updated)" if self.response.file_updated else ""
        return (
            f"Task toggled to {state}{file_note}\n"
            f"Description: {self.response.task_description}\n"
            f"TraceWitness: {self.response.trace_witness_id}"
        )


# =============================================================================
# AGENTESE Node Registration
# =============================================================================


@node(
    "self.document",
    description="Interactive Text - documents as live control surfaces",
    dependencies=("interactive_text_service",),
    examples=[
        ("parse", {"text": "- [x] Done\n- [ ] Todo"}, "Parse task list"),
        ("task_toggle", {"text": "- [ ] Todo", "line_number": 1}, "Toggle task"),
    ],
)
class InteractiveTextNode(BaseLogosNode):
    """
    AGENTESE node for Interactive Text service.

    Exposes document parsing and task toggling via AGENTESE protocol.
    All interactions capture TraceWitness for verification.

    Paths:
    - self.document.manifest - Service status
    - self.document.parse - Markdown -> SceneGraph
    - self.document.task.toggle - Toggle with TraceWitness
    """

    def __init__(self, interactive_text_service: InteractiveTextService) -> None:
        """
        Initialize with injected service.

        Args:
            interactive_text_service: The InteractiveTextService instance
                (injected by DI container via dependencies=(...))
        """
        self._service = interactive_text_service

    @property
    def handle(self) -> str:
        """The AGENTESE path to this node."""
        return "self.document"

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """
        Return archetype-specific affordances.

        Developer/Editor: Full access to parse and toggle
        Guest/Viewer: Parse only (read-only)
        """
        archetype_lower = archetype.lower() if archetype else "guest"

        if archetype_lower in ("developer", "operator", "admin", "editor"):
            return ("parse", "task_toggle")
        elif archetype_lower in ("architect", "researcher"):
            return ("parse",)

        # Guest: read-only parsing
        return ("parse",)

    async def manifest(self, observer: "Umwelt[Any, Any]", **kwargs: Any) -> Renderable:
        """
        Return service status and capabilities.

        AGENTESE: self.document.manifest
        """
        response = await self._service.manifest()
        return DocumentManifestRendering(response=response)

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """
        Route aspect invocations to service methods.

        Args:
            aspect: The aspect name (parse, task_toggle)
            observer: Observer context
            **kwargs: Aspect-specific arguments

        Returns:
            Aspect-specific result (dict for JSON serialization)
        """
        match aspect:
            case "parse":
                text = kwargs.get("text", "")
                layout_mode = kwargs.get("layout_mode", "COMFORTABLE")

                parse_response = await self._service.parse_document(
                    text=text,
                    layout_mode=layout_mode,
                )
                return ParseRendering(response=parse_response).to_dict()

            case "task_toggle":
                # Build request from kwargs
                request = TaskToggleRequest(
                    file_path=kwargs.get("file_path"),
                    task_id=kwargs.get("task_id"),
                    text=kwargs.get("text"),
                    line_number=kwargs.get("line_number"),
                )

                # Extract observer for trace witness
                from services.interactive_text.contracts import (
                    Observer as ITObserver,
                    ObserverDensity,
                    ObserverRole,
                )

                it_observer = ITObserver(
                    id=getattr(observer, "id", "unknown"),
                    archetype=getattr(getattr(observer, "dna", None), "archetype", "guest"),
                    density=ObserverDensity.COMFORTABLE,
                    role=ObserverRole.EDITOR,
                    capabilities=frozenset(),
                )

                toggle_response = await self._service.toggle_task(
                    request=request,
                    observer=it_observer,
                )
                return TaskToggleRendering(response=toggle_response).to_dict()

            case _:
                # Unknown aspect - return error
                return {
                    "error": f"Unknown aspect: {aspect}",
                    "available": ["manifest", "parse", "task_toggle"],
                }


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "InteractiveTextNode",
    "DocumentManifestRendering",
    "ParseRendering",
    "TaskToggleRendering",
]
