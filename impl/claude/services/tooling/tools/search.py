"""
Search Tools: Thin Tool[A,B] Adapters for Glob and Grep.

Phase 1 of U-gent Tooling: Search operations that delegate to
world.file.glob and world.file.grep implementations.

Key Principle: "Reuse > rewrite. The simplest composition wins."

These tools provide categorical composition for search pipelines:
- GlobTool: Pattern-based file discovery
- GrepTool: Content search with regex

Composition Example:
    pipeline = GlobTool() >> ReadTool() >> GrepTool()
    result = await executor.execute(pipeline, request, observer)

Note: Unlike file tools that delegate to FileEditGuard, search tools
implement their logic directly (matching world_file.py implementation)
because FileEditGuard doesn't handle search operations.

See: plans/ugent-tooling-phase1-handoff.md
See: protocols/agentese/contexts/world_file.py (reference implementation)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from ..base import Tool, ToolCategory, ToolEffect, ToolError
from ..contracts import (
    GlobQuery,
    GlobResponse,
    GrepMatch,
    GrepQuery,
    GrepResponse,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# GlobTool: Pattern-Based File Discovery
# =============================================================================


@dataclass
class GlobTool(Tool[GlobQuery, GlobResponse]):
    """
    GlobTool: Find files matching a glob pattern.

    Trust Level: L0 (READ_ONLY)
    Effects: READS(filesystem)
    Cacheable: True (filesystem is relatively stable)

    Examples:
        GlobQuery(pattern="**/*.py")  # All Python files
        GlobQuery(pattern="src/**/*.tsx", path=".")  # TSX in src
    """

    @property
    def name(self) -> str:
        return "search.glob"

    @property
    def description(self) -> str:
        return "Find files matching a glob pattern"

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
        return True  # Filesystem relatively stable

    async def invoke(self, request: GlobQuery) -> GlobResponse:
        """
        Find files matching the glob pattern.

        Args:
            request: GlobQuery with pattern, optional path and limit

        Returns:
            GlobResponse with matching file paths

        Raises:
            ToolError: On glob failure
        """
        try:
            root = Path(request.path) if request.path else Path(".")
            path_matches = list(root.glob(request.pattern))

            # Filter to files only
            matches: list[str] = [str(m) for m in path_matches if m.is_file()]
            total = len(matches)
            truncated = total > request.limit

            if truncated:
                matches = matches[: request.limit]

            return GlobResponse(
                pattern=request.pattern,
                matches=matches,
                count=len(matches),
                truncated=truncated,
            )

        except Exception as e:
            raise ToolError(f"Glob failed: {e}", self.name) from e


# =============================================================================
# GrepTool: Content Search with Regex
# =============================================================================


@dataclass
class GrepTool(Tool[GrepQuery, GrepResponse]):
    """
    GrepTool: Search file contents for a regex pattern.

    Trust Level: L0 (READ_ONLY)
    Effects: READS(filesystem)
    Cacheable: False (content may change)

    Output Modes:
        - "files_with_matches": Only file paths (default)
        - "content": Matching lines with context
        - "count": Match counts per file

    Examples:
        GrepQuery(pattern="TODO", path="src")
        GrepQuery(pattern=r"def\\s+\\w+", glob="*.py", output_mode="content")
    """

    @property
    def name(self) -> str:
        return "search.grep"

    @property
    def description(self) -> str:
        return "Search file contents for a regex pattern"

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
        return False  # Content may change

    async def invoke(self, request: GrepQuery) -> GrepResponse:
        """
        Search file contents for the regex pattern.

        Args:
            request: GrepQuery with pattern, path, glob, output_mode, etc.

        Returns:
            GrepResponse with matches

        Raises:
            ToolError: On invalid regex or search failure
        """
        try:
            # Compile regex
            flags = re.IGNORECASE if request.case_insensitive else 0
            regex = re.compile(request.pattern, flags)
        except re.error as e:
            raise ToolError(f"Invalid regex pattern: {e}", self.name) from e

        root = Path(request.path) if request.path else Path(".")
        file_glob = request.glob or "**/*"

        matches: list[GrepMatch] = []
        files_with_matches: set[str] = set()

        try:
            for file_path in root.glob(file_glob):
                if not file_path.is_file():
                    continue

                try:
                    content = file_path.read_text()
                except (UnicodeDecodeError, PermissionError):
                    # Skip binary or inaccessible files
                    continue

                lines = content.splitlines()

                for i, line in enumerate(lines):
                    if regex.search(line):
                        files_with_matches.add(str(file_path))

                        if request.output_mode == "files_with_matches":
                            # Only need to record file once
                            break

                        # Get context lines
                        context_before: list[str] = []
                        context_after: list[str] = []

                        if request.context_lines > 0:
                            start = max(0, i - request.context_lines)
                            end = min(len(lines), i + request.context_lines + 1)
                            context_before = lines[start:i]
                            context_after = lines[i + 1 : end]

                        matches.append(
                            GrepMatch(
                                file_path=str(file_path),
                                line_number=i + 1,
                                content=line,
                                context_before=context_before,
                                context_after=context_after,
                            )
                        )

                        if len(matches) >= request.limit:
                            break

                if len(matches) >= request.limit:
                    break

            # Build response based on output mode
            if request.output_mode == "files_with_matches":
                # Convert files to GrepMatch with just file_path
                file_matches = [GrepMatch(file_path=f) for f in sorted(files_with_matches)]
                if len(file_matches) > request.limit:
                    file_matches = file_matches[: request.limit]
                return GrepResponse(
                    pattern=request.pattern,
                    matches=file_matches,
                    count=len(file_matches),
                    output_mode=request.output_mode,
                    truncated=len(files_with_matches) > request.limit,
                )

            return GrepResponse(
                pattern=request.pattern,
                matches=matches,
                count=len(matches),
                output_mode=request.output_mode,
                truncated=len(matches) >= request.limit,
            )

        except Exception as e:
            raise ToolError(f"Grep failed: {e}", self.name) from e


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "GlobTool",
    "GrepTool",
]
