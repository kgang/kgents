"""
Activation Condition Engine: Evaluates Skills Against Context

The ActivationConditionEngine computes activation scores for skills
based on the current task context, using weighted condition matching
and stigmergic learning from past usage.

Philosophy:
    "Context-aware activation based on task patterns."
    "Learn from what worked, forget what didn't."

AGENTESE: self.skill.activate
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .registry import SkillRegistry, get_skill_registry
from .types import (
    ActivationCondition,
    ContextType,
    InjectionResult,
    Skill,
    SkillActivation,
    SkillComposition,
    TaskContext,
)

if TYPE_CHECKING:
    from .stigmergic_memory import StigmergicMemory

logger = logging.getLogger(__name__)


@dataclass
class ActivationConfig:
    """
    Configuration for the activation engine.

    Teaching:
        gotcha: `max_skills` prevents context overload.
                More than 3-4 skills at once dilutes attention.
                (Evidence: test_activation_engine.py::test_max_skills_limit)

        gotcha: `min_score` filters out weak matches.
                Set too low: noise. Set too high: miss relevant skills.
                0.3 is a good default for most use cases.
                (Evidence: test_activation_engine.py::test_min_score_threshold)
    """

    max_skills: int = 3  # Maximum skills to activate
    min_score: float = 0.3  # Minimum score to consider
    include_dependencies: bool = True  # Include dependency skills
    boost_from_memory: float = 0.2  # Boost for skills with good history
    penalize_from_memory: float = 0.3  # Penalty for skills with bad history
    prefer_compositions: bool = True  # Prefer pre-defined compositions


@dataclass
class ActivationScore:
    """
    Detailed activation score for a skill.

    Contains the breakdown of how the score was computed.
    """

    skill_id: str
    base_score: float  # Score from condition matching
    memory_adjustment: float  # Adjustment from stigmergic memory
    dependency_boost: float  # Boost from being a dependency
    final_score: float  # Combined final score
    matched_conditions: list[ActivationCondition] = field(default_factory=list)
    match_snippets: list[str] = field(default_factory=list)


class ActivationConditionEngine:
    """
    Evaluates skills against context to determine activation.

    The engine combines:
    1. Pattern matching against activation conditions
    2. Stigmergic memory (what worked before)
    3. Dependency resolution
    4. Composition detection

    Teaching:
        gotcha: Call `select_skills` for JIT injection, not `evaluate`.
                `evaluate` returns ALL matches; `select_skills` applies
                limits and compositions.
                (Evidence: test_activation_engine.py::test_select_vs_evaluate)

        gotcha: Pass a StigmergicMemory instance to enable learning.
                Without memory, scores are stateless.
                (Evidence: test_activation_engine.py::test_with_memory)
    """

    def __init__(
        self,
        registry: SkillRegistry | None = None,
        memory: "StigmergicMemory | None" = None,
        config: ActivationConfig | None = None,
    ) -> None:
        """
        Initialize the activation engine.

        Args:
            registry: Skill registry (uses global if not provided)
            memory: Stigmergic memory for learning
            config: Activation configuration
        """
        self._registry = registry or get_skill_registry()
        self._memory = memory
        self._config = config or ActivationConfig()

    @property
    def config(self) -> ActivationConfig:
        """Get the current configuration."""
        return self._config

    def evaluate(self, skill: Skill, context: TaskContext) -> ActivationScore:
        """
        Evaluate a single skill against context.

        Args:
            skill: The skill to evaluate
            context: The task context

        Returns:
            Detailed activation score
        """
        base_score = 0.0
        matched_conditions: list[ActivationCondition] = []
        match_snippets: list[str] = []

        context_strings = context.all_context_strings()

        # Evaluate activation conditions
        for condition in skill.activation_conditions:
            for ctx_str, ctx_type in context_strings:
                if condition.context_type == ctx_type and condition.matches(ctx_str):
                    base_score += condition.priority
                    matched_conditions.append(condition)
                    snippet = ctx_str[:50] + "..." if len(ctx_str) > 50 else ctx_str
                    match_snippets.append(snippet)

        # Check keywords in task description
        for keyword in skill.keywords:
            if keyword.lower() in context.task_description.lower():
                base_score += 0.5
                match_snippets.append(f"keyword: {keyword}")

        # Normalize base score (cap at 1.0)
        base_score = min(base_score, 1.0)

        # Apply memory adjustments
        memory_adjustment = 0.0
        if self._memory is not None:
            success_rate = self._memory.get_success_rate(skill.id)
            if success_rate is not None:
                if success_rate > 0.7:
                    memory_adjustment = self._config.boost_from_memory
                elif success_rate < 0.3:
                    memory_adjustment = -self._config.penalize_from_memory

        final_score = max(0.0, min(1.0, base_score + memory_adjustment))

        return ActivationScore(
            skill_id=skill.id,
            base_score=base_score,
            memory_adjustment=memory_adjustment,
            dependency_boost=0.0,  # Set by caller if needed
            final_score=final_score,
            matched_conditions=matched_conditions,
            match_snippets=match_snippets,
        )

    def evaluate_all(self, context: TaskContext) -> list[ActivationScore]:
        """
        Evaluate all skills against context.

        Args:
            context: The task context

        Returns:
            List of activation scores, sorted by final_score descending
        """
        scores = [self.evaluate(skill, context) for skill in self._registry.list_skills()]

        # Filter by minimum score
        scores = [s for s in scores if s.final_score >= self._config.min_score]

        # Sort by score descending
        scores.sort(key=lambda s: s.final_score, reverse=True)

        return scores

    def select_skills(self, context: TaskContext) -> list[SkillActivation]:
        """
        Select the most relevant skills for injection.

        This is the primary method for JIT skill injection.
        Applies limits, compositions, and dependencies.

        Args:
            context: The task context

        Returns:
            List of skill activations (limited by config.max_skills)
        """
        # First, check for composition matches
        if self._config.prefer_compositions:
            composition = self._detect_composition(context)
            if composition:
                return self._resolve_composition(composition, context)

        # Evaluate all skills
        scores = self.evaluate_all(context)

        # Take top skills up to max_skills
        top_scores = scores[: self._config.max_skills]

        # Resolve dependencies if enabled
        if self._config.include_dependencies:
            top_scores = self._include_dependencies(top_scores, context)

        # Convert to activations
        activations = []
        for score in top_scores:
            skill = self._registry.get_skill_or_none(score.skill_id)
            if skill:
                activations.append(
                    SkillActivation(
                        skill=skill,
                        score=score.final_score,
                        matched_conditions=tuple(score.matched_conditions),
                        context_snippet="; ".join(score.match_snippets[:3]),
                    )
                )

        return activations

    def _detect_composition(self, context: TaskContext) -> SkillComposition | None:
        """
        Detect if context matches a pre-defined composition.

        Args:
            context: The task context

        Returns:
            Matching composition or None
        """
        task_lower = context.task_description.lower()

        # Check for composition-triggering patterns
        composition_patterns = [
            ("crown jewel", "new-crown-jewel"),
            ("agentese node", "new-agentese-node"),
            ("@node", "new-agentese-node"),
            ("new agent", "new-agent"),
            ("polynomial agent", "new-agent"),
            ("event flow", "debug-event-flow"),
            ("event not propagating", "debug-event-flow"),
        ]

        for pattern, comp_id in composition_patterns:
            if pattern in task_lower:
                composition = self._registry.get_composition(comp_id)
                if composition:
                    logger.debug(f"Detected composition: {comp_id} from pattern: {pattern}")
                    return composition

        return None

    def _resolve_composition(
        self, composition: SkillComposition, context: TaskContext
    ) -> list[SkillActivation]:
        """
        Resolve a composition into skill activations.

        Args:
            composition: The composition to resolve
            context: The task context

        Returns:
            List of skill activations
        """
        activations = []

        for i, skill_id in enumerate(composition.skill_ids):
            skill = self._registry.get_skill_or_none(skill_id)
            if skill:
                # Primary skill gets higher score
                score = 1.0 - (i * 0.1)  # 1.0, 0.9, 0.8, ...
                activations.append(
                    SkillActivation(
                        skill=skill,
                        score=max(0.5, score),
                        matched_conditions=(),
                        context_snippet=f"composition: {composition.name}",
                    )
                )

        return activations

    def _include_dependencies(
        self, scores: list[ActivationScore], context: TaskContext
    ) -> list[ActivationScore]:
        """
        Include dependency skills in the activation list.

        Args:
            scores: Current activation scores
            context: The task context

        Returns:
            Extended list with dependencies included
        """
        seen_ids = {s.skill_id for s in scores}
        result = list(scores)

        for score in scores:
            skill = self._registry.get_skill_or_none(score.skill_id)
            if skill:
                for dep_id in skill.dependencies:
                    if dep_id not in seen_ids:
                        dep_skill = self._registry.get_skill_or_none(dep_id)
                        if dep_skill:
                            # Evaluate dependency in context
                            dep_score = self.evaluate(dep_skill, context)
                            dep_score.dependency_boost = 0.2
                            dep_score.final_score = min(
                                1.0, dep_score.final_score + dep_score.dependency_boost
                            )
                            result.append(dep_score)
                            seen_ids.add(dep_id)

        return result


# Global engine instance
_engine: ActivationConditionEngine | None = None


def get_activation_engine() -> ActivationConditionEngine:
    """Get the global activation engine instance."""
    global _engine
    if _engine is None:
        _engine = ActivationConditionEngine()
    return _engine


def set_activation_engine(engine: ActivationConditionEngine) -> None:
    """Set the global activation engine instance (for testing)."""
    global _engine
    _engine = engine


def reset_activation_engine() -> None:
    """Reset the global activation engine (for testing)."""
    global _engine
    _engine = None


__all__ = [
    "ActivationConditionEngine",
    "ActivationConfig",
    "ActivationScore",
    "get_activation_engine",
    "reset_activation_engine",
    "set_activation_engine",
]
