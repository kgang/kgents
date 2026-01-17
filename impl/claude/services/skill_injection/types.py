"""
Skill Injection Core Types

The foundational types for the JIT Skill Injection system.

Philosophy:
    "Skills surface exactly when needed, not before."
    "Context-aware activation based on task patterns."

The Five Core Types:
- Skill: A documented capability with activation conditions
- ActivationCondition: When a skill should surface
- TaskContext: The current task environment
- SkillUsageTrace: Evidence of skill usage
- SkillComposition: Combined skills for complex tasks

AGENTESE: self.skill
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal


class ContextType(Enum):
    """The type of context that triggers skill activation."""

    TASK = "task"  # Task description pattern
    FILE = "file"  # File being edited pattern
    ERROR = "error"  # Error message pattern
    QUESTION = "question"  # Question being asked pattern
    COMMAND = "command"  # CLI command pattern
    KEYWORD = "keyword"  # Explicit keyword match


class SkillCategory(Enum):
    """Skill categories for organization and routing."""

    FOUNDATION = "foundation"  # Categorical ground (polynomial-agent, building-agent)
    PROTOCOL = "protocol"  # AGENTESE (agentese-path, agentese-node-registration)
    ARCHITECTURE = "architecture"  # Vertical slice (crown-jewel, metaphysical-fullstack)
    WITNESS = "witness"  # Evidence & derivation (witness-for-agents, derivation-edges)
    PROCESS = "process"  # N-Phase & research (research-protocol, cli-strategy-tools)
    PROJECTION = "projection"  # Multi-target (projection-target, elastic-ui-patterns)
    UNIVERSAL = "universal"  # Applies to any project


class UsageOutcome(Enum):
    """Outcome of a skill usage."""

    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    SKIPPED = "skipped"  # User skipped reading the skill


@dataclass(frozen=True)
class ActivationCondition:
    """
    A condition that triggers skill activation.

    Activation conditions define WHEN a skill should surface.
    Multiple conditions can combine (OR logic for activation).

    Teaching:
        gotcha: Pattern is a regex when context_type is TASK, FILE, ERROR.
                For KEYWORD, it's a simple case-insensitive match.
                (Evidence: test_types.py::test_activation_condition_pattern_types)

        gotcha: Priority 1.0 means "always surface if matched".
                Priority 0.0 means "never surface (disabled)".
                Typical range: 0.3-0.9 for context-dependent activation.
                (Evidence: test_types.py::test_activation_condition_priority)
    """

    pattern: str  # Regex or keyword pattern
    context_type: ContextType  # What triggers this condition
    priority: float = 0.5  # 0.0-1.0, higher = more likely to activate
    description: str = ""  # Human-readable description of when this fires

    def __post_init__(self) -> None:
        """Validate priority range."""
        if not 0.0 <= self.priority <= 1.0:
            raise ValueError(f"Priority must be 0.0-1.0, got {self.priority}")

    def matches(self, context: str) -> bool:
        """
        Check if this condition matches the given context.

        Args:
            context: The context string to match against

        Returns:
            True if the condition matches
        """
        if self.context_type == ContextType.KEYWORD:
            return self.pattern.lower() in context.lower()
        else:
            try:
                return bool(re.search(self.pattern, context, re.IGNORECASE))
            except re.error:
                return False


@dataclass(frozen=True)
class Skill:
    """
    A documented capability with activation conditions.

    Skills are the atomic units of knowledge in kgents.
    Each skill represents a documented pattern that can be
    surfaced just-in-time when the context calls for it.

    Teaching:
        gotcha: The `name` field should be LLM-friendly (meta-epistemic naming).
                Use action-oriented names: "Building Polynomial Agent" not "polynomial-agent".
                (Evidence: test_types.py::test_skill_meta_epistemic_naming)

        gotcha: `dependencies` are OTHER skills that should be co-activated.
                Not to be confused with DI dependencies in @node decorators.
                (Evidence: test_types.py::test_skill_dependencies)
    """

    id: str  # Unique identifier (e.g., "polynomial-agent")
    name: str  # Meta-epistemic name (LLM-friendly, e.g., "Building Polynomial Agents")
    path: str  # Path to skill file (e.g., "docs/skills/polynomial-agent.md")
    category: SkillCategory  # Skill category
    activation_conditions: tuple[ActivationCondition, ...] = ()  # When to surface
    dependencies: tuple[str, ...] = ()  # Other skill IDs this builds on
    keywords: tuple[str, ...] = ()  # Explicit trigger keywords
    description: str = ""  # Brief description
    estimated_read_time_minutes: int = 10  # How long to read

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "category": self.category.value,
            "activation_conditions": [
                {
                    "pattern": c.pattern,
                    "context_type": c.context_type.value,
                    "priority": c.priority,
                    "description": c.description,
                }
                for c in self.activation_conditions
            ],
            "dependencies": list(self.dependencies),
            "keywords": list(self.keywords),
            "description": self.description,
            "estimated_read_time_minutes": self.estimated_read_time_minutes,
        }


@dataclass(frozen=True)
class TaskContext:
    """
    The current task environment for skill activation.

    TaskContext captures everything about the current moment
    that might inform which skills to surface.

    Teaching:
        gotcha: `active_files` should be absolute paths.
                The engine uses these to match FILE-type conditions.
                (Evidence: test_types.py::test_task_context_file_paths)
    """

    task_description: str  # What the user is trying to do
    active_files: tuple[str, ...] = ()  # Files being edited
    error_messages: tuple[str, ...] = ()  # Recent errors
    recent_commands: tuple[str, ...] = ()  # Recent CLI commands
    user_keywords: tuple[str, ...] = ()  # Explicit keywords from user
    session_id: str = ""  # Current session ID

    def all_context_strings(self) -> list[tuple[str, ContextType]]:
        """
        Get all context strings with their types.

        Returns:
            List of (context_string, context_type) tuples
        """
        result: list[tuple[str, ContextType]] = []

        if self.task_description:
            result.append((self.task_description, ContextType.TASK))

        for f in self.active_files:
            result.append((f, ContextType.FILE))

        for e in self.error_messages:
            result.append((e, ContextType.ERROR))

        for c in self.recent_commands:
            result.append((c, ContextType.COMMAND))

        for k in self.user_keywords:
            result.append((k, ContextType.KEYWORD))

        return result

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_description": self.task_description,
            "active_files": list(self.active_files),
            "error_messages": list(self.error_messages),
            "recent_commands": list(self.recent_commands),
            "user_keywords": list(self.user_keywords),
            "session_id": self.session_id,
        }


@dataclass
class SkillUsageTrace:
    """
    Evidence of skill usage for stigmergic learning.

    Usage traces inform future activation decisions.
    High success rates increase a skill's priority for similar contexts.
    Failures inform what NOT to surface.

    Teaching:
        gotcha: `context_hash` should be a stable hash of the context
                that triggered activation. Used for pattern matching.
                (Evidence: test_types.py::test_skill_usage_trace_hash)
    """

    skill_id: str
    context_hash: str  # Hash of the context that triggered activation
    context_summary: str  # Human-readable context summary
    outcome: UsageOutcome
    timestamp: datetime
    duration_seconds: float = 0.0  # How long the skill was active
    feedback: str = ""  # Optional user feedback
    session_id: str = ""  # Session where this occurred

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "skill_id": self.skill_id,
            "context_hash": self.context_hash,
            "context_summary": self.context_summary,
            "outcome": self.outcome.value,
            "timestamp": self.timestamp.isoformat(),
            "duration_seconds": self.duration_seconds,
            "feedback": self.feedback,
            "session_id": self.session_id,
        }


@dataclass(frozen=True)
class SkillActivation:
    """
    A skill activation with its computed score.

    Represents a skill that has been selected for injection
    along with the reasoning for why it was selected.
    """

    skill: Skill
    score: float  # 0.0-1.0 activation score
    matched_conditions: tuple[ActivationCondition, ...]  # Which conditions matched
    context_snippet: str = ""  # What part of context triggered it

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "skill": self.skill.to_dict(),
            "score": self.score,
            "matched_conditions": [
                {
                    "pattern": c.pattern,
                    "context_type": c.context_type.value,
                    "priority": c.priority,
                }
                for c in self.matched_conditions
            ],
            "context_snippet": self.context_snippet,
        }


@dataclass(frozen=True)
class SkillComposition:
    """
    A composition of multiple skills for complex tasks.

    Skills compose naturally. Building a Crown Jewel requires:
    - crown-jewel-patterns (primary)
    - metaphysical-fullstack (architecture)
    - agentese-node-registration (API)
    - test-patterns (testing)

    Teaching:
        gotcha: Order matters! Primary skill should be first.
                Readers follow the order for learning path.
                (Evidence: test_types.py::test_skill_composition_order)
    """

    id: str  # Composition identifier
    name: str  # Human-friendly name
    skill_ids: tuple[str, ...]  # Ordered list of skill IDs
    description: str = ""
    usage_count: int = 0  # How often this composition is used

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "skill_ids": list(self.skill_ids),
            "description": self.description,
            "usage_count": self.usage_count,
        }


@dataclass
class InjectionResult:
    """
    Result of skill injection.

    Contains the injected content and metadata about
    which skills were activated and why.
    """

    content: str  # The injected skill content
    activations: list[SkillActivation]  # Which skills were activated
    composition: SkillComposition | None = None  # If a composition was used
    total_read_time_minutes: int = 0  # Estimated total read time

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "content": self.content,
            "activations": [a.to_dict() for a in self.activations],
            "composition": self.composition.to_dict() if self.composition else None,
            "total_read_time_minutes": self.total_read_time_minutes,
        }


# Predefined skill compositions (from ROUTING.md common workflows)
COMMON_COMPOSITIONS: dict[str, SkillComposition] = {
    "new-agentese-node": SkillComposition(
        id="new-agentese-node",
        name="Adding a New AGENTESE Node",
        skill_ids=(
            "agentese-node-registration",
            "agentese-path",
            "test-patterns",
            "metaphysical-fullstack",
        ),
        description="Full workflow for adding a new AGENTESE endpoint",
    ),
    "new-crown-jewel": SkillComposition(
        id="new-crown-jewel",
        name="Building a Crown Jewel",
        skill_ids=(
            "crown-jewel-patterns",
            "metaphysical-fullstack",
            "unified-storage",
            "data-bus-integration",
            "agentese-node-registration",
            "elastic-ui-patterns",
            "test-patterns",
        ),
        description="Full workflow for building a new Crown Jewel service",
    ),
    "new-agent": SkillComposition(
        id="new-agent",
        name="Creating a New Agent",
        skill_ids=(
            "building-agent",
            "polynomial-agent",
            "test-patterns",
        ),
        description="Workflow for creating a new categorical agent",
    ),
    "debug-event-flow": SkillComposition(
        id="debug-event-flow",
        name="Debugging Event Flow",
        skill_ids=(
            "data-bus-integration",
            "crown-jewel-patterns",
        ),
        description="Workflow for debugging event propagation issues",
    ),
}


__all__ = [
    "ActivationCondition",
    "COMMON_COMPOSITIONS",
    "ContextType",
    "InjectionResult",
    "Skill",
    "SkillActivation",
    "SkillCategory",
    "SkillComposition",
    "SkillUsageTrace",
    "TaskContext",
    "UsageOutcome",
]
