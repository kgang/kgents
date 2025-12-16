"""
TextGRAD Improver: Apply textual gradients to improve prompts.

The core self-improvement engine for the Evergreen Prompt System.

Based on the TextGRAD approach:
1. Parse feedback into textual gradients
2. Filter gradients by section rigidity
3. Apply improvements to targeted sections
4. Checkpoint for rollback capability
5. Return improved prompt in monad

See: spec/heritage.md Part II, Section 9 (TextGRAD)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from .feedback_parser import FeedbackParser, ParsedFeedback
from .gradient import GradientDirection, GradientStep, TextualGradient

if TYPE_CHECKING:
    from ..monad import PromptM, Source
    from ..rollback.registry import RollbackRegistry
    from ..section_base import Section

logger = logging.getLogger(__name__)


@runtime_checkable
class SectionImprover(Protocol):
    """Protocol for section-specific improvement."""

    def improve(
        self,
        section_name: str,
        content: str,
        steps: list[GradientStep],
    ) -> tuple[str, list[str]]:
        """
        Apply gradient steps to section content.

        Returns:
            Tuple of (improved_content, reasoning_traces)
        """
        ...


@dataclass(frozen=True)
class ImprovementResult:
    """Result of applying a textual gradient."""

    original_content: str
    improved_content: str
    gradient: TextualGradient
    sections_modified: tuple[str, ...]
    reasoning_trace: tuple[str, ...]
    checkpoint_id: str | None = None
    success: bool = True

    @property
    def content_changed(self) -> bool:
        """True if the content was actually modified."""
        return self.original_content != self.improved_content


@dataclass
class RuleBasedSectionImprover:
    """
    Rule-based section improver.

    Applies gradient steps using simple text transformations.
    For production use, an LLM-based improver would provide better results.
    """

    def improve(
        self,
        section_name: str,
        content: str,
        steps: list[GradientStep],
    ) -> tuple[str, list[str]]:
        """Apply gradient steps using rule-based transformations."""
        traces: list[str] = [f"Improving {section_name} with {len(steps)} steps"]
        result = content

        for step in steps:
            traces.append(f"  Applying: {step}")

            if step.direction == GradientDirection.CONDENSE:
                result = self._condense(result, step.magnitude)
                traces.append(f"    Condensed by {step.magnitude:.0%}")

            elif step.direction == GradientDirection.EXPAND:
                # Expansion is harder without LLM - just note it
                traces.append(
                    f"    Expansion requested (magnitude {step.magnitude:.2f}) - requires LLM"
                )

            elif step.direction == GradientDirection.CLARIFY:
                # Clarification is harder without LLM - just note it
                traces.append("    Clarification requested - requires LLM")

            elif step.direction == GradientDirection.REMOVE and step.target_content:
                result = result.replace(step.target_content, "")
                traces.append(f"    Removed: '{step.target_content[:30]}...'")

            elif step.direction == GradientDirection.ADD and step.replacement:
                result = result + "\n" + step.replacement
                traces.append(f"    Added: '{step.replacement[:30]}...'")

        return result, traces

    def _condense(self, content: str, magnitude: float) -> str:
        """
        Condense content by removing less essential parts.

        Simple heuristic: remove lines with lower information density.
        """
        lines = content.split("\n")
        if len(lines) <= 3:
            return content

        # Calculate target line count
        target_count = max(3, int(len(lines) * (1 - magnitude * 0.3)))

        # Keep lines with more content (simple heuristic)
        scored_lines = [(len(line.strip()), i, line) for i, line in enumerate(lines)]
        scored_lines.sort(reverse=True)

        # Keep top lines by content, restore original order
        kept_indices = sorted([i for _, i, _ in scored_lines[:target_count]])
        kept_lines = [lines[i] for i in kept_indices]

        return "\n".join(kept_lines)


@dataclass
class TextGRADImprover:
    """
    Improve prompts using textual gradients.

    The main entry point for self-improvement in the Evergreen Prompt System.
    """

    parser: FeedbackParser = field(default_factory=FeedbackParser)
    section_improver: SectionImprover = field(default_factory=RuleBasedSectionImprover)
    learning_rate: float = 0.5  # Default learning rate
    rollback_registry: "RollbackRegistry | None" = None

    def improve(
        self,
        sections: dict[str, str],
        feedback: str,
        rigidity_lookup: dict[str, float] | None = None,
    ) -> ImprovementResult:
        """
        Apply feedback to improve sections.

        Args:
            sections: Dict of section_name -> content
            feedback: Natural language feedback
            rigidity_lookup: Dict of section_name -> rigidity (0.0-1.0)

        Returns:
            ImprovementResult with improved content
        """
        traces: list[str] = [
            f"TextGRAD improvement starting at {datetime.now().isoformat()}",
            f"Feedback: {feedback[:100]}...",
            f"Learning rate: {self.learning_rate}",
        ]

        # Handle empty feedback (identity law)
        if not feedback or not feedback.strip():
            traces.append("Empty feedback - returning unchanged (identity law)")
            combined = self._combine_sections(sections)
            return ImprovementResult(
                original_content=combined,
                improved_content=combined,
                gradient=TextualGradient.zero(),
                sections_modified=(),
                reasoning_trace=tuple(traces),
            )

        # Parse feedback
        parsed = self.parser.parse(feedback)
        traces.extend(parsed.reasoning)

        if parsed.is_empty:
            traces.append("No targets extracted from feedback")
            combined = self._combine_sections(sections)
            return ImprovementResult(
                original_content=combined,
                improved_content=combined,
                gradient=TextualGradient.zero(),
                sections_modified=(),
                reasoning_trace=tuple(traces),
            )

        # Convert to gradient
        gradient = parsed.to_gradient(self.learning_rate)
        traces.append(f"Generated gradient with {len(gradient)} steps")

        # Filter by rigidity
        if rigidity_lookup:
            gradient = gradient.filter_by_rigidity(
                lambda s: rigidity_lookup.get(s, 0.5)
            )
            traces.extend(gradient.reasoning)
            traces.append(f"After rigidity filter: {len(gradient)} steps remain")

        # Apply improvements
        improved_sections = dict(sections)
        modified: list[str] = []

        for section_name in gradient.affected_sections():
            if section_name == "*":
                # Global feedback - apply to all sections
                for name, content in sections.items():
                    steps = gradient.for_section("*")
                    new_content, step_traces = self.section_improver.improve(
                        name, content, steps
                    )
                    traces.extend(step_traces)
                    if new_content != content:
                        improved_sections[name] = new_content
                        modified.append(name)
            elif section_name in sections:
                steps = gradient.for_section(section_name)
                content = sections[section_name]
                new_content, step_traces = self.section_improver.improve(
                    section_name, content, steps
                )
                traces.extend(step_traces)
                if new_content != content:
                    improved_sections[section_name] = new_content
                    modified.append(section_name)

        # Combine sections
        original = self._combine_sections(sections)
        improved = self._combine_sections(improved_sections)

        traces.append(f"Modified {len(modified)} sections: {modified}")

        # Checkpoint if registry available
        checkpoint_id = None
        if self.rollback_registry and original != improved:
            try:
                checkpoint_id = self.rollback_registry.checkpoint(
                    before_content=original,
                    after_content=improved,
                    before_sections=tuple(sections.keys()),
                    after_sections=tuple(improved_sections.keys()),
                    reason=f"TextGRAD: {feedback[:50]}...",
                    reasoning_traces=tuple(traces),
                )
                traces.append(f"Checkpointed as {checkpoint_id}")
            except Exception as e:
                traces.append(f"Checkpoint failed: {e}")
                logger.warning(f"Failed to checkpoint: {e}")

        return ImprovementResult(
            original_content=original,
            improved_content=improved,
            gradient=gradient,
            sections_modified=tuple(modified),
            reasoning_trace=tuple(traces),
            checkpoint_id=checkpoint_id,
        )

    def improve_monadic(
        self,
        sections: dict[str, str],
        feedback: str,
        rigidity_lookup: dict[str, float] | None = None,
    ) -> "PromptM[ImprovementResult]":
        """
        Apply feedback and wrap result in PromptM monad.

        This enables chaining improvements monadically.
        """
        from ..monad import PromptM, Source

        result = self.improve(sections, feedback, rigidity_lookup)

        return PromptM(
            value=result,
            reasoning_trace=result.reasoning_trace,
            provenance=(Source.TEXTGRAD,),
            checkpoint_id=result.checkpoint_id,
        )

    def _combine_sections(self, sections: dict[str, str]) -> str:
        """Combine sections into a single string."""
        parts: list[str] = []
        for name, content in sections.items():
            parts.append(f"## {name}\n\n{content}")
        return "\n\n".join(parts)


def improve_prompt(
    sections: dict[str, str],
    feedback: str,
    learning_rate: float = 0.5,
) -> ImprovementResult:
    """
    Convenience function to improve sections with feedback.

    Args:
        sections: Dict of section_name -> content
        feedback: Natural language feedback
        learning_rate: How aggressively to apply changes (0.0-1.0)

    Returns:
        ImprovementResult with improved content
    """
    improver = TextGRADImprover(learning_rate=learning_rate)
    return improver.improve(sections, feedback)


__all__ = [
    "SectionImprover",
    "RuleBasedSectionImprover",
    "ImprovementResult",
    "TextGRADImprover",
    "improve_prompt",
]
