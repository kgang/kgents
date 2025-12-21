"""
Interactive Text Service: Crown Jewel Business Logic.

This service implements the core functionality for Interactive Text:
- Parse markdown to SceneGraph for frontend rendering
- Toggle task checkboxes with file mutation and TraceWitness capture
- Coordinate between parser, sheaf, and AGENTESE nodes

AGENTESE Paths:
- self.document.manifest - Service status
- self.document.parse - Markdown -> SceneGraph
- self.document.task.toggle - Toggle with TraceWitness

The Metaphysical Fullstack Pattern (AD-009):
- The text IS the interface
- Documents are live control surfaces
- Toggles capture constructive proofs

See: spec/protocols/interactive-text.md

Teaching:
    gotcha: Toggle requires EITHER file_path OR text, not both. When using file mode,
            you need file_path + (task_id OR line_number). Text mode needs text + line_number.
            Mixing modes or missing required params returns error response with success=False.
            (Evidence: test_properties.py::TestProperty6DocumentPolynomialStateValidity)

    gotcha: Line numbers are 1-indexed for human ergonomics. The toggle_task_at_line()
            method converts to 0-indexed internally. Off-by-one errors are common when
            directly manipulating the lines list—always use (line_number - 1).
            (Evidence: test_parser.py::TestTokenRecognition::test_task_checkbox_checked)

    gotcha: TraceWitness is ALWAYS captured on successful toggle, even in text mode where
            no file is modified. The trace captures previous_state → new_state for audit.
            If you need to skip trace capture, you must use the internal _toggle_task_at_line()
            method directly (not recommended for production use).
            (Evidence: test_tokens_base.py::TestTraceWitness::test_create_witness)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from .contracts import Observer, ObserverDensity, ObserverRole
from .parser import ParsedDocument, parse_markdown, render_markdown
from .sheaf import DocumentSheaf, Edit
from .tokens.base import ExecutionTrace, TraceWitness

if TYPE_CHECKING:
    from protocols.agentese.projection.scene import SceneGraph


# =============================================================================
# Request/Response Types
# =============================================================================


@dataclass(frozen=True)
class ParseRequest:
    """Request to parse markdown text.

    Attributes:
        text: Markdown text to parse
        layout_mode: Density mode for SceneGraph (default: COMFORTABLE)
    """

    text: str
    layout_mode: str = "COMFORTABLE"

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "layout_mode": self.layout_mode}


@dataclass(frozen=True)
class ParseResponse:
    """Response from parse operation.

    Attributes:
        scene_graph: The SceneGraph for frontend rendering
        token_count: Number of tokens detected
        token_types: Breakdown by token type
    """

    scene_graph: dict[str, Any]
    token_count: int
    token_types: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "scene_graph": self.scene_graph,
            "token_count": self.token_count,
            "token_types": self.token_types,
        }


@dataclass(frozen=True)
class TaskToggleRequest:
    """Request to toggle a task checkbox.

    Attributes:
        file_path: Path to the markdown file
        task_id: ID of the task to toggle (format: "task:start:end")
        text: Alternative: raw markdown text (for in-memory toggle)
        line_number: Alternative: line number of the task (1-indexed)
    """

    file_path: str | None = None
    task_id: str | None = None
    text: str | None = None
    line_number: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "task_id": self.task_id,
            "text": self.text,
            "line_number": self.line_number,
        }


@dataclass(frozen=True)
class TaskToggleResponse:
    """Response from task toggle operation.

    Attributes:
        success: Whether toggle succeeded
        new_state: New checkbox state (True = checked)
        task_description: Description of the toggled task
        trace_witness_id: ID of the captured TraceWitness
        file_updated: Whether the file was modified on disk
        error: Error message if toggle failed
    """

    success: bool
    new_state: bool = False
    task_description: str = ""
    trace_witness_id: str | None = None
    file_updated: bool = False
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "new_state": self.new_state,
            "task_description": self.task_description,
            "trace_witness_id": self.trace_witness_id,
            "file_updated": self.file_updated,
            "error": self.error,
        }


@dataclass(frozen=True)
class DocumentManifestResponse:
    """Response for manifest (status) operation.

    Attributes:
        status: Service status ("healthy", "degraded", "error")
        token_types: Supported token types
        features: Available features
    """

    status: str = "healthy"
    token_types: tuple[str, ...] = (
        "agentese_path",
        "task_checkbox",
        "image",
        "code_block",
        "principle_ref",
        "requirement_ref",
    )
    features: tuple[str, ...] = (
        "parse",
        "task_toggle",
        "roundtrip_fidelity",
        "trace_witness",
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "token_types": list(self.token_types),
            "features": list(self.features),
        }


# =============================================================================
# Service Implementation
# =============================================================================


class InteractiveTextService:
    """
    Interactive Text Crown Jewel Service.

    Provides the core business logic for document-as-interface:
    - Parsing markdown to SceneGraph
    - Toggling task checkboxes with file mutation
    - Capturing TraceWitness for verification

    Per AD-009 (Metaphysical Fullstack), this service:
    - Lives at services/interactive_text/
    - Is exposed via AGENTESE node (self.document)
    - Uses D-gent for persistence (via DocumentSheaf)
    """

    # Pattern for matching task checkboxes in markdown
    TASK_PATTERN = re.compile(r"^(- \[)([ xX])(\] .+)$", re.MULTILINE)

    def __init__(self) -> None:
        """Initialize the service."""
        # Sheaf instances per document path (for multi-view coherence)
        self._sheafs: dict[str, DocumentSheaf] = {}

    async def manifest(self) -> DocumentManifestResponse:
        """
        Get service status and capabilities.

        Returns:
            DocumentManifestResponse with status and features
        """
        return DocumentManifestResponse()

    async def parse_document(
        self,
        text: str,
        layout_mode: str = "COMFORTABLE",
    ) -> ParseResponse:
        """
        Parse markdown text to SceneGraph for frontend rendering.

        Args:
            text: Markdown text to parse
            layout_mode: Density mode (COMPACT, COMFORTABLE, SPACIOUS)

        Returns:
            ParseResponse with SceneGraph and token statistics

        Example:
            >>> service = InteractiveTextService()
            >>> response = await service.parse_document("Check `self.brain`")
            >>> response.token_count
            1
        """
        from protocols.agentese.projection.scene import LayoutMode
        from protocols.agentese.projection.tokens_to_scene import markdown_to_scene_graph

        # Map layout mode string to enum
        mode_map = {
            "COMPACT": LayoutMode.COMPACT,
            "COMFORTABLE": LayoutMode.COMFORTABLE,
            "SPACIOUS": LayoutMode.SPACIOUS,
        }
        mode = mode_map.get(layout_mode.upper(), LayoutMode.COMFORTABLE)

        # Parse to SceneGraph
        scene = await markdown_to_scene_graph(text, layout_mode=mode)

        # Count tokens by type
        token_types: dict[str, int] = {}
        for node in scene.nodes:
            kind = node.metadata.get("meaning_token_kind", "PLAIN_TEXT")
            token_types[kind] = token_types.get(kind, 0) + 1

        # Calculate token count (non-plain-text tokens)
        token_count = sum(
            count for kind, count in token_types.items() if kind != "PLAIN_TEXT"
        )

        return ParseResponse(
            scene_graph=scene.to_dict(),
            token_count=token_count,
            token_types=token_types,
        )

    async def toggle_task(
        self,
        request: TaskToggleRequest,
        observer: Observer | None = None,
    ) -> TaskToggleResponse:
        """
        Toggle a task checkbox and capture TraceWitness.

        Supports two modes:
        1. File mode: Toggle task in a file on disk (file_path + task_id/line_number)
        2. Text mode: Toggle task in provided text (text + line_number)

        Args:
            request: TaskToggleRequest with file_path/text and task_id/line_number
            observer: Observer for trace witness (optional)

        Returns:
            TaskToggleResponse with new state and trace_witness_id

        Example:
            >>> service = InteractiveTextService()
            >>> request = TaskToggleRequest(
            ...     file_path="/path/to/doc.md",
            ...     line_number=5
            ... )
            >>> response = await service.toggle_task(request)
            >>> response.success
            True
        """
        observer = observer or Observer(
            id=str(uuid4()),
            archetype="developer",
            density=ObserverDensity.COMFORTABLE,
            role=ObserverRole.EDITOR,
            capabilities=frozenset(),
        )

        # Determine mode and get content
        if request.file_path:
            return await self._toggle_task_in_file(request, observer)
        elif request.text:
            return await self._toggle_task_in_text(request, observer)
        else:
            return TaskToggleResponse(
                success=False,
                error="Either file_path or text must be provided",
            )

    async def _toggle_task_in_file(
        self,
        request: TaskToggleRequest,
        observer: Observer,
    ) -> TaskToggleResponse:
        """Toggle task in a file on disk."""
        file_path = Path(request.file_path)  # type: ignore

        if not file_path.exists():
            return TaskToggleResponse(
                success=False,
                error=f"File not found: {file_path}",
            )

        # Read file content
        content = file_path.read_text()

        # Find task by task_id or line_number
        if request.task_id:
            # task_id format: "task:start:end"
            parts = request.task_id.split(":")
            if len(parts) == 3:
                start = int(parts[1])
                end = int(parts[2])
                result = self._toggle_task_at_position(content, start, end)
            else:
                return TaskToggleResponse(
                    success=False,
                    error=f"Invalid task_id format: {request.task_id}",
                )
        elif request.line_number:
            result = self._toggle_task_at_line(content, request.line_number)
        else:
            return TaskToggleResponse(
                success=False,
                error="Either task_id or line_number required for file mode",
            )

        if not result["success"]:
            return TaskToggleResponse(
                success=False,
                error=result.get("error", "Toggle failed"),
            )

        # Write updated content to file
        file_path.write_text(result["new_content"])

        # Capture TraceWitness
        trace = ExecutionTrace(
            agent_path="self.document.task.toggle",
            operation="toggle",
            input_data={
                "file_path": str(file_path),
                "previous_state": not result["new_state"],
            },
            output_data={
                "new_state": result["new_state"],
                "task_description": result["description"],
            },
            observer_id=observer.id,
        )

        witness = TraceWitness(
            id=str(uuid4()),
            trace=trace,
        )

        return TaskToggleResponse(
            success=True,
            new_state=result["new_state"],
            task_description=result["description"],
            trace_witness_id=witness.id,
            file_updated=True,
        )

    async def _toggle_task_in_text(
        self,
        request: TaskToggleRequest,
        observer: Observer,
    ) -> TaskToggleResponse:
        """Toggle task in provided text (no file mutation)."""
        if not request.line_number:
            return TaskToggleResponse(
                success=False,
                error="line_number required for text mode",
            )

        result = self._toggle_task_at_line(request.text or "", request.line_number)

        if not result["success"]:
            return TaskToggleResponse(
                success=False,
                error=result.get("error", "Toggle failed"),
            )

        # Capture TraceWitness
        trace = ExecutionTrace(
            agent_path="self.document.task.toggle",
            operation="toggle",
            input_data={"previous_state": not result["new_state"]},
            output_data={
                "new_state": result["new_state"],
                "task_description": result["description"],
            },
            observer_id=observer.id,
        )

        witness = TraceWitness(
            id=str(uuid4()),
            trace=trace,
        )

        return TaskToggleResponse(
            success=True,
            new_state=result["new_state"],
            task_description=result["description"],
            trace_witness_id=witness.id,
            file_updated=False,
        )

    def _toggle_task_at_line(
        self,
        content: str,
        line_number: int,
    ) -> dict[str, Any]:
        """Toggle task checkbox at specific line number."""
        lines = content.split("\n")

        if line_number < 1 or line_number > len(lines):
            return {"success": False, "error": f"Line {line_number} out of range"}

        line = lines[line_number - 1]  # Convert to 0-indexed
        match = self.TASK_PATTERN.match(line)

        if not match:
            return {"success": False, "error": f"No task checkbox at line {line_number}"}

        # Toggle the checkbox
        prefix, checkbox, suffix = match.groups()
        new_checkbox = "x" if checkbox == " " else " "
        new_line = f"{prefix}{new_checkbox}{suffix}"

        lines[line_number - 1] = new_line
        new_content = "\n".join(lines)

        # Extract description (remove "- [x] " prefix)
        description = suffix[2:] if suffix.startswith("] ") else suffix

        return {
            "success": True,
            "new_content": new_content,
            "new_state": new_checkbox == "x",
            "description": description,
        }

    def _toggle_task_at_position(
        self,
        content: str,
        start: int,
        end: int,
    ) -> dict[str, Any]:
        """Toggle task checkbox at specific character position."""
        task_text = content[start:end]
        match = self.TASK_PATTERN.match(task_text)

        if not match:
            return {"success": False, "error": f"No task checkbox at position {start}:{end}"}

        # Toggle the checkbox
        prefix, checkbox, suffix = match.groups()
        new_checkbox = "x" if checkbox == " " else " "
        new_task_text = f"{prefix}{new_checkbox}{suffix}"

        new_content = content[:start] + new_task_text + content[end:]

        # Extract description
        description = suffix[2:] if suffix.startswith("] ") else suffix

        return {
            "success": True,
            "new_content": new_content,
            "new_state": new_checkbox == "x",
            "description": description,
        }


# =============================================================================
# Factory Function (for DI registration)
# =============================================================================


def get_interactive_text_service() -> InteractiveTextService:
    """
    Factory function for InteractiveTextService.

    Used by the DI container for service registration.

    Returns:
        InteractiveTextService instance
    """
    return InteractiveTextService()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Request/Response types
    "ParseRequest",
    "ParseResponse",
    "TaskToggleRequest",
    "TaskToggleResponse",
    "DocumentManifestResponse",
    # Service
    "InteractiveTextService",
    "get_interactive_text_service",
]
