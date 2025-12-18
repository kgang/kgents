"""
Skills Section Compiler.

Compiles the skills directory section from docs/skills/*.md.

Wave 2: Now reads dynamically from docs/skills/*.md with fallback.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from ..section_base import (
    NPhase,
    Section,
    estimate_tokens,
    extract_skills_from_directory,
    glob_source_paths,
)

if TYPE_CHECKING:
    from ..compiler import CompilationContext

logger = logging.getLogger(__name__)


class SkillsSectionCompiler:
    """
    Compile the skills section of CLAUDE.md.

    Wave 2: Reads dynamically from docs/skills/*.md.
    Falls back to hardcoded content if source directory is missing.

    Curated descriptions are maintained here to ensure rich, actionable
    descriptions are preserved (rather than auto-generating generic ones).
    """

    # Curated descriptions for skills - these are maintained manually
    # to preserve rich, actionable descriptions in the compiled output.
    # Key: filename stem (without .md), Value: rich description
    CURATED_DESCRIPTIONS: dict[str, str] = {
        "agentese-path": "Adding AGENTESE paths (e.g., `self.soul.*`)",
        "building-agent": "Creating `Agent[A, B]` with functors",
        "cli-command": "Adding CLI commands to kgents",
        "flux-agent": "Lifting agents to stream processing",
        "handler-patterns": "CLI handler patterns",
        "plan-file": "Forest Protocol plan files",
        "polynomial-agent": "Creating `PolyAgent[S, A, B]` with state machines",
        "test-patterns": "Testing conventions and fixtures",
        "ux-reference-patterns": "Cross-cutting UX patterns from research",
        "user-flow-documentation": "Documenting precise user flows with ASCII wireframes",
    }

    @property
    def name(self) -> str:
        return "skills"

    @property
    def required(self) -> bool:
        return False  # Optional, can be omitted under pressure

    @property
    def phases(self) -> frozenset[NPhase]:
        return frozenset()  # All phases

    def compile(self, context: CompilationContext) -> Section:
        """
        Compile skills section.

        Attempts to read from docs/skills/*.md, falls back to hardcoded.
        """
        if context.docs_path:
            skills_dir = context.docs_path / "skills"
            source_paths = glob_source_paths(skills_dir, "*.md")

            if source_paths:
                content = self._compile_dynamic(context.docs_path, source_paths)
                if content:
                    return Section(
                        name=self.name,
                        content=content,
                        token_cost=estimate_tokens(content),
                        required=self.required,
                        phases=self.phases,
                        source_paths=source_paths,
                    )

        # Fallback to hardcoded
        logger.info("Using fallback content for skills section")
        content = self._compile_fallback()
        return Section(
            name=self.name,
            content=content,
            token_cost=estimate_tokens(content),
            required=self.required,
            phases=self.phases,
            source_paths=(),
        )

    def estimate_tokens(self) -> int:
        """Estimate ~350 tokens for skills section."""
        return 350

    def _compile_dynamic(self, docs_path: Path, source_paths: tuple[Path, ...]) -> str | None:
        """
        Read and aggregate skills from docs/skills/*.md.

        Uses curated descriptions for known skills to preserve rich,
        actionable descriptions. Falls back to H1 header for unknown skills.
        """
        skills = extract_skills_from_directory(docs_path)
        if not skills:
            return None

        # Build skills table - select most important skills for prompt
        # Priority: core skills that are frequently used
        priority_skills = [
            "agentese-path",
            "building-agent",
            "cli-command",
            "flux-agent",
            "handler-patterns",
            "plan-file",
            "polynomial-agent",
            "test-patterns",
            "ux-reference-patterns",
            "user-flow-documentation",
        ]

        # Sort: priority skills first, then alphabetically
        def sort_key(skill_tuple):
            name, desc, path = skill_tuple
            stem = path.stem
            if stem in priority_skills:
                return (0, priority_skills.index(stem))
            return (1, stem)

        sorted_skills = sorted(skills, key=sort_key)

        # Build table with top 15 skills
        # Use curated descriptions for known skills, fall back to H1 header
        table_lines = ["| Skill | Description |", "|-------|-------------|"]
        for name, desc, path in sorted_skills[:15]:
            # Prefer curated description, fall back to H1 header from file
            curated = self.CURATED_DESCRIPTIONS.get(path.stem)
            description = curated if curated else name
            table_lines.append(f"| `{path.name}` | {description} |")

        skills_table = "\n".join(table_lines)
        skill_count = len(skills)

        return f"""## Skills Directory

`docs/skills/` contains {skill_count} documented patterns for common tasks:

{skills_table}

## Working With This Repo

- **CHECK `docs/systems-reference.md` BEFORE assuming you need to build something new**
- When adding new agent concepts, **start in `spec/`**
- Implementations should faithfully follow specs
- Composability is paramount (C-gents principles apply everywhere)
- Read `spec/principles.md` before contributing
- **Use AGENTESE paths** for agent-world interaction when possible
- **Consult skills** in `docs/skills/` for common patterns"""

    def _compile_fallback(self) -> str:
        """Hardcoded fallback content when source directory is unavailable."""
        return """## Skills Directory

`docs/skills/` contains documented patterns for common tasks:

| Skill | Description |
|-------|-------------|
| `agentese-path.md` | Adding AGENTESE paths (e.g., `self.soul.*`) |
| `building-agent.md` | Creating `Agent[A, B]` with functors |
| `cli-command.md` | Adding CLI commands to kgents |
| `flux-agent.md` | Lifting agents to stream processing |
| `handler-patterns.md` | CLI handler patterns |
| `plan-file.md` | Forest Protocol plan files |
| `polynomial-agent.md` | Creating `PolyAgent[S, A, B]` with state machines |
| `test-patterns.md` | Testing conventions and fixtures |
| `ux-reference-patterns.md` | Cross-cutting UX patterns from research |
| `user-flow-documentation.md` | Documenting precise user flows with ASCII wireframes |

## Working With This Repo

- **CHECK `docs/systems-reference.md` BEFORE assuming you need to build something new**
- When adding new agent concepts, **start in `spec/`**
- Implementations should faithfully follow specs
- Composability is paramount (C-gents principles apply everywhere)
- Read `spec/principles.md` before contributing
- **Use AGENTESE paths** for agent-world interaction when possible
- **Consult skills** in `docs/skills/` for common patterns"""


__all__ = ["SkillsSectionCompiler"]
