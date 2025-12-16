"""
File Source: Read section content from files.

File sources read from static files in the project.
They are relatively rigid (0.8) since the content is
determined by file contents, not inference.

Features:
- Read entire file
- Extract markdown section by heading
- Support for multiple file patterns (glob)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from .base import SectionSource, SourcePriority, SourceResult

if TYPE_CHECKING:
    from ..compiler import CompilationContext

logger = logging.getLogger(__name__)


# Default max file size: 1MB (prevent OOM on large files)
DEFAULT_MAX_FILE_SIZE = 1024 * 1024


@dataclass
class FileSource(SectionSource):
    """
    Source that reads from a file.

    Can read entire file or extract a specific section.

    Attributes:
        path_resolver: Function to get file path from context
        section_heading: If set, extract section under this heading
        section_level: Heading level (2 = ##, 3 = ###)
        include_heading: Whether to include the heading in output
        transform: Optional function to transform content after reading
        max_file_size: Maximum file size in bytes (default 1MB)
    """

    path_resolver: Callable[["CompilationContext"], Path | None] = field(
        default=lambda ctx: None
    )
    section_heading: str | None = None
    section_level: int = 2
    include_heading: bool = False
    transform: Callable[[str], str] | None = None
    max_file_size: int = DEFAULT_MAX_FILE_SIZE
    priority: SourcePriority = field(default=SourcePriority.FILE)
    rigidity: float = 0.8

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Read content from file."""
        traces = [f"FileSource: Resolving path for {self.name}"]

        # Resolve path
        path = self.path_resolver(context)
        if path is None:
            traces.append("Path resolver returned None")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                source_path=None,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        traces.append(f"Resolved path: {path}")

        # Check file exists
        if not path.exists():
            traces.append(f"File not found: {path}")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                source_path=path,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        # Check file size before reading (prevent OOM)
        file_size = path.stat().st_size
        if file_size > self.max_file_size:
            traces.append(
                f"File too large: {file_size:,} bytes > {self.max_file_size:,} bytes max"
            )
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                source_path=path,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        traces.append(f"File size: {file_size:,} bytes (within limit)")

        # Read file
        try:
            content = path.read_text(encoding="utf-8")
            traces.append(f"Read {len(content)} chars from {path.name}")
        except OSError as e:
            traces.append(f"Error reading file: {e}")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                source_path=path,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        # Extract section if requested
        if self.section_heading:
            traces.append(f"Extracting section: {self.section_heading}")
            content = self._extract_section(content, traces)
            if content is None:
                traces.append(f"Section '{self.section_heading}' not found")
                return SourceResult(
                    content=None,
                    success=False,
                    source_name=self.name,
                    source_path=path,
                    reasoning_trace=tuple(traces),
                    rigidity=self.rigidity,
                )
            traces.append(f"Extracted {len(content)} chars")

        # Apply transform if provided
        if self.transform:
            traces.append("Applying transform")
            content = self.transform(content)
            traces.append(f"After transform: {len(content)} chars")

        return SourceResult(
            content=content,
            success=True,
            source_name=self.name,
            source_path=path,
            reasoning_trace=tuple(traces),
            rigidity=self.rigidity,
        )

    def _extract_section(self, content: str, traces: list[str]) -> str | None:
        """Extract content under a specific markdown heading."""
        if not self.section_heading:
            return content

        # Build pattern for heading at specified level
        prefix = "#" * self.section_level
        # Match heading with optional numbering (e.g., "## 1. Tasteful" or "## Tasteful")
        pattern = rf"^{prefix}\s+(?:\d+\.\s+)?{re.escape(self.section_heading)}\s*$"

        lines = content.split("\n")
        start_idx = None
        end_idx = len(lines)

        for i, line in enumerate(lines):
            if re.match(pattern, line, re.IGNORECASE):
                start_idx = i if self.include_heading else i + 1
                traces.append(f"Found heading at line {i + 1}")
            elif start_idx is not None:
                # Check if this is a heading of same or higher level
                if re.match(rf"^#{{{1},{self.section_level}}}\s+", line):
                    end_idx = i
                    break

        if start_idx is None:
            return None

        # Strip leading/trailing blank lines
        section_lines = lines[start_idx:end_idx]
        while section_lines and not section_lines[0].strip():
            section_lines.pop(0)
        while section_lines and not section_lines[-1].strip():
            section_lines.pop()

        return "\n".join(section_lines) if section_lines else None


@dataclass
class GlobFileSource(SectionSource):
    """
    Source that reads from multiple files matching a glob pattern.

    Useful for sections like Skills that aggregate multiple files.
    """

    base_path_resolver: Callable[["CompilationContext"], Path | None] = field(
        default=lambda ctx: None
    )
    pattern: str = "*.md"
    combiner: Callable[[list[tuple[Path, str]]], str] | None = None
    priority: SourcePriority = field(default=SourcePriority.FILE)
    rigidity: float = 0.7  # Slightly less rigid due to aggregation

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Read and combine multiple files."""
        traces = [f"GlobFileSource: Resolving base path for {self.name}"]

        # Resolve base path
        base_path = self.base_path_resolver(context)
        if base_path is None or not base_path.exists():
            traces.append(f"Base path not found: {base_path}")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                source_path=None,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        traces.append(f"Base path: {base_path}")
        traces.append(f"Pattern: {self.pattern}")

        # Glob for files
        paths = sorted(base_path.glob(self.pattern))
        traces.append(f"Found {len(paths)} files")

        if not paths:
            traces.append("No files matched pattern")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                source_path=base_path,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        # Read all files
        files: list[tuple[Path, str]] = []
        for path in paths:
            try:
                content = path.read_text(encoding="utf-8")
                files.append((path, content))
                traces.append(f"  Read {path.name}: {len(content)} chars")
            except OSError as e:
                traces.append(f"  Error reading {path.name}: {e}")

        if not files:
            traces.append("No files successfully read")
            return SourceResult(
                content=None,
                success=False,
                source_name=self.name,
                source_path=base_path,
                reasoning_trace=tuple(traces),
                rigidity=self.rigidity,
            )

        # Combine files
        if self.combiner:
            content = self.combiner(files)
        else:
            # Default: concatenate with headers
            parts = []
            for path, file_content in files:
                parts.append(f"### {path.stem}\n\n{file_content}")
            content = "\n\n".join(parts)

        traces.append(f"Combined to {len(content)} chars")

        return SourceResult(
            content=content,
            success=True,
            source_name=self.name,
            source_path=base_path,
            reasoning_trace=tuple(traces),
            rigidity=self.rigidity,
        )


__all__ = [
    "FileSource",
    "GlobFileSource",
]
