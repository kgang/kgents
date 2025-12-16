"""
Policy-Based Resolution: Resolve conflicts using learned habits.

Wave 5 of the Evergreen Prompt System.

Per taste decision: merge heuristically, not with hard precedence.

Resolution uses PolicyVector from HabitEncoder to make informed choices:
1. VERBOSITY-WEIGHTED: Choose based on content length preferences
2. RIGIDITY-WEIGHTED: Choose based on source rigidity
3. DOMAIN-FOCUSED: Choose based on domain relevance
4. RECENCY-WEIGHTED: Choose based on source freshness
5. HYBRID: Combine multiple strategies

This is the "textual gradient" part of TextGRAD - policy influences direction.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

from .conflict import Conflict, ConflictSeverity, ConflictType

if TYPE_CHECKING:
    from ..habits.policy import PolicyVector
    from ..sources.base import SourceResult

logger = logging.getLogger(__name__)

# Constants for validation
MIN_RIGIDITY = 0.0
MAX_RIGIDITY = 1.0


class ResolutionError(Exception):
    """Exception raised for resolution errors."""

    pass


class ResolutionStrategy(Enum):
    """Strategies for resolving conflicts."""

    PREFER_HIGHER_RIGIDITY = auto()  # Choose more rigid source
    PREFER_LOWER_RIGIDITY = auto()  # Choose more adaptive source
    PREFER_VERBOSITY = auto()  # Match policy verbosity preference
    PREFER_DOMAIN_MATCH = auto()  # Match domain focus
    PREFER_RECENCY = auto()  # Choose more recent source
    PREFER_SOURCE_A = auto()  # Explicitly prefer first source
    PREFER_SOURCE_B = auto()  # Explicitly prefer second source
    MERGE_CONCAT = auto()  # Concatenate both
    MERGE_INTERLEAVE = auto()  # Interleave content
    HYBRID = auto()  # Combine strategies


@dataclass(frozen=True)
class Resolution:
    """
    A resolution for a specific conflict.

    Attributes:
        conflict: The conflict being resolved
        strategy: Strategy used to resolve
        chosen_source: Which source was chosen ("a", "b", "merged")
        resolved_content: The resolved content
        reasoning: Why this resolution was chosen
        confidence: How confident we are in this resolution (0.0-1.0)
    """

    conflict: Conflict
    strategy: ResolutionStrategy
    chosen_source: str
    resolved_content: str
    reasoning: str
    confidence: float = 0.5

    @property
    def summary(self) -> str:
        """One-line summary of the resolution."""
        return f"[{self.strategy.name}] → {self.chosen_source}: {self.reasoning[:50]}"


@dataclass
class PolicyResolver:
    """
    Resolve conflicts using PolicyVector.

    Per taste decision: merge heuristically using learned habits.

    Example:
        >>> resolver = PolicyResolver(policy=PolicyVector.default())
        >>> resolution = resolver.resolve(conflict, content_a, content_b)
        >>> print(resolution.chosen_source)
        "a"
    """

    policy: "PolicyVector | None" = None
    default_strategy: ResolutionStrategy = ResolutionStrategy.HYBRID

    def _validate_rigidity(self, rigidity: float, name: str) -> float:
        """Validate and clamp rigidity value."""
        if not isinstance(rigidity, (int, float)):
            raise ResolutionError(
                f"{name} must be numeric, got {type(rigidity).__name__}"
            )
        # Clamp to valid range
        clamped = max(MIN_RIGIDITY, min(MAX_RIGIDITY, rigidity))
        if clamped != rigidity:
            logger.warning(
                f"{name}={rigidity} out of range [{MIN_RIGIDITY}, {MAX_RIGIDITY}], clamped to {clamped}"
            )
        return clamped

    def _validate_content(self, content: str, name: str) -> None:
        """Validate content string."""
        if content is None:
            raise ResolutionError(f"{name} cannot be None")
        if not isinstance(content, str):
            raise ResolutionError(
                f"{name} must be a string, got {type(content).__name__}"
            )

    def resolve(
        self,
        conflict: Conflict,
        content_a: str,
        content_b: str,
        rigidity_a: float = 0.5,
        rigidity_b: float = 0.5,
        domain_hint: str = "",
    ) -> Resolution:
        """
        Resolve a conflict between two content strings.

        Args:
            conflict: The conflict to resolve
            content_a: Content from source A
            content_b: Content from source B
            rigidity_a: Rigidity of source A (0.0-1.0)
            rigidity_b: Rigidity of source B (0.0-1.0)
            domain_hint: Hint about the domain (for domain-focused resolution)

        Returns:
            Resolution with chosen content and reasoning

        Raises:
            ResolutionError: If inputs are invalid
        """
        # Validate inputs
        if conflict is None:
            raise ResolutionError("conflict cannot be None")
        self._validate_content(content_a, "content_a")
        self._validate_content(content_b, "content_b")
        rigidity_a = self._validate_rigidity(rigidity_a, "rigidity_a")
        rigidity_b = self._validate_rigidity(rigidity_b, "rigidity_b")

        logger.debug(
            f"Resolving {conflict.conflict_type.name} conflict between sources (rigidity: {rigidity_a:.2f} vs {rigidity_b:.2f})"
        )

        # Handle specific conflict types
        if conflict.conflict_type == ConflictType.DUPLICATION:
            return self._resolve_duplication(
                conflict, content_a, content_b, rigidity_a, rigidity_b
            )

        if conflict.conflict_type == ConflictType.CONTRADICTION:
            return self._resolve_contradiction(
                conflict, content_a, content_b, rigidity_a, rigidity_b
            )

        if conflict.conflict_type == ConflictType.INCOMPATIBLE:
            return self._resolve_incompatibility(
                conflict, content_a, content_b, rigidity_a, rigidity_b
            )

        if conflict.conflict_type == ConflictType.OVERWRITE:
            return self._resolve_overwrite(
                conflict, content_a, content_b, rigidity_a, rigidity_b, domain_hint
            )

        # Default: semantic conflict - use hybrid strategy
        return self._resolve_semantic(
            conflict, content_a, content_b, rigidity_a, rigidity_b, domain_hint
        )

    def _resolve_duplication(
        self,
        conflict: Conflict,
        content_a: str,
        content_b: str,
        rigidity_a: float,
        rigidity_b: float,
    ) -> Resolution:
        """Resolve duplication by choosing the more rigid source."""
        # For duplicates, prefer higher rigidity (more stable)
        if rigidity_a >= rigidity_b:
            return Resolution(
                conflict=conflict,
                strategy=ResolutionStrategy.PREFER_HIGHER_RIGIDITY,
                chosen_source="a",
                resolved_content=content_a,
                reasoning=f"Duplicate content, choosing source A (rigidity={rigidity_a:.2f})",
                confidence=0.9,
            )
        else:
            return Resolution(
                conflict=conflict,
                strategy=ResolutionStrategy.PREFER_HIGHER_RIGIDITY,
                chosen_source="b",
                resolved_content=content_b,
                reasoning=f"Duplicate content, choosing source B (rigidity={rigidity_b:.2f})",
                confidence=0.9,
            )

    def _resolve_contradiction(
        self,
        conflict: Conflict,
        content_a: str,
        content_b: str,
        rigidity_a: float,
        rigidity_b: float,
    ) -> Resolution:
        """
        Resolve contradiction using policy.

        For contradictions, we need to make a choice. Policy risk_tolerance
        influences whether we prefer the safer (higher rigidity) or
        more experimental (lower rigidity) option.
        """
        risk_tolerance = self.policy.risk_tolerance if self.policy else 0.4

        # High risk tolerance → prefer less rigid (more flexible)
        # Low risk tolerance → prefer more rigid (safer)
        if risk_tolerance > 0.6:
            # Experimental: prefer lower rigidity
            if rigidity_a <= rigidity_b:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_LOWER_RIGIDITY,
                    chosen_source="a",
                    resolved_content=content_a,
                    reasoning=f"Contradiction: policy prefers experimental (risk={risk_tolerance:.2f}), source A more adaptive",
                    confidence=0.6,
                )
            else:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_LOWER_RIGIDITY,
                    chosen_source="b",
                    resolved_content=content_b,
                    reasoning=f"Contradiction: policy prefers experimental (risk={risk_tolerance:.2f}), source B more adaptive",
                    confidence=0.6,
                )
        else:
            # Conservative: prefer higher rigidity
            if rigidity_a >= rigidity_b:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_HIGHER_RIGIDITY,
                    chosen_source="a",
                    resolved_content=content_a,
                    reasoning=f"Contradiction: policy prefers safe (risk={risk_tolerance:.2f}), source A more stable",
                    confidence=0.7,
                )
            else:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_HIGHER_RIGIDITY,
                    chosen_source="b",
                    resolved_content=content_b,
                    reasoning=f"Contradiction: policy prefers safe (risk={risk_tolerance:.2f}), source B more stable",
                    confidence=0.7,
                )

    def _resolve_incompatibility(
        self,
        conflict: Conflict,
        content_a: str,
        content_b: str,
        rigidity_a: float,
        rigidity_b: float,
    ) -> Resolution:
        """
        Resolve structural incompatibility.

        For incompatible formats, prefer the format that matches
        policy formality preference.
        """
        formality = self.policy.formality if self.policy else 0.6

        # Check which content is more "formal" (has structure)
        has_table_a = "|" in content_a and "---" in content_a
        has_table_b = "|" in content_b and "---" in content_b
        has_headers_a = content_a.count("#") > 2
        has_headers_b = content_b.count("#") > 2

        formal_score_a = (1 if has_table_a else 0) + (1 if has_headers_a else 0)
        formal_score_b = (1 if has_table_b else 0) + (1 if has_headers_b else 0)

        # High formality → prefer more structured
        if formality > 0.6:
            if formal_score_a >= formal_score_b:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_VERBOSITY,
                    chosen_source="a",
                    resolved_content=content_a,
                    reasoning=f"Incompatible: policy prefers formal (formality={formality:.2f}), source A more structured",
                    confidence=0.7,
                )
            else:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_VERBOSITY,
                    chosen_source="b",
                    resolved_content=content_b,
                    reasoning=f"Incompatible: policy prefers formal (formality={formality:.2f}), source B more structured",
                    confidence=0.7,
                )
        else:
            # Prefer simpler format
            if formal_score_a <= formal_score_b:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_VERBOSITY,
                    chosen_source="a",
                    resolved_content=content_a,
                    reasoning=f"Incompatible: policy prefers casual (formality={formality:.2f}), source A simpler",
                    confidence=0.7,
                )
            else:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_VERBOSITY,
                    chosen_source="b",
                    resolved_content=content_b,
                    reasoning=f"Incompatible: policy prefers casual (formality={formality:.2f}), source B simpler",
                    confidence=0.7,
                )

    def _resolve_overwrite(
        self,
        conflict: Conflict,
        content_a: str,
        content_b: str,
        rigidity_a: float,
        rigidity_b: float,
        domain_hint: str,
    ) -> Resolution:
        """
        Resolve section overwrite conflict.

        Uses domain focus and verbosity to choose.
        """
        verbosity = self.policy.verbosity if self.policy else 0.5
        domain_focus = (
            self.policy.get_domain_focus(domain_hint, 0.5) if self.policy else 0.5
        )

        # If domain has high focus, prefer the longer/more detailed content
        if domain_focus > 0.7:
            if len(content_a) >= len(content_b):
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_DOMAIN_MATCH,
                    chosen_source="a",
                    resolved_content=content_a,
                    reasoning=f"Overwrite: high domain focus ({domain_hint}={domain_focus:.2f}), source A more complete",
                    confidence=0.7,
                )
            else:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_DOMAIN_MATCH,
                    chosen_source="b",
                    resolved_content=content_b,
                    reasoning=f"Overwrite: high domain focus ({domain_hint}={domain_focus:.2f}), source B more complete",
                    confidence=0.7,
                )

        # Otherwise, use verbosity preference
        len_a = len(content_a)
        len_b = len(content_b)

        if verbosity > 0.6:
            # Prefer longer content
            if len_a >= len_b:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_VERBOSITY,
                    chosen_source="a",
                    resolved_content=content_a,
                    reasoning=f"Overwrite: policy prefers verbose (verbosity={verbosity:.2f}), source A longer",
                    confidence=0.6,
                )
            else:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_VERBOSITY,
                    chosen_source="b",
                    resolved_content=content_b,
                    reasoning=f"Overwrite: policy prefers verbose (verbosity={verbosity:.2f}), source B longer",
                    confidence=0.6,
                )
        elif verbosity < 0.4:
            # Prefer shorter content
            if len_a <= len_b:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_VERBOSITY,
                    chosen_source="a",
                    resolved_content=content_a,
                    reasoning=f"Overwrite: policy prefers terse (verbosity={verbosity:.2f}), source A shorter",
                    confidence=0.6,
                )
            else:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_VERBOSITY,
                    chosen_source="b",
                    resolved_content=content_b,
                    reasoning=f"Overwrite: policy prefers terse (verbosity={verbosity:.2f}), source B shorter",
                    confidence=0.6,
                )
        else:
            # Neutral: prefer higher rigidity
            if rigidity_a >= rigidity_b:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_HIGHER_RIGIDITY,
                    chosen_source="a",
                    resolved_content=content_a,
                    reasoning=f"Overwrite: neutral verbosity, preferring higher rigidity (source A={rigidity_a:.2f})",
                    confidence=0.6,
                )
            else:
                return Resolution(
                    conflict=conflict,
                    strategy=ResolutionStrategy.PREFER_HIGHER_RIGIDITY,
                    chosen_source="b",
                    resolved_content=content_b,
                    reasoning=f"Overwrite: neutral verbosity, preferring higher rigidity (source B={rigidity_b:.2f})",
                    confidence=0.6,
                )

    def _resolve_semantic(
        self,
        conflict: Conflict,
        content_a: str,
        content_b: str,
        rigidity_a: float,
        rigidity_b: float,
        domain_hint: str,
    ) -> Resolution:
        """
        Resolve general semantic conflict using hybrid strategy.

        Combines multiple factors:
        1. Rigidity (stability)
        2. Verbosity match
        3. Domain focus
        """
        # Collect scores
        scores_a = 0.0
        scores_b = 0.0
        reasons: list[str] = []

        # Factor 1: Rigidity (higher = more stable)
        rigidity_diff = rigidity_a - rigidity_b
        scores_a += rigidity_diff * 0.3
        scores_b -= rigidity_diff * 0.3
        reasons.append(f"rigidity: A={rigidity_a:.2f}, B={rigidity_b:.2f}")

        if self.policy:
            # Factor 2: Verbosity match
            verbosity = self.policy.verbosity
            len_a = len(content_a)
            len_b = len(content_b)

            if verbosity > 0.5:
                # Prefer longer
                if len_a > len_b:
                    scores_a += 0.2
                else:
                    scores_b += 0.2
                reasons.append(f"verbosity prefers {'A' if len_a > len_b else 'B'}")
            else:
                # Prefer shorter
                if len_a < len_b:
                    scores_a += 0.2
                else:
                    scores_b += 0.2
                reasons.append(f"terseness prefers {'A' if len_a < len_b else 'B'}")

            # Factor 3: Domain focus
            if domain_hint:
                domain_focus = self.policy.get_domain_focus(domain_hint, 0.5)
                if domain_focus > 0.6:
                    # High focus: prefer more complete content
                    if len_a > len_b:
                        scores_a += 0.3
                    else:
                        scores_b += 0.3
                    reasons.append(
                        f"domain {domain_hint} ({domain_focus:.2f}) prefers {'A' if len_a > len_b else 'B'}"
                    )

        # Make decision
        if scores_a >= scores_b:
            return Resolution(
                conflict=conflict,
                strategy=ResolutionStrategy.HYBRID,
                chosen_source="a",
                resolved_content=content_a,
                reasoning=f"Hybrid resolution: {', '.join(reasons)} → A ({scores_a:.2f} vs {scores_b:.2f})",
                confidence=0.5 + abs(scores_a - scores_b) * 0.3,
            )
        else:
            return Resolution(
                conflict=conflict,
                strategy=ResolutionStrategy.HYBRID,
                chosen_source="b",
                resolved_content=content_b,
                reasoning=f"Hybrid resolution: {', '.join(reasons)} → B ({scores_b:.2f} vs {scores_a:.2f})",
                confidence=0.5 + abs(scores_a - scores_b) * 0.3,
            )

    def resolve_all(
        self,
        conflicts: list[Conflict],
        content_a: str,
        content_b: str,
        rigidity_a: float = 0.5,
        rigidity_b: float = 0.5,
        domain_hint: str = "",
    ) -> list[Resolution]:
        """
        Resolve all conflicts between two content strings.

        Args:
            conflicts: List of conflicts to resolve
            content_a: Content from source A
            content_b: Content from source B
            rigidity_a: Rigidity of source A
            rigidity_b: Rigidity of source B
            domain_hint: Domain hint for resolution

        Returns:
            List of resolutions
        """
        return [
            self.resolve(
                conflict, content_a, content_b, rigidity_a, rigidity_b, domain_hint
            )
            for conflict in conflicts
        ]


def resolve_conflict(
    conflict: Conflict,
    content_a: str,
    content_b: str,
    policy: "PolicyVector | None" = None,
    rigidity_a: float = 0.5,
    rigidity_b: float = 0.5,
) -> Resolution:
    """
    Convenience function to resolve a single conflict.

    Args:
        conflict: The conflict to resolve
        content_a: Content from source A
        content_b: Content from source B
        policy: Optional PolicyVector for informed resolution
        rigidity_a: Rigidity of source A
        rigidity_b: Rigidity of source B

    Returns:
        Resolution with chosen content

    Raises:
        ResolutionError: If inputs are invalid
    """
    try:
        resolver = PolicyResolver(policy=policy)
        return resolver.resolve(conflict, content_a, content_b, rigidity_a, rigidity_b)
    except ResolutionError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in conflict resolution: {e}")
        raise ResolutionError(f"Failed to resolve conflict: {e}") from e


__all__ = [
    "ResolutionStrategy",
    "Resolution",
    "ResolutionError",
    "PolicyResolver",
    "resolve_conflict",
    "MIN_RIGIDITY",
    "MAX_RIGIDITY",
]
