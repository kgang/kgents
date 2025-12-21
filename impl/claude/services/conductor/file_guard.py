"""
FileEditGuard: Read-before-edit enforcement.

CLI v7 Phase 1: File I/O Primitives

This implements Pattern #15 (No Hollow Services) from crown-jewel-patterns.md:
- FileEditGuard MUST be injected via DI, never instantiated directly
- Guards file edits by requiring a prior read
- Caches file state for change detection
- Emits synergy events for cross-jewel awareness

The Claude Code Pattern:
1. Agent must READ file before editing (understanding before modification)
2. Edits use EXACT string replacement (no ambiguous regex)
3. Old string must be UNIQUE in file (prevents wrong match)
4. Stale reads are rejected (file may have changed)

Usage:
    guard = get_file_guard()  # From DI container

    # Read first
    response = await guard.read_file("/path/to/file.py")

    # Now edit is allowed
    result = await guard.edit_file(
        path="/path/to/file.py",
        old_string="def foo",
        new_string="def bar",
    )

Teaching:
    gotcha: Edits without prior read fail with EditError.NOT_READ.
            The guard returns a structured error response rather than raising,
            so you MUST check response.success before assuming the edit worked.
            (Evidence: test_file_guard.py::TestEditOperations::test_edit_requires_prior_read)

    gotcha: Non-unique old_string returns EditError.NOT_UNIQUE, not an exception.
            Use replace_all=True when you intentionally want to replace all
            occurrences. The error response includes a suggestion to help the user.
            (Evidence: test_file_guard.py::TestEditOperations::test_edit_string_not_unique)
"""

from __future__ import annotations

import asyncio
import difflib
import hashlib
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

from opentelemetry import trace

from .contracts import (
    EditError,
    FileCacheEntry,
    FileEditRequest,
    FileEditResponse,
    FileReadRequest,
    FileReadResponse,
    FileWriteRequest,
    FileWriteResponse,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# OTEL tracer
_tracer = trace.get_tracer("kgents.file_guard")


# =============================================================================
# Errors
# =============================================================================


class FileGuardError(Exception):
    """Base error for file guard operations."""

    def __init__(
        self,
        error_type: EditError,
        message: str,
        suggestion: str | None = None,
    ):
        self.error_type = error_type
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)


class NotReadError(FileGuardError):
    """File was not read before edit attempt."""

    def __init__(self, path: str):
        super().__init__(
            error_type=EditError.NOT_READ,
            message=f"File not read: {path}",
            suggestion=f"First: world.file.read[path='{path}']",
        )


class StringNotFoundError(FileGuardError):
    """Old string not found in file."""

    def __init__(self, path: str, old_string: str):
        preview = old_string[:50] + "..." if len(old_string) > 50 else old_string
        super().__init__(
            error_type=EditError.NOT_FOUND,
            message=f"String not found in {path}: '{preview}'",
            suggestion="Read the file again to verify the exact content",
        )


class StringNotUniqueError(FileGuardError):
    """Old string appears multiple times."""

    def __init__(self, path: str, old_string: str, count: int):
        preview = old_string[:50] + "..." if len(old_string) > 50 else old_string
        super().__init__(
            error_type=EditError.NOT_UNIQUE,
            message=f"String appears {count} times in {path}: '{preview}'",
            suggestion="Provide more context to make the match unique, or use replace_all=True",
        )


class FileChangedError(FileGuardError):
    """File was modified since last read."""

    def __init__(self, path: str):
        super().__init__(
            error_type=EditError.FILE_CHANGED,
            message=f"File changed since read: {path}",
            suggestion=f"Read the file again: world.file.read[path='{path}']",
        )


# =============================================================================
# FileEditGuard
# =============================================================================


@dataclass
class FileEditGuard:
    """
    Enforces Claude Code's read-before-edit pattern.

    Pattern #15 (No Hollow Services):
    - This guard MUST be obtained from the DI container
    - Never instantiate directly in application code
    - Inject via @node(dependencies=("file_guard",))

    Thread Safety:
    - The cache is protected by an asyncio lock
    - Safe for concurrent access from multiple agents
    """

    # Configuration
    cache_ttl_seconds: float = 300.0  # 5 minutes
    max_cached_files: int = 100  # LRU eviction threshold

    # Internal state
    _cache: dict[str, FileCacheEntry] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    # Statistics
    _reads: int = field(default=0, init=False)
    _edits: int = field(default=0, init=False)
    _cache_hits: int = field(default=0, init=False)
    _cache_misses: int = field(default=0, init=False)

    # Event emitter (injected)
    _emit_event: Any = field(default=None, init=False)

    def set_event_emitter(self, emitter: Any) -> None:
        """Inject the synergy event emitter."""
        self._emit_event = emitter

    # === Read Operations ===

    async def read_file(
        self,
        request: FileReadRequest | str,
        *,
        agent_id: str = "unknown",
    ) -> FileReadResponse:
        """
        Read a file and cache for subsequent edits.

        Args:
            request: FileReadRequest or path string
            agent_id: ID of the requesting agent (for auditing)

        Returns:
            FileReadResponse with content and metadata
        """
        if isinstance(request, str):
            request = FileReadRequest(path=request)

        with _tracer.start_as_current_span("file_guard.read") as span:
            span.set_attribute("file.path", request.path)
            span.set_attribute("agent.id", agent_id)

            path = Path(request.path)

            # Read content
            try:
                content = path.read_text(encoding=request.encoding)
            except FileNotFoundError:
                span.set_attribute("error", "file_not_found")
                raise FileNotFoundError(f"File not found: {request.path}")
            except PermissionError:
                span.set_attribute("error", "permission_denied")
                raise PermissionError(f"Permission denied: {request.path}")

            # Apply line range if specified
            lines = content.split("\n")
            total_lines = len(lines)
            truncated = False

            if request.start_line is not None or request.end_line is not None:
                start = request.start_line or 0
                end = request.end_line or total_lines
                lines = lines[start:end]
                content = "\n".join(lines)
                truncated = True

            # Get file metadata
            stat = path.stat()
            mtime = stat.st_mtime

            # Compute content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            # Cache the entry
            cache_entry = FileCacheEntry(
                path=str(path.absolute()),
                content_hash=content_hash,
                mtime=mtime,
                cached_at=datetime.now(),
                size=len(content),
                lines=total_lines,
            )

            async with self._lock:
                self._cache[request.path] = cache_entry
                self._reads += 1

                # LRU eviction
                if len(self._cache) > self.max_cached_files:
                    await self._evict_oldest()

            span.set_attribute("file.size", len(content))
            span.set_attribute("file.lines", total_lines)

            logger.debug(f"Read file: {request.path} ({len(content)} bytes)")

            return FileReadResponse(
                path=request.path,
                content=content,
                size=len(content),
                mtime=mtime,
                encoding=request.encoding,
                cached_at=cache_entry.cached_at.timestamp(),
                lines=total_lines,
                truncated=truncated,
            )

    # === Edit Operations ===

    async def edit_file(
        self,
        request: FileEditRequest,
        *,
        agent_id: str = "unknown",
    ) -> FileEditResponse:
        """
        Edit a file using exact string replacement.

        Claude Code pattern:
        1. File MUST have been read first
        2. old_string must be found in file
        3. old_string must be unique (unless replace_all=True)
        4. File must not have changed since read

        Args:
            request: FileEditRequest with old/new strings
            agent_id: ID of the requesting agent

        Returns:
            FileEditResponse with success/failure details
        """
        with _tracer.start_as_current_span("file_guard.edit") as span:
            span.set_attribute("file.path", request.path)
            span.set_attribute("agent.id", agent_id)
            span.set_attribute("replace_all", request.replace_all)

            try:
                # 1. Check if file was read
                await self._require_read(request.path)

                # 2. Read current content
                path = Path(request.path)
                content = path.read_text()

                # 3. Check file hasn't changed
                async with self._lock:
                    cache_entry = self._cache.get(request.path)

                if cache_entry:
                    current_mtime = path.stat().st_mtime
                    if current_mtime != cache_entry.mtime:
                        raise FileChangedError(request.path)

                # 4. Find occurrences
                count = content.count(request.old_string)
                span.set_attribute("match.count", count)

                if count == 0:
                    raise StringNotFoundError(request.path, request.old_string)

                if count > 1 and not request.replace_all:
                    raise StringNotUniqueError(request.path, request.old_string, count)

                # 5. Perform replacement
                old_size = len(content)
                if request.replace_all:
                    new_content = content.replace(request.old_string, request.new_string)
                    replacements = count
                else:
                    new_content = content.replace(request.old_string, request.new_string, 1)
                    replacements = 1

                # 6. Generate diff preview
                diff_preview = self._generate_diff_preview(content, new_content, request.path)

                # 7. Write back
                path.write_text(new_content)
                new_size = len(new_content)

                # 8. Update cache
                await self._update_cache_after_edit(request.path, new_content)

                self._edits += 1

                span.set_attribute("file.old_size", old_size)
                span.set_attribute("file.new_size", new_size)
                span.set_attribute("edit.replacements", replacements)

                logger.info(f"Edited file: {request.path} ({replacements} replacement(s))")

                # 9. Emit synergy event
                await self._emit_file_edited_event(
                    path=request.path,
                    old_size=old_size,
                    new_size=new_size,
                    replacements=replacements,
                    agent_id=agent_id,
                )

                return FileEditResponse(
                    success=True,
                    path=request.path,
                    replacements=replacements,
                    diff_preview=diff_preview,
                )

            except FileGuardError as e:
                span.set_attribute("error.type", e.error_type.value)
                return FileEditResponse(
                    success=False,
                    path=request.path,
                    replacements=0,
                    diff_preview="",
                    error=e.error_type,
                    error_message=e.message,
                    suggestion=e.suggestion,
                )

    # === Write Operations ===

    async def write_file(
        self,
        request: FileWriteRequest,
        *,
        agent_id: str = "unknown",
    ) -> FileWriteResponse:
        """
        Write a new file (or overwrite existing).

        Note: For existing files, use edit_file for safer modifications.

        Args:
            request: FileWriteRequest with content
            agent_id: ID of the requesting agent

        Returns:
            FileWriteResponse with success/failure details
        """
        with _tracer.start_as_current_span("file_guard.write") as span:
            span.set_attribute("file.path", request.path)
            span.set_attribute("agent.id", agent_id)

            try:
                path = Path(request.path)
                created_dirs: list[str] = []

                # Create parent directories if needed
                if request.create_dirs and not path.parent.exists():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    created_dirs = [
                        str(p) for p in path.parents if not p.exists() or p == path.parent
                    ]

                # Write content
                path.write_text(request.content, encoding=request.encoding)
                size = len(request.content)

                # Add to cache
                await self.read_file(request.path, agent_id=agent_id)

                span.set_attribute("file.size", size)
                span.set_attribute("dirs.created", len(created_dirs))

                logger.info(f"Wrote file: {request.path} ({size} bytes)")

                # Emit synergy event
                await self._emit_file_created_event(
                    path=request.path,
                    size=size,
                    agent_id=agent_id,
                )

                return FileWriteResponse(
                    success=True,
                    path=request.path,
                    size=size,
                    created_dirs=created_dirs,
                )

            except PermissionError:
                return FileWriteResponse(
                    success=False,
                    path=request.path,
                    size=0,
                    error="Permission denied",
                )
            except Exception as e:
                return FileWriteResponse(
                    success=False,
                    path=request.path,
                    size=0,
                    error=str(e),
                )

    # === Cache Management ===

    async def can_edit(self, path: str) -> bool:
        """Check if a file can be edited (has been read recently)."""
        async with self._lock:
            entry = self._cache.get(path)
            if entry is None:
                return False
            return entry.is_fresh(self.cache_ttl_seconds)

    async def invalidate(self, path: str) -> bool:
        """Remove a file from cache."""
        async with self._lock:
            if path in self._cache:
                del self._cache[path]
                return True
            return False

    async def clear_cache(self) -> int:
        """Clear entire cache. Returns number of entries cleared."""
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def get_statistics(self) -> dict[str, Any]:
        """Get guard statistics."""
        return {
            "reads": self._reads,
            "edits": self._edits,
            "cache_size": len(self._cache),
            "cache_hits": self._cache_hits,
            "cache_misses": self._cache_misses,
        }

    # === Private Helpers ===

    async def _require_read(self, path: str) -> FileCacheEntry:
        """Ensure file was read. Raises NotReadError if not."""
        async with self._lock:
            entry = self._cache.get(path)

            if entry is None:
                self._cache_misses += 1
                raise NotReadError(path)

            if not entry.is_fresh(self.cache_ttl_seconds):
                self._cache_misses += 1
                raise NotReadError(path)

            self._cache_hits += 1
            return entry

    async def _evict_oldest(self) -> None:
        """Evict oldest cache entry (LRU policy)."""
        if not self._cache:
            return

        oldest_path = min(
            self._cache.keys(),
            key=lambda p: self._cache[p].cached_at,
        )
        del self._cache[oldest_path]
        logger.debug(f"Evicted from cache: {oldest_path}")

    async def _update_cache_after_edit(self, path: str, new_content: str) -> None:
        """Update cache entry after successful edit."""
        stat = Path(path).stat()
        content_hash = hashlib.sha256(new_content.encode()).hexdigest()

        async with self._lock:
            self._cache[path] = FileCacheEntry(
                path=path,
                content_hash=content_hash,
                mtime=stat.st_mtime,
                cached_at=datetime.now(),
                size=len(new_content),
                lines=new_content.count("\n") + 1,
            )

    def _generate_diff_preview(
        self, old: str, new: str, filename: str, max_chars: int = 500
    ) -> str:
        """Generate unified diff preview."""
        diff = difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
        )
        diff_str = "".join(diff)
        if len(diff_str) > max_chars:
            return diff_str[:max_chars] + "\n... (truncated)"
        return diff_str

    async def _emit_file_edited_event(
        self,
        path: str,
        old_size: int,
        new_size: int,
        replacements: int,
        agent_id: str,
    ) -> None:
        """Emit FILE_EDITED synergy event."""
        if self._emit_event is None:
            return

        try:
            await self._emit_event(
                event_type="file_edited",
                payload={
                    "path": path,
                    "old_size": old_size,
                    "new_size": new_size,
                    "replacements": replacements,
                    "editor": agent_id,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to emit FILE_EDITED event: {e}")

    async def _emit_file_created_event(
        self,
        path: str,
        size: int,
        agent_id: str,
    ) -> None:
        """Emit FILE_CREATED synergy event."""
        if self._emit_event is None:
            return

        try:
            await self._emit_event(
                event_type="file_created",
                payload={
                    "path": path,
                    "size": size,
                    "creator": agent_id,
                },
            )
        except Exception as e:
            logger.warning(f"Failed to emit FILE_CREATED event: {e}")


# =============================================================================
# Singleton Management (Pattern #15)
# =============================================================================

_guard: FileEditGuard | None = None


def get_file_guard() -> FileEditGuard:
    """
    Get or create the singleton FileEditGuard.

    Pattern #15: Use this for DI registration, not direct instantiation.
    """
    global _guard
    if _guard is None:
        _guard = FileEditGuard()
    return _guard


def reset_file_guard() -> None:
    """Reset the singleton (for testing)."""
    global _guard
    _guard = None


__all__ = [
    "FileEditGuard",
    "FileGuardError",
    "NotReadError",
    "StringNotFoundError",
    "StringNotUniqueError",
    "FileChangedError",
    "get_file_guard",
    "reset_file_guard",
]
