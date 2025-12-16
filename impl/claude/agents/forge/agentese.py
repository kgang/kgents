"""
AGENTESE Integration for Coalition Forge Tasks.

This module provides LogosNode implementations for:
- concept.task.manifest → Show all task templates
- concept.task[type].manifest → Show specific template details
- ?concept.task.* → Query available templates

From the spec (coalition-forge.md):
    | AGENTESE Path | Aspect | Handler | Effects |
    |---------------|--------|---------|---------|
    | `concept.task.manifest` | manifest | Show task template schema | — |
    | `concept.task[type].manifest` | manifest | Show specific template | — |
    | `?concept.task.*` | query | Search available templates | — |

The key insight: Tasks are concepts—they're reusable patterns for
coordination. The concept.task.* paths expose them through AGENTESE.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from protocols.agentese.node import BaseLogosNode, BasicRendering, Renderable

from .templates import TASK_TEMPLATES, TaskTemplate, get_template, list_templates

if TYPE_CHECKING:
    from bootstrap.umwelt import Umwelt


# =============================================================================
# Task Concept Node
# =============================================================================


@dataclass
class TaskConceptNode(BaseLogosNode):
    """
    LogosNode for concept.task paths.

    Handles:
    - concept.task → All templates
    - concept.task[type] → Specific template
    - concept.task.* → Query templates

    Example:
        >>> node = TaskConceptNode("concept.task")
        >>> result = await node.manifest(observer)
        >>> # Returns list of all templates

        >>> node = TaskConceptNode("concept.task.research_report")
        >>> result = await node.manifest(observer)
        >>> # Returns research report template details
    """

    _handle: str
    _template_id: str | None = None  # If specific template
    _template: TaskTemplate | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Extract template_id from handle if present."""
        if self._template_id is None:
            # Parse handle: concept.task or concept.task.research_report
            parts = self._handle.split(".")
            if len(parts) >= 3:
                self._template_id = parts[2]  # e.g., "research_report"
                try:
                    self._template = get_template(self._template_id)
                except KeyError:
                    pass  # Unknown template, will handle in manifest

    @property
    def handle(self) -> str:
        return self._handle

    @property
    def template(self) -> TaskTemplate | None:
        """Get the associated template, if any."""
        return self._template

    def _get_affordances_for_archetype(self, archetype: str) -> tuple[str, ...]:
        """Task concepts have limited affordances."""
        base = ("relate", "explain")
        if archetype in ("engineer", "developer"):
            return base + ("implement", "validate")
        return base

    async def manifest(self, observer: "Umwelt[Any, Any]") -> Renderable:
        """
        Render task concept for observer.

        If template_id is set, shows specific template.
        Otherwise shows all available templates.
        """
        meta = self._umwelt_to_meta(observer)

        if self._template is not None:
            # Specific template
            return self._manifest_template(self._template, meta.archetype)
        elif self._template_id is not None:
            # Unknown template
            return BasicRendering(
                summary=f"Unknown task template: {self._template_id}",
                content=f"Template '{self._template_id}' not found.\n\n"
                f"Available templates: {', '.join(TASK_TEMPLATES.keys())}",
                metadata={"error": "template_not_found"},
            )
        else:
            # All templates
            return self._manifest_all_templates(meta.archetype)

    def _manifest_template(
        self,
        template: TaskTemplate,
        archetype: str,
    ) -> Renderable:
        """Render a specific template."""
        manifest = template.manifest()

        # Format based on archetype
        if archetype == "engineer":
            # Technical view
            content = f"""# Task Template: {template.name}

**ID**: `{template.template_id}`
**Credits**: {template.base_credits}
**Output**: {template.output_format.name}

## Coalition Shape

- **Required**: {", ".join(manifest["coalition_shape"]["required"])}
- **Optional**: {", ".join(manifest["coalition_shape"]["optional"]) or "None"}
- **Lead**: {manifest["coalition_shape"]["lead"]}
- **Pattern**: {manifest["coalition_shape"]["pattern"]}

## Phase Sequence

{chr(10).join(f"- {phase}" for phase in manifest["phase_sequence"])}

## Handoffs

{chr(10).join(f"- **{k}**: {v}" for k, v in manifest["handoffs"].items())}

## Integration

```python
from agents.forge import get_template, TaskInput

template = get_template("{template.template_id}")
input = TaskInput(description="...")
output = await template.execute(input, coalition)
```
"""
        else:
            # User-friendly view
            content = f"""# {template.name}

{template.description}

**Cost**: {template.base_credits} credits
**Format**: {template.output_format.name}

## How It Works

This task uses a coalition of:
- {", ".join(manifest["coalition_shape"]["required"])}

The {manifest["coalition_shape"]["lead"]} leads the team through:
{chr(10).join(f"{i + 1}. {phase}" for i, phase in enumerate(manifest["phase_sequence"]))}
"""

        return BasicRendering(
            summary=f"Task: {template.name}",
            content=content,
            metadata=manifest,
        )

    def _manifest_all_templates(self, archetype: str) -> Renderable:
        """Render all templates."""
        templates_list = list_templates()

        if archetype == "engineer":
            # Table format
            rows = ["| ID | Name | Credits | Output |", "|---|---|---|---|"]
            for t in templates_list:
                rows.append(
                    f"| `{t['id']}` | {t['name']} | {t['credits']} | {t['output_format']} |"
                )
            content = f"""# Task Templates Registry

{chr(10).join(rows)}

## Usage

```python
from agents.forge import get_template, TaskInput

template = get_template("research_report")
```
"""
        else:
            # Friendly format
            items = []
            for t in templates_list:
                items.append(
                    f"**{t['name']}** (`{t['id']}`)\n"
                    f"  {t['description']}\n"
                    f"  Cost: {t['credits']} credits"
                )
            content = f"""# Available Task Templates

{chr(10).join(items)}

---
Use `concept.task[id].manifest` to see details for a specific template.
"""

        return BasicRendering(
            summary=f"Task Templates: {len(templates_list)} available",
            content=content,
            metadata={"templates": templates_list},
        )

    async def _invoke_aspect(
        self,
        aspect: str,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> Any:
        """Handle task-specific aspects."""
        match aspect:
            case "explain":
                return await self._explain(observer, **kwargs)
            case "validate":
                return await self._validate(observer, **kwargs)
            case "implement":
                return await self._implement(observer, **kwargs)
            case _:
                return {"aspect": aspect, "status": "not implemented"}

    async def _explain(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Explain the task template."""
        if self._template is None:
            return {
                "error": "No template specified",
                "hint": "Use concept.task[template_id].explain",
            }

        level = kwargs.get("level", "basic")
        return {
            "template": self._template.template_id,
            "level": level,
            "explanation": self._template.description,
            "coalition": self._template.coalition_shape.required,
            "cost": self._template.base_credits,
        }

    async def _validate(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Validate input against template requirements."""
        if self._template is None:
            return {"error": "No template to validate against"}

        from .task import TaskInput

        # Get input from kwargs
        description = kwargs.get("description", "")
        target = kwargs.get("target")
        depth = kwargs.get("depth", "standard")
        context = kwargs.get("context", {})

        input = TaskInput(
            description=description,
            target=target,
            depth=depth,
            context=context,
        )

        is_valid, errors = self._template.validate_input(input)
        estimated_credits = self._template.estimate_credits(input)

        return {
            "template": self._template.template_id,
            "valid": is_valid,
            "errors": errors,
            "estimated_credits": estimated_credits,
            "suggested_coalition": self._template.suggest_coalition(input).required,
        }

    async def _implement(
        self,
        observer: "Umwelt[Any, Any]",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Show how to implement/use this task."""
        if self._template is None:
            return {"error": "No template to implement"}

        code = f'''
from agents.forge import get_template, TaskInput, ForgeTaskInstance

# Get the template
template = get_template("{self._template.template_id}")

# Create task input
input = TaskInput(
    description="Your task description here",
    target="Optional target entity",
    depth="standard",  # "quick", "standard", or "deep"
    context={{
        # Template-specific context
    }},
)

# Validate input
is_valid, errors = template.validate_input(input)
if not is_valid:
    print(f"Validation errors: {{errors}}")

# Estimate cost
credits = template.estimate_credits(input)
print(f"Estimated credits: {{credits}}")

# Create task instance
instance = ForgeTaskInstance.create("{self._template.template_id}", input)

# Execute with coalition (requires WorkshopEnvironment)
# output = await template.execute(input, coalition)
'''

        return {
            "template": self._template.template_id,
            "implementation": code.strip(),
            "required_imports": ["agents.forge"],
        }


# =============================================================================
# Factory Functions
# =============================================================================


def create_task_node(
    handle: str,
    template_id: str | None = None,
) -> TaskConceptNode:
    """
    Create a TaskConceptNode for an AGENTESE path.

    Args:
        handle: AGENTESE path (e.g., "concept.task" or "concept.task.research_report")
        template_id: Optional explicit template ID

    Returns:
        TaskConceptNode configured for the path
    """
    return TaskConceptNode(
        _handle=handle,
        _template_id=template_id,
    )


def resolve_task_path(holon: str, rest: list[str]) -> TaskConceptNode:
    """
    Resolve a concept.task.* path.

    This is called by the concept context resolver.

    Args:
        holon: First component after "concept." (should be "task")
        rest: Remaining path components

    Returns:
        TaskConceptNode for the path
    """
    if holon != "task":
        raise ValueError(f"Expected 'task', got '{holon}'")

    if rest:
        # concept.task.research_report or similar
        template_id = rest[0]
        handle = f"concept.task.{template_id}"
        return TaskConceptNode(_handle=handle, _template_id=template_id)
    else:
        # concept.task (all templates)
        return TaskConceptNode(_handle="concept.task")


# =============================================================================
# Query Support
# =============================================================================


def query_tasks(
    pattern: str | None = None,
    min_credits: int | None = None,
    max_credits: int | None = None,
    output_format: str | None = None,
    required_archetype: str | None = None,
) -> list[dict[str, Any]]:
    """
    Query task templates with filters.

    Used by ?concept.task.* queries.

    Args:
        pattern: Name pattern to match
        min_credits: Minimum credit cost
        max_credits: Maximum credit cost
        output_format: Required output format
        required_archetype: Must include this archetype

    Returns:
        List of matching template summaries
    """
    results = []

    for template_id, template in TASK_TEMPLATES.items():
        # Pattern match
        if pattern and pattern.lower() not in template.name.lower():
            continue

        # Credit filters
        if min_credits is not None and template.base_credits < min_credits:
            continue
        if max_credits is not None and template.base_credits > max_credits:
            continue

        # Output format filter
        if (
            output_format
            and template.output_format.name.lower() != output_format.lower()
        ):
            continue

        # Archetype filter
        if required_archetype:
            if required_archetype not in template.coalition_shape.required:
                continue

        results.append(
            {
                "id": template_id,
                "name": template.name,
                "description": template.description,
                "credits": template.base_credits,
                "output_format": template.output_format.name,
                "required_archetypes": template.coalition_shape.required,
            }
        )

    return results


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "TaskConceptNode",
    "create_task_node",
    "resolve_task_path",
    "query_tasks",
]
