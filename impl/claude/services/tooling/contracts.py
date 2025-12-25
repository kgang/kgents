"""
Tool AGENTESE Contracts: Type-safe request/response definitions.

These dataclasses define the contracts for all Tool aspects.
They serve as the single source of truth for BE/FE type alignment.

Pattern 13 (Contract-First Types):
- @node(contracts={...}) is the authority
- Frontend discovers contracts at build time
- Type drift caught in CI

See: docs/skills/crown-jewel-patterns.md
See: services/witness/contracts.py (reference)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

# =============================================================================
# File Tool Contracts
# =============================================================================


@dataclass
class ReadRequest:
    """Request for file.read aspect."""

    file_path: str  # Absolute path to file
    offset: int | None = None  # Line offset for large files
    limit: int | None = None  # Line limit for large files


@dataclass
class FileContent:
    """Response for file.read aspect."""

    path: str
    content: str
    line_count: int
    truncated: bool = False
    offset: int = 0
    encoding: str = "utf-8"


@dataclass
class ReadProof:
    """
    Evidence that a file was read before write.

    Causal constraint: writes require proof of prior read.
    This prevents blind overwrites and ensures the agent
    understands what it's modifying.
    """

    path: str
    content_hash: str  # SHA-256 of content at read time
    read_at: str  # ISO datetime string
    session_id: str = ""

    def is_valid_for(self, target_path: str) -> bool:
        """Check if proof is valid for a target path."""
        return self.path == target_path


@dataclass
class WriteRequest:
    """Request for file.write aspect."""

    file_path: str
    content: str
    read_proof: ReadProof | None = None  # Required for existing files


@dataclass
class WriteResponse:
    """Response for file.write aspect."""

    path: str
    success: bool
    bytes_written: int
    created: bool  # True if file was created
    backup_path: str | None = None  # Rollback checkpoint


@dataclass
class EditRequest:
    """Request for file.edit aspect (old_string/new_string replacement)."""

    file_path: str
    old_string: str
    new_string: str
    replace_all: bool = False  # Replace all occurrences
    read_proof: ReadProof | None = None


@dataclass
class EditResponse:
    """Response for file.edit aspect."""

    path: str
    success: bool
    replacements: int  # Number of replacements made
    backup_path: str | None = None


# =============================================================================
# Search Tool Contracts
# =============================================================================


@dataclass
class GlobQuery:
    """Request for search.glob aspect."""

    pattern: str  # Glob pattern (e.g., "**/*.py")
    path: str | None = None  # Base directory (defaults to cwd)
    limit: int = 100  # Max results


@dataclass
class GlobResponse:
    """Response for search.glob aspect."""

    pattern: str
    matches: list[str]  # Matching paths
    count: int
    truncated: bool = False


@dataclass
class GrepQuery:
    """Request for search.grep aspect."""

    pattern: str  # Regex pattern
    path: str | None = None  # File or directory
    glob: str | None = None  # Glob filter (e.g., "*.py")
    output_mode: str = "files_with_matches"  # content | files_with_matches | count
    context_lines: int = 0  # Lines before/after (-C)
    case_insensitive: bool = False
    limit: int = 100


@dataclass
class GrepMatch:
    """A single grep match."""

    file_path: str
    line_number: int | None = None
    content: str | None = None
    context_before: list[str] = field(default_factory=list)
    context_after: list[str] = field(default_factory=list)


@dataclass
class GrepResponse:
    """Response for search.grep aspect."""

    pattern: str
    matches: list[GrepMatch]
    count: int
    output_mode: str
    truncated: bool = False


# =============================================================================
# System Tool Contracts
# =============================================================================


@dataclass
class BashCommand:
    """Request for system.bash aspect."""

    command: str
    description: str = ""  # 5-10 word description
    timeout_ms: int = 120_000  # Default 2 minutes
    run_in_background: bool = False
    working_directory: str | None = None


@dataclass
class BashResult:
    """Response for system.bash aspect."""

    command: str
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    truncated: bool = False
    background_task_id: str | None = None  # If run_in_background


@dataclass
class KillShellRequest:
    """Request for system.kill aspect."""

    shell_id: str


@dataclass
class KillShellResponse:
    """Response for system.kill aspect."""

    shell_id: str
    success: bool
    message: str = ""


# =============================================================================
# Web Tool Contracts
# =============================================================================


@dataclass
class WebFetchRequest:
    """Request for web.fetch aspect."""

    url: str
    prompt: str  # What to extract from the page


@dataclass
class WebFetchResponse:
    """Response for web.fetch aspect."""

    url: str
    content: str  # Processed/extracted content
    cached: bool = False
    redirect_url: str | None = None


@dataclass
class WebSearchQuery:
    """Request for web.search aspect."""

    query: str
    allowed_domains: list[str] = field(default_factory=list)
    blocked_domains: list[str] = field(default_factory=list)


@dataclass
class WebSearchResult:
    """A single search result."""

    title: str
    url: str
    snippet: str


@dataclass
class WebSearchResponse:
    """Response for web.search aspect."""

    query: str
    results: list[WebSearchResult]
    count: int


# =============================================================================
# Task Tool Contracts (self.tools.task.*)
# =============================================================================


@dataclass
class TodoItem:
    """A single todo item."""

    content: str
    status: str  # pending | in_progress | completed
    active_form: str  # Present continuous form


@dataclass
class TodoListRequest:
    """Request for task.list aspect."""

    status_filter: str | None = None  # Filter by status


@dataclass
class TodoListResponse:
    """Response for task.list aspect."""

    todos: list[TodoItem]
    count: int


@dataclass
class TodoCreateRequest:
    """Request for task.create aspect."""

    todos: list[TodoItem]


@dataclass
class TodoCreateResponse:
    """Response for task.create aspect."""

    success: bool
    count: int


@dataclass
class TodoUpdateRequest:
    """Request for task.update aspect."""

    index: int
    status: str  # pending | in_progress | completed


@dataclass
class TodoUpdateResponse:
    """Response for task.update aspect."""

    success: bool
    todo: TodoItem | None = None


# =============================================================================
# Mode Tool Contracts (self.tools.mode.*)
# =============================================================================


@dataclass
class EnterPlanModeRequest:
    """Request for mode.plan aspect."""

    pass  # No args needed


@dataclass
class EnterPlanModeResponse:
    """Response for mode.plan aspect."""

    success: bool
    message: str = ""


@dataclass
class ExitPlanModeRequest:
    """Request for mode.execute aspect."""

    launch_swarm: bool = False
    teammate_count: int = 0


@dataclass
class ExitPlanModeResponse:
    """Response for mode.execute aspect."""

    success: bool
    approved: bool = False
    message: str = ""


@dataclass
class ClarifyRequest:
    """Request for clarify (AskUserQuestion) aspect."""

    questions: list[dict[str, Any]]  # Complex question structure


@dataclass
class ClarifyResponse:
    """Response for clarify aspect."""

    answers: dict[str, str]


# =============================================================================
# Portal Tool Contracts
# =============================================================================


@dataclass(frozen=True)
class PortalRequest:
    """Request to open a portal in chat."""

    # The destination path (file, spec, symbol)
    destination: str
    # Edge type (e.g., "references", "implements", "context")
    edge_type: str = "context"
    # Access level for chat participants
    access: str = "read"  # "read" | "readwrite"
    # Optional preview lines (how much to show inline)
    preview_lines: int = 10
    # Auto-expand in chat?
    auto_expand: bool = True


@dataclass
class PortalDestination:
    """A portal destination with content."""

    path: str
    title: str | None = None
    preview: str | None = None
    exists: bool = True


@dataclass
class PortalEmission:
    """A portal emitted into the chat stream."""

    portal_id: str
    destination: str
    edge_type: str
    access: str  # "read" | "readwrite"
    # Resolved content for preview
    content_preview: str | None = None
    content_full: str | None = None
    line_count: int = 0
    # Metadata
    exists: bool = True
    auto_expand: bool = True
    emitted_at: str = ""  # ISO datetime

    def to_dict(self) -> dict[str, Any]:
        """Serialize for wire transfer."""
        return {
            "portal_id": self.portal_id,
            "destination": self.destination,
            "edge_type": self.edge_type,
            "access": self.access,
            "content_preview": self.content_preview,
            "content_full": self.content_full,
            "line_count": self.line_count,
            "exists": self.exists,
            "auto_expand": self.auto_expand,
            "emitted_at": self.emitted_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PortalEmission":
        """Deserialize from wire format."""
        return cls(
            portal_id=data["portal_id"],
            destination=data["destination"],
            edge_type=data["edge_type"],
            access=data["access"],
            content_preview=data.get("content_preview"),
            content_full=data.get("content_full"),
            line_count=data.get("line_count", 0),
            exists=data.get("exists", True),
            auto_expand=data.get("auto_expand", True),
            emitted_at=data.get("emitted_at", ""),
        )


@dataclass(frozen=True)
class PortalWriteRequest:
    """Request to write through an open portal."""

    portal_id: str
    content: str
    # Optional: specific line range to update
    start_line: int | None = None
    end_line: int | None = None


@dataclass
class PortalWriteResponse:
    """Response from writing through a portal."""

    portal_id: str
    success: bool
    bytes_written: int
    new_content_hash: str
    error_message: str = ""


# =============================================================================
# Manifest Contracts
# =============================================================================


@dataclass
class ToolMetaItem:
    """Tool metadata for manifest response."""

    name: str
    description: str
    category: str
    trust_required: int
    effects: list[str]
    cacheable: bool
    streaming: bool


@dataclass
class ToolManifestResponse:
    """Response for world.tools.manifest aspect."""

    total_tools: int
    tools_by_category: dict[str, int]
    tools: list[ToolMetaItem]


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # File tools
    "ReadRequest",
    "FileContent",
    "ReadProof",
    "WriteRequest",
    "WriteResponse",
    "EditRequest",
    "EditResponse",
    # Search tools
    "GlobQuery",
    "GlobResponse",
    "GrepQuery",
    "GrepMatch",
    "GrepResponse",
    # System tools
    "BashCommand",
    "BashResult",
    "KillShellRequest",
    "KillShellResponse",
    # Web tools
    "WebFetchRequest",
    "WebFetchResponse",
    "WebSearchQuery",
    "WebSearchResult",
    "WebSearchResponse",
    # Task tools
    "TodoItem",
    "TodoListRequest",
    "TodoListResponse",
    "TodoCreateRequest",
    "TodoCreateResponse",
    "TodoUpdateRequest",
    "TodoUpdateResponse",
    # Mode tools
    "EnterPlanModeRequest",
    "EnterPlanModeResponse",
    "ExitPlanModeRequest",
    "ExitPlanModeResponse",
    "ClarifyRequest",
    "ClarifyResponse",
    # Portal tools
    "PortalRequest",
    "PortalDestination",
    "PortalEmission",
    "PortalWriteRequest",
    "PortalWriteResponse",
    # Manifest
    "ToolMetaItem",
    "ToolManifestResponse",
]
