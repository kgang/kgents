"""
Base TaskTemplate: Abstract base for all task templates.

TaskTemplate provides the scaffold that concrete templates fill in.
It handles common validation, credit calculation, and coalition suggestions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar

from ..task import (
    CoalitionShape,
    HandoffPattern,
    OutputFormat,
    TaskInput,
    TaskOutput,
    calculate_credits,
)


@dataclass
class TaskTemplate(ABC):
    """
    Abstract base class for task templates.

    Templates are factory patterns that create executable tasks.
    They encode domain knowledge about:
    - What coalition shape works best
    - How to validate inputs
    - How to estimate costs
    - What output format to use
    """

    # Class-level constants (must be overridden)
    template_id: ClassVar[str]
    name: ClassVar[str]
    description: ClassVar[str]
    base_credits: ClassVar[int]
    output_format: ClassVar[OutputFormat]

    # Instance configuration
    coalition_shape: CoalitionShape = field(
        default_factory=lambda: CoalitionShape(required=("Scout",))
    )

    # Optional customization
    custom_credits: int | None = None
    custom_output_format: OutputFormat | None = None

    @property
    def effective_credits(self) -> int:
        """Get credits (custom or base)."""
        return self.custom_credits or self.base_credits

    @property
    def effective_output_format(self) -> OutputFormat:
        """Get output format (custom or base)."""
        return self.custom_output_format or self.output_format

    @abstractmethod
    async def execute(
        self,
        input: TaskInput,
        coalition: Any,
    ) -> TaskOutput:
        """
        Execute the task with the given coalition.

        Subclasses implement domain-specific execution logic.
        """
        ...

    def estimate_credits(self, input: TaskInput) -> int:
        """
        Estimate credit cost for this input.

        Default implementation uses calculate_credits utility.
        Subclasses can override for domain-specific estimation.
        """
        return calculate_credits(
            self.effective_credits,
            input,
            self.coalition_shape,
        )

    def validate_input(self, input: TaskInput) -> tuple[bool, list[str]]:
        """
        Validate input before execution.

        Default implementation checks basic requirements.
        Subclasses should call super() and add domain-specific checks.
        """
        errors: list[str] = []

        if not input.description or len(input.description.strip()) < 10:
            errors.append("Task description must be at least 10 characters")

        if input.depth not in ("quick", "standard", "deep"):
            errors.append(f"Invalid depth: {input.depth}. Use: quick, standard, deep")

        return len(errors) == 0, errors

    def suggest_coalition(self, input: TaskInput) -> CoalitionShape:
        """
        Suggest optimal coalition shape for this input.

        Default returns base shape. Subclasses can adjust based on input.
        """
        return self.coalition_shape

    @abstractmethod
    def get_phase_sequence(self) -> list[str]:
        """
        Get the expected phase sequence for this task.

        Returns list of phase names in execution order.
        """
        ...

    @abstractmethod
    def get_handoff_descriptions(self) -> dict[str, str]:
        """
        Get descriptions of expected handoffs.

        Returns mapping of "from→to" to description.
        """
        ...

    def manifest(self) -> dict[str, Any]:
        """
        Render template as a dictionary for AGENTESE manifest.

        Used by concept.task[type].manifest
        """
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "base_credits": self.base_credits,
            "output_format": self.output_format.name,
            "coalition_shape": {
                "required": self.coalition_shape.required,
                "optional": self.coalition_shape.optional,
                "lead": self.coalition_shape.effective_lead,
                "pattern": self.coalition_shape.pattern.name,
            },
            "phase_sequence": self.get_phase_sequence(),
            "handoffs": self.get_handoff_descriptions(),
        }

    # =========================================================================
    # Projection Protocol (Pattern 3 from synthesis)
    # =========================================================================

    def to_cli(self) -> str:
        """
        Project template to CLI format.

        Returns ASCII-art table representation suitable for terminal.
        """
        lines = [
            f"Task Template: {self.name}",
            "=" * 50,
            f"ID:       {self.template_id}",
            f"Credits:  {self.base_credits}",
            f"Output:   {self.output_format.name}",
            "",
            "Coalition Shape:",
            f"  Required: {', '.join(self.coalition_shape.required)}",
            f"  Optional: {', '.join(self.coalition_shape.optional) or 'None'}",
            f"  Lead:     {self.coalition_shape.effective_lead}",
            f"  Pattern:  {self.coalition_shape.pattern.name}",
            "",
            "Phase Sequence:",
        ]
        for i, phase in enumerate(self.get_phase_sequence(), 1):
            lines.append(f"  {i}. {phase}")

        lines.extend(["", "Handoffs:"])
        for handoff, desc in self.get_handoff_descriptions().items():
            lines.append(f"  {handoff}: {desc}")

        lines.extend(["", "=" * 50])
        return "\n".join(lines)

    def to_web(self) -> dict[str, Any]:
        """
        Project template to web format.

        Returns structured dict for React/JSON rendering.
        """
        return {
            "type": "task_template",
            "id": self.template_id,
            "name": self.name,
            "description": self.description,
            "credits": {
                "base": self.base_credits,
                "effective": self.effective_credits,
            },
            "output_format": self.output_format.name,
            "coalition": {
                "required": list(self.coalition_shape.required),
                "optional": list(self.coalition_shape.optional),
                "lead": self.coalition_shape.effective_lead,
                "pattern": self.coalition_shape.pattern.name,
                "min_size": self.coalition_shape.min_size,
                "max_size": self.coalition_shape.max_size,
            },
            "execution": {
                "phases": self.get_phase_sequence(),
                "handoffs": self.get_handoff_descriptions(),
            },
        }

    def to_json(self) -> dict[str, Any]:
        """
        Project template to JSON format.

        Universal fallback that works everywhere.
        """
        return self.to_web()

    def project(self, target: str = "cli") -> str | dict[str, Any]:
        """
        Project to specified target.

        Args:
            target: One of "cli", "web", "json"

        Returns:
            Projected representation
        """
        match target:
            case "cli":
                return self.to_cli()
            case "web":
                return self.to_web()
            case "json":
                return self.to_json()
            case _:
                return self.to_json()  # Default fallback

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.template_id}, credits={self.effective_credits})>"


# =============================================================================
# Standard Coalition Shapes
# =============================================================================

# Scout-led research (EXPLORING → DESIGNING)
RESEARCH_SHAPE = CoalitionShape(
    required=("Scout", "Sage"),
    optional=("Spark", "Steady"),
    lead="Scout",
    pattern=HandoffPattern.SEQUENTIAL,
    min_eigenvector={"analytical": 0.7, "creativity": 0.3},
)

# Steady-led review (REFINING → INTEGRATING)
REVIEW_SHAPE = CoalitionShape(
    required=("Steady", "Sync"),
    optional=("Sage",),
    lead="Steady",
    pattern=HandoffPattern.ITERATIVE,
    min_eigenvector={"analytical": 0.8, "reliability": 0.8},
)

# Spark-led creation (PROTOTYPING → REFINING)
CREATION_SHAPE = CoalitionShape(
    required=("Spark", "Sage"),
    optional=("Steady", "Scribe"),
    lead="Spark",
    pattern=HandoffPattern.PIPELINE,
    min_eigenvector={"creativity": 0.8, "social": 0.5},
)

# Full-team decision (all phases)
DECISION_SHAPE = CoalitionShape(
    required=("Scout", "Sage", "Spark", "Steady", "Sync"),
    optional=(),
    lead="Sync",
    pattern=HandoffPattern.HUB_AND_SPOKE,
    min_eigenvector={"analytical": 0.6, "social": 0.5},
)

# Intel-focused research (EXPLORING heavy)
INTEL_SHAPE = CoalitionShape(
    required=("Scout", "Scout", "Scout", "Sage"),  # Multiple scouts
    optional=("Steady",),
    lead="Scout",
    pattern=HandoffPattern.PARALLEL,
    min_eigenvector={"analytical": 0.9, "creativity": 0.4},
)


__all__ = [
    "TaskTemplate",
    # Standard shapes
    "RESEARCH_SHAPE",
    "REVIEW_SHAPE",
    "CREATION_SHAPE",
    "DECISION_SHAPE",
    "INTEL_SHAPE",
]
