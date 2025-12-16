"""
Textual Gradient: The core abstraction for prompt improvement.

A TextualGradient represents the "direction" of improvement for a prompt,
analogous to numerical gradients in optimization. It encapsulates:
- Which sections to modify
- What direction to modify them (add, remove, rephrase)
- The magnitude of change (learning rate via rigidity)

See: spec/heritage.md Part II, Section 9 (TextGRAD)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable


class GradientDirection(Enum):
    """Direction of improvement for a section."""

    EXPAND = auto()  # Add more content
    CONDENSE = auto()  # Make more concise
    CLARIFY = auto()  # Improve clarity
    FORMALIZE = auto()  # Make more formal
    CASUALIZE = auto()  # Make more casual
    REORDER = auto()  # Change structure
    EMPHASIZE = auto()  # Strengthen points
    DEEMPHASIZE = auto()  # Weaken points
    REMOVE = auto()  # Delete content
    ADD = auto()  # Add new content


@dataclass(frozen=True)
class GradientStep:
    """
    A single improvement step for a specific section.

    Represents a discrete modification to apply to a section.
    """

    section_name: str
    direction: GradientDirection
    magnitude: float  # 0.0 = no change, 1.0 = full change
    description: str
    target_content: str | None = None  # Specific content to modify
    replacement: str | None = None  # What to replace with (for targeted edits)

    def __str__(self) -> str:
        return f"[{self.section_name}] {self.direction.name} ({self.magnitude:.1f}): {self.description}"

    def scale(self, factor: float) -> GradientStep:
        """Scale the magnitude by a factor (learning rate)."""
        return GradientStep(
            section_name=self.section_name,
            direction=self.direction,
            magnitude=self.magnitude * factor,
            description=self.description,
            target_content=self.target_content,
            replacement=self.replacement,
        )

    def should_apply(self, rigidity: float) -> bool:
        """
        Whether to apply this step given a section's rigidity.

        Low rigidity = more changeable = higher threshold for applying.
        High rigidity = less changeable = lower threshold for applying.

        The formula ensures:
        - High rigidity sections only change with large magnitudes
        - Low rigidity sections change more easily
        """
        # Inverse relationship: high rigidity requires high magnitude
        threshold = rigidity
        return self.magnitude >= threshold


@dataclass(frozen=True)
class TextualGradient:
    """
    A textual gradient: the direction of improvement for a prompt.

    Composed of multiple GradientSteps, one per affected section.
    Analogous to a gradient vector in numerical optimization.

    Properties:
    - Composable: gradients can be added/combined
    - Scalable: gradients can be scaled by a "learning rate"
    - Directional: each step has a clear direction
    """

    steps: tuple[GradientStep, ...]
    reasoning: tuple[str, ...]
    source_feedback: str

    @staticmethod
    def zero() -> TextualGradient:
        """The zero gradient (no change)."""
        return TextualGradient(
            steps=(),
            reasoning=("Zero gradient - no changes",),
            source_feedback="",
        )

    def __add__(self, other: TextualGradient) -> TextualGradient:
        """
        Add two gradients.

        For steps affecting the same section, magnitudes are combined.
        """
        # Combine steps, merging those for same section
        combined: dict[str, list[GradientStep]] = {}
        for step in self.steps:
            if step.section_name not in combined:
                combined[step.section_name] = []
            combined[step.section_name].append(step)

        for step in other.steps:
            if step.section_name not in combined:
                combined[step.section_name] = []
            combined[step.section_name].append(step)

        # Flatten back to list
        all_steps: list[GradientStep] = []
        for steps in combined.values():
            all_steps.extend(steps)

        return TextualGradient(
            steps=tuple(all_steps),
            reasoning=self.reasoning + other.reasoning,
            source_feedback=f"{self.source_feedback} + {other.source_feedback}",
        )

    def scale(self, learning_rate: float) -> TextualGradient:
        """
        Scale all steps by a learning rate.

        Lower learning rate = more conservative changes.
        Higher learning rate = more aggressive changes.
        """
        return TextualGradient(
            steps=tuple(step.scale(learning_rate) for step in self.steps),
            reasoning=self.reasoning + (f"Scaled by {learning_rate}",),
            source_feedback=self.source_feedback,
        )

    def filter_by_rigidity(
        self,
        rigidity_lookup: Callable[[str], float],
    ) -> TextualGradient:
        """
        Filter steps based on section rigidity.

        Only keeps steps whose magnitude exceeds the section's rigidity.
        """
        filtered: list[GradientStep] = []
        reasoning: list[str] = list(self.reasoning)

        for step in self.steps:
            rigidity = rigidity_lookup(step.section_name)
            if step.should_apply(rigidity):
                filtered.append(step)
                reasoning.append(
                    f"  → {step.section_name}: applying (magnitude {step.magnitude:.2f} >= rigidity {rigidity:.2f})"
                )
            else:
                reasoning.append(
                    f"  → {step.section_name}: skipping (magnitude {step.magnitude:.2f} < rigidity {rigidity:.2f})"
                )

        return TextualGradient(
            steps=tuple(filtered),
            reasoning=tuple(reasoning),
            source_feedback=self.source_feedback,
        )

    def for_section(self, section_name: str) -> list[GradientStep]:
        """Get all steps targeting a specific section."""
        return [s for s in self.steps if s.section_name == section_name]

    def affected_sections(self) -> set[str]:
        """Get the set of sections affected by this gradient."""
        return {s.section_name for s in self.steps}

    def __len__(self) -> int:
        """Number of steps in this gradient."""
        return len(self.steps)

    def __bool__(self) -> bool:
        """True if gradient has any steps."""
        return len(self.steps) > 0


__all__ = [
    "GradientDirection",
    "GradientStep",
    "TextualGradient",
]
