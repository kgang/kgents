"""
Portal Tools: Emit portal references with read/write access in chat.

Portal tokens are expandable hyperedges: @[edge_type -> destination]
In chat, portals auto-expand to show content inline with read/write access
for all chat participants.

Key Principle: "The doc comes to you."

These tools enable:
- PortalTool: Emit a portal reference into the chat stream
- PortalWriteTool: Write through an open portal

Integration:
- Uses FileEditGuard for actual file operations
- Tracks open portals in session state
- Emits witness marks for portal actions

See: spec/protocols/portal-token.md
See: services/witness/portal_marks.py
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from services.conductor.file_guard import FileEditGuard, get_file_guard

from ..base import CausalityViolation, Tool, ToolCategory, ToolEffect, ToolError
from ..contracts import (
    PortalEmission,
    PortalRequest,
    PortalWriteRequest,
    PortalWriteResponse,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Portal Session State (In-memory tracking)
# =============================================================================


@dataclass
class OpenPortal:
    """Tracks an open portal in the current session."""

    portal_id: str
    destination: str
    edge_type: str
    access: str  # "read" | "readwrite"
    content_hash: str  # SHA-256 at open time
    opened_at: datetime
    last_accessed: datetime


# Global portal registry (in-memory, session-scoped)
_OPEN_PORTALS: dict[str, OpenPortal] = {}


def get_open_portals() -> dict[str, OpenPortal]:
    """Get currently open portals."""
    return _OPEN_PORTALS


def reset_open_portals() -> None:
    """Reset portal registry (for testing)."""
    global _OPEN_PORTALS
    _OPEN_PORTALS = {}


# =============================================================================
# PortalTool: Emit a portal reference into chat
# =============================================================================


@dataclass
class PortalTool(Tool[PortalRequest, PortalEmission]):
    """
    PortalTool: Emit a portal reference into the chat stream.

    When invoked, opens a "portal" to the destination that:
    - Shows preview content inline in chat
    - Provides read/write access to all participants
    - Syncs changes back to the source

    Trust Level: L1 (READS) or L2 (WRITES) based on access level
    Effects: READS(destination) or WRITES(destination)
    """

    _guard: FileEditGuard | None = None

    def __post_init__(self) -> None:
        if self._guard is None:
            self._guard = get_file_guard()

    @property
    def name(self) -> str:
        return "portal.emit"

    @property
    def description(self) -> str:
        return "Open a portal to a file/resource, providing inline read/write access in chat"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ORCHESTRATION

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.reads("filesystem")]

    @property
    def trust_required(self) -> int:
        return 1  # L1 - Reads files (writes require L2 via PortalWriteTool)

    @property
    def cacheable(self) -> bool:
        return False  # Portal state is session-dependent

    async def invoke(self, request: PortalRequest) -> PortalEmission:
        """
        Emit a portal into the chat stream.

        Args:
            request: PortalRequest with destination, edge_type, access

        Returns:
            PortalEmission with content preview and metadata

        Raises:
            ToolError: If destination not found or permission denied
        """
        assert self._guard is not None

        destination = Path(request.destination)

        # Check if destination exists
        if not destination.exists():
            return PortalEmission(
                portal_id=str(uuid.uuid4()),
                destination=request.destination,
                edge_type=request.edge_type,
                access=request.access,
                content_preview=None,
                content_full=None,
                line_count=0,
                exists=False,
                auto_expand=request.auto_expand,
                emitted_at=datetime.now(UTC).isoformat(),
            )

        # Read the file
        try:
            from services.conductor.contracts import FileReadRequest

            read_request = FileReadRequest(
                path=request.destination,
                encoding="utf-8",
            )

            response = await self._guard.read_file(read_request)
            content = response.content

            # Generate portal ID
            portal_id = str(uuid.uuid4())

            # Create preview (first N lines)
            lines = content.split("\n")
            preview_lines_list = lines[: request.preview_lines]
            preview = "\n".join(preview_lines_list)

            # Track open portal
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            now = datetime.now(UTC)
            _OPEN_PORTALS[portal_id] = OpenPortal(
                portal_id=portal_id,
                destination=request.destination,
                edge_type=request.edge_type,
                access=request.access,
                content_hash=content_hash,
                opened_at=now,
                last_accessed=now,
            )

            return PortalEmission(
                portal_id=portal_id,
                destination=request.destination,
                edge_type=request.edge_type,
                access=request.access,
                content_preview=preview if len(lines) > request.preview_lines else None,
                content_full=content,
                line_count=len(lines),
                exists=True,
                auto_expand=request.auto_expand,
                emitted_at=now.isoformat(),
            )

        except FileNotFoundError as e:
            raise ToolError(f"Destination not found: {request.destination}", self.name) from e
        except PermissionError as e:
            raise ToolError(
                f"Permission denied: {request.destination}", self.name
            ) from e
        except Exception as e:
            raise ToolError(f"Portal emission failed: {e}", self.name) from e


# =============================================================================
# PortalWriteTool: Write through an open portal
# =============================================================================


@dataclass
class PortalWriteTool(Tool[PortalWriteRequest, PortalWriteResponse]):
    """
    PortalWriteTool: Write through an open portal.

    Allows chat participants to write back through a portal that was
    opened with readwrite access.

    Trust Level: L2 (WRITES)
    Effects: WRITES(filesystem)
    """

    _guard: FileEditGuard | None = None

    def __post_init__(self) -> None:
        if self._guard is None:
            self._guard = get_file_guard()

    @property
    def name(self) -> str:
        return "portal.write"

    @property
    def description(self) -> str:
        return "Write content through an open portal"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.ORCHESTRATION

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.writes("filesystem")]

    @property
    def trust_required(self) -> int:
        return 2  # L2 - Writes files

    @property
    def cacheable(self) -> bool:
        return False  # Writes are not cacheable

    async def invoke(self, request: PortalWriteRequest) -> PortalWriteResponse:
        """
        Write through an open portal.

        Args:
            request: PortalWriteRequest with portal_id and content

        Returns:
            PortalWriteResponse with success status

        Raises:
            CausalityViolation: If portal not open or read-only
            ToolError: On write failure
        """
        assert self._guard is not None

        # Check portal exists
        if request.portal_id not in _OPEN_PORTALS:
            raise CausalityViolation(
                f"Portal not open: {request.portal_id}. "
                f"First: PortalTool().invoke(PortalRequest(destination='...'))",
                self.name,
            )

        portal = _OPEN_PORTALS[request.portal_id]

        # Check write access
        if portal.access != "readwrite":
            raise CausalityViolation(
                f"Portal is read-only: {request.portal_id}. "
                f"Open with access='readwrite' to enable writes.",
                self.name,
            )

        # Write the file
        try:
            from services.conductor.contracts import FileWriteRequest

            write_request = FileWriteRequest(
                path=portal.destination,
                content=request.content,
                encoding="utf-8",
                create_dirs=False,  # Portal destination must exist
            )

            response = await self._guard.write_file(write_request)

            if not response.success:
                return PortalWriteResponse(
                    portal_id=request.portal_id,
                    success=False,
                    bytes_written=0,
                    new_content_hash="",
                    error_message="Write failed",
                )

            # Update portal state
            new_hash = hashlib.sha256(request.content.encode()).hexdigest()
            portal.content_hash = new_hash
            portal.last_accessed = datetime.now(UTC)

            return PortalWriteResponse(
                portal_id=request.portal_id,
                success=True,
                bytes_written=response.size,
                new_content_hash=new_hash,
            )

        except PermissionError as e:
            raise ToolError(
                f"Permission denied: {portal.destination}", self.name
            ) from e
        except Exception as e:
            raise ToolError(f"Portal write failed: {e}", self.name) from e


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "PortalTool",
    "PortalWriteTool",
    "OpenPortal",
    "get_open_portals",
    "reset_open_portals",
]
