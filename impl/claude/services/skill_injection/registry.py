"""
Skill Registry: Central Registry for Skills with Activation Conditions

The SkillRegistry maintains all registered skills and provides
lookup by context, keywords, and direct ID.

Philosophy:
    "Skills surface exactly when needed."
    "The registry is the ground truth for what skills exist."

AGENTESE: self.skill.registry
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .types import (
    ActivationCondition,
    ContextType,
    Skill,
    SkillCategory,
    SkillComposition,
    TaskContext,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class SkillNotFoundError(Exception):
    """Raised when a skill is not found in the registry."""

    def __init__(self, skill_id: str) -> None:
        self.skill_id = skill_id
        super().__init__(f"Skill not found: {skill_id}")


class DuplicateSkillError(Exception):
    """Raised when trying to register a skill that already exists."""

    def __init__(self, skill_id: str) -> None:
        self.skill_id = skill_id
        super().__init__(f"Skill already registered: {skill_id}")


@dataclass
class SkillMatch:
    """A skill that matches a search criteria."""

    skill: Skill
    score: float  # Match relevance score
    match_reason: str  # Why this skill matched


@dataclass
class SkillRegistry:
    """
    Central registry for skills with activation conditions.

    The registry is the single source of truth for what skills exist
    and how they should be activated.

    Teaching:
        gotcha: Register skills at startup time, not during requests.
                The registry should be stable during a session.
                (Evidence: test_registry.py::test_registry_startup)

        gotcha: Use find_by_context for JIT injection (evaluates all conditions).
                Use find_by_keywords for explicit user requests.
                Use get_skill for direct access when you know the ID.
                (Evidence: test_registry.py::test_registry_lookup_methods)
    """

    _skills: dict[str, Skill] = field(default_factory=dict)
    _keyword_index: dict[str, set[str]] = field(default_factory=dict)  # keyword -> skill_ids
    _category_index: dict[SkillCategory, set[str]] = field(
        default_factory=dict
    )  # category -> skill_ids
    _compositions: dict[str, SkillComposition] = field(default_factory=dict)

    def register(self, skill: Skill, *, allow_overwrite: bool = False) -> None:
        """
        Register a skill in the registry.

        Args:
            skill: The skill to register
            allow_overwrite: If True, allow overwriting existing skills

        Raises:
            DuplicateSkillError: If skill already exists and allow_overwrite is False
        """
        if skill.id in self._skills and not allow_overwrite:
            raise DuplicateSkillError(skill.id)

        self._skills[skill.id] = skill

        # Index keywords
        for keyword in skill.keywords:
            keyword_lower = keyword.lower()
            if keyword_lower not in self._keyword_index:
                self._keyword_index[keyword_lower] = set()
            self._keyword_index[keyword_lower].add(skill.id)

        # Index category
        if skill.category not in self._category_index:
            self._category_index[skill.category] = set()
        self._category_index[skill.category].add(skill.id)

        logger.debug(f"Registered skill: {skill.id} ({skill.name})")

    def unregister(self, skill_id: str) -> None:
        """
        Remove a skill from the registry.

        Args:
            skill_id: The ID of the skill to remove

        Raises:
            SkillNotFoundError: If skill doesn't exist
        """
        if skill_id not in self._skills:
            raise SkillNotFoundError(skill_id)

        skill = self._skills[skill_id]

        # Remove from keyword index
        for keyword in skill.keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in self._keyword_index:
                self._keyword_index[keyword_lower].discard(skill_id)
                if not self._keyword_index[keyword_lower]:
                    del self._keyword_index[keyword_lower]

        # Remove from category index
        if skill.category in self._category_index:
            self._category_index[skill.category].discard(skill_id)
            if not self._category_index[skill.category]:
                del self._category_index[skill.category]

        del self._skills[skill_id]
        logger.debug(f"Unregistered skill: {skill_id}")

    def get_skill(self, skill_id: str) -> Skill:
        """
        Get a skill by ID.

        Args:
            skill_id: The skill ID

        Returns:
            The skill

        Raises:
            SkillNotFoundError: If skill doesn't exist
        """
        if skill_id not in self._skills:
            raise SkillNotFoundError(skill_id)
        return self._skills[skill_id]

    def get_skill_or_none(self, skill_id: str) -> Skill | None:
        """
        Get a skill by ID, returning None if not found.

        Args:
            skill_id: The skill ID

        Returns:
            The skill or None
        """
        return self._skills.get(skill_id)

    def list_skills(self) -> list[Skill]:
        """
        List all registered skills.

        Returns:
            List of all skills
        """
        return list(self._skills.values())

    def list_skill_ids(self) -> list[str]:
        """
        List all registered skill IDs.

        Returns:
            List of skill IDs
        """
        return list(self._skills.keys())

    def find_by_keywords(self, keywords: list[str]) -> list[SkillMatch]:
        """
        Find skills by keyword match.

        Args:
            keywords: List of keywords to search for

        Returns:
            List of matching skills with scores
        """
        skill_scores: dict[str, float] = {}
        skill_reasons: dict[str, list[str]] = {}

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Exact keyword match
            if keyword_lower in self._keyword_index:
                for skill_id in self._keyword_index[keyword_lower]:
                    skill_scores[skill_id] = skill_scores.get(skill_id, 0) + 1.0
                    if skill_id not in skill_reasons:
                        skill_reasons[skill_id] = []
                    skill_reasons[skill_id].append(f"keyword: {keyword}")

            # Partial keyword match in skill name/description
            for skill in self._skills.values():
                if keyword_lower in skill.name.lower():
                    skill_scores[skill.id] = skill_scores.get(skill.id, 0) + 0.7
                    if skill.id not in skill_reasons:
                        skill_reasons[skill.id] = []
                    skill_reasons[skill.id].append(f"name contains: {keyword}")
                elif keyword_lower in skill.description.lower():
                    skill_scores[skill.id] = skill_scores.get(skill.id, 0) + 0.5
                    if skill.id not in skill_reasons:
                        skill_reasons[skill.id] = []
                    skill_reasons[skill.id].append(f"description contains: {keyword}")

        # Normalize scores and create matches
        max_score = max(skill_scores.values()) if skill_scores else 1.0
        matches = [
            SkillMatch(
                skill=self._skills[skill_id],
                score=score / max_score,
                match_reason="; ".join(skill_reasons[skill_id]),
            )
            for skill_id, score in skill_scores.items()
        ]

        # Sort by score descending
        matches.sort(key=lambda m: m.score, reverse=True)
        return matches

    def find_by_context(self, context: TaskContext) -> list[SkillMatch]:
        """
        Find skills by evaluating activation conditions against context.

        This is the primary method for JIT skill injection.

        Args:
            context: The current task context

        Returns:
            List of matching skills with scores
        """
        skill_scores: dict[str, float] = {}
        skill_reasons: dict[str, list[str]] = {}

        context_strings = context.all_context_strings()

        for skill in self._skills.values():
            total_score = 0.0
            reasons: list[str] = []

            # Evaluate activation conditions
            for condition in skill.activation_conditions:
                for ctx_str, ctx_type in context_strings:
                    if condition.context_type == ctx_type and condition.matches(ctx_str):
                        total_score += condition.priority
                        snippet = ctx_str[:50] + "..." if len(ctx_str) > 50 else ctx_str
                        reasons.append(f"{ctx_type.value} matched: {snippet}")

            # Also check keywords in task description
            for keyword in skill.keywords:
                if keyword.lower() in context.task_description.lower():
                    total_score += 0.5
                    reasons.append(f"keyword in task: {keyword}")

            if total_score > 0:
                skill_scores[skill.id] = total_score
                skill_reasons[skill.id] = reasons

        # Normalize and create matches
        max_score = max(skill_scores.values()) if skill_scores else 1.0
        matches = [
            SkillMatch(
                skill=self._skills[skill_id],
                score=min(score / max_score, 1.0),  # Cap at 1.0
                match_reason="; ".join(skill_reasons[skill_id][:3]),  # Top 3 reasons
            )
            for skill_id, score in skill_scores.items()
        ]

        matches.sort(key=lambda m: m.score, reverse=True)
        return matches

    def find_by_category(self, category: SkillCategory) -> list[Skill]:
        """
        Find skills by category.

        Args:
            category: The skill category

        Returns:
            List of skills in that category
        """
        if category not in self._category_index:
            return []
        return [self._skills[sid] for sid in self._category_index[category]]

    def register_composition(
        self, composition: SkillComposition, *, allow_overwrite: bool = False
    ) -> None:
        """
        Register a skill composition.

        Args:
            composition: The composition to register
            allow_overwrite: If True, allow overwriting existing compositions
        """
        if composition.id in self._compositions and not allow_overwrite:
            raise DuplicateSkillError(f"composition:{composition.id}")
        self._compositions[composition.id] = composition
        logger.debug(f"Registered composition: {composition.id}")

    def get_composition(self, composition_id: str) -> SkillComposition | None:
        """
        Get a composition by ID.

        Args:
            composition_id: The composition ID

        Returns:
            The composition or None
        """
        return self._compositions.get(composition_id)

    def list_compositions(self) -> list[SkillComposition]:
        """
        List all registered compositions.

        Returns:
            List of all compositions
        """
        return list(self._compositions.values())

    def resolve_dependencies(self, skill_id: str, depth: int = 3) -> list[str]:
        """
        Resolve all dependencies for a skill (transitive).

        Args:
            skill_id: The skill to resolve dependencies for
            depth: Maximum depth to traverse (prevents cycles)

        Returns:
            List of all dependency skill IDs (including the original)
        """
        if depth <= 0:
            return [skill_id]

        skill = self.get_skill_or_none(skill_id)
        if skill is None:
            return [skill_id]

        result = [skill_id]
        seen = {skill_id}

        for dep_id in skill.dependencies:
            if dep_id not in seen:
                seen.add(dep_id)
                result.append(dep_id)  # Add the dependency itself
                # Then recursively add its dependencies
                for transitive_dep in self.resolve_dependencies(dep_id, depth - 1):
                    if transitive_dep not in seen:
                        seen.add(transitive_dep)
                        result.append(transitive_dep)

        return result

    def stats(self) -> dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary of statistics
        """
        category_counts = {cat.value: len(skills) for cat, skills in self._category_index.items()}
        return {
            "total_skills": len(self._skills),
            "total_compositions": len(self._compositions),
            "total_keywords": len(self._keyword_index),
            "skills_by_category": category_counts,
        }


# Global registry instance
_registry: SkillRegistry | None = None


def get_skill_registry() -> SkillRegistry:
    """Get the global skill registry instance."""
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry


def set_skill_registry(registry: SkillRegistry) -> None:
    """Set the global skill registry instance (for testing)."""
    global _registry
    _registry = registry


def reset_skill_registry() -> None:
    """Reset the global skill registry (for testing)."""
    global _registry
    _registry = None


__all__ = [
    "DuplicateSkillError",
    "SkillMatch",
    "SkillNotFoundError",
    "SkillRegistry",
    "get_skill_registry",
    "reset_skill_registry",
    "set_skill_registry",
]
