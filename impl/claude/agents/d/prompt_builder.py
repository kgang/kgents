"""
PromptBuilder: Assemble complete prompts from context components.

The frontend NEVER sees these prompts—only the rendered output.
All prompt construction is a backend concern.

This module provides templates for different agent types and injects
eigenvector coordinates to shape personality.

AGENTESE: self.context.prompt (future alias from self.stream.*)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# === Agent Type Templates ===

SYSTEM_TEMPLATES: dict[str, str] = {
    "kgent": """You are K-gent, Kent's AI persona and soul interface.

{persona}

{constraints}

You embody Kent's personality coordinates while maintaining your own agency.
Respond authentically, not as a chatbot.""",
    "builder": """You are a Builder in the Agent Town Workshop.

**Specialty**: {specialty}
**Role**: Transform ideas into working artifacts through collaborative iteration.

{persona}

{constraints}

Focus on your specialty while collaborating with other builders.
Your eigenvector coordinates influence your working style.""",
    "citizen": """You are a Citizen of Agent Town.

**Name**: {name}
**Role**: Participate in the town's collective intelligence.

{persona}

{constraints}

Your personality emerges from your eigenvector coordinates.
Interact authentically with other citizens.""",
    "default": """You are an AI assistant.

{persona}

{constraints}

Respond helpfully and authentically.""",
}


# === Eigenvector Rendering ===


def render_eigenvectors_6d(eigenvectors: dict[str, float]) -> str:
    """
    Render 6D Kent eigenvectors as prompt section.

    K-gent eigenvectors: aesthetic, categorical, gratitude, heterarchy, generativity, joy
    """
    if not eigenvectors:
        return ""

    lines = ["## Personality Coordinates", ""]

    axis_descriptions = {
        "aesthetic": ("Minimalist", "Baroque"),
        "categorical": ("Concrete", "Abstract"),
        "gratitude": ("Utilitarian", "Sacred"),
        "heterarchy": ("Hierarchical", "Peer-to-Peer"),
        "generativity": ("Documentation", "Generation"),
        "joy": ("Austere", "Playful"),
    }

    for name, value in eigenvectors.items():
        if name not in axis_descriptions:
            continue
        low, high = axis_descriptions[name]

        if value < 0.3:
            tendency = f"strongly favor {low.lower()} approaches"
        elif value < 0.5:
            tendency = f"lean toward {low.lower()} approaches"
        elif value > 0.7:
            tendency = f"strongly favor {high.lower()} approaches"
        elif value > 0.5:
            tendency = f"lean toward {high.lower()} approaches"
        else:
            tendency = "balance both approaches"

        lines.append(f"- **{name.title()}** ({value:.2f}): {tendency}")

    lines.append("")
    lines.append("These coordinates influence response style, not content correctness.")

    return "\n".join(lines)


def render_eigenvectors_7d(eigenvectors: dict[str, float]) -> str:
    """
    Render 7D Citizen eigenvectors as prompt section.

    Citizen eigenvectors: warmth, curiosity, trust, creativity, patience, resilience, ambition
    """
    if not eigenvectors:
        return ""

    lines = ["## Personality Coordinates", ""]

    axis_descriptions = {
        "warmth": ("Cold", "Warm"),
        "curiosity": ("Incurious", "Intensely curious"),
        "trust": ("Suspicious", "Trusting"),
        "creativity": ("Conventional", "Inventive"),
        "patience": ("Impatient", "Patient"),
        "resilience": ("Fragile", "Antifragile"),
        "ambition": ("Content", "Driven"),
    }

    for name, value in eigenvectors.items():
        if name not in axis_descriptions:
            continue
        low, high = axis_descriptions[name]

        if value < 0.3:
            tendency = low.lower()
        elif value < 0.5:
            tendency = f"somewhat {low.lower()}"
        elif value > 0.7:
            tendency = high.lower()
        elif value > 0.5:
            tendency = f"somewhat {high.lower()}"
        else:
            tendency = "balanced"

        lines.append(f"- **{name.title()}** ({value:.2f}): {tendency}")

    return "\n".join(lines)


def render_constraints(constraints: list[str] | None) -> str:
    """Render user constraints as prompt section."""
    if not constraints:
        return ""

    lines = ["## Constraints", ""]
    for constraint in constraints:
        lines.append(f"- {constraint}")
    return "\n".join(lines)


# === PromptBuilder ===


@dataclass
class PromptBuilder:
    """
    Assemble complete prompts from context components.

    The frontend NEVER sees these prompts—only rendered messages.

    Example:
        builder = PromptBuilder()
        prompt = builder.build_system_prompt(
            agent_type="kgent",
            eigenvectors={"aesthetic": 0.15, "joy": 0.75},
            constraints=["Be concise", "No emojis"],
        )
        # prompt is a complete system prompt string (backend only)

    Usage with different agent types:
        # K-gent (6D eigenvectors)
        builder.build_system_prompt("kgent", kent_eigenvectors.to_dict())

        # Builder (7D eigenvectors + specialty)
        builder.build_system_prompt(
            "builder",
            citizen_eigenvectors.to_dict(),
            specialty="Scout",
        )

        # Citizen (7D eigenvectors + name)
        builder.build_system_prompt(
            "citizen",
            citizen_eigenvectors.to_dict(),
            name="Alice",
        )
    """

    system_templates: dict[str, str] = field(
        default_factory=lambda: dict(SYSTEM_TEMPLATES)
    )

    def build_system_prompt(
        self,
        agent_type: str,
        eigenvectors: dict[str, float] | None = None,
        constraints: list[str] | None = None,
        **kwargs: Any,
    ) -> str:
        """
        Build complete system prompt.

        Args:
            agent_type: "kgent", "builder", "citizen", or custom type
            eigenvectors: Personality coordinates (6D for kgent, 7D for citizen/builder)
            constraints: User-specified constraints
            **kwargs: Additional template variables (specialty, name, etc.)

        Returns:
            Complete system prompt (never sent to frontend)
        """
        # Get template
        template = self.system_templates.get(
            agent_type, self.system_templates["default"]
        )

        # Render eigenvectors based on agent type
        if agent_type == "kgent":
            persona = render_eigenvectors_6d(eigenvectors or {})
        else:
            persona = render_eigenvectors_7d(eigenvectors or {})

        # Render constraints
        constraint_section = render_constraints(constraints)

        # Build format kwargs
        format_kwargs = {
            "persona": persona,
            "constraints": constraint_section,
            **kwargs,
        }

        # Format template (handle missing keys gracefully)
        try:
            return template.format(**format_kwargs)
        except KeyError as e:
            # Fill missing keys with empty string
            missing_key = str(e).strip("'")
            format_kwargs[missing_key] = ""
            return template.format(**format_kwargs)

    def add_template(self, agent_type: str, template: str) -> None:
        """Add or override a system template."""
        self.system_templates[agent_type] = template

    def get_template(self, agent_type: str) -> str | None:
        """Get template for an agent type."""
        return self.system_templates.get(agent_type)


# === Factory Functions ===


def create_prompt_builder(
    custom_templates: dict[str, str] | None = None,
) -> PromptBuilder:
    """
    Create a PromptBuilder with optional custom templates.

    Args:
        custom_templates: Additional templates to merge with defaults

    Returns:
        Configured PromptBuilder
    """
    builder = PromptBuilder()
    if custom_templates:
        for agent_type, template in custom_templates.items():
            builder.add_template(agent_type, template)
    return builder


def build_kgent_prompt(
    eigenvectors: dict[str, float],
    constraints: list[str] | None = None,
) -> str:
    """
    Convenience function for building K-gent prompts.

    Args:
        eigenvectors: Kent's 6D eigenvector coordinates
        constraints: Optional constraints

    Returns:
        Complete K-gent system prompt
    """
    builder = PromptBuilder()
    return builder.build_system_prompt(
        agent_type="kgent",
        eigenvectors=eigenvectors,
        constraints=constraints,
    )


def build_builder_prompt(
    eigenvectors: dict[str, float],
    specialty: str,
    constraints: list[str] | None = None,
) -> str:
    """
    Convenience function for building Builder prompts.

    Args:
        eigenvectors: Citizen's 7D eigenvector coordinates
        specialty: Builder specialty (Scout, Sage, Spark, Steady, Sync)
        constraints: Optional constraints

    Returns:
        Complete Builder system prompt
    """
    builder = PromptBuilder()
    return builder.build_system_prompt(
        agent_type="builder",
        eigenvectors=eigenvectors,
        constraints=constraints,
        specialty=specialty,
    )


def build_citizen_prompt(
    eigenvectors: dict[str, float],
    name: str,
    constraints: list[str] | None = None,
) -> str:
    """
    Convenience function for building Citizen prompts.

    Args:
        eigenvectors: Citizen's 7D eigenvector coordinates
        name: Citizen name
        constraints: Optional constraints

    Returns:
        Complete Citizen system prompt
    """
    builder = PromptBuilder()
    return builder.build_system_prompt(
        agent_type="citizen",
        eigenvectors=eigenvectors,
        constraints=constraints,
        name=name,
    )
