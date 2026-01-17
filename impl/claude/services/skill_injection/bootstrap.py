"""
Skill Bootstrap: Load Existing Skills into Registry

Parses docs/skills/*.md files and extracts activation conditions
to register them in the SkillRegistry.

Philosophy:
    "Existing knowledge should be immediately available."
    "Parse structure from content, not configuration."

AGENTESE: self.skill.bootstrap
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import yaml

from .registry import SkillRegistry, get_skill_registry
from .types import (
    COMMON_COMPOSITIONS,
    ActivationCondition,
    ContextType,
    Skill,
    SkillCategory,
)

logger = logging.getLogger(__name__)


# Mapping from skill file patterns to categories
SKILL_CATEGORY_PATTERNS: list[tuple[str, SkillCategory]] = [
    (r"polynomial-agent|building-agent", SkillCategory.FOUNDATION),
    (r"agentese-", SkillCategory.PROTOCOL),
    (r"crown-jewel|metaphysical|data-bus|hypergraph|unified-storage", SkillCategory.ARCHITECTURE),
    (r"witness|derivation", SkillCategory.WITNESS),
    (r"research|cli-strategy|witnessed-regeneration|plan-file|spec-", SkillCategory.PROCESS),
    (r"projection|marimo|test-|elastic-ui|tui-", SkillCategory.PROJECTION),
]

# Task patterns that trigger specific skills
# Format: (pattern, skill_id, priority, context_type)
SKILL_ACTIVATION_PATTERNS: list[tuple[str, str, float, ContextType]] = [
    # Foundation skills
    (r"\bagent\b.*state\s*machine", "polynomial-agent", 0.8, ContextType.TASK),
    (r"polynomial\s*agent", "polynomial-agent", 0.9, ContextType.TASK),
    (r"\bPolyAgent\b", "polynomial-agent", 0.9, ContextType.KEYWORD),
    (r"new\s+agent", "building-agent", 0.7, ContextType.TASK),
    (r"Agent\[A,\s*B\]", "building-agent", 0.8, ContextType.KEYWORD),
    # Protocol skills
    (r"@node", "agentese-node-registration", 0.9, ContextType.KEYWORD),
    (r"AGENTESE\s*node", "agentese-node-registration", 0.8, ContextType.TASK),
    (r"DependencyNotFoundError", "agentese-node-registration", 0.95, ContextType.ERROR),
    (r"node\s*not\s*registered", "agentese-node-registration", 0.9, ContextType.ERROR),
    (r"agentese\s*path", "agentese-path", 0.8, ContextType.TASK),
    (r"world\.|self\.|concept\.|void\.|time\.", "agentese-path", 0.6, ContextType.KEYWORD),
    # Architecture skills
    (r"crown\s*jewel", "crown-jewel-patterns", 0.9, ContextType.TASK),
    (r"service\s*implementation", "crown-jewel-patterns", 0.7, ContextType.TASK),
    (r"metaphysical|fullstack|vertical\s*slice", "metaphysical-fullstack", 0.8, ContextType.TASK),
    (r"event.*bus|DataBus|SynergyBus", "data-bus-integration", 0.8, ContextType.TASK),
    (r"event\s*not\s*propagating", "data-bus-integration", 0.9, ContextType.ERROR),
    (r"hypergraph|K-Block", "hypergraph-editor", 0.8, ContextType.TASK),
    (r"dual.track|storage.*provider", "unified-storage", 0.8, ContextType.TASK),
    # Witness skills
    (r"witness|mark|decision", "witness-for-agents", 0.7, ContextType.TASK),
    (r"crystallize", "witness-for-agents", 0.8, ContextType.KEYWORD),
    (r"derivation|edge\s*evidence", "derivation-edges", 0.8, ContextType.TASK),
    # Process skills
    (r"experiment|hypothesis|research", "research-protocol", 0.7, ContextType.TASK),
    (
        r"kg\s*(audit|annotate|probe|compose|experiment)",
        "cli-strategy-tools",
        0.8,
        ContextType.COMMAND,
    ),
    (r"regenerat.*pilot", "witnessed-regeneration", 0.8, ContextType.TASK),
    (r"writing\s*spec|spec\s*template", "spec-template", 0.8, ContextType.TASK),
    (r"spec\s*bloat|compression", "spec-hygiene", 0.7, ContextType.TASK),
    # Projection skills
    (r"responsive|elastic|three.*mode", "elastic-ui-patterns", 0.8, ContextType.TASK),
    (r"UI\s*component|frontend", "elastic-ui-patterns", 0.6, ContextType.TASK),
    (r"projection.*target|CLI.*TUI.*JSON", "projection-target", 0.8, ContextType.TASK),
    (r"marimo", "marimo-projection", 0.9, ContextType.KEYWORD),
    (r"test.*pattern|T-gent|property.*based", "test-patterns", 0.8, ContextType.TASK),
    (r"pytest|hypothesis", "test-patterns", 0.7, ContextType.KEYWORD),
    (r"TUI.*pattern", "tui-patterns", 0.8, ContextType.TASK),
    # File patterns
    (r"impl/claude/agents/.*polynomial", "polynomial-agent", 0.7, ContextType.FILE),
    (r"impl/claude/services/.*node\.py", "agentese-node-registration", 0.6, ContextType.FILE),
    (r"impl/claude/web/.*\.tsx", "elastic-ui-patterns", 0.5, ContextType.FILE),
    (r"_tests/.*test_", "test-patterns", 0.5, ContextType.FILE),
]

# Keywords extracted from skill content
SKILL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "polynomial-agent": ("polynomial", "state machine", "PolyAgent", "mode-dependent"),
    "building-agent": ("agent", "functor", "D-gent", "composition"),
    "agentese-node-registration": ("@node", "decorator", "DI", "dependency injection", "container"),
    "agentese-path": ("AGENTESE", "path", "context", "world", "self", "concept"),
    "crown-jewel-patterns": ("crown jewel", "service", "pattern", "container-owns-workflow"),
    "metaphysical-fullstack": ("fullstack", "vertical slice", "AD-009", "persistence"),
    "data-bus-integration": ("DataBus", "SynergyBus", "EventBus", "event", "reactive"),
    "hypergraph-editor": ("hypergraph", "K-Block", "modal editing", "six-mode"),
    "unified-storage": ("D-gent", "storage", "dual-track", "TableAdapter"),
    "witness-for-agents": ("witness", "mark", "decision", "evidence", "stigmergy"),
    "derivation-edges": ("derivation", "edge", "provenance", "evidence"),
    "research-protocol": ("experiment", "hypothesis", "Bayesian", "evidence"),
    "cli-strategy-tools": ("audit", "annotate", "probe", "compose", "experiment"),
    "witnessed-regeneration": ("regeneration", "pilot", "archive", "validate"),
    "spec-template": ("spec", "template", "compression", "generative"),
    "spec-hygiene": ("bloat", "hygiene", "compression", "anti-pattern"),
    "elastic-ui-patterns": ("elastic", "responsive", "compact", "comfortable", "spacious"),
    "projection-target": ("projection", "CLI", "TUI", "JSON", "marimo"),
    "marimo-projection": ("marimo", "notebook", "callback", "late-binding"),
    "test-patterns": ("test", "T-gent", "hypothesis", "property-based", "chaos"),
    "tui-patterns": ("TUI", "terminal", "modal", "keybinding"),
}

# Meta-epistemic names (LLM-friendly)
SKILL_FRIENDLY_NAMES: dict[str, str] = {
    "polynomial-agent": "Building Polynomial Agents (State Machines)",
    "building-agent": "Creating Categorical Agents",
    "agentese-node-registration": "Registering AGENTESE Nodes (@node)",
    "agentese-path": "AGENTESE Path Structure",
    "crown-jewel-patterns": "Crown Jewel Service Patterns",
    "metaphysical-fullstack": "Metaphysical Fullstack Architecture",
    "data-bus-integration": "Event Bus Integration (DataBus/SynergyBus)",
    "hypergraph-editor": "Hypergraph Editor & K-Block",
    "unified-storage": "Unified Storage with D-gent",
    "witness-for-agents": "Witness System for Agents",
    "derivation-edges": "Derivation Edge Evidence",
    "research-protocol": "Research Protocol (Experiments)",
    "cli-strategy-tools": "CLI Strategy Tools (audit/probe/compose)",
    "witnessed-regeneration": "Witnessed Regeneration Protocol",
    "spec-template": "Writing Specifications",
    "spec-hygiene": "Specification Hygiene",
    "elastic-ui-patterns": "Elastic UI Patterns (Responsive)",
    "projection-target": "Multi-Target Projection",
    "marimo-projection": "Marimo Notebook Projection",
    "test-patterns": "Testing Patterns (T-gent)",
    "tui-patterns": "TUI Patterns",
    "zero-seed-for-agents": "Zero Seed Protocol",
    "analysis-operad": "Analysis Operad",
    "aspect-form-projection": "Aspect-Form Projection",
    "cli-handler-patterns": "CLI Handler Patterns",
    "nphase-integration": "N-Phase Integration",
    "proof-verifier-bridge": "Proof-Verifier Bridge",
    "validation": "Validation Patterns",
    "storybook-for-agents": "Storybook for Agents",
    "mypy-best-practices": "MyPy Best Practices",
}


def categorize_skill(skill_id: str) -> SkillCategory:
    """Determine the category for a skill based on its ID."""
    for pattern, category in SKILL_CATEGORY_PATTERNS:
        if re.search(pattern, skill_id):
            return category
    return SkillCategory.UNIVERSAL


def extract_activation_conditions(skill_id: str) -> list[ActivationCondition]:
    """Extract activation conditions for a skill."""
    conditions = []

    for pattern, sid, priority, ctx_type in SKILL_ACTIVATION_PATTERNS:
        if sid == skill_id:
            conditions.append(
                ActivationCondition(
                    pattern=pattern,
                    context_type=ctx_type,
                    priority=priority,
                    description=f"Pattern: {pattern}",
                )
            )

    return conditions


def parse_skill_frontmatter(content: str) -> dict[str, Any]:
    """Parse YAML frontmatter from skill content."""
    if not content.startswith("---"):
        return {}

    try:
        # Find the closing ---
        end_idx = content.index("---", 3)
        frontmatter = content[3:end_idx].strip()
        return yaml.safe_load(frontmatter) or {}
    except (ValueError, yaml.YAMLError):
        return {}


def estimate_read_time(content: str) -> int:
    """Estimate read time in minutes (200 words per minute)."""
    words = len(content.split())
    return max(5, words // 200)


def load_skill_from_file(skill_path: Path) -> Skill | None:
    """
    Load a skill from a markdown file.

    Args:
        skill_path: Path to the skill file

    Returns:
        Skill object or None if parsing fails
    """
    try:
        content = skill_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning(f"Failed to read skill file {skill_path}: {e}")
        return None

    skill_id = skill_path.stem  # filename without extension
    frontmatter = parse_skill_frontmatter(content)

    # Get friendly name
    name = SKILL_FRIENDLY_NAMES.get(skill_id, skill_id.replace("-", " ").title())

    # Get category
    category = categorize_skill(skill_id)

    # Get activation conditions
    conditions = extract_activation_conditions(skill_id)

    # Get keywords
    keywords = SKILL_KEYWORDS.get(skill_id, ())

    # Extract description from first non-empty line after frontmatter
    description = ""
    lines = content.split("\n")
    for line in lines:
        if line.startswith("---"):
            continue
        if line.startswith(">"):
            description = line.lstrip("> ").strip("*").strip()
            break
        if line.startswith("#"):
            # Skip title line
            continue

    # Determine dependencies from content
    dependencies: list[str] = []
    if "polynomial-agent" in content.lower() and skill_id != "polynomial-agent":
        dependencies.append("polynomial-agent")
    if "agentese-node-registration" in content.lower() and skill_id != "agentese-node-registration":
        dependencies.append("agentese-node-registration")
    if "metaphysical-fullstack" in content.lower() and skill_id != "metaphysical-fullstack":
        dependencies.append("metaphysical-fullstack")

    # Estimate read time
    read_time = estimate_read_time(content)

    return Skill(
        id=skill_id,
        name=name,
        path=str(skill_path),
        category=category,
        activation_conditions=tuple(conditions),
        dependencies=tuple(dependencies[:3]),  # Max 3 dependencies
        keywords=keywords,
        description=description,
        estimated_read_time_minutes=read_time,
    )


def bootstrap_skills(
    skills_dir: Path | str | None = None,
    registry: SkillRegistry | None = None,
) -> int:
    """
    Bootstrap skills from the skills directory.

    Args:
        skills_dir: Path to skills directory (default: docs/skills)
        registry: Registry to populate (default: global registry)

    Returns:
        Number of skills loaded
    """
    if skills_dir is None:
        # Try to find skills directory relative to this file
        this_file = Path(__file__)
        # Go up to impl/claude, then to docs/skills
        skills_dir = this_file.parents[3] / "docs" / "skills"

    skills_dir = Path(skills_dir)
    if not skills_dir.exists():
        logger.warning(f"Skills directory not found: {skills_dir}")
        return 0

    registry = registry or get_skill_registry()

    loaded = 0
    for skill_path in skills_dir.glob("*.md"):
        # Skip special files
        if skill_path.name in ("README.md", "ROUTING.md", "QUICK-REFERENCE.md"):
            continue

        skill = load_skill_from_file(skill_path)
        if skill:
            try:
                registry.register(skill, allow_overwrite=True)
                loaded += 1
            except Exception as e:
                logger.warning(f"Failed to register skill {skill.id}: {e}")

    # Register common compositions
    for composition in COMMON_COMPOSITIONS.values():
        try:
            registry.register_composition(composition, allow_overwrite=True)
        except Exception as e:
            logger.warning(f"Failed to register composition {composition.id}: {e}")

    logger.info(f"Bootstrapped {loaded} skills from {skills_dir}")
    return loaded


def bootstrap_skills_from_routing() -> int:
    """
    Bootstrap skills from CLAUDE.md skill routing table.

    This is a lighter-weight bootstrap that uses the existing routing table.

    Returns:
        Number of skills registered
    """
    registry = get_skill_registry()

    # Skills from CLAUDE.md routing table
    routing_skills = [
        ("polynomial-agent", "agent, state machine, polynomial"),
        ("agentese-node-registration", "AGENTESE, @node, node registration, DI"),
        ("metaphysical-fullstack", "persist, storage, database, dual-track"),
        ("test-patterns", "test, testing, T-gent, property-based"),
        ("elastic-ui-patterns", "UI, frontend, component, elastic, responsive"),
        ("data-bus-integration", "event, bus, reactive, DataBus"),
        ("spec-template", "spec, specification, writing specs"),
        ("witness-for-agents", "witness, mark, decision, crystallize"),
        ("plan-file", "plan, planning, forest"),
        ("research-protocol", "research, experiment, hypothesis"),
    ]

    loaded = 0
    for skill_id, keywords_str in routing_skills:
        keywords = tuple(k.strip() for k in keywords_str.split(","))
        name = SKILL_FRIENDLY_NAMES.get(skill_id, skill_id)
        category = categorize_skill(skill_id)
        conditions = extract_activation_conditions(skill_id)

        skill = Skill(
            id=skill_id,
            name=name,
            path=f"docs/skills/{skill_id}.md",
            category=category,
            activation_conditions=tuple(conditions),
            keywords=keywords,
        )

        try:
            registry.register(skill, allow_overwrite=True)
            loaded += 1
        except Exception as e:
            logger.warning(f"Failed to register skill {skill_id}: {e}")

    return loaded


__all__ = [
    "bootstrap_skills",
    "bootstrap_skills_from_routing",
    "categorize_skill",
    "extract_activation_conditions",
    "load_skill_from_file",
    "parse_skill_frontmatter",
]
