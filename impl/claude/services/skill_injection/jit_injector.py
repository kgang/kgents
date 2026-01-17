"""
JIT Skill Injector: Runtime Skill Content Injection

The JITInjector reads skill files and injects their content
into the context based on activation decisions.

Philosophy:
    "Skills surface exactly when needed, not before."
    "Inject the minimum necessary for the task."
    "Content adapts to context."

AGENTESE: self.skill.inject
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .activation_engine import ActivationConditionEngine, get_activation_engine
from .registry import SkillRegistry, get_skill_registry
from .stigmergic_memory import StigmergicMemory, compute_context_hash, get_stigmergic_memory
from .types import (
    COMMON_COMPOSITIONS,
    InjectionResult,
    Skill,
    SkillActivation,
    SkillComposition,
    SkillUsageTrace,
    TaskContext,
    UsageOutcome,
)

logger = logging.getLogger(__name__)


@dataclass
class InjectionConfig:
    """
    Configuration for the JIT injector.

    Teaching:
        gotcha: `max_content_chars` prevents context overload.
                Skills are truncated at section boundaries.
                (Evidence: test_jit_injector.py::test_content_truncation)

        gotcha: `include_gotchas` extracts just the Teaching: sections
                when full content is too long. Better to have gotchas than nothing.
                (Evidence: test_jit_injector.py::test_gotcha_extraction)
    """

    max_content_chars: int = 15000  # Maximum total content characters
    max_skills: int = 4  # Maximum skills to inject
    include_gotchas: bool = True  # Extract gotchas when truncating
    include_metadata: bool = True  # Include skill metadata header
    base_path: Path | None = None  # Base path for skill files


class SkillContentReader:
    """
    Reads and processes skill file content.

    Handles markdown parsing, section extraction, and truncation.
    """

    def __init__(self, base_path: Path | None = None) -> None:
        """
        Initialize the content reader.

        Args:
            base_path: Base path for resolving relative skill paths
        """
        self._base_path = base_path or Path.cwd()

    def read_skill(self, skill: Skill) -> str | None:
        """
        Read the full content of a skill file.

        Args:
            skill: The skill to read

        Returns:
            File content or None if not found
        """
        skill_path = self._resolve_path(skill.path)

        if not skill_path.exists():
            logger.warning(f"Skill file not found: {skill_path}")
            return None

        try:
            return skill_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.error(f"Error reading skill {skill.id}: {e}")
            return None

    def read_skill_summary(self, skill: Skill, max_chars: int = 2000) -> str:
        """
        Read a summarized version of a skill.

        Extracts overview, quick reference, and gotchas.

        Args:
            skill: The skill to read
            max_chars: Maximum characters

        Returns:
            Summarized content
        """
        content = self.read_skill(skill)
        if content is None:
            return f"# {skill.name}\n\n[Content not available]"

        return self._extract_summary(content, skill, max_chars)

    def read_gotchas(self, skill: Skill) -> list[str]:
        """
        Extract just the gotchas from a skill.

        Args:
            skill: The skill to read

        Returns:
            List of gotcha strings
        """
        content = self.read_skill(skill)
        if content is None:
            return []

        return self._extract_gotchas(content)

    def _resolve_path(self, skill_path: str) -> Path:
        """Resolve a skill path relative to base_path."""
        path = Path(skill_path)
        if path.is_absolute():
            return path
        return self._base_path / path

    def _extract_summary(self, content: str, skill: Skill, max_chars: int) -> str:
        """Extract a summary from content."""
        lines = content.split("\n")
        summary_lines: list[str] = []
        char_count = 0
        in_code_block = False
        current_section = ""

        # Sections to prioritize
        priority_sections = {"overview", "quick reference", "the core", "example"}

        for line in lines:
            # Track code blocks
            if line.strip().startswith("```"):
                in_code_block = not in_code_block

            # Track section headers
            if line.startswith("## "):
                current_section = line.lower()

            # Always include title and first paragraph
            if char_count < 500:
                summary_lines.append(line)
                char_count += len(line) + 1
                continue

            # Prioritize certain sections
            if any(s in current_section for s in priority_sections):
                if char_count + len(line) < max_chars:
                    summary_lines.append(line)
                    char_count += len(line) + 1
                else:
                    break

            # Include gotchas
            if "gotcha:" in line.lower() or "teaching:" in line.lower():
                if char_count + len(line) < max_chars:
                    summary_lines.append(line)
                    char_count += len(line) + 1

        return "\n".join(summary_lines)

    def _extract_gotchas(self, content: str) -> list[str]:
        """Extract gotcha lines from content."""
        gotchas: list[str] = []
        lines = content.split("\n")
        in_gotcha = False
        current_gotcha: list[str] = []

        for line in lines:
            if "gotcha:" in line.lower():
                in_gotcha = True
                current_gotcha = [line.strip()]
            elif in_gotcha:
                if line.strip().startswith("-") or line.strip().startswith("("):
                    current_gotcha.append(line.strip())
                elif line.strip() and not line.startswith(" "):
                    # End of gotcha
                    gotchas.append(" ".join(current_gotcha))
                    in_gotcha = False
                    current_gotcha = []
                elif line.strip():
                    current_gotcha.append(line.strip())

        # Don't forget last gotcha
        if current_gotcha:
            gotchas.append(" ".join(current_gotcha))

        return gotchas


class JITInjector:
    """
    Runtime skill content injection.

    Coordinates between the activation engine and content reader
    to inject relevant skills into the context.

    Teaching:
        gotcha: Call `inject_for_task` with a task description.
                Call `inject_skills` if you already have activations.
                (Evidence: test_jit_injector.py::test_inject_methods)

        gotcha: The injector tracks injection for stigmergic learning.
                Call `record_outcome` after the task completes.
                (Evidence: test_jit_injector.py::test_outcome_tracking)
    """

    def __init__(
        self,
        registry: SkillRegistry | None = None,
        engine: ActivationConditionEngine | None = None,
        memory: StigmergicMemory | None = None,
        config: InjectionConfig | None = None,
    ) -> None:
        """
        Initialize the JIT injector.

        Args:
            registry: Skill registry
            engine: Activation engine
            memory: Stigmergic memory
            config: Injection configuration
        """
        self._registry = registry or get_skill_registry()
        self._engine = engine or get_activation_engine()
        self._memory = memory or get_stigmergic_memory()
        self._config = config or InjectionConfig()
        self._reader = SkillContentReader(self._config.base_path)

        # Track current injection for outcome recording
        self._current_context_hash: str | None = None
        self._current_activations: list[SkillActivation] = []

    @property
    def config(self) -> InjectionConfig:
        """Get the current configuration."""
        return self._config

    async def inject_for_task(self, task: str, **context_kwargs: Any) -> InjectionResult:
        """
        Inject skills for a task description.

        This is the primary method for JIT skill injection.

        Args:
            task: The task description
            **context_kwargs: Additional context (active_files, error_messages, etc.)

        Returns:
            Injection result with content and metadata
        """
        # Build context
        context = TaskContext(
            task_description=task,
            active_files=tuple(context_kwargs.get("active_files", [])),
            error_messages=tuple(context_kwargs.get("error_messages", [])),
            recent_commands=tuple(context_kwargs.get("recent_commands", [])),
            user_keywords=tuple(context_kwargs.get("user_keywords", [])),
            session_id=context_kwargs.get("session_id", ""),
        )

        # Get activations
        activations = self._engine.select_skills(context)

        # Limit activations
        activations = activations[: self._config.max_skills]

        # Track for outcome recording
        self._current_context_hash = compute_context_hash(task, context.active_files)
        self._current_activations = activations

        return await self.inject_skills(activations)

    async def inject_skills(self, activations: list[SkillActivation]) -> InjectionResult:
        """
        Inject content for specific skill activations.

        Args:
            activations: List of skill activations

        Returns:
            Injection result
        """
        if not activations:
            return InjectionResult(
                content="",
                activations=[],
                composition=None,
                total_read_time_minutes=0,
            )

        # Check if activations form a composition
        composition = self._detect_composition(activations)

        # Build content
        content_parts: list[str] = []
        total_chars = 0
        total_read_time = 0

        for activation in activations:
            skill = activation.skill

            # Calculate remaining budget
            remaining = self._config.max_content_chars - total_chars

            if remaining < 500:
                # Not enough space, add gotchas only
                if self._config.include_gotchas:
                    gotchas = self._reader.read_gotchas(skill)
                    if gotchas:
                        gotcha_section = self._format_gotcha_section(skill, gotchas)
                        content_parts.append(gotcha_section)
                        total_chars += len(gotcha_section)
                break

            # Read skill content
            skill_content: str | None = None
            if remaining < 2000:
                # Limited space, get summary
                skill_content = self._reader.read_skill_summary(skill, remaining - 100)
            else:
                skill_content = self._reader.read_skill(skill)
                if skill_content and len(skill_content) > remaining:
                    skill_content = self._reader.read_skill_summary(skill, remaining - 100)

            if skill_content:
                # Add metadata header if configured
                if self._config.include_metadata:
                    header = self._format_skill_header(skill, activation)
                    content_parts.append(header + skill_content)
                    total_chars += len(header) + len(skill_content)
                else:
                    content_parts.append(skill_content)
                    total_chars += len(skill_content)

                total_read_time += skill.estimated_read_time_minutes

        # Join content with separators
        content = "\n\n---\n\n".join(content_parts)

        return InjectionResult(
            content=content,
            activations=activations,
            composition=composition,
            total_read_time_minutes=total_read_time,
        )

    async def inject_gotchas_only(self, task: str) -> str:
        """
        Inject just the gotchas for a task (lightweight injection).

        Args:
            task: The task description

        Returns:
            Gotchas content
        """
        context = TaskContext(task_description=task)
        activations = self._engine.select_skills(context)

        gotcha_parts: list[str] = []
        for activation in activations[: self._config.max_skills]:
            gotchas = self._reader.read_gotchas(activation.skill)
            if gotchas:
                gotcha_parts.append(self._format_gotcha_section(activation.skill, gotchas))

        return "\n\n".join(gotcha_parts)

    def record_outcome(
        self,
        outcome: UsageOutcome,
        feedback: str = "",
        duration_seconds: float = 0.0,
    ) -> None:
        """
        Record the outcome of the current injection.

        Call this after the task completes to enable learning.

        Args:
            outcome: The outcome of using the injected skills
            feedback: Optional user feedback
            duration_seconds: How long the skills were active
        """
        if not self._current_activations or not self._current_context_hash:
            logger.debug("No current injection to record outcome for")
            return

        from datetime import UTC, datetime

        for activation in self._current_activations:
            trace = SkillUsageTrace(
                skill_id=activation.skill.id,
                context_hash=self._current_context_hash,
                context_summary=activation.context_snippet,
                outcome=outcome,
                timestamp=datetime.now(UTC),
                duration_seconds=duration_seconds,
                feedback=feedback,
            )
            self._memory.record_usage(trace)

        # Record composition if multiple skills
        if len(self._current_activations) > 1:
            skill_ids = tuple(a.skill.id for a in self._current_activations)
            self._memory.record_composition_usage(
                skill_ids=skill_ids,
                context_hash=self._current_context_hash,
                success=outcome == UsageOutcome.SUCCESS,
            )

        logger.debug(
            f"Recorded outcome: {outcome.value} for {len(self._current_activations)} skills"
        )

    def _detect_composition(self, activations: list[SkillActivation]) -> SkillComposition | None:
        """Detect if activations match a known composition."""
        if len(activations) < 2:
            return None

        skill_ids = {a.skill.id for a in activations}

        for composition in COMMON_COMPOSITIONS.values():
            comp_ids = set(composition.skill_ids)
            # Check if activations are a subset of composition
            if skill_ids <= comp_ids or comp_ids <= skill_ids:
                return composition

        return None

    def _format_skill_header(self, skill: Skill, activation: SkillActivation) -> str:
        """Format a skill header with metadata."""
        lines = [
            f"# Skill: {skill.name}",
            f"*ID: {skill.id} | Category: {skill.category.value} | "
            f"Score: {activation.score:.2f} | Read time: ~{skill.estimated_read_time_minutes}min*",
            "",
        ]
        if activation.context_snippet:
            lines.append(f"*Activated by: {activation.context_snippet}*")
            lines.append("")

        return "\n".join(lines)

    def _format_gotcha_section(self, skill: Skill, gotchas: list[str]) -> str:
        """Format a gotchas-only section."""
        lines = [
            f"## Gotchas: {skill.name}",
            "",
        ]
        for gotcha in gotchas[:5]:  # Max 5 gotchas
            lines.append(f"- {gotcha}")

        return "\n".join(lines)


# Global injector instance
_injector: JITInjector | None = None


def get_jit_injector() -> JITInjector:
    """Get the global JIT injector instance."""
    global _injector
    if _injector is None:
        _injector = JITInjector()
    return _injector


def set_jit_injector(injector: JITInjector) -> None:
    """Set the global JIT injector instance (for testing)."""
    global _injector
    _injector = injector


def reset_jit_injector() -> None:
    """Reset the global JIT injector (for testing)."""
    global _injector
    _injector = None


__all__ = [
    "InjectionConfig",
    "JITInjector",
    "SkillContentReader",
    "get_jit_injector",
    "reset_jit_injector",
    "set_jit_injector",
]
