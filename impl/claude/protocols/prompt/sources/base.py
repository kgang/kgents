"""
Base Source Abstraction: Protocol for section content sources.

Sources are the atoms of the rigidity spectrum. Each source:
1. Has a priority for ordering
2. Can attempt to fetch content
3. Records reasoning traces for transparency
4. Reports whether it produced usable content
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..compiler import CompilationContext


class SourcePriority(IntEnum):
    """
    Priority levels for sources.

    Higher priority sources are tried first.
    File sources typically have highest priority (most rigid),
    LLM sources have lowest (least rigid).
    """

    TEMPLATE = 100  # Hardcoded templates (rigidity=1.0)
    FILE = 80  # Read from files (rigidity=0.8)
    GIT = 60  # Read from git history (rigidity=0.6)
    MEMORY = 40  # Read from memory/session (rigidity=0.4)
    INFERENCE = 20  # LLM inference (rigidity=0.2)
    FALLBACK = 0  # Last resort fallback


@dataclass(frozen=True)
class SourceResult:
    """
    Result of attempting to fetch from a source.

    Captures both content (if successful) and reasoning traces
    for transparency (per taste decision).

    Attributes:
        content: The fetched content, or None if failed
        success: Whether the source produced usable content
        source_name: Name of the source for tracing
        source_path: Path if this came from a file (for cache invalidation)
        reasoning_trace: Steps taken to fetch this content
        rigidity: How "rigid" this source is (0.0-1.0)
    """

    content: str | None
    success: bool
    source_name: str
    source_path: Path | None = None
    reasoning_trace: tuple[str, ...] = ()
    rigidity: float = 0.5

    def __str__(self) -> str:
        status = "✓" if self.success else "✗"
        length = len(self.content) if self.content else 0
        return f"[{status}] {self.source_name}: {length} chars (rigidity={self.rigidity:.1f})"


@dataclass
class SectionSource(ABC):
    """
    Abstract base class for section sources.

    A source knows how to fetch content from a specific location.
    Sources are stateless; all context comes via CompilationContext.

    Attributes:
        name: Human-readable name for this source
        priority: Priority for ordering (higher = tried first)
        rigidity: How "rigid" this source is (0.0=soft, 1.0=hard)
    """

    name: str
    priority: SourcePriority = SourcePriority.FILE
    rigidity: float = 0.5

    @abstractmethod
    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """
        Attempt to fetch content from this source.

        Args:
            context: Compilation context with paths and options

        Returns:
            SourceResult with content (if successful) and traces
        """
        ...

    def __lt__(self, other: "SectionSource") -> bool:
        """Sources are ordered by priority (higher first)."""
        return self.priority > other.priority  # Note: reversed for descending


@dataclass
class TemplateSource(SectionSource):
    """
    Source that returns a hardcoded template.

    The most rigid source type (rigidity=1.0).
    Used for sections that should never change dynamically.
    """

    template: str = ""
    priority: SourcePriority = field(default=SourcePriority.TEMPLATE)
    rigidity: float = 1.0

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Return the hardcoded template."""
        traces = [
            f"Using hardcoded template for {self.name}",
            f"Template length: {len(self.template)} chars",
        ]

        return SourceResult(
            content=self.template,
            success=bool(self.template),
            source_name=self.name,
            source_path=None,
            reasoning_trace=tuple(traces),
            rigidity=self.rigidity,
        )


@dataclass
class FallbackSource(SectionSource):
    """
    Source that returns a fallback message.

    Used when all other sources fail.
    Lowest priority (rigidity=0.0).
    """

    fallback_message: str = "Content unavailable."
    priority: SourcePriority = field(default=SourcePriority.FALLBACK)
    rigidity: float = 0.0

    async def fetch(self, context: "CompilationContext") -> SourceResult:
        """Return the fallback message."""
        traces = [
            f"All sources failed, using fallback for {self.name}",
            f"Fallback: {self.fallback_message[:50]}...",
        ]

        return SourceResult(
            content=self.fallback_message,
            success=True,  # Fallback always "succeeds"
            source_name=f"{self.name}:fallback",
            source_path=None,
            reasoning_trace=tuple(traces),
            rigidity=self.rigidity,
        )


__all__ = [
    "SourcePriority",
    "SourceResult",
    "SectionSource",
    "TemplateSource",
    "FallbackSource",
]
