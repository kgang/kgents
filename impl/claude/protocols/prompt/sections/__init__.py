"""
Section Compilers for the Evergreen Prompt System.

Each section of CLAUDE.md has its own compiler that:
1. Reads from source files (spec, docs, config)
2. Renders markdown based on context
3. Tracks source paths for cache invalidation

Available compilers:
- IdentitySectionCompiler: Project identity and philosophy
- PrinciplesSectionCompiler: The seven principles
- SystemsSectionCompiler: Built infrastructure reference
- SkillsSectionCompiler: Skills directory
- DirectoriesSectionCompiler: Key directories
- CommandsSectionCompiler: DevEx commands
- AgenteseSectionCompiler: AGENTESE ontology

Usage:
    from protocols.prompt.sections import get_default_compilers
    compilers = get_default_compilers()
"""

from .agentese import AgenteseSectionCompiler
from .commands import CommandsSectionCompiler
from .context import (
    CombinedContextSource,
    ContextSectionCompiler,
    GitContextSectionCompiler,
    PhaseSource,
    SessionSource,
    create_context_soft_section,
)
from .directories import DirectoriesSectionCompiler

# Wave 3 Phase 2: Dynamic Sections
from .forest import ForestSectionCompiler, ForestSource, create_forest_soft_section
from .identity import IdentitySectionCompiler
from .principles import PrinciplesSectionCompiler
from .skills import SkillsSectionCompiler
from .systems import SystemsSectionCompiler


def get_default_compilers() -> list:
    """
    Get the default ordered list of section compilers.

    Order matters for the final prompt structure.
    """
    return [
        IdentitySectionCompiler(),
        PrinciplesSectionCompiler(),
        AgenteseSectionCompiler(),
        SystemsSectionCompiler(),
        DirectoriesSectionCompiler(),
        SkillsSectionCompiler(),
        CommandsSectionCompiler(),
    ]


def get_full_compilers() -> list:
    """
    Get all compilers including dynamic sections (Wave 3+).

    Includes:
    - Context (git, phase, session) - placed early for situational awareness
    - Forest (current focus from plans/) - placed after systems
    """
    return [
        IdentitySectionCompiler(),
        ContextSectionCompiler(),  # NEW: Session context early
        PrinciplesSectionCompiler(),
        AgenteseSectionCompiler(),
        SystemsSectionCompiler(),
        ForestSectionCompiler(),  # NEW: Forest after systems
        DirectoriesSectionCompiler(),
        SkillsSectionCompiler(),
        CommandsSectionCompiler(),
    ]


__all__ = [
    # Wave 1-2 compilers
    "IdentitySectionCompiler",
    "PrinciplesSectionCompiler",
    "SystemsSectionCompiler",
    "SkillsSectionCompiler",
    "DirectoriesSectionCompiler",
    "CommandsSectionCompiler",
    "AgenteseSectionCompiler",
    # Wave 3 Phase 2: Dynamic sections
    "ForestSectionCompiler",
    "ForestSource",
    "create_forest_soft_section",
    "ContextSectionCompiler",
    "GitContextSectionCompiler",
    "PhaseSource",
    "SessionSource",
    "CombinedContextSource",
    "create_context_soft_section",
    # Compiler lists
    "get_default_compilers",
    "get_full_compilers",
]
