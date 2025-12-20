"""
File I/O Contracts: Type definitions for world.file operations.

CLI v7 Phase 1: File I/O Primitives

These contracts define the request/response types for file operations,
following Pattern #13 (Contract-First Types) from crown-jewel-patterns.md.

The contracts enable:
1. Type safety between Python backend and TypeScript frontend
2. Validation at AGENTESE node boundaries
3. Automatic OpenAPI schema generation

All file operations enforce Claude Code's read-before-edit pattern:
- FileReadResponse.cached_at tracks when file was read
- FileEditRequest requires a prior read (enforced by FileEditGuard)
- Exact string replacement prevents merge conflicts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# =============================================================================
# File Read Contracts
# =============================================================================


@dataclass
class FileReadRequest:
    """
    Request to read a file.

    The read operation caches the content for subsequent edits.
    """

    path: str
    encoding: str = "utf-8"
    # Optional: line range for large files
    start_line: int | None = None
    end_line: int | None = None


@dataclass
class FileReadResponse:
    """
    Response from reading a file.

    Contains the file content and metadata needed for edit validation.
    """

    path: str
    content: str
    size: int
    mtime: float  # Last modification time
    encoding: str
    cached_at: float  # When this read occurred (for edit guard)
    lines: int  # Total line count
    truncated: bool = False  # True if content was truncated


# =============================================================================
# File Edit Contracts
# =============================================================================


class EditError(Enum):
    """Error types for file edit operations."""

    NOT_READ = "not_read"  # File wasn't read first
    NOT_FOUND = "not_found"  # Old string not found
    NOT_UNIQUE = "not_unique"  # Old string appears multiple times
    FILE_CHANGED = "file_changed"  # File modified since read
    PERMISSION_DENIED = "permission_denied"  # Write permission denied


@dataclass
class FileEditRequest:
    """
    Request to edit a file using exact string replacement.

    Claude Code pattern: old_string must be unique unless replace_all=True.
    """

    path: str
    old_string: str
    new_string: str
    replace_all: bool = False


@dataclass
class FileEditResponse:
    """
    Response from editing a file.

    Includes diff preview for verification.
    """

    success: bool
    path: str
    replacements: int
    diff_preview: str  # First 500 chars of unified diff
    # Error details (populated on failure)
    error: EditError | None = None
    error_message: str | None = None
    suggestion: str | None = None  # Actionable fix


# =============================================================================
# File Write Contracts
# =============================================================================


@dataclass
class FileWriteRequest:
    """
    Request to write a new file (overwrite semantics).

    This is for new files. For existing files, use edit.
    """

    path: str
    content: str
    encoding: str = "utf-8"
    create_dirs: bool = True  # Create parent directories if missing


@dataclass
class FileWriteResponse:
    """Response from writing a file."""

    success: bool
    path: str
    size: int
    created_dirs: list[str] = field(default_factory=list)
    # Error details
    error: str | None = None


# =============================================================================
# File Search Contracts (Glob/Grep)
# =============================================================================


@dataclass
class FileGlobRequest:
    """Request to glob for files by pattern."""

    pattern: str
    root: str = "."
    max_results: int = 100


@dataclass
class FileGlobResponse:
    """Response from glob operation."""

    pattern: str
    matches: list[str]
    total: int
    truncated: bool = False  # True if results exceeded max


@dataclass
class FileGrepRequest:
    """Request to grep for content."""

    pattern: str  # Regex pattern
    path: str = "."  # Root path
    glob: str | None = None  # Optional file pattern filter
    max_results: int = 50
    context_lines: int = 2


@dataclass
class FileGrepMatch:
    """A single grep match."""

    path: str
    line_number: int
    content: str
    context_before: list[str]
    context_after: list[str]


@dataclass
class FileGrepResponse:
    """Response from grep operation."""

    pattern: str
    matches: list[FileGrepMatch]
    total: int
    files_searched: int
    truncated: bool = False


# =============================================================================
# Output Artifact Contracts
# =============================================================================


class ArtifactType(Enum):
    """Types of artifacts that can be output."""

    CODE = "code"
    DOC = "doc"
    PLAN = "plan"
    TEST = "test"
    CONFIG = "config"


@dataclass
class OutputArtifactRequest:
    """
    Request to write an artifact to disk.

    Artifacts are agent-generated content with optional git commit.
    """

    artifact_type: ArtifactType
    content: str
    path: str
    commit: bool = False
    message: str | None = None  # Commit message (required if commit=True)


@dataclass
class OutputArtifactResponse:
    """Response from artifact output."""

    success: bool
    path: str
    size: int
    artifact_type: ArtifactType
    committed: bool = False
    commit_sha: str | None = None
    # Error details
    error: str | None = None


# =============================================================================
# Cache Entry (Internal)
# =============================================================================


@dataclass
class FileCacheEntry:
    """
    Internal cache entry for read-before-edit validation.

    Pattern #15: FileEditGuard uses this to track read files.
    """

    path: str
    content_hash: str  # SHA256 of content
    mtime: float  # File mtime at read time
    cached_at: datetime  # When we read it
    size: int
    lines: int

    def is_fresh(self, max_age_seconds: float = 300) -> bool:
        """Check if cache entry is still valid."""
        age = (datetime.now() - self.cached_at).total_seconds()
        return age < max_age_seconds

    def to_dict(self) -> dict[str, Any]:
        """Serialize for persistence."""
        return {
            "path": self.path,
            "content_hash": self.content_hash,
            "mtime": self.mtime,
            "cached_at": self.cached_at.isoformat(),
            "size": self.size,
            "lines": self.lines,
        }


# =============================================================================
# Synergy Event Payloads
# =============================================================================


@dataclass
class FileEditedPayload:
    """Payload for FILE_EDITED synergy event."""

    path: str
    old_size: int
    new_size: int
    replacements: int
    editor: str  # Agent ID that made the edit


@dataclass
class FileCreatedPayload:
    """Payload for FILE_CREATED synergy event."""

    path: str
    size: int
    artifact_type: ArtifactType | None
    creator: str  # Agent ID that created the file
    committed: bool = False


__all__ = [
    # Read
    "FileReadRequest",
    "FileReadResponse",
    # Edit
    "EditError",
    "FileEditRequest",
    "FileEditResponse",
    # Write
    "FileWriteRequest",
    "FileWriteResponse",
    # Search
    "FileGlobRequest",
    "FileGlobResponse",
    "FileGrepRequest",
    "FileGrepMatch",
    "FileGrepResponse",
    # Artifact
    "ArtifactType",
    "OutputArtifactRequest",
    "OutputArtifactResponse",
    # Internal
    "FileCacheEntry",
    # Synergy
    "FileEditedPayload",
    "FileCreatedPayload",
]
