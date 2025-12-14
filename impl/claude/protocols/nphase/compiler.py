"""
N-Phase Prompt Compiler.

The Meta-Meta-Prompt: generates N-Phase prompts from project definitions.

AGENTESE handle: concept.nphase.compile

Laws:
- compile(parse(yaml)) produces valid N-Phase prompt
- compile is idempotent on stable projects
- compile preserves all project information (no loss)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .schema import ProjectDefinition
from .template import NPhaseTemplate


@dataclass
class NPhasePrompt:
    """Compiled N-Phase prompt."""

    content: str
    project: ProjectDefinition

    def __str__(self) -> str:
        return self.content

    def save(self, path: str | Path) -> None:
        """Save prompt to file."""
        Path(path).write_text(self.content)


class NPhasePromptCompiler:
    """
    The Meta-Meta-Prompt: generates N-Phase prompts from project definitions.

    AGENTESE handle: concept.nphase.compile

    Laws:
    - compile(parse(yaml)) produces valid N-Phase prompt
    - compile is idempotent on stable projects
    - compile preserves all project information (no loss)
    """

    def compile(self, definition: ProjectDefinition) -> NPhasePrompt:
        """
        Compile a project definition into an N-Phase Meta-Prompt.

        Steps:
        1. Validate definition
        2. Load phase templates
        3. Render shared context
        4. Render each phase section
        5. Assemble final prompt

        Raises:
            ValueError: If definition is invalid
        """
        # Step 1: Validate
        result = definition.validate()
        result.raise_if_invalid()

        # Step 2-5: Render via template
        template = NPhaseTemplate(n_phases=definition.n_phases)
        content = template.render(definition)

        return NPhasePrompt(content=content, project=definition)

    def compile_from_yaml(self, yaml_content: str) -> NPhasePrompt:
        """Convenience: parse YAML and compile."""
        definition = ProjectDefinition.from_yaml(yaml_content)
        return self.compile(definition)

    def compile_from_yaml_file(self, yaml_path: str | Path) -> NPhasePrompt:
        """Convenience: load YAML file and compile."""
        definition = ProjectDefinition.from_yaml_file(yaml_path)
        return self.compile(definition)

    def compile_from_plan(self, plan_path: str | Path) -> NPhasePrompt:
        """
        Bootstrap compilation from existing plan file.

        Useful for incremental adoption: existing plans can be
        converted to compiled prompts.
        """
        definition = ProjectDefinition.from_plan_header(plan_path)
        return self.compile(definition)


# Singleton for convenience
compiler = NPhasePromptCompiler()
