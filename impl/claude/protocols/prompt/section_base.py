"""
Section Base: Protocol and Types for Prompt Sections.

Each section of CLAUDE.md is compiled by a SectionCompiler that:
1. Reads from source files (spec, docs, config)
2. Renders content based on context
3. Estimates token cost

The Section dataclass captures the output of compilation.

See: spec/protocols/evergreen-prompt-system.md Part III
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .compiler import CompilationContext

logger = logging.getLogger(__name__)


class NPhase(Enum):
    """N-Phase development phases for phase-aware sections."""

    PLAN = auto()
    RESEARCH = auto()
    DEVELOP = auto()
    STRATEGIZE = auto()
    CROSS_SYNERGIZE = auto()
    IMPLEMENT = auto()
    QA = auto()
    TEST = auto()
    EDUCATE = auto()
    MEASURE = auto()
    REFLECT = auto()


@dataclass(frozen=True)
class Section:
    """
    A compiled section of the prompt.

    Immutable output from SectionCompiler.compile() or SoftSection.crystallize().

    Attributes:
        name: Section identifier (e.g., "identity", "principles")
        content: Rendered markdown content
        token_cost: Estimated token count
        required: If True, always included regardless of context
        phases: Set of phases where this section is relevant (empty = all phases)
        source_paths: Files this section was compiled from (for cache invalidation)
        reasoning_trace: Steps taken to compile this section (Wave 3+ transparency)
        rigidity: How "rigid" this section is (0.0=soft/inferred, 1.0=hard/template)
    """

    name: str
    content: str
    token_cost: int
    required: bool = True
    phases: frozenset[NPhase] = field(default_factory=frozenset)
    source_paths: tuple[Path, ...] = ()
    # Wave 3+ additions for transparency
    reasoning_trace: tuple[str, ...] = ()
    rigidity: float = 1.0  # Default to hard/template for backward compatibility

    def __post_init__(self) -> None:
        """Validate section content."""
        if not self.name:
            raise ValueError("Section name cannot be empty")
        if not self.content:
            raise ValueError(f"Section '{self.name}' content cannot be empty")

    def is_phase_relevant(self, phase: NPhase | None) -> bool:
        """Check if section is relevant to a given phase."""
        if not self.phases:
            return True  # Empty phases = relevant to all
        if phase is None:
            return True  # No phase specified = include all
        return phase in self.phases

    def with_content(self, new_content: str) -> Section:
        """Return a new Section with updated content."""
        return Section(
            name=self.name,
            content=new_content,
            token_cost=estimate_tokens(new_content),
            required=self.required,
            phases=self.phases,
            source_paths=self.source_paths,
            reasoning_trace=self.reasoning_trace,
            rigidity=self.rigidity,
        )

    def with_reasoning(self, traces: tuple[str, ...]) -> "Section":
        """Return a new Section with added reasoning traces."""
        return Section(
            name=self.name,
            content=self.content,
            token_cost=self.token_cost,
            required=self.required,
            phases=self.phases,
            source_paths=self.source_paths,
            reasoning_trace=self.reasoning_trace + traces,
            rigidity=self.rigidity,
        )


@runtime_checkable
class SectionCompiler(Protocol):
    """
    Protocol for section compilers.

    Each section type has its own compiler that:
    1. Knows how to read source data
    2. Renders markdown based on context
    3. Estimates token cost

    Implementations should be stateless - all state comes via CompilationContext.
    """

    @property
    def name(self) -> str:
        """Section identifier."""
        ...

    @property
    def required(self) -> bool:
        """Whether this section is always included."""
        ...

    @property
    def phases(self) -> frozenset[NPhase]:
        """Phases where this section is relevant (empty = all)."""
        ...

    def compile(self, context: CompilationContext) -> Section:
        """
        Compile section from sources.

        Args:
            context: Compilation context with paths, phase, and options

        Returns:
            Compiled Section with content and metadata
        """
        ...

    def estimate_tokens(self) -> int:
        """
        Estimate token cost without full compilation.

        Useful for budget planning before compilation.
        """
        ...


def estimate_tokens(content: str) -> int:
    """
    Estimate token count for content.

    Simple heuristic: ~4 characters per token on average.
    This is a rough estimate for planning purposes.
    """
    return len(content) // 4


def compose_sections(sections: list[Section], separator: str = "\n\n") -> str:
    """
    Compose multiple sections into final prompt content.

    The composition is associative:
        compose([a, b, c]) == compose([compose([a, b]), c])
                          == compose([a, compose([b, c])])

    This is the identity law for section composition.
    """
    return separator.join(s.content for s in sections)


# =============================================================================
# File Reading Utilities (Wave 2)
# =============================================================================


def read_file_safe(path: Path) -> str | None:
    """
    Read a file safely, returning None if the file doesn't exist.

    This is the core utility for dynamic section compilers.
    Logs a warning when falling back.

    Args:
        path: Path to the file to read

    Returns:
        File content as string, or None if file doesn't exist
    """
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.warning(f"Source file not found: {path}")
        return None
    except OSError as e:
        logger.warning(f"Error reading {path}: {e}")
        return None


def extract_markdown_section(
    content: str,
    heading: str,
    *,
    level: int = 2,
    include_heading: bool = False,
) -> str | None:
    """
    Extract content under a specific markdown heading.

    Args:
        content: Full markdown content
        heading: The heading text to find (without the # prefix)
        level: Heading level (2 = ##, 3 = ###, etc.)
        include_heading: Whether to include the heading line in output

    Returns:
        Content under the heading, or None if not found

    Example:
        >>> content = "## Principles\\n\\nText here\\n\\n## Next Section"
        >>> extract_markdown_section(content, "Principles")
        'Text here'
    """
    # Build pattern for heading at specified level
    prefix = "#" * level
    # Match heading with optional numbering (e.g., "## 1. Tasteful" or "## Tasteful")
    pattern = rf"^{prefix}\s+(?:\d+\.\s+)?{re.escape(heading)}\s*$"

    lines = content.split("\n")
    start_idx = None
    end_idx = len(lines)

    for i, line in enumerate(lines):
        if re.match(pattern, line, re.IGNORECASE):
            start_idx = i if include_heading else i + 1
        elif start_idx is not None:
            # Check if this is a heading of same or higher level
            if re.match(rf"^#{{{1},{level}}}\s+", line):
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


def extract_principle_summary(content: str) -> str | None:
    """
    Extract a summary of the 7 principles from principles.md.

    Extracts just the principle names and one-line descriptions,
    suitable for the system prompt.

    Returns:
        Formatted summary string, or None if parsing fails
    """
    # Pattern to match principle headings like "## 1. Tasteful" or "## 1. Joy-Inducing"
    # \w+ won't match hyphens, so we use [\w-]+ instead
    pattern = r"^##\s+(\d+)\.\s+([\w-]+)\s*$"
    # Pattern to match the principle's tagline (> blockquote on next line)
    tagline_pattern = r"^>\s*(.+)$"

    lines = content.split("\n")
    principles: list[tuple[str, str, str]] = []  # (num, name, tagline)

    i = 0
    while i < len(lines):
        match = re.match(pattern, lines[i])
        if match:
            num, name = match.groups()
            # Look for tagline in next few lines
            tagline = ""
            for j in range(i + 1, min(i + 5, len(lines))):
                tagline_match = re.match(tagline_pattern, lines[j])
                if tagline_match:
                    tagline = tagline_match.group(1)
                    break
            principles.append((num, name, tagline))
        i += 1

    if len(principles) < 7:
        return None

    # Format as summary
    result_lines = []
    for num, name, tagline in principles[:7]:
        # Shorten the tagline for the summary
        short = tagline.split(";")[0].strip() if tagline else ""
        result_lines.append(f"{num}. **{name}** - {short}")

    return "\n".join(result_lines)


def extract_skills_from_directory(docs_path: Path) -> list[tuple[str, str, Path]]:
    """
    Extract skill names and descriptions from docs/skills/*.md.

    Reads the YAML frontmatter and first heading from each skill file.

    Args:
        docs_path: Path to docs directory

    Returns:
        List of (skill_name, description, path) tuples, sorted by name
    """
    skills_dir = docs_path / "skills"
    if not skills_dir.exists():
        return []

    skills: list[tuple[str, str, Path]] = []

    for path in sorted(skills_dir.glob("*.md")):
        if path.name == "README.md":
            continue

        content = read_file_safe(path)
        if not content:
            continue

        # Extract skill name from first # heading (usually "# Skill: <name>")
        heading_match = re.search(r"^#\s+(?:Skill:\s*)?(.+)$", content, re.MULTILINE)
        if heading_match:
            name = heading_match.group(1).strip()
        else:
            # Fall back to filename
            name = path.stem.replace("-", " ").title()

        # Description is the filename for now (could extract from frontmatter)
        description = f"`{path.name}`"

        skills.append((name, description, path))

    return skills


def glob_source_paths(base_path: Path, pattern: str) -> tuple[Path, ...]:
    """
    Glob for source files and return as a sorted tuple.

    Ensures deterministic ordering for cache invalidation.

    Args:
        base_path: Base directory to glob from
        pattern: Glob pattern (e.g., "*.md")

    Returns:
        Sorted tuple of matching paths
    """
    if not base_path.exists():
        return ()
    return tuple(sorted(base_path.glob(pattern)))


# =============================================================================
# Async Utilities (Wave 3)
# =============================================================================


def run_sync(coro):
    """
    Run an async coroutine from synchronous code, safely handling event loops.

    This utility handles the common case where section compilers need to call
    async sources from the synchronous compile() method.

    Handles three cases:
    1. No event loop running → create one and run
    2. Event loop running but not in async context → safe to run_until_complete
    3. Event loop running in async context → use concurrent.futures

    Args:
        coro: The coroutine to run

    Returns:
        The result of the coroutine

    Example:
        async def fetch_data():
            return "data"

        # Can be called from sync code safely
        result = run_sync(fetch_data())
    """
    import asyncio
    import concurrent.futures

    try:
        # Check if there's a running event loop
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop - safe to create one and run
        return asyncio.run(coro)

    # There's a running loop - we're being called from async context
    # This happens when the compiler is used from an async framework
    # Use a thread pool to avoid blocking the event loop

    # Create a new event loop in a thread
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result(timeout=30.0)


__all__ = [
    "NPhase",
    "Section",
    "SectionCompiler",
    "estimate_tokens",
    "compose_sections",
    # Wave 2 additions
    "read_file_safe",
    "extract_markdown_section",
    "extract_principle_summary",
    "extract_skills_from_directory",
    "glob_source_paths",
    # Wave 3 additions
    "run_sync",
]
