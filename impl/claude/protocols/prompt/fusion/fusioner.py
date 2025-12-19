"""
PromptFusion: The main semantic fusion class.

Wave 5 of the Evergreen Prompt System.

Per taste decision: merge heuristically, not with hard precedence.

PromptFusion orchestrates:
1. Semantic similarity computation
2. Conflict detection
3. Policy-based resolution
4. Content merging

It produces a FusionResult with full reasoning traces for transparency.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from .conflict import Conflict, ConflictDetector, ConflictError, ConflictSeverity
from .resolution import PolicyResolver, Resolution, ResolutionError
from .similarity import (
    SemanticSimilarity,
    SimilarityError,
    SimilarityResult,
    SimilarityStrategy,
)

if TYPE_CHECKING:
    from ..habits.policy import PolicyVector
    from ..sources.base import SourceResult

logger = logging.getLogger(__name__)

# Constants for validation
MAX_CONTENT_LENGTH = 1_000_000  # 1MB max content size
MIN_THRESHOLD = 0.0
MAX_THRESHOLD = 1.0


class FusionError(Exception):
    """Exception raised for fusion errors."""

    pass


@dataclass(frozen=True)
class FusionResult:
    """
    Result of fusing multiple sources.

    Attributes:
        content: The fused content
        similarity: Similarity between input sources
        conflicts: Detected conflicts
        resolutions: How conflicts were resolved
        effective_rigidity: Rigidity of the fused result
        reasoning_trace: Full trace of fusion decisions
        success: Whether fusion succeeded
        timestamp: When fusion occurred
    """

    content: str
    similarity: SimilarityResult | None = None
    conflicts: tuple[Conflict, ...] = ()
    resolutions: tuple[Resolution, ...] = ()
    effective_rigidity: float = 0.5
    reasoning_trace: tuple[str, ...] = ()
    success: bool = True
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def has_blocking_conflicts(self) -> bool:
        """Check if there are unresolved blocking conflicts."""
        if not self.conflicts:
            return False
        resolved_ids = {id(r.conflict) for r in self.resolutions}
        unresolved = [c for c in self.conflicts if id(c) not in resolved_ids and c.is_blocking()]
        return len(unresolved) > 0

    @property
    def summary(self) -> str:
        """One-line summary of fusion result."""
        sim_str = f"sim={self.similarity.score:.2f}" if self.similarity else "sim=N/A"
        return f"[{'OK' if self.success else 'FAIL'}] {len(self.content)} chars, {sim_str}, {len(self.conflicts)} conflicts"


@dataclass
class PromptFusion:
    """
    Orchestrate semantic fusion of multiple source contents.

    Per taste decision: merge heuristically using similarity,
    conflict detection, and policy-based resolution.

    Example:
        >>> from protocols.prompt.habits.policy import PolicyVector
        >>> fusion = PromptFusion(policy=PolicyVector.default())
        >>> result = fusion.fuse(content_a, content_b)
        >>> print(result.content)
    """

    policy: "PolicyVector | None" = None
    similarity_strategy: SimilarityStrategy = SimilarityStrategy.COMBINED
    high_similarity_threshold: float = 0.9  # Above this = use either source
    low_similarity_threshold: float = 0.3  # Below this = significant difference

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not (MIN_THRESHOLD <= self.high_similarity_threshold <= MAX_THRESHOLD):
            raise FusionError(
                f"high_similarity_threshold must be between {MIN_THRESHOLD} and {MAX_THRESHOLD}"
            )
        if not (MIN_THRESHOLD <= self.low_similarity_threshold <= MAX_THRESHOLD):
            raise FusionError(
                f"low_similarity_threshold must be between {MIN_THRESHOLD} and {MAX_THRESHOLD}"
            )
        if self.low_similarity_threshold >= self.high_similarity_threshold:
            raise FusionError(
                f"low_similarity_threshold ({self.low_similarity_threshold}) must be less than high_similarity_threshold ({self.high_similarity_threshold})"
            )

    def _validate_content(self, content: str, name: str) -> None:
        """Validate content string."""
        if content is None:
            raise FusionError(f"{name} cannot be None")
        if not isinstance(content, str):
            raise FusionError(f"{name} must be a string, got {type(content).__name__}")
        if len(content) > MAX_CONTENT_LENGTH:
            raise FusionError(f"{name} exceeds maximum length of {MAX_CONTENT_LENGTH} chars")

    def _validate_rigidity(self, rigidity: float, name: str) -> float:
        """Validate and clamp rigidity value."""
        if not isinstance(rigidity, (int, float)):
            raise FusionError(f"{name} must be numeric, got {type(rigidity).__name__}")
        return max(0.0, min(1.0, rigidity))

    def fuse(
        self,
        content_a: str,
        content_b: str,
        source_a_name: str = "source_a",
        source_b_name: str = "source_b",
        rigidity_a: float = 0.5,
        rigidity_b: float = 0.5,
        domain_hint: str = "",
    ) -> FusionResult:
        """
        Fuse two content strings using semantic analysis.

        Algorithm:
        1. Compute semantic similarity
        2. If high similarity (>0.9), use higher rigidity source
        3. If moderate similarity, detect conflicts and resolve
        4. If low similarity (<0.3), concatenate or merge structurally
        5. Return fused content with full reasoning trace

        Args:
            content_a: First content string
            content_b: Second content string
            source_a_name: Name for source A (for tracing)
            source_b_name: Name for source B (for tracing)
            rigidity_a: Rigidity of source A
            rigidity_b: Rigidity of source B
            domain_hint: Domain hint for policy resolution

        Returns:
            FusionResult with fused content and reasoning

        Raises:
            FusionError: If content is invalid (None, wrong type, too large)
        """
        # Validate inputs
        self._validate_content(content_a, "content_a")
        self._validate_content(content_b, "content_b")
        rigidity_a = self._validate_rigidity(rigidity_a, "rigidity_a")
        rigidity_b = self._validate_rigidity(rigidity_b, "rigidity_b")

        logger.debug(
            f"Starting fusion: {source_a_name} ({len(content_a)} chars) vs {source_b_name} ({len(content_b)} chars)"
        )

        traces: list[str] = [
            f"PromptFusion starting at {datetime.now().isoformat()}",
            f"Fusing {source_a_name} ({len(content_a)} chars, rigidity={rigidity_a:.2f})",
            f"   with {source_b_name} ({len(content_b)} chars, rigidity={rigidity_b:.2f})",
        ]

        # Handle edge cases
        if not content_a and not content_b:
            traces.append("Both sources empty, returning empty")
            return FusionResult(
                content="",
                reasoning_trace=tuple(traces),
                effective_rigidity=0.0,
            )

        if not content_a:
            traces.append("Source A empty, using source B directly")
            return FusionResult(
                content=content_b,
                reasoning_trace=tuple(traces),
                effective_rigidity=rigidity_b,
            )

        if not content_b:
            traces.append("Source B empty, using source A directly")
            return FusionResult(
                content=content_a,
                reasoning_trace=tuple(traces),
                effective_rigidity=rigidity_a,
            )

        if content_a == content_b:
            traces.append("Contents identical, using source A")
            return FusionResult(
                content=content_a,
                similarity=SimilarityResult(
                    score=1.0,
                    strategy=self.similarity_strategy,
                    reasoning="Identical content",
                ),
                reasoning_trace=tuple(traces),
                effective_rigidity=max(rigidity_a, rigidity_b),
            )

        # Step 1: Compute semantic similarity
        similarity_calc = SemanticSimilarity(strategy=self.similarity_strategy)
        similarity = similarity_calc.compare(content_a, content_b)
        traces.append(f"Similarity: {similarity.score:.2f} ({similarity.reasoning})")

        # Step 2: Handle high similarity
        if similarity.score >= self.high_similarity_threshold:
            traces.append(
                f"High similarity ({similarity.score:.2f} >= {self.high_similarity_threshold})"
            )
            # Use higher rigidity source
            if rigidity_a >= rigidity_b:
                traces.append(f"Using source A (higher rigidity: {rigidity_a:.2f})")
                return FusionResult(
                    content=content_a,
                    similarity=similarity,
                    reasoning_trace=tuple(traces),
                    effective_rigidity=rigidity_a,
                )
            else:
                traces.append(f"Using source B (higher rigidity: {rigidity_b:.2f})")
                return FusionResult(
                    content=content_b,
                    similarity=similarity,
                    reasoning_trace=tuple(traces),
                    effective_rigidity=rigidity_b,
                )

        # Step 3: Detect conflicts
        conflict_detector = ConflictDetector()
        conflicts = conflict_detector.detect(content_a, content_b, source_a_name, source_b_name)
        traces.append(f"Detected {len(conflicts)} conflicts")
        for conflict in conflicts:
            traces.append(f"  - {conflict.summary}")

        # Step 4: Resolve conflicts
        resolver = PolicyResolver(policy=self.policy)
        resolutions = resolver.resolve_all(
            conflicts,
            content_a,
            content_b,
            rigidity_a,
            rigidity_b,
            domain_hint,
        )
        for resolution in resolutions:
            traces.append(f"  → {resolution.summary}")

        # Step 5: Determine fusion strategy based on similarity
        if similarity.score >= self.low_similarity_threshold:
            # Moderate similarity: use conflict resolutions
            fused_content, effective_rigidity = self._fuse_with_resolutions(
                content_a,
                content_b,
                rigidity_a,
                rigidity_b,
                resolutions,
                traces,
            )
        else:
            # Low similarity: structural merge
            traces.append(
                f"Low similarity ({similarity.score:.2f} < {self.low_similarity_threshold})"
            )
            fused_content, effective_rigidity = self._fuse_structurally(
                content_a,
                content_b,
                rigidity_a,
                rigidity_b,
                traces,
            )

        traces.append(
            f"Fusion complete: {len(fused_content)} chars, rigidity={effective_rigidity:.2f}"
        )

        return FusionResult(
            content=fused_content,
            similarity=similarity,
            conflicts=tuple(conflicts),
            resolutions=tuple(resolutions),
            effective_rigidity=effective_rigidity,
            reasoning_trace=tuple(traces),
        )

    def _fuse_with_resolutions(
        self,
        content_a: str,
        content_b: str,
        rigidity_a: float,
        rigidity_b: float,
        resolutions: list[Resolution],
        traces: list[str],
    ) -> tuple[str, float]:
        """
        Fuse content using conflict resolutions.

        If most resolutions favor A, use A.
        If most favor B, use B.
        Otherwise, attempt to merge.
        """
        if not resolutions:
            # No conflicts: prefer higher rigidity
            traces.append("No conflicts, using higher rigidity source")
            if rigidity_a >= rigidity_b:
                return content_a, rigidity_a
            else:
                return content_b, rigidity_b

        # Count resolution choices
        a_count = sum(1 for r in resolutions if r.chosen_source == "a")
        b_count = sum(1 for r in resolutions if r.chosen_source == "b")
        merged_count = sum(1 for r in resolutions if r.chosen_source == "merged")

        traces.append(f"Resolution tally: A={a_count}, B={b_count}, merged={merged_count}")

        if merged_count > 0:
            # If any resolution suggests merging, try structural merge
            traces.append("Resolutions suggest merging")
            return self._fuse_structurally(
                content_a,
                content_b,
                rigidity_a,
                rigidity_b,
                traces,
            )
        elif a_count > b_count:
            traces.append(f"Majority resolutions favor A ({a_count} > {b_count})")
            return content_a, rigidity_a
        elif b_count > a_count:
            traces.append(f"Majority resolutions favor B ({b_count} > {a_count})")
            return content_b, rigidity_b
        else:
            # Tie: prefer higher rigidity
            traces.append("Resolution tie, using higher rigidity")
            if rigidity_a >= rigidity_b:
                return content_a, rigidity_a
            else:
                return content_b, rigidity_b

    def _fuse_structurally(
        self,
        content_a: str,
        content_b: str,
        rigidity_a: float,
        rigidity_b: float,
        traces: list[str],
    ) -> tuple[str, float]:
        """
        Fuse content structurally (for low similarity).

        Attempts to:
        1. Merge markdown sections if both have them
        2. Otherwise concatenate with separator
        """
        import re

        # Check if both have markdown structure
        headers_a = re.findall(r"^(#+\s+.+?)$", content_a, re.MULTILINE)
        headers_b = re.findall(r"^(#+\s+.+?)$", content_b, re.MULTILINE)

        if headers_a and headers_b:
            # Both have structure: merge sections
            traces.append("Both have markdown structure, merging sections")
            merged = self._merge_markdown_sections(content_a, content_b, traces)
            avg_rigidity = (rigidity_a + rigidity_b) / 2
            return merged, avg_rigidity
        else:
            # No structure: concatenate
            traces.append("No common structure, concatenating")

            # Order by rigidity (higher first)
            if rigidity_a >= rigidity_b:
                merged = f"{content_a}\n\n---\n\n{content_b}"
            else:
                merged = f"{content_b}\n\n---\n\n{content_a}"

            avg_rigidity = (rigidity_a + rigidity_b) / 2
            return merged, avg_rigidity

    def _merge_markdown_sections(
        self,
        content_a: str,
        content_b: str,
        traces: list[str],
    ) -> str:
        """
        Merge two markdown documents by combining their sections.

        Handles:
        - Common headers: merge content
        - Unique headers from A: include
        - Unique headers from B: append
        """
        import re

        # Parse into section dict: header -> content
        def parse_sections(content: str) -> dict[str, str]:
            sections: dict[str, str] = {}
            lines = content.split("\n")
            current_header = ""
            current_content: list[str] = []

            for line in lines:
                if re.match(r"^#+\s", line):
                    # Save previous section
                    if current_header:
                        sections[current_header] = "\n".join(current_content).strip()
                    current_header = line
                    current_content = []
                else:
                    current_content.append(line)

            # Save last section
            if current_header:
                sections[current_header] = "\n".join(current_content).strip()

            return sections

        sections_a = parse_sections(content_a)
        sections_b = parse_sections(content_b)

        traces.append(f"A has {len(sections_a)} sections, B has {len(sections_b)} sections")

        # Merge sections
        merged_sections: dict[str, str] = {}

        # Start with A's sections
        for header, content in sections_a.items():
            merged_sections[header] = content

        # Add/merge B's sections
        for header, content in sections_b.items():
            if header in merged_sections:
                # Merge if different
                if merged_sections[header] != content:
                    # Simple merge: keep both
                    merged_sections[header] = f"{merged_sections[header]}\n\n{content}"
                    traces.append(f"Merged section: {header}")
            else:
                merged_sections[header] = content
                traces.append(f"Added section from B: {header}")

        # Reconstruct markdown
        parts: list[str] = []
        for header, content in merged_sections.items():
            parts.append(f"{header}\n\n{content}")

        return "\n\n".join(parts)

    def fuse_sources(
        self,
        sources: list["SourceResult"],
        domain_hint: str = "",
    ) -> FusionResult:
        """
        Fuse multiple SourceResults.

        Performs pairwise fusion, accumulating results.

        Args:
            sources: List of SourceResults to fuse
            domain_hint: Domain hint for policy resolution

        Returns:
            FusionResult with fused content
        """
        valid_sources = [s for s in sources if s.success and s.content]

        if not valid_sources:
            return FusionResult(
                content="",
                reasoning_trace=("No valid sources to fuse",),
                success=False,
            )

        if len(valid_sources) == 1:
            source = valid_sources[0]
            return FusionResult(
                content=source.content or "",
                reasoning_trace=(f"Single source: {source.source_name}",),
                effective_rigidity=source.rigidity,
            )

        # Pairwise fusion
        current = valid_sources[0]
        traces = [f"Starting fusion with {len(valid_sources)} sources"]

        for next_source in valid_sources[1:]:
            result = self.fuse(
                current.content or "",
                next_source.content or "",
                current.source_name,
                next_source.source_name,
                current.rigidity,
                next_source.rigidity,
                domain_hint,
            )
            traces.extend(result.reasoning_trace)

            # Update current with fused result
            from ..sources.base import SourceResult

            current = SourceResult(
                content=result.content,
                success=True,
                source_name=f"fused({current.source_name},{next_source.source_name})",
                rigidity=result.effective_rigidity,
            )

        return FusionResult(
            content=current.content or "",
            reasoning_trace=tuple(traces),
            effective_rigidity=current.rigidity,
        )


def fuse_sources(
    content_a: str,
    content_b: str,
    policy: "PolicyVector | None" = None,
    rigidity_a: float = 0.5,
    rigidity_b: float = 0.5,
) -> FusionResult:
    """
    Convenience function to fuse two content strings.

    Args:
        content_a: First content
        content_b: Second content
        policy: Optional PolicyVector for resolution
        rigidity_a: Rigidity of source A
        rigidity_b: Rigidity of source B

    Returns:
        FusionResult with fused content

    Raises:
        FusionError: If content is invalid or fusion fails
    """
    try:
        fusion = PromptFusion(policy=policy)
        return fusion.fuse(content_a, content_b, rigidity_a=rigidity_a, rigidity_b=rigidity_b)
    except FusionError:
        raise
    except (SimilarityError, ConflictError, ResolutionError) as e:
        logger.error(f"Upstream error in fusion: {e}")
        raise FusionError(f"Fusion failed due to upstream error: {e}") from e
    except Exception as e:
        logger.error(f"Unexpected error in fusion: {e}")
        raise FusionError(f"Fusion failed unexpectedly: {e}") from e


__all__ = [
    "FusionError",
    "FusionResult",
    "PromptFusion",
    "fuse_sources",
    "MAX_CONTENT_LENGTH",
]
