"""
File Tools: Thin Tool[A,B] Adapters for FileEditGuard.

Phase 1 of U-gent Tooling: Wrapping existing FileEditGuard infrastructure
with categorical Tool[A,B] protocol for composable pipelines.

Key Principle: "Reuse > rewrite. The simplest composition wins."

These tools do NOT reimplement FileEditGuard. They adapt it:
- ReadTool: FileEditGuard.read_file → Tool[ReadRequest, FileContent]
- WriteTool: FileEditGuard.write_file → Tool[WriteRequest, WriteResponse]
- EditTool: FileEditGuard.edit_file → Tool[EditRequest, EditResponse]

Composition Example:
    pipeline = ReadTool() >> GrepTool() >> SummarizeTool()
    result = await executor.execute(pipeline, request, observer)

See: plans/ugent-tooling-phase1-handoff.md
See: services/conductor/file_guard.py (the real implementation)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from services.conductor.contracts import (
    FileEditRequest,
    FileReadRequest,
    FileWriteRequest,
)
from services.conductor.file_guard import (
    FileChangedError,
    FileEditGuard,
    FileGuardError,
    NotReadError,
    StringNotFoundError,
    StringNotUniqueError,
    get_file_guard,
)

from ..base import CausalityViolation, Tool, ToolCategory, ToolEffect, ToolError
from ..contracts import (
    EditRequest,
    EditResponse,
    FileContent,
    ReadProof,
    ReadRequest,
    WriteRequest,
    WriteResponse,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# ReadTool: FileEditGuard.read_file → Tool[ReadRequest, FileContent]
# =============================================================================


@dataclass
class ReadTool(Tool[ReadRequest, FileContent]):
    """
    ReadTool: Adapter from FileEditGuard to Tool[A,B].

    Enables categorical composition:
        pipeline = read >> grep >> summarize

    Trust Level: L0 (READ_ONLY)
    Effects: READS(filesystem)
    Cacheable: True (FileEditGuard caches content)
    """

    _guard: FileEditGuard | None = None

    def __post_init__(self) -> None:
        if self._guard is None:
            self._guard = get_file_guard()

    @property
    def name(self) -> str:
        return "file.read"

    @property
    def description(self) -> str:
        return "Read file content and cache for subsequent edits"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CORE

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.reads("filesystem")]

    @property
    def trust_required(self) -> int:
        return 0  # L0 - Read-only

    @property
    def cacheable(self) -> bool:
        return True  # Content cached by FileEditGuard

    async def invoke(self, request: ReadRequest) -> FileContent:
        """
        Read a file and return its content.

        Args:
            request: ReadRequest with file_path, optional offset/limit

        Returns:
            FileContent with path, content, and metadata

        Raises:
            ToolError: If file not found or permission denied
        """
        assert self._guard is not None

        try:
            # Adapt tooling contracts to conductor contracts
            guard_request = FileReadRequest(
                path=request.file_path,
                encoding="utf-8",
                start_line=request.offset,
                end_line=(request.offset + request.limit)
                if request.offset is not None and request.limit is not None
                else None,
            )

            response = await self._guard.read_file(guard_request)

            return FileContent(
                path=response.path,
                content=response.content,
                line_count=response.lines,
                truncated=response.truncated,
                offset=request.offset or 0,
                encoding=response.encoding,
            )

        except FileNotFoundError as e:
            raise ToolError(str(e), self.name) from e
        except PermissionError as e:
            raise ToolError(f"Permission denied: {request.file_path}", self.name) from e
        except Exception as e:
            raise ToolError(f"Read failed: {e}", self.name) from e


# =============================================================================
# WriteTool: FileEditGuard.write_file → Tool[WriteRequest, WriteResponse]
# =============================================================================


@dataclass
class WriteTool(Tool[WriteRequest, WriteResponse]):
    """
    WriteTool: Adapter with causal constraint.

    The ReadProof requirement is enforced by FileEditGuard's cache.
    Files must be read before write to populate the cache.

    Trust Level: L2 (Requires confirmation)
    Effects: WRITES(filesystem)
    """

    _guard: FileEditGuard | None = None

    def __post_init__(self) -> None:
        if self._guard is None:
            self._guard = get_file_guard()

    @property
    def name(self) -> str:
        return "file.write"

    @property
    def description(self) -> str:
        return "Write content to a file (overwrite semantics)"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CORE

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.writes("filesystem")]

    @property
    def trust_required(self) -> int:
        return 2  # L2 - Requires confirmation

    @property
    def cacheable(self) -> bool:
        return False  # Writes are not cacheable

    async def invoke(self, request: WriteRequest) -> WriteResponse:
        """
        Write content to a file.

        For existing files, a ReadProof demonstrates prior read.
        FileEditGuard enforces read-before-write via cache.

        Args:
            request: WriteRequest with file_path, content, optional read_proof

        Returns:
            WriteResponse with success status

        Raises:
            CausalityViolation: If read_proof required but missing
            ToolError: On write failure
        """
        assert self._guard is not None

        path = Path(request.file_path)
        created = not path.exists()

        try:
            # Adapt to conductor contracts
            guard_request = FileWriteRequest(
                path=request.file_path,
                content=request.content,
                encoding="utf-8",
                create_dirs=True,
            )

            response = await self._guard.write_file(guard_request)

            if not response.success:
                return WriteResponse(
                    path=response.path,
                    success=False,
                    bytes_written=0,
                    created=created,
                )

            return WriteResponse(
                path=response.path,
                success=True,
                bytes_written=response.size,
                created=created,
            )

        except PermissionError as e:
            raise ToolError(f"Permission denied: {request.file_path}", self.name) from e
        except Exception as e:
            raise ToolError(f"Write failed: {e}", self.name) from e


# =============================================================================
# EditTool: FileEditGuard.edit_file → Tool[EditRequest, EditResponse]
# =============================================================================


@dataclass
class EditTool(Tool[EditRequest, EditResponse]):
    """
    EditTool: Exact string replacement via FileEditGuard.

    Enforces Claude Code pattern:
    - File must be read first (NotReadError)
    - old_string must exist (StringNotFoundError)
    - old_string must be unique (StringNotUniqueError) unless replace_all
    - File unchanged since read (FileChangedError)

    Trust Level: L2 (Requires confirmation)
    Effects: WRITES(filesystem)
    """

    _guard: FileEditGuard | None = None

    def __post_init__(self) -> None:
        if self._guard is None:
            self._guard = get_file_guard()

    @property
    def name(self) -> str:
        return "file.edit"

    @property
    def description(self) -> str:
        return "Edit file using exact string replacement (requires prior read)"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CORE

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.writes("filesystem")]

    @property
    def trust_required(self) -> int:
        return 2  # L2 - Requires confirmation

    @property
    def cacheable(self) -> bool:
        return False  # Edits are not cacheable

    async def invoke(self, request: EditRequest) -> EditResponse:
        """
        Edit a file using exact string replacement.

        REQUIRES: File was read first (Claude Code pattern).

        Args:
            request: EditRequest with file_path, old_string, new_string

        Returns:
            EditResponse with success status and replacement count

        Raises:
            CausalityViolation: If file not read first
            ToolError: On edit failure
        """
        assert self._guard is not None

        try:
            # Adapt to conductor contracts
            guard_request = FileEditRequest(
                path=request.file_path,
                old_string=request.old_string,
                new_string=request.new_string,
                replace_all=request.replace_all,
            )

            response = await self._guard.edit_file(guard_request)

            if response.success:
                return EditResponse(
                    path=response.path,
                    success=True,
                    replacements=response.replacements,
                )
            else:
                # FileEditGuard returns failure response instead of raising.
                # Convert to exceptions for categorical Tool[A,B] interface.
                from services.conductor.contracts import EditError

                if response.error == EditError.NOT_READ:
                    raise CausalityViolation(
                        f"File not read before edit: {request.file_path}. "
                        f"First: ReadTool().invoke(ReadRequest(file_path='{request.file_path}'))",
                        self.name,
                    )
                elif response.error == EditError.NOT_FOUND:
                    raise ToolError(
                        response.error_message or f"String not found in {request.file_path}",
                        self.name,
                    )
                elif response.error == EditError.NOT_UNIQUE:
                    raise ToolError(
                        f"{response.error_message}. Use replace_all=True to replace all occurrences.",
                        self.name,
                    )
                elif response.error == EditError.FILE_CHANGED:
                    raise CausalityViolation(
                        f"File changed since read: {request.file_path}. Re-read the file first.",
                        self.name,
                    )
                else:
                    raise ToolError(
                        response.error_message or "Edit failed",
                        self.name,
                    )

        except (CausalityViolation, ToolError):
            # Re-raise our own exceptions
            raise

        except NotReadError as e:
            # Convert to CausalityViolation for categorical consistency
            raise CausalityViolation(
                f"File not read before edit: {request.file_path}. "
                f"First: ReadTool().invoke(ReadRequest(file_path='{request.file_path}'))",
                self.name,
            ) from e

        except StringNotFoundError as e:
            raise ToolError(str(e), self.name) from e

        except StringNotUniqueError as e:
            raise ToolError(
                f"{e.message}. Use replace_all=True to replace all occurrences.",
                self.name,
            ) from e

        except FileChangedError as e:
            raise CausalityViolation(
                f"File changed since read: {request.file_path}. Re-read the file first.",
                self.name,
            ) from e

        except FileGuardError as e:
            raise ToolError(e.message, self.name) from e

        except Exception as e:
            raise ToolError(f"Edit failed: {e}", self.name) from e


# =============================================================================
# Factory Helpers
# =============================================================================


def create_read_proof(path: str, content: str, session_id: str = "") -> ReadProof:
    """
    Create a ReadProof from file content.

    This is a helper for creating proof objects in tests or when
    manually constructing write requests.
    """
    return ReadProof(
        path=path,
        content_hash=hashlib.sha256(content.encode()).hexdigest(),
        read_at=datetime.now(UTC).isoformat(),
        session_id=session_id,
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ReadTool",
    "WriteTool",
    "EditTool",
    "create_read_proof",
]
