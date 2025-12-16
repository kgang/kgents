"""
Content Creation Task Template.

Coalition Shape: Spark + Sage + audience-tuned
Output Format: Multi-format
Credits: 40

Content creation showcases creative collaboration.
Spark generates ideas, Sage provides structure,
and the coalition adapts to the target audience.

Flow:
    1. Spark brainstorms creative approaches
    2. Sage structures and refines
    3. Audience-tuning adapts voice and style
    4. Output in multiple formats (user selects)
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

# Coalition shape for content creation
CONTENT_CREATION_SHAPE = CoalitionShape(
    required=("Spark", "Sage"),
    optional=("Steady", "Scout"),  # Polish and research
    lead="Spark",
    pattern=HandoffPattern.PIPELINE,
    min_eigenvector={"creativity": 0.8, "social": 0.5},
)


@dataclass
class ContentCreationTask(TaskTemplate):
    """
    Content Creation: Creative content for any medium.

    Input: Content brief, audience, tone, format preferences
    Output: Multi-format content:
        - Blog post / article
        - Social media posts
        - Marketing copy
        - Technical documentation
        - Creative writing
    """

    template_id: ClassVar[str] = "content_creation"
    name: ClassVar[str] = "Content Creation"
    description: ClassVar[str] = (
        "Creative content generation for any audience. "
        "Spark generates ideas, Sage structures them, "
        "output adapts to specified format and tone."
    )
    base_credits: ClassVar[int] = 40
    output_format: ClassVar[OutputFormat] = OutputFormat.MULTI_FORMAT

    coalition_shape: CoalitionShape = field(
        default_factory=lambda: CONTENT_CREATION_SHAPE
    )

    def validate_input(self, input: TaskInput) -> tuple[bool, list[str]]:
        """Validate content creation requirements."""
        is_valid, errors = super().validate_input(input)

        # Content benefits from audience specification
        if not input.context.get("audience"):
            errors.append(
                "Content creation works best with a target audience. "
                "Consider adding context={'audience': 'developers'} or similar."
            )
            # Warning only, not blocking

        # Check for content type
        valid_types = (
            "blog",
            "social",
            "marketing",
            "documentation",
            "creative",
            "email",
        )
        content_type = input.context.get("content_type", "blog")
        if content_type not in valid_types:
            errors.append(
                f"Unknown content_type: {content_type}. "
                f"Valid types: {', '.join(valid_types)}"
            )

        return is_valid, errors

    def suggest_coalition(self, input: TaskInput) -> CoalitionShape:
        """Adjust coalition based on content type."""
        content_type = input.context.get("content_type", "blog")

        if content_type == "documentation":
            # Technical docs need more structure
            return CoalitionShape(
                required=("Sage", "Steady"),
                optional=("Scout",),
                lead="Sage",
                pattern=HandoffPattern.SEQUENTIAL,
            )
        elif content_type == "creative":
            # Pure creativity: Spark leads everything
            return CoalitionShape(
                required=("Spark",),
                optional=("Sage",),
                lead="Spark",
                pattern=HandoffPattern.SEQUENTIAL,
            )
        elif content_type == "social":
            # Social needs engagement focus
            return CoalitionShape(
                required=("Spark", "Sync"),
                optional=(),
                lead="Spark",
                pattern=HandoffPattern.ITERATIVE,
            )

        return self.coalition_shape

    def get_phase_sequence(self) -> list[str]:
        """Content creation: PROTOTYPING → DESIGNING → REFINING."""
        return ["PROTOTYPING", "DESIGNING", "REFINING"]

    def get_handoff_descriptions(self) -> dict[str, str]:
        """Describe expected handoffs."""
        return {
            "Spark→Sage": "Spark passes creative draft to Sage for structure",
            "Sage→Spark": "Sage returns structured outline for creative filling",
            "Spark→Steady": "Final draft to Steady for polish and consistency",
        }

    async def execute(
        self,
        input: TaskInput,
        coalition: Any,
    ) -> TaskOutput:
        """Execute content creation."""
        content_type = input.context.get("content_type", "blog")
        audience = input.context.get("audience", "general")
        tone = input.context.get("tone", "professional")

        # Generate multi-format content
        formats: dict[str, Any] = {}

        if content_type in ("blog", "documentation"):
            formats["markdown"] = f"""# {input.target or "Untitled"}

*Written for {audience} in a {tone} tone.*

## Introduction

{input.description}

## Key Points

1. First key point
2. Second key point
3. Third key point

## Conclusion

Summary and call to action.

---
*Generated by Coalition Forge - Content Creation*
"""

        if content_type in ("social", "marketing"):
            formats["social_posts"] = [
                f"Thread 1/3: Introducing {input.target or 'this topic'}...",
                f"2/3: Here's what makes it special: {input.description[:100]}...",
                "3/3: Want to learn more? Check the link in bio!",
            ]

        if content_type == "email":
            formats["email"] = {
                "subject": f"Re: {input.target or input.description[:30]}",
                "body": f"Dear reader,\n\n{input.description}\n\nBest regards",
            }

        content = {
            "primary_format": content_type,
            "audience": audience,
            "tone": tone,
            "formats": formats,
        }

        return TaskOutput(
            content=content,
            format=OutputFormat.MULTI_FORMAT,
            summary=f"Created {content_type} content for {audience}",
            coalition_used=self.coalition_shape.required,
            handoffs=len(self.get_handoff_descriptions()),
            confidence=0.75,
            coverage=0.8,
            artifacts=[
                {
                    "type": "word_count",
                    "value": sum(len(str(v)) for v in formats.values()),
                },
            ],
        )


# Singleton template instance
CONTENT_CREATION_TEMPLATE = ContentCreationTask()

__all__ = ["ContentCreationTask", "CONTENT_CREATION_TEMPLATE", "CONTENT_CREATION_SHAPE"]
