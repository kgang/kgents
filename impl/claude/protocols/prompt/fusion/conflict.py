"""
Conflict Detection: Identify contradictions between multiple source contents.

Wave 5 of the Evergreen Prompt System.

A conflict occurs when multiple sources provide content that:
1. CONTRADICTS: Makes opposing claims (e.g., "use X" vs "don't use X")
2. OVERWRITES: Different values for the same field/section
3. DUPLICATES: Redundant information that shouldn't repeat
4. INCOMPATIBLE: Structurally incompatible formats

Conflict detection uses pattern matching and heuristics.
For complex semantic conflicts, consider LLM-as-judge (Wave 6).
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING

from .similarity import SemanticSimilarity, SimilarityError, SimilarityResult

if TYPE_CHECKING:
    from ..sources.base import SourceResult

logger = logging.getLogger(__name__)

# Constants for validation
MAX_CONTENT_LENGTH = 1_000_000  # 1MB max content size
MAX_PATTERN_COUNT = 100  # Maximum number of patterns to prevent regex DoS


class ConflictError(Exception):
    """Exception raised for conflict detection errors."""

    pass


class ConflictType(Enum):
    """Types of conflicts between sources."""

    CONTRADICTION = auto()  # Opposing claims
    OVERWRITE = auto()  # Same field, different values
    DUPLICATION = auto()  # Redundant content
    INCOMPATIBLE = auto()  # Structural incompatibility
    SEMANTIC = auto()  # Semantic disagreement (needs resolution)


class ConflictSeverity(Enum):
    """Severity levels for conflicts."""

    LOW = auto()  # Cosmetic/minor differences
    MEDIUM = auto()  # Needs attention but not blocking
    HIGH = auto()  # Must be resolved before merge
    CRITICAL = auto()  # Cannot proceed without resolution


@dataclass(frozen=True)
class Conflict:
    """
    A detected conflict between two source contents.

    Attributes:
        conflict_type: What kind of conflict this is
        severity: How severe the conflict is
        source_a_name: Name of first source
        source_b_name: Name of second source
        description: Human-readable description
        location_a: Where in source A the conflict appears
        location_b: Where in source B the conflict appears
        snippet_a: Conflicting content from A
        snippet_b: Conflicting content from B
        resolution_hint: Suggested resolution strategy
    """

    conflict_type: ConflictType
    severity: ConflictSeverity
    source_a_name: str
    source_b_name: str
    description: str
    location_a: str = ""
    location_b: str = ""
    snippet_a: str = ""
    snippet_b: str = ""
    resolution_hint: str = ""

    @property
    def summary(self) -> str:
        """One-line summary of the conflict."""
        return f"[{self.severity.name}] {self.conflict_type.name}: {self.description[:60]}"

    def is_blocking(self) -> bool:
        """Check if this conflict blocks merging."""
        return self.severity in (ConflictSeverity.HIGH, ConflictSeverity.CRITICAL)


@dataclass
class ConflictDetector:
    """
    Detect conflicts between multiple source contents.

    Uses heuristic patterns to identify common conflict types.

    Example:
        >>> detector = ConflictDetector()
        >>> conflicts = detector.detect(source_a, source_b)
        >>> for c in conflicts:
        ...     print(c.summary)
    """

    similarity_threshold: float = 0.9  # Above this = no semantic conflict
    duplication_threshold: float = 0.95  # Above this = duplication
    contradiction_patterns: list[tuple[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize default contradiction patterns and validate thresholds."""
        # Validate thresholds
        if not (0.0 <= self.similarity_threshold <= 1.0):
            raise ConflictError(
                f"similarity_threshold must be between 0.0 and 1.0, got {self.similarity_threshold}"
            )
        if not (0.0 <= self.duplication_threshold <= 1.0):
            raise ConflictError(
                f"duplication_threshold must be between 0.0 and 1.0, got {self.duplication_threshold}"
            )

        if not self.contradiction_patterns:
            # Patterns that indicate contradictions when both match
            # Note: These are independent patterns - we don't use backreferences across patterns
            self.contradiction_patterns = [
                # Negation patterns (simpler - just detect presence of positive/negative terms)
                (
                    r"\b(use|prefer|recommend)\b",
                    r"\b(don\'t use|do not use|avoid|never use)\b",
                ),
                (r"\b(enable|activate)\b", r"\b(disable|deactivate)\b"),
                (r"\balways\b", r"\bnever\b"),
                # Boolean patterns
                (r"\brequired:\s*true\b", r"\brequired:\s*false\b"),
                (r"\benabled:\s*true\b", r"\benabled:\s*false\b"),
                # Instruction conflicts
                (r"\bmust\b", r"\bmust not\b"),
                (r"\bshould\b", r"\bshould not\b"),
            ]

    def _validate_content(self, content: str, name: str) -> None:
        """Validate content string."""
        if content is None:
            raise ConflictError(f"{name} cannot be None")
        if not isinstance(content, str):
            raise ConflictError(f"{name} must be a string, got {type(content).__name__}")
        if len(content) > MAX_CONTENT_LENGTH:
            raise ConflictError(f"{name} exceeds maximum length of {MAX_CONTENT_LENGTH} chars")

    def detect(
        self,
        content_a: str,
        content_b: str,
        source_a_name: str = "source_a",
        source_b_name: str = "source_b",
    ) -> list[Conflict]:
        """
        Detect conflicts between two content strings.

        Args:
            content_a: First content
            content_b: Second content
            source_a_name: Name for source A
            source_b_name: Name for source B

        Returns:
            List of detected conflicts

        Raises:
            ConflictError: If content is invalid (None, wrong type, too large)
        """
        # Validate inputs
        self._validate_content(content_a, "content_a")
        self._validate_content(content_b, "content_b")

        logger.debug(
            f"Detecting conflicts between '{source_a_name}' ({len(content_a)} chars) and '{source_b_name}' ({len(content_b)} chars)"
        )

        conflicts: list[Conflict] = []

        # Check for identical content (no conflict)
        if content_a == content_b:
            logger.debug("Contents are identical, no conflicts")
            return conflicts

        # Check for duplication
        dup_conflict = self._check_duplication(content_a, content_b, source_a_name, source_b_name)
        if dup_conflict:
            conflicts.append(dup_conflict)
            # If it's near-duplicate, likely no other conflicts
            if dup_conflict.severity == ConflictSeverity.LOW:
                return conflicts

        # Check for contradiction patterns
        contradiction_conflicts = self._check_contradictions(
            content_a, content_b, source_a_name, source_b_name
        )
        conflicts.extend(contradiction_conflicts)

        # Check for structural incompatibility
        struct_conflict = self._check_structural_incompatibility(
            content_a, content_b, source_a_name, source_b_name
        )
        if struct_conflict:
            conflicts.append(struct_conflict)

        # Check for header/section overwrites
        overwrite_conflicts = self._check_section_overwrites(
            content_a, content_b, source_a_name, source_b_name
        )
        conflicts.extend(overwrite_conflicts)

        # Check semantic similarity for remaining content
        semantic_conflict = self._check_semantic_conflict(
            content_a, content_b, source_a_name, source_b_name
        )
        if semantic_conflict:
            conflicts.append(semantic_conflict)

        return conflicts

    def detect_from_results(
        self,
        results: list["SourceResult"],
    ) -> list[Conflict]:
        """
        Detect conflicts between multiple SourceResults.

        Compares each pair of results that have content.
        """
        conflicts: list[Conflict] = []

        # Filter to successful results with content
        valid_results = [r for r in results if r.success and r.content]

        # Compare each pair
        for i, result_a in enumerate(valid_results):
            for result_b in valid_results[i + 1 :]:
                pair_conflicts = self.detect(
                    result_a.content or "",
                    result_b.content or "",
                    result_a.source_name,
                    result_b.source_name,
                )
                conflicts.extend(pair_conflicts)

        return conflicts

    def _check_duplication(
        self,
        content_a: str,
        content_b: str,
        source_a_name: str,
        source_b_name: str,
    ) -> Conflict | None:
        """Check if contents are near-duplicates."""
        similarity = SemanticSimilarity()
        result = similarity.compare(content_a, content_b)

        if result.score >= self.duplication_threshold:
            return Conflict(
                conflict_type=ConflictType.DUPLICATION,
                severity=ConflictSeverity.LOW,
                source_a_name=source_a_name,
                source_b_name=source_b_name,
                description=f"Near-duplicate content (similarity={result.score:.2f})",
                resolution_hint="Use either source, or merge trivially",
            )

        return None

    def _check_contradictions(
        self,
        content_a: str,
        content_b: str,
        source_a_name: str,
        source_b_name: str,
    ) -> list[Conflict]:
        """Check for contradiction patterns."""
        conflicts: list[Conflict] = []
        content_a_lower = content_a.lower()
        content_b_lower = content_b.lower()

        for pattern_pos, pattern_neg in self.contradiction_patterns:
            try:
                # Check if A has positive and B has negative
                matches_a_pos = re.findall(pattern_pos, content_a_lower)
                matches_b_neg = re.findall(pattern_neg, content_b_lower)

                if matches_a_pos and matches_b_neg:
                    conflicts.append(
                        Conflict(
                            conflict_type=ConflictType.CONTRADICTION,
                            severity=ConflictSeverity.HIGH,
                            source_a_name=source_a_name,
                            source_b_name=source_b_name,
                            description=f"Contradicting instructions: '{matches_a_pos[0]}' vs '{matches_b_neg[0]}'",
                            snippet_a=str(matches_a_pos[0])[:100],
                            snippet_b=str(matches_b_neg[0])[:100],
                            resolution_hint="Choose one instruction based on policy",
                        )
                    )

                # Check reverse (A has negative, B has positive)
                matches_a_neg = re.findall(pattern_neg, content_a_lower)
                matches_b_pos = re.findall(pattern_pos, content_b_lower)

                if matches_a_neg and matches_b_pos:
                    conflicts.append(
                        Conflict(
                            conflict_type=ConflictType.CONTRADICTION,
                            severity=ConflictSeverity.HIGH,
                            source_a_name=source_a_name,
                            source_b_name=source_b_name,
                            description=f"Contradicting instructions: '{matches_a_neg[0]}' vs '{matches_b_pos[0]}'",
                            snippet_a=str(matches_a_neg[0])[:100],
                            snippet_b=str(matches_b_pos[0])[:100],
                            resolution_hint="Choose one instruction based on policy",
                        )
                    )
            except re.error as e:
                # Log and skip invalid patterns
                logger.warning(f"Invalid regex pattern skipped: {pattern_pos} / {pattern_neg}: {e}")
                continue

        return conflicts

    def _check_structural_incompatibility(
        self,
        content_a: str,
        content_b: str,
        source_a_name: str,
        source_b_name: str,
    ) -> Conflict | None:
        """Check for structural incompatibility."""
        # Check if one is markdown and one is not
        has_markdown_a = bool(re.search(r"^#+\s", content_a, re.MULTILINE))
        has_markdown_b = bool(re.search(r"^#+\s", content_b, re.MULTILINE))

        # Check if one has code blocks and other doesn't

        # Check if one is table-formatted
        has_table_a = "|" in content_a and "---" in content_a
        has_table_b = "|" in content_b and "---" in content_b

        # Different formats = structural incompatibility
        if has_markdown_a != has_markdown_b:
            return Conflict(
                conflict_type=ConflictType.INCOMPATIBLE,
                severity=ConflictSeverity.MEDIUM,
                source_a_name=source_a_name,
                source_b_name=source_b_name,
                description="Different markdown structure (one uses headers, one doesn't)",
                resolution_hint="Convert to common format before merging",
            )

        if has_table_a != has_table_b:
            return Conflict(
                conflict_type=ConflictType.INCOMPATIBLE,
                severity=ConflictSeverity.MEDIUM,
                source_a_name=source_a_name,
                source_b_name=source_b_name,
                description="Different format (one uses tables, one doesn't)",
                resolution_hint="Choose table or prose format",
            )

        return None

    def _check_section_overwrites(
        self,
        content_a: str,
        content_b: str,
        source_a_name: str,
        source_b_name: str,
    ) -> list[Conflict]:
        """Check for overlapping sections with different content."""
        conflicts: list[Conflict] = []

        # Extract headers
        headers_a = set(re.findall(r"^(#+\s+.+?)$", content_a, re.MULTILINE))
        headers_b = set(re.findall(r"^(#+\s+.+?)$", content_b, re.MULTILINE))

        # Find overlapping headers
        common_headers = headers_a & headers_b

        for header in common_headers:
            # Extract content under this header from both
            section_a = self._extract_section(content_a, header)
            section_b = self._extract_section(content_b, header)

            if section_a and section_b and section_a != section_b:
                similarity = SemanticSimilarity()
                result = similarity.compare(section_a, section_b)

                if result.score < self.similarity_threshold:
                    conflicts.append(
                        Conflict(
                            conflict_type=ConflictType.OVERWRITE,
                            severity=ConflictSeverity.MEDIUM,
                            source_a_name=source_a_name,
                            source_b_name=source_b_name,
                            description=f"Section '{header}' has different content",
                            location_a=header,
                            location_b=header,
                            snippet_a=section_a[:100],
                            snippet_b=section_b[:100],
                            resolution_hint=f"Merge section content (similarity={result.score:.2f})",
                        )
                    )

        return conflicts

    def _extract_section(self, content: str, header: str) -> str:
        """Extract content under a markdown header."""
        # Escape special regex chars in header
        escaped_header = re.escape(header)

        # Find header level
        match = re.match(r"^(#+)", header)
        if not match:
            return ""
        level = len(match.group(1))

        # Pattern: from this header to next header of same or higher level
        pattern = rf"^{escaped_header}$\s*\n(.*?)(?=^#{{{1},{level}}}\s|\Z)"
        section_match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

        if section_match:
            return section_match.group(1).strip()
        return ""

    def _check_semantic_conflict(
        self,
        content_a: str,
        content_b: str,
        source_a_name: str,
        source_b_name: str,
    ) -> Conflict | None:
        """Check for general semantic disagreement."""
        similarity = SemanticSimilarity()
        result = similarity.compare(content_a, content_b)

        # If similarity is in the "unclear" zone, flag for review
        if 0.3 < result.score < self.similarity_threshold:
            return Conflict(
                conflict_type=ConflictType.SEMANTIC,
                severity=ConflictSeverity.LOW,
                source_a_name=source_a_name,
                source_b_name=source_b_name,
                description=f"Moderate semantic difference (similarity={result.score:.2f})",
                resolution_hint="Consider policy-based merge or manual review",
            )

        return None


def detect_conflicts(
    content_a: str,
    content_b: str,
    source_a_name: str = "source_a",
    source_b_name: str = "source_b",
) -> list[Conflict]:
    """
    Convenience function to detect conflicts between two strings.

    Args:
        content_a: First content
        content_b: Second content
        source_a_name: Name for source A
        source_b_name: Name for source B

    Returns:
        List of detected conflicts

    Raises:
        ConflictError: If content is invalid (None, wrong type, too large)
    """
    try:
        detector = ConflictDetector()
        return detector.detect(content_a, content_b, source_a_name, source_b_name)
    except ConflictError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in conflict detection: {e}")
        raise ConflictError(f"Failed to detect conflicts: {e}") from e


__all__ = [
    "ConflictType",
    "ConflictSeverity",
    "Conflict",
    "ConflictError",
    "ConflictDetector",
    "detect_conflicts",
    "MAX_CONTENT_LENGTH",
]
