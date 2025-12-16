"""
Soft Section: The core abstraction for the rigidity spectrum.

A SoftSection exists somewhere on the spectrum:
    0.0 (pure LLM inference) ←→ 1.0 (pure template)

It has:
- Multiple sources, ordered by priority
- A merge strategy for when multiple sources produce content
- Reasoning traces throughout (per transparency taste decision)

The crystallize() method turns a SoftSection into a hard Section
by attempting sources in order and applying the merge strategy.

Category Law (must hold):
    crystallize(crystallize(s)) == crystallize(s)  # Idempotence
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

from .section_base import Section, estimate_tokens
from .sources.base import SectionSource, SourceResult

if TYPE_CHECKING:
    from .compiler import CompilationContext

logger = logging.getLogger(__name__)


class MergeStrategy(Enum):
    """
    Strategy for merging multiple source results.

    Per taste decision: merge heuristically, not with hard precedence.
    """

    FIRST_WINS = auto()  # Use first successful source (simplest)
    HIGHEST_RIGIDITY = auto()  # Prefer more rigid sources
    CONCAT = auto()  # Concatenate all results
    SEMANTIC_FUSION = auto()  # LLM-assisted semantic merge (Wave 5)


@dataclass(frozen=True)
class CrystallizationResult:
    """
    Result of crystallizing a soft section.

    Captures the resulting content and full reasoning trace
    for transparency.
    """

    section: Section
    reasoning_trace: tuple[str, ...]
    source_results: tuple[SourceResult, ...]
    effective_rigidity: float


@dataclass
class SoftSection:
    """
    A section that exists on the rigidity spectrum.

    SoftSection is the key abstraction of the reformation.
    Unlike hard Section (which has fixed content), a SoftSection
    has multiple sources that are tried in priority order.

    Attributes:
        name: Section identifier
        sources: Ordered list of sources (higher priority first)
        merge_strategy: How to combine multiple successful sources
        required: If True, always included regardless of context
        default_rigidity: Rigidity when no sources produce content
    """

    name: str
    sources: list[SectionSource] = field(default_factory=list)
    merge_strategy: MergeStrategy = MergeStrategy.FIRST_WINS
    required: bool = True
    default_rigidity: float = 0.5

    def __post_init__(self) -> None:
        """Sort sources by priority (highest first)."""
        self.sources = sorted(self.sources)

    async def crystallize(
        self,
        context: "CompilationContext",
    ) -> CrystallizationResult:
        """
        Crystallize from available sources.

        Algorithm:
        1. Try sources in priority order
        2. For each source that produces content, record it
        3. If multiple sources, apply merge_strategy
        4. Record reasoning trace throughout
        5. Return hard Section with full provenance

        This is the core operation that turns a soft section into
        a hard section ready for compilation.
        """
        traces: list[str] = [f"Crystallizing section: {self.name}"]
        results: list[SourceResult] = []
        candidates: list[SourceResult] = []

        # Try each source in priority order
        for source in self.sources:
            traces.append(
                f"Trying source: {source.name} (priority={source.priority.name})"
            )
            result = await source.fetch(context)
            results.append(result)

            # Add reasoning traces from the source
            for trace in result.reasoning_trace:
                traces.append(f"  {trace}")

            if result.success and result.content:
                traces.append(
                    f"  → Success: {len(result.content)} chars (rigidity={result.rigidity:.1f})"
                )
                candidates.append(result)

                # For FIRST_WINS, stop after first success
                if self.merge_strategy == MergeStrategy.FIRST_WINS:
                    traces.append("  → Using FIRST_WINS, stopping here")
                    break
            else:
                traces.append("  → Failed")

        # Handle no candidates
        if not candidates:
            traces.append("No sources produced content")
            # Return empty section with low rigidity
            return CrystallizationResult(
                section=Section(
                    name=self.name,
                    content=f"<!-- Section '{self.name}' unavailable -->",
                    token_cost=10,
                    required=self.required,
                ),
                reasoning_trace=tuple(traces),
                source_results=tuple(results),
                effective_rigidity=0.0,
            )

        # Merge if multiple candidates
        if len(candidates) == 1:
            content = candidates[0].content
            effective_rigidity = candidates[0].rigidity
            source_paths = (
                (candidates[0].source_path,) if candidates[0].source_path else ()
            )
        else:
            content, effective_rigidity = await self._merge(candidates, context, traces)
            source_paths = tuple(r.source_path for r in candidates if r.source_path)

        traces.append(
            f"Final content: {len(content)} chars, rigidity={effective_rigidity:.2f}"
        )

        return CrystallizationResult(
            section=Section(
                name=self.name,
                content=content,
                token_cost=estimate_tokens(content),
                required=self.required,
                source_paths=source_paths,
            ),
            reasoning_trace=tuple(traces),
            source_results=tuple(results),
            effective_rigidity=effective_rigidity,
        )

    async def _merge(
        self,
        candidates: list[SourceResult],
        context: "CompilationContext",
        traces: list[str],
    ) -> tuple[str, float]:
        """
        Merge multiple candidate results.

        Returns (content, effective_rigidity).
        """
        traces.append(
            f"Merging {len(candidates)} candidates via {self.merge_strategy.name}"
        )

        if self.merge_strategy == MergeStrategy.HIGHEST_RIGIDITY:
            # Sort by rigidity (highest first) and take first
            sorted_candidates = sorted(
                candidates, key=lambda r: r.rigidity, reverse=True
            )
            winner = sorted_candidates[0]
            traces.append(
                f"Highest rigidity: {winner.source_name} ({winner.rigidity:.2f})"
            )
            return winner.content, winner.rigidity

        elif self.merge_strategy == MergeStrategy.CONCAT:
            # Concatenate all candidates
            parts = [r.content for r in candidates if r.content]
            content = "\n\n".join(parts)
            # Average rigidity
            avg_rigidity = sum(r.rigidity for r in candidates) / len(candidates)
            traces.append(
                f"Concatenated {len(parts)} parts, avg rigidity={avg_rigidity:.2f}"
            )
            return content, avg_rigidity

        elif self.merge_strategy == MergeStrategy.SEMANTIC_FUSION:
            # Wave 5: Use PromptFusion for semantic merging
            from .fusion.fusioner import PromptFusion

            traces.append("Using SEMANTIC_FUSION (Wave 5)")

            # Create fusioner (policy will be injected via context in future)
            fusioner = PromptFusion()

            # Fuse all candidates pairwise
            result = fusioner.fuse_sources(candidates)

            # Add fusion reasoning traces
            for trace in result.reasoning_trace:
                traces.append(f"  [fusion] {trace}")

            return result.content, result.effective_rigidity

        else:
            # Default: FIRST_WINS (should not reach here due to early break)
            winner = candidates[0]
            traces.append(f"First wins: {winner.source_name}")
            return winner.content, winner.rigidity

    @classmethod
    def from_hard(cls, section: Section) -> "SoftSection":
        """
        Create a SoftSection from a hard Section.

        Useful for testing idempotence law:
            crystallize(from_hard(crystallize(s))) == crystallize(s)
        """
        from .sources.base import TemplateSource

        return cls(
            name=section.name,
            sources=[
                TemplateSource(
                    name=f"{section.name}:template",
                    template=section.content,
                )
            ],
            required=section.required,
            default_rigidity=1.0,
        )


def soft_section_from_compiler(
    name: str,
    file_path_resolver,
    fallback_content: str,
    required: bool = True,
) -> SoftSection:
    """
    Create a SoftSection from a Wave 2 style compiler pattern.

    Helper function for migrating existing section compilers
    to the SoftSection model.
    """
    from .sources.base import FallbackSource, TemplateSource
    from .sources.file_source import FileSource

    return SoftSection(
        name=name,
        sources=[
            FileSource(
                name=f"{name}:file",
                path_resolver=file_path_resolver,
            ),
            TemplateSource(
                name=f"{name}:fallback",
                template=fallback_content,
            ),
        ],
        required=required,
    )


__all__ = [
    "MergeStrategy",
    "CrystallizationResult",
    "SoftSection",
    "soft_section_from_compiler",
]
