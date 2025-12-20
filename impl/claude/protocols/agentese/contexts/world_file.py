"""
AGENTESE World File Context: Safe file manipulation via Claude Code patterns.

CLI v7 Phase 1: File I/O Primitives

This implements the file manipulation primitives puppetized from Claude Code:
- world.file.read → Read file and cache for edits
- world.file.edit → Exact string replacement (requires prior read)
- world.file.write → Write new file
- world.file.glob → Pattern-based file discovery
- world.file.grep → Content search

Key Patterns:
- READ-BEFORE-EDIT: You must understand before you modify
- EXACT REPLACEMENT: No regex, find exact string
- UNIQUE MATCH: old_string must appear exactly once (or use replace_all)

The FileEditGuard enforces these patterns:
1. Edit fails if file wasn't read first
2. Edit fails if old_string not found
3. Edit fails if old_string not unique (unless replace_all)
4. Edit fails if file changed since read

AGENTESE: world.file.*

Principle Alignment:
- Ethical: Prevents blind file modifications
- Composable: Each operation is a pure function
- Joy-Inducing: Warm error messages guide correct usage
"""

from __future__ import annotations

import fnmatch
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from opentelemetry import trace

from services.conductor.contracts import (
    EditError,
    FileEditRequest,
    FileEditResponse,
    FileGlobRequest,
    FileGlobResponse,
    FileGrepMatch,
    FileGrepRequest,
    FileGrepResponse,
    FileReadRequest,
    FileReadResponse,
    FileWriteRequest,
    FileWriteResponse,
)
from services.conductor.file_guard import (
    FileEditGuard,
    FileGuardError,
    get_file_guard,
)

from ..affordances import AspectCategory, Effect, aspect
from ..contract import Contract, Response
from ..node import BaseLogosNode, BasicRendering, Renderable
from ..registry import node

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt

logger = logging.getLogger(__name__)


def _get_agent_id(observer: Any) -> str:
    """Safely extract agent ID from observer."""
    try:
        meta = getattr(observer, "meta", None)
        if meta is not None:
            return getattr(meta, "name", "unknown")
    except Exception:
        pass
    return "unknown"


# OTEL tracer
_tracer = trace.get_tracer("kgents.file")

# File affordances
FILE_AFFORDANCES: tuple[str, ...] = (
    "manifest",
    "read",
    "edit",
    "write",
    "glob",
    "grep",
)


@node(
    "world.file",
    description="Safe file manipulation with read-before-edit guard",
    singleton=True,
    contracts={
        "read": Response(FileReadResponse),
        "edit": Contract(FileEditRequest, FileEditResponse),
        "write": Contract(FileWriteRequest, FileWriteResponse),
        "glob": Contract(FileGlobRequest, FileGlobResponse),
        "grep": Contract(FileGrepRequest, FileGrepResponse),
    },
    examples=[
        ("read", {"path": "src/main.py"}, "Read a Python file"),
        (
            "edit",
            {"path": "src/main.py", "old_string": "def foo", "new_string": "def bar"},
            "Rename a function",
        ),
        ("glob", {"pattern": "**/*.py"}, "Find all Python files"),
    ],
)
@dataclass
class FileNode(BaseLogosNode):
    """
    world.file - Safe file manipulation node.

    Puppetizes Claude Code patterns for agent-safe file I/O:
    - Read-before-edit enforced
    - Exact string replacement
    - Warm error messages

    The guard is injected via DI (Pattern #15: No Hollow Services).
    """

    _handle: str = "world.file"
    _guard: FileEditGuard | None = None

    @property
    def handle(self) -> str:
        return self._handle

    def set_guard(self, guard: FileEditGuard) -> None:
        """Inject the FileEditGuard (DI pattern)."""
        self._guard = guard

    def _get_guard(self) -> FileEditGuard:
        """Get the guard, using singleton if not injected."""
        if self._guard is None:
            self._guard = get_file_guard()
        return self._guard

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """File affordances available to all archetypes."""
        return FILE_AFFORDANCES

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """View file node status and capabilities."""
        guard = self._get_guard()
        stats = guard.get_statistics()

        content_lines = [
            "File I/O: Claude Code Patterns",
            "",
            "Capabilities:",
            "  - read: Read file and cache for edits",
            "  - edit: Exact string replacement",
            "  - write: Write new file",
            "  - glob: Pattern-based file discovery",
            "  - grep: Content search",
            "",
            "The Claude Code Pattern:",
            "  1. READ file before editing",
            "  2. Use EXACT string replacement",
            "  3. old_string must be UNIQUE",
            "",
            "Cache Statistics:",
            f"  - Files cached: {stats['cache_size']}",
            f"  - Total reads: {stats['reads']}",
            f"  - Total edits: {stats['edits']}",
            f"  - Cache hits: {stats['cache_hits']}",
        ]

        return BasicRendering(
            summary="File I/O: Claude Code Patterns",
            content="\n".join(content_lines),
            metadata={
                "affordances": list(FILE_AFFORDANCES),
                "statistics": stats,
            },
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle file-specific aspects."""
        match aspect:
            case "read":
                return await self._read(observer, **kwargs)
            case "edit":
                return await self._edit(observer, **kwargs)
            case "write":
                return await self._write(observer, **kwargs)
            case "glob":
                return await self._glob(observer, **kwargs)
            case "grep":
                return await self._grep(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    # =========================================================================
    # Read Aspect
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("filesystem")],
        help="Read a file and cache for subsequent edits",
        examples=[
            "world.file.read[path='src/main.py']",
            "world.file.read[path='README.md', encoding='utf-8']",
        ],
    )
    async def _read(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Read a file and cache for subsequent edits.

        Args:
            path: File path to read
            encoding: Text encoding (default: utf-8)
            start_line: Optional start line for partial read
            end_line: Optional end line for partial read

        Returns:
            File content with metadata (path, content, size, lines, cached_at)
        """
        with _tracer.start_as_current_span("file.read") as span:
            path = kwargs.get("path")

            if not path:
                return {
                    "status": "error",
                    "error": "path_required",
                    "message": "path parameter is required",
                    "suggestion": "world.file.read[path='src/main.py']",
                }

            span.set_attribute("file.path", path)

            try:
                request = FileReadRequest(
                    path=path,
                    encoding=kwargs.get("encoding", "utf-8"),
                    start_line=kwargs.get("start_line"),
                    end_line=kwargs.get("end_line"),
                )

                guard = self._get_guard()
                response = await guard.read_file(
                    request,
                    agent_id=_get_agent_id(observer),
                )

                return {
                    "status": "success",
                    "path": response.path,
                    "content": response.content,
                    "size": response.size,
                    "lines": response.lines,
                    "mtime": response.mtime,
                    "cached_at": response.cached_at,
                    "truncated": response.truncated,
                }

            except FileNotFoundError:
                return {
                    "status": "error",
                    "error": "not_found",
                    "message": f"File not found: {path}",
                    "suggestion": f"Check the path exists: world.file.glob[pattern='**/{Path(path).name}']",
                }
            except PermissionError:
                return {
                    "status": "error",
                    "error": "permission_denied",
                    "message": f"Permission denied: {path}",
                }
            except Exception as e:
                logger.exception(f"Failed to read file: {path}")
                return {
                    "status": "error",
                    "error": "read_failed",
                    "message": str(e),
                }

    # =========================================================================
    # Edit Aspect
    # =========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("filesystem")],
        help="Edit file using exact string replacement (requires prior read)",
        examples=[
            "world.file.edit[path='src/main.py', old_string='def foo', new_string='def bar']",
            "world.file.edit[path='config.py', old_string='DEBUG = True', new_string='DEBUG = False']",
        ],
    )
    async def _edit(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Edit a file using exact string replacement.

        REQUIRES: File was read first (enforces Claude Code pattern).

        Args:
            path: File path to edit
            old_string: Exact string to find (must be unique unless replace_all)
            new_string: Replacement string
            replace_all: Replace all occurrences (default: False)

        Returns:
            Edit result with diff preview on success, or error with suggestion
        """
        with _tracer.start_as_current_span("file.edit") as span:
            path = kwargs.get("path")
            old_string = kwargs.get("old_string")
            new_string = kwargs.get("new_string")
            replace_all = kwargs.get("replace_all", False)

            # Validate required params
            if not path:
                return {
                    "status": "error",
                    "error": "path_required",
                    "message": "path parameter is required",
                }
            if not old_string:
                return {
                    "status": "error",
                    "error": "old_string_required",
                    "message": "old_string parameter is required",
                }
            if new_string is None:  # Allow empty string
                return {
                    "status": "error",
                    "error": "new_string_required",
                    "message": "new_string parameter is required",
                }

            span.set_attribute("file.path", path)

            try:
                request = FileEditRequest(
                    path=path,
                    old_string=old_string,
                    new_string=new_string,
                    replace_all=replace_all,
                )

                guard = self._get_guard()
                response = await guard.edit_file(
                    request,
                    agent_id=_get_agent_id(observer),
                )

                if response.success:
                    return {
                        "status": "success",
                        "path": response.path,
                        "replacements": response.replacements,
                        "diff_preview": response.diff_preview,
                    }
                else:
                    return {
                        "status": "error",
                        "error": response.error.value if response.error else "unknown",
                        "message": response.error_message,
                        "suggestion": response.suggestion,
                    }

            except FileGuardError as e:
                return {
                    "status": "error",
                    "error": e.error_type.value,
                    "message": e.message,
                    "suggestion": e.suggestion,
                }
            except Exception as e:
                logger.exception(f"Failed to edit file: {path}")
                return {
                    "status": "error",
                    "error": "edit_failed",
                    "message": str(e),
                }

    # =========================================================================
    # Write Aspect
    # =========================================================================

    @aspect(
        category=AspectCategory.MUTATION,
        effects=[Effect.WRITES("filesystem")],
        help="Write a new file (overwrite semantics)",
        examples=[
            "world.file.write[path='output.txt', content='Hello, world!']",
            "world.file.write[path='new/dir/file.py', content='# New file', create_dirs=True]",
        ],
    )
    async def _write(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Write a new file (or overwrite existing).

        For existing files, consider using edit for safer modifications.

        Args:
            path: File path to write
            content: Content to write
            encoding: Text encoding (default: utf-8)
            create_dirs: Create parent directories if missing (default: True)

        Returns:
            Write result with path and size
        """
        with _tracer.start_as_current_span("file.write") as span:
            path = kwargs.get("path")
            content = kwargs.get("content")

            if not path:
                return {
                    "status": "error",
                    "error": "path_required",
                    "message": "path parameter is required",
                }
            if content is None:
                return {
                    "status": "error",
                    "error": "content_required",
                    "message": "content parameter is required",
                }

            span.set_attribute("file.path", path)

            try:
                request = FileWriteRequest(
                    path=path,
                    content=content,
                    encoding=kwargs.get("encoding", "utf-8"),
                    create_dirs=kwargs.get("create_dirs", True),
                )

                guard = self._get_guard()
                response = await guard.write_file(
                    request,
                    agent_id=_get_agent_id(observer),
                )

                if response.success:
                    return {
                        "status": "success",
                        "path": response.path,
                        "size": response.size,
                        "created_dirs": response.created_dirs,
                    }
                else:
                    return {
                        "status": "error",
                        "error": "write_failed",
                        "message": response.error,
                    }

            except Exception as e:
                logger.exception(f"Failed to write file: {path}")
                return {
                    "status": "error",
                    "error": "write_failed",
                    "message": str(e),
                }

    # =========================================================================
    # Glob Aspect
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("filesystem")],
        help="Find files matching a glob pattern",
        examples=[
            "world.file.glob[pattern='**/*.py']",
            "world.file.glob[pattern='src/**/*.tsx', root='.']",
        ],
    )
    async def _glob(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Find files matching a glob pattern.

        Args:
            pattern: Glob pattern (e.g., "**/*.py")
            root: Root directory (default: ".")
            max_results: Maximum results to return (default: 100)

        Returns:
            List of matching file paths
        """
        with _tracer.start_as_current_span("file.glob") as span:
            pattern = kwargs.get("pattern")

            if not pattern:
                return {
                    "status": "error",
                    "error": "pattern_required",
                    "message": "pattern parameter is required",
                    "suggestion": "world.file.glob[pattern='**/*.py']",
                }

            root = Path(kwargs.get("root", "."))
            max_results = kwargs.get("max_results", 100)

            span.set_attribute("glob.pattern", pattern)
            span.set_attribute("glob.root", str(root))

            try:
                path_matches = list(root.glob(pattern))
                matches: list[str] = [str(m) for m in path_matches if m.is_file()]
                total = len(matches)
                truncated = total > max_results

                if truncated:
                    matches = matches[:max_results]

                return {
                    "status": "success",
                    "pattern": pattern,
                    "matches": matches,
                    "total": total,
                    "truncated": truncated,
                }

            except Exception as e:
                logger.exception(f"Glob failed: {pattern}")
                return {
                    "status": "error",
                    "error": "glob_failed",
                    "message": str(e),
                }

    # =========================================================================
    # Grep Aspect
    # =========================================================================

    @aspect(
        category=AspectCategory.PERCEPTION,
        effects=[Effect.READS("filesystem")],
        help="Search file contents for a pattern",
        examples=[
            "world.file.grep[pattern='TODO', path='src']",
            "world.file.grep[pattern='def\\s+\\w+', glob='**/*.py']",
        ],
    )
    async def _grep(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Search file contents for a regex pattern.

        Args:
            pattern: Regex pattern to search for
            path: Root path to search (default: ".")
            glob: Optional file pattern filter (e.g., "*.py")
            max_results: Maximum matches to return (default: 50)
            context_lines: Lines of context to include (default: 2)

        Returns:
            List of matches with file path, line number, and context
        """
        with _tracer.start_as_current_span("file.grep") as span:
            pattern = kwargs.get("pattern")

            if not pattern:
                return {
                    "status": "error",
                    "error": "pattern_required",
                    "message": "pattern parameter is required",
                }

            root = Path(kwargs.get("path", "."))
            file_glob = kwargs.get("glob", "**/*")
            max_results = kwargs.get("max_results", 50)
            context_lines = kwargs.get("context_lines", 2)

            span.set_attribute("grep.pattern", pattern)
            span.set_attribute("grep.root", str(root))

            try:
                regex = re.compile(pattern)
            except re.error as e:
                return {
                    "status": "error",
                    "error": "invalid_pattern",
                    "message": f"Invalid regex: {e}",
                }

            matches: list[dict[str, Any]] = []
            files_searched = 0

            try:
                for file_path in root.glob(file_glob):
                    if not file_path.is_file():
                        continue

                    files_searched += 1

                    try:
                        content = file_path.read_text()
                        lines = content.splitlines()

                        for i, line in enumerate(lines):
                            if regex.search(line):
                                # Get context
                                start = max(0, i - context_lines)
                                end = min(len(lines), i + context_lines + 1)

                                matches.append(
                                    {
                                        "path": str(file_path),
                                        "line_number": i + 1,
                                        "content": line,
                                        "context_before": lines[start:i],
                                        "context_after": lines[i + 1 : end],
                                    }
                                )

                                if len(matches) >= max_results:
                                    break

                    except (UnicodeDecodeError, PermissionError):
                        # Skip binary or inaccessible files
                        continue

                    if len(matches) >= max_results:
                        break

                return {
                    "status": "success",
                    "pattern": pattern,
                    "matches": matches,
                    "total": len(matches),
                    "files_searched": files_searched,
                    "truncated": len(matches) >= max_results,
                }

            except Exception as e:
                logger.exception(f"Grep failed: {pattern}")
                return {
                    "status": "error",
                    "error": "grep_failed",
                    "message": str(e),
                }


# Factory function
def create_file_node() -> FileNode:
    """Create a FileNode instance."""
    return FileNode()


__all__ = [
    "FileNode",
    "FILE_AFFORDANCES",
    "create_file_node",
]
