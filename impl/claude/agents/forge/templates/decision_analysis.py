"""
Decision Analysis Task Template.

Coalition Shape: Full archetype set (Scout, Sage, Spark, Steady, Sync)
Output Format: Pros/Cons Matrix
Credits: 75

Decision analysis uses the full coalition to provide
comprehensive multi-perspective analysis of complex decisions.

Flow:
    1. Scout researches all options and context
    2. Sage structures the decision framework
    3. Spark generates creative alternatives
    4. Steady evaluates risks and feasibility
    5. Sync synthesizes into final recommendation

This is the most expensive template because it uses all builders.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from ..task import (
    CoalitionShape,
    HandoffPattern,
    OutputFormat,
    TaskInput,
    TaskOutput,
)
from .base import TaskTemplate

# Coalition shape for decision analysis - full team
DECISION_ANALYSIS_SHAPE = CoalitionShape(
    required=("Scout", "Sage", "Spark", "Steady", "Sync"),
    optional=(),
    lead="Sync",  # Coordinator leads decisions
    pattern=HandoffPattern.HUB_AND_SPOKE,  # Sync mediates all interactions
    min_eigenvector={"analytical": 0.6, "social": 0.5},
)


@dataclass
class DecisionAnalysisTask(TaskTemplate):
    """
    Decision Analysis: Multi-perspective analysis for complex decisions.

    Input: Decision to make, options to consider, constraints
    Output: Structured decision matrix with:
        - Options compared
        - Pros/cons for each
        - Risk assessment
        - Recommendation with rationale
        - Minority opinions (if any)
    """

    template_id: ClassVar[str] = "decision_analysis"
    name: ClassVar[str] = "Decision Analysis"
    description: ClassVar[str] = (
        "Comprehensive decision analysis using all archetypes. "
        "Scout researches, Sage structures, Spark innovates, "
        "Steady validates, Sync synthesizes."
    )
    base_credits: ClassVar[int] = 75
    output_format: ClassVar[OutputFormat] = OutputFormat.MATRIX

    coalition_shape: CoalitionShape = field(
        default_factory=lambda: DECISION_ANALYSIS_SHAPE
    )

    def validate_input(self, input: TaskInput) -> tuple[bool, list[str]]:
        """Validate decision analysis requirements."""
        is_valid, errors = super().validate_input(input)

        # Decision analysis needs options
        options = input.context.get("options", [])
        if not options:
            errors.append(
                "Decision analysis requires options to compare. "
                "Add context={'options': ['Option A', 'Option B', ...]}."
            )
            is_valid = False

        # Warn if only 2 options (binary is limiting)
        if len(options) == 2:
            errors.append(
                "Only 2 options provided. Consider if there are "
                "alternative approaches worth exploring."
            )
            # Warning only

        return is_valid, errors

    def suggest_coalition(self, input: TaskInput) -> CoalitionShape:
        """Full coalition always for decisions."""
        # Decision analysis always uses full coalition
        # Could optimize for quick decisions:
        if input.depth == "quick":
            return CoalitionShape(
                required=("Sage", "Steady", "Sync"),
                optional=("Scout", "Spark"),
                lead="Sync",
                pattern=HandoffPattern.HUB_AND_SPOKE,
            )

        return self.coalition_shape

    def get_phase_sequence(self) -> list[str]:
        """Full cycle for decisions."""
        return ["EXPLORING", "DESIGNING", "PROTOTYPING", "REFINING", "INTEGRATING"]

    def get_handoff_descriptions(self) -> dict[str, str]:
        """Hub-and-spoke means Sync mediates all."""
        return {
            "Scout→Sync": "Scout reports research findings to coordinator",
            "Sync→Sage": "Sync routes findings to Sage for structuring",
            "Sage→Sync": "Sage returns decision framework",
            "Sync→Spark": "Sync asks Spark for creative alternatives",
            "Spark→Sync": "Spark proposes novel options",
            "Sync→Steady": "Sync routes options to Steady for validation",
            "Steady→Sync": "Steady returns risk assessment",
            "Sync→All": "Sync synthesizes final recommendation",
        }

    async def execute(
        self,
        input: TaskInput,
        coalition: Any,
    ) -> TaskOutput:
        """Execute decision analysis."""
        options = input.context.get("options", ["Option A", "Option B"])
        criteria = input.context.get(
            "criteria", ["Cost", "Risk", "Benefit", "Feasibility"]
        )
        constraints = list(input.constraints)

        # Build decision matrix
        matrix = []
        for option in options:
            row = {
                "option": option,
                "scores": {},
                "pros": [f"Pro for {option}"],
                "cons": [f"Con for {option}"],
                "risks": [f"Risk: {option} might not scale"],
            }
            for criterion in criteria:
                # Simulate scoring (real impl would use coalition)
                import hashlib

                score = (
                    int(
                        hashlib.md5(f"{option}{criterion}".encode()).hexdigest()[:2], 16
                    )
                    % 5
                ) + 1
                row["scores"][criterion] = score
            matrix.append(row)

        # Determine recommendation
        best_option = max(matrix, key=lambda x: sum(x["scores"].values()))

        content = {
            "question": input.description,
            "options": options,
            "criteria": criteria,
            "constraints": constraints,
            "matrix": matrix,
            "recommendation": {
                "choice": best_option["option"],
                "rationale": f"Based on analysis across {len(criteria)} criteria, "
                f"{best_option['option']} scores highest overall.",
                "confidence": "medium" if len(options) < 4 else "high",
            },
            "minority_opinions": [
                {
                    "builder": "Spark",
                    "opinion": "Consider a hybrid approach combining elements of multiple options.",
                },
            ],
            "next_steps": [
                "Validate assumptions with stakeholders",
                "Prototype the recommended option",
                "Monitor key risk factors",
            ],
        }

        return TaskOutput(
            content=content,
            format=OutputFormat.MATRIX,
            summary=f"Decision analysis complete. Recommendation: {best_option['option']}",
            coalition_used=self.coalition_shape.required,
            handoffs=len(self.get_handoff_descriptions()),
            confidence=0.7,
            coverage=0.9,
            artifacts=[
                {"type": "options_analyzed", "value": len(options)},
                {"type": "criteria_evaluated", "value": len(criteria)},
            ],
        )


# Singleton template instance
DECISION_ANALYSIS_TEMPLATE = DecisionAnalysisTask()

__all__ = [
    "DecisionAnalysisTask",
    "DECISION_ANALYSIS_TEMPLATE",
    "DECISION_ANALYSIS_SHAPE",
]
