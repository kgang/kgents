"""
K-Block Splitting: Heuristics for when one document should become multiple K-Blocks.

> *"A document that tries to say everything says nothing."*

This module implements the K-Block splitting heuristics from the Zero Seed Genesis
Grand Strategy. It detects when a single document should be split into multiple
K-Blocks for better coherence and organization.

Heuristics:
    1. Multiple distinct concepts (headings at same level)
    2. Internal contradiction (super-additive loss)
    3. Size threshold (> 5000 tokens)
    4. Layer mixing (L3 goals with L5 implementations)

Philosophy:
    "Splitting is never forced. We suggest, show evidence, and let the user decide.
     This is the Linear design philosophy—the product adapts to the user."

Laws:
    Law 1: Splitting is always a suggestion, never automatic
    Law 2: Splitting requires user approval
    Law 3: Split recommendations include evidence (loss scores, sections)

See: plans/zero-seed-genesis-grand-strategy.md (Phase 2, Section 5.3)
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Split Types
# =============================================================================


class SplitReasonType(Enum):
    """Reason why a split is recommended."""

    MULTIPLE_CONCEPTS = "multiple_concepts"  # Too many distinct topics
    INTERNAL_CONTRADICTION = "internal_contradiction"  # Sections contradict
    SIZE_THRESHOLD = "size_threshold"  # Document too large
    LAYER_MIXING = "layer_mixing"  # Mixing L3 goals with L5 implementation


@dataclass
class SplitReason:
    """
    A reason to split a document.

    Attributes:
        type: Type of split reason
        description: Human-readable description
        confidence: Confidence score (0.0-1.0)
        evidence: Additional evidence (section names, loss scores, etc.)
    """

    type: SplitReasonType
    description: str
    confidence: float
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "type": self.type.value,
            "description": self.description,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


@dataclass
class SplitSection:
    """
    A section that would become its own K-Block.

    Attributes:
        title: Section title
        content: Section content
        start_line: Starting line number
        end_line: Ending line number
        estimated_layer: Estimated layer assignment
        estimated_tokens: Estimated token count
    """

    title: str
    content: str
    start_line: int
    end_line: int
    estimated_layer: int | None = None
    estimated_tokens: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "estimated_layer": self.estimated_layer,
            "estimated_tokens": self.estimated_tokens,
        }


@dataclass
class SplitPlan:
    """
    A plan for how to split a document.

    Attributes:
        sections: Sections that would become separate K-Blocks
        recommended_paths: Suggested file paths for each section
        total_loss_before: Total Galois loss before split
        estimated_loss_after: Estimated total loss after split
        improvement: Expected improvement in coherence
    """

    sections: list[SplitSection]
    recommended_paths: list[str] = field(default_factory=list)
    total_loss_before: float = 1.0
    estimated_loss_after: float = 0.8
    improvement: float = 0.2

    @property
    def num_sections(self) -> int:
        """Number of sections in the split."""
        return len(self.sections)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "sections": [section.to_dict() for section in self.sections],
            "recommended_paths": self.recommended_paths,
            "total_loss_before": self.total_loss_before,
            "estimated_loss_after": self.estimated_loss_after,
            "improvement": self.improvement,
            "num_sections": self.num_sections,
        }


@dataclass
class SplitRecommendation:
    """
    A recommendation to split a document.

    Attributes:
        should_split: Whether splitting is recommended
        reasons: Reasons why splitting is recommended
        plan: The split plan (if should_split is True)
        requires_user_approval: Whether user must approve
    """

    should_split: bool
    reasons: list[SplitReason] = field(default_factory=list)
    plan: SplitPlan | None = None
    requires_user_approval: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "should_split": self.should_split,
            "reasons": [reason.to_dict() for reason in self.reasons],
            "plan": self.plan.to_dict() if self.plan else None,
            "requires_user_approval": self.requires_user_approval,
        }


# =============================================================================
# Splitting Service
# =============================================================================


class SplittingService:
    """
    Service for analyzing documents and recommending splits.

    Implements the four heuristics from the Grand Strategy.
    """

    # Thresholds (tunable)
    MAX_TOKENS = 5000  # Token threshold for size-based split
    MAX_SECTIONS = 3  # Section count threshold for concept-based split
    CONTRADICTION_THRESHOLD = 0.4  # Loss threshold for contradiction detection
    LAYER_DIVERSITY_THRESHOLD = 2  # Max layer spread allowed

    def __init__(self):
        """Initialize splitting service."""
        pass

    async def analyze_for_splitting(
        self, content: bytes, path: str, galois_loss: float = 0.5
    ) -> SplitRecommendation:
        """
        Analyze document for splitting recommendations.

        Applies all four heuristics:
        1. Multiple distinct concepts
        2. Internal contradiction
        3. Size threshold
        4. Layer mixing

        Args:
            content: Document content
            path: Document path
            galois_loss: Current Galois loss score

        Returns:
            SplitRecommendation with all findings
        """
        reasons: list[SplitReason] = []

        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            # Binary files cannot be split
            return SplitRecommendation(should_split=False)

        # Extract sections
        sections = self._extract_sections(text)

        # HEURISTIC 1: Multiple distinct concepts
        if len(sections) > self.MAX_SECTIONS:
            reasons.append(
                SplitReason(
                    type=SplitReasonType.MULTIPLE_CONCEPTS,
                    description=f"Document has {len(sections)} distinct sections",
                    confidence=0.7,
                    evidence={"section_count": len(sections), "sections": sections},
                )
            )

        # HEURISTIC 2: Internal contradiction
        internal_loss = await self._compute_internal_contradiction(sections)
        if internal_loss > self.CONTRADICTION_THRESHOLD:
            reasons.append(
                SplitReason(
                    type=SplitReasonType.INTERNAL_CONTRADICTION,
                    description=f"Sections contradict each other (loss: {internal_loss:.2f})",
                    confidence=0.9,
                    evidence={
                        "internal_loss": internal_loss,
                        "threshold": self.CONTRADICTION_THRESHOLD,
                    },
                )
            )

        # HEURISTIC 3: Size threshold
        estimated_tokens = len(text.split())  # Rough approximation
        if estimated_tokens > self.MAX_TOKENS:
            reasons.append(
                SplitReason(
                    type=SplitReasonType.SIZE_THRESHOLD,
                    description=f"Document is large ({estimated_tokens} tokens > {self.MAX_TOKENS})",
                    confidence=0.6,
                    evidence={
                        "estimated_tokens": estimated_tokens,
                        "threshold": self.MAX_TOKENS,
                    },
                )
            )

        # HEURISTIC 4: Layer mixing
        section_layers = await self._assign_section_layers(sections)
        layer_diversity = len(set(section_layers))
        if layer_diversity > self.LAYER_DIVERSITY_THRESHOLD:
            reasons.append(
                SplitReason(
                    type=SplitReasonType.LAYER_MIXING,
                    description=f"Sections span layers {set(section_layers)}",
                    confidence=0.6,
                    evidence={
                        "layer_diversity": layer_diversity,
                        "section_layers": section_layers,
                    },
                )
            )

        # If no reasons, no split recommended
        if not reasons:
            return SplitRecommendation(should_split=False, reasons=[])

        # Generate split plan
        plan = await self._generate_split_plan(sections, path, galois_loss)

        return SplitRecommendation(
            should_split=True,
            reasons=reasons,
            plan=plan,
            requires_user_approval=True,  # Always require approval
        )

    def _extract_sections(self, text: str) -> list[SplitSection]:
        """
        Extract sections from markdown content.

        Sections are defined by headings (## or ###).

        Args:
            text: Document text

        Returns:
            List of sections
        """
        sections: list[SplitSection] = []
        lines = text.split("\n")

        current_section: SplitSection | None = None
        current_content: list[str] = []

        for i, line in enumerate(lines):
            # Check if this is a heading (## or ###)
            heading_match = re.match(r"^(#{2,3})\s+(.+)$", line)

            if heading_match:
                # Save previous section if exists
                if current_section:
                    current_section.content = "\n".join(current_content)
                    current_section.end_line = i - 1
                    sections.append(current_section)

                # Start new section
                title = heading_match.group(2)
                current_section = SplitSection(
                    title=title,
                    content="",
                    start_line=i,
                    end_line=i,
                    estimated_tokens=0,
                )
                current_content = [line]

            elif current_section:
                # Add to current section
                current_content.append(line)

        # Save last section
        if current_section:
            current_section.content = "\n".join(current_content)
            current_section.end_line = len(lines) - 1
            current_section.estimated_tokens = len(current_section.content.split())
            sections.append(current_section)

        return sections

    async def _compute_internal_contradiction(
        self, sections: list[SplitSection]
    ) -> float:
        """
        Compute internal contradiction loss between sections.

        Uses super-additive loss: L(A+B) - (L(A) + L(B))

        Args:
            sections: List of sections

        Returns:
            Internal contradiction score (0.0-1.0)
        """
        # TODO: Integrate with Galois service for real loss computation
        # For now, use heuristic: more sections = higher potential contradiction

        if len(sections) <= 1:
            return 0.0

        # Simple heuristic: more sections = higher loss
        # Real implementation would compute semantic similarity
        base_loss = min(0.1 * len(sections), 0.5)

        # Check for contradictory keywords
        contradiction_keywords = [
            ("always", "never"),
            ("must", "optional"),
            ("required", "forbidden"),
            ("true", "false"),
        ]

        contradiction_count = 0
        for section in sections:
            content_lower = section.content.lower()
            for word1, word2 in contradiction_keywords:
                if word1 in content_lower and word2 in content_lower:
                    contradiction_count += 1

        contradiction_boost = min(0.1 * contradiction_count, 0.3)

        return min(base_loss + contradiction_boost, 1.0)

    async def _assign_section_layers(
        self, sections: list[SplitSection]
    ) -> list[int]:
        """
        Assign layers to sections based on content.

        Args:
            sections: List of sections

        Returns:
            List of layer assignments (one per section)
        """
        layers: list[int] = []

        for section in sections:
            content_lower = section.content.lower()

            # Simple heuristics for layer detection
            if "axiom" in content_lower or "principle" in content_lower:
                layer = 1  # L1: Axioms
            elif "value" in content_lower or "goal" in content_lower:
                layer = 3  # L3: Goals
            elif "spec" in content_lower or "protocol" in content_lower:
                layer = 4  # L4: Specifications
            elif (
                "impl" in content_lower
                or "implementation" in content_lower
                or "code" in content_lower
            ):
                layer = 5  # L5: Implementation
            else:
                layer = 6  # L6: Documentation

            section.estimated_layer = layer
            layers.append(layer)

        return layers

    async def _generate_split_plan(
        self, sections: list[SplitSection], original_path: str, total_loss: float
    ) -> SplitPlan:
        """
        Generate a plan for how to split the document.

        Args:
            sections: Sections to split into
            original_path: Original document path
            total_loss: Total Galois loss before split

        Returns:
            SplitPlan with recommended paths and loss estimates
        """
        # Generate recommended paths for each section
        base_path = original_path.rsplit(".", 1)[0]  # Remove extension
        recommended_paths: list[str] = []

        for i, section in enumerate(sections):
            # Slugify section title
            slug = re.sub(r"[^a-z0-9]+", "-", section.title.lower()).strip("-")

            # Construct path: original-title-section-name.md
            if i == 0:
                # First section keeps original path
                recommended_paths.append(original_path)
            else:
                # Subsequent sections get numbered paths
                recommended_paths.append(f"{base_path}-{slug}.md")

        # Estimate loss after split
        # Heuristic: splitting reduces loss by 20-40% depending on quality
        estimated_loss_after = total_loss * 0.7  # Assume 30% improvement
        improvement = total_loss - estimated_loss_after

        return SplitPlan(
            sections=sections,
            recommended_paths=recommended_paths,
            total_loss_before=total_loss,
            estimated_loss_after=estimated_loss_after,
            improvement=improvement,
        )

    async def execute_split(
        self, plan: SplitPlan, original_path: str, content: bytes
    ) -> list[tuple[str, bytes]]:
        """
        Execute a split plan to generate new files.

        Args:
            plan: The split plan to execute
            original_path: Original file path
            content: Original file content

        Returns:
            List of (path, content) tuples for new files
        """
        results: list[tuple[str, bytes]] = []

        for section, recommended_path in zip(plan.sections, plan.recommended_paths):
            # Extract section content
            section_content = section.content.encode("utf-8")

            results.append((recommended_path, section_content))

        return results


# =============================================================================
# Service Factory
# =============================================================================


_splitting_service: SplittingService | None = None


def get_splitting_service() -> SplittingService:
    """
    Get or create the global SplittingService.

    Returns:
        SplittingService singleton
    """
    global _splitting_service

    if _splitting_service is None:
        _splitting_service = SplittingService()

    return _splitting_service


def reset_splitting_service() -> None:
    """Reset the global SplittingService (for testing)."""
    global _splitting_service
    _splitting_service = None
