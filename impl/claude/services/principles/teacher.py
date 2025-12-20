"""
Principle Teacher: Interactive principle teaching mode.

Provides teaching content at varying depths:
- overview: High-level summary
- examples: Concrete examples and case studies
- exercises: Practice prompts and challenges

See: spec/principles/node.md for the teach aspect specification.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from .types import (
    PRINCIPLE_NAMES,
    PRINCIPLE_NUMBERS,
    THE_SEVEN_PRINCIPLES,
    TeachingContent,
)

if TYPE_CHECKING:
    from .loader import PrincipleLoader

# === Teaching Materials ===

PRINCIPLE_EXAMPLES: dict[int, tuple[str, ...]] = {
    1: (  # Tasteful
        "K-gent: serves the clear purpose of personalizing agent outputs",
        "D-gent: does one thing well - semantic storage routing",
        "Anti-example: A 'universal agent' that tries to handle everything",
    ),
    2: (  # Curated
        "The kgents taxonomy: 26 letters, each with justified purpose",
        "Removing deprecated agents rather than keeping 'just in case'",
        "Anti-example: An 'awesome-agents' list with 500 untested entries",
    ),
    3: (  # Ethical
        "Consent tracking in Park's crisis scenarios",
        "Transparent confidence levels in all LLM outputs",
        "Anti-example: An agent claiming 100% certainty on predictions",
    ),
    4: (  # Joy-Inducing
        "K-gent's personality space navigation",
        "Gardener's seasonal metaphor for project lifecycle",
        "Anti-example: A blank JSON response with no formatting",
    ),
    5: (  # Composable
        "Polynomial agents with the >> operator",
        "Single output per invocation for pipeline composition",
        "Anti-example: An agent that returns an array of 10 results",
    ),
    6: (  # Heterarchical
        "Flux agents: can run autonomously or be composed",
        "Town citizens: contextual leadership based on task",
        "Anti-example: Fixed orchestrator/worker hierarchy",
    ),
    7: (  # Generative
        "AGENTESE spec generates implementation via JIT",
        "AD-009 Metaphysical Fullstack: spec < impl (compression)",
        "Anti-example: A spec that just describes existing code",
    ),
}

PRINCIPLE_EXERCISES: dict[int, tuple[str, ...]] = {
    1: (  # Tasteful
        "Take an existing agent and ask: 'Why does this need to exist?'",
        "Identify one feature that could be removed without losing purpose",
        "Write a one-sentence justification for a proposed new agent",
    ),
    2: (  # Curated
        "Review a list of 10 agents - which 3 should be kept?",
        "Find two agents that do similar things - should they merge?",
        "Propose removing one legacy component and defend the decision",
    ),
    3: (  # Ethical
        "Audit an agent for hidden data collection",
        "Add uncertainty markers to an agent's outputs",
        "Design a consent flow for a sensitive operation",
    ),
    4: (  # Joy-Inducing
        "Add a personality quirk to a bland agent response",
        "Design a delightful error message",
        "Create a surprise 'easter egg' interaction",
    ),
    5: (  # Composable
        "Compose three agents using the >> operator",
        "Refactor an array-returning agent to single output",
        "Write a test verifying identity law: Id >> f == f",
    ),
    6: (  # Heterarchical
        "Design an agent that can both lead and follow",
        "Remove a fixed hierarchy from an agent system",
        "Implement dynamic role switching based on context",
    ),
    7: (  # Generative
        "Write a spec smaller than its implementation",
        "Delete an implementation and regenerate from spec",
        "Measure spec:impl compression ratio for a component",
    ),
}


@dataclass
class PrincipleTeacher:
    """
    Provides interactive teaching content for principles.

    The teacher offers three depth levels:
    - overview: The principle's essence and core questions
    - examples: Concrete examples from kgents
    - exercises: Practice prompts for learning

    Example:
        teacher = PrincipleTeacher(loader)
        content = await teacher.teach(principle=5, depth="examples")
        for example in content.examples:
            print(f"- {example}")
    """

    loader: "PrincipleLoader"

    def _resolve_principle(self, principle: int | str | None) -> int | None:
        """
        Resolve principle from number or name.

        Args:
            principle: Principle number (1-7), name, or None for all

        Returns:
            Principle number or None for all
        """
        if principle is None:
            return None

        if isinstance(principle, int):
            if 1 <= principle <= 7:
                return principle
            return None

        # Try to match by name
        name_lower = principle.lower().strip()
        if name_lower in PRINCIPLE_NAMES:
            return PRINCIPLE_NAMES[name_lower]

        # Try partial match
        for name, num in PRINCIPLE_NAMES.items():
            if name_lower in name or name in name_lower:
                return num

        return None

    async def teach(
        self,
        principle: int | str | None = None,
        depth: Literal["overview", "examples", "exercises"] = "overview",
    ) -> TeachingContent:
        """
        Get teaching content for a principle.

        Args:
            principle: Principle number/name, or None for overview of all
            depth: Level of detail

        Returns:
            TeachingContent with appropriate material
        """
        resolved = self._resolve_principle(principle)

        if resolved is None:
            # All principles overview
            return await self._teach_all(depth)

        return await self._teach_one(resolved, depth)

    async def _teach_all(
        self,
        depth: Literal["overview", "examples", "exercises"],
    ) -> TeachingContent:
        """Teach all seven principles."""
        content_parts: list[str] = []

        content_parts.append("# The Seven Principles\n")

        for p in THE_SEVEN_PRINCIPLES:
            content_parts.append(f"\n## {p.number}. {p.name}")
            content_parts.append(f"> {p.tagline}\n")
            content_parts.append(f"**Question**: {p.question}\n")

            if depth in ("examples", "exercises"):
                examples = PRINCIPLE_EXAMPLES.get(p.number, ())
                if examples:
                    content_parts.append("**Examples**:")
                    for ex in examples:
                        content_parts.append(f"  - {ex}")

            if depth == "exercises":
                exercises = PRINCIPLE_EXERCISES.get(p.number, ())
                if exercises:
                    content_parts.append("**Exercises**:")
                    for ex in exercises:
                        content_parts.append(f"  - {ex}")

        # Collect all examples and exercises for metadata
        all_examples: list[str] = []
        all_exercises: list[str] = []

        if depth in ("examples", "exercises"):
            for examples in PRINCIPLE_EXAMPLES.values():
                all_examples.extend(examples)

        if depth == "exercises":
            for exercises in PRINCIPLE_EXERCISES.values():
                all_exercises.extend(exercises)

        return TeachingContent(
            principle=None,
            principle_name=None,
            depth=depth,
            content="\n".join(content_parts),
            examples=tuple(all_examples) if depth in ("examples", "exercises") else (),
            exercises=tuple(all_exercises) if depth == "exercises" else (),
        )

    async def _teach_one(
        self,
        principle: int,
        depth: Literal["overview", "examples", "exercises"],
    ) -> TeachingContent:
        """Teach a single principle."""
        p = THE_SEVEN_PRINCIPLES[principle - 1]

        content_parts: list[str] = []
        content_parts.append(f"# {p.number}. {p.name}")
        content_parts.append(f"\n> {p.tagline}\n")

        # Load full content from file
        constitution = await self.loader.load("CONSTITUTION.md")

        # Extract the section for this principle
        section_content = self._extract_principle_section(constitution, principle)
        if section_content:
            content_parts.append(section_content)
        else:
            content_parts.append(f"**Question**: {p.question}\n")
            if p.anti_patterns:
                content_parts.append("\n**Anti-patterns**:")
                for ap in p.anti_patterns:
                    content_parts.append(f"  - {ap}")

        examples = PRINCIPLE_EXAMPLES.get(principle, ())
        exercises = PRINCIPLE_EXERCISES.get(principle, ())

        if depth in ("examples", "exercises") and examples:
            content_parts.append("\n## Examples")
            for ex in examples:
                content_parts.append(f"- {ex}")

        if depth == "exercises" and exercises:
            content_parts.append("\n## Exercises")
            for ex in exercises:
                content_parts.append(f"- {ex}")

        return TeachingContent(
            principle=principle,
            principle_name=p.name,
            depth=depth,
            content="\n".join(content_parts),
            examples=examples if depth in ("examples", "exercises") else (),
            exercises=exercises if depth == "exercises" else (),
        )

    def _extract_principle_section(
        self,
        constitution: str,
        principle: int,
    ) -> str | None:
        """Extract a principle's section from the constitution."""
        p = THE_SEVEN_PRINCIPLES[principle - 1]
        heading = f"## {principle}. {p.name}"

        lines = constitution.split("\n")
        start_idx = None
        end_idx = None

        for i, line in enumerate(lines):
            if heading in line:
                start_idx = i
            elif start_idx is not None and line.startswith("## "):
                end_idx = i
                break

        if start_idx is None:
            return None

        section_lines = lines[start_idx:end_idx] if end_idx else lines[start_idx:]
        return "\n".join(section_lines)

    async def quiz(self, principle: int | None = None) -> dict[str, str]:
        """
        Generate a quiz question for a principle.

        Args:
            principle: Principle number, or None for random

        Returns:
            Dict with question, options, and answer
        """
        import random

        if principle is None:
            principle = random.randint(1, 7)

        p = THE_SEVEN_PRINCIPLES[principle - 1]

        # Generate a question about anti-patterns
        if p.anti_patterns:
            anti = random.choice(p.anti_patterns)
            return {
                "question": f"Which principle does this anti-pattern violate: '{anti}'?",
                "options": ", ".join(PRINCIPLE_NUMBERS.values()),
                "answer": p.name,
                "principle": str(principle),
            }

        return {
            "question": p.question,
            "options": "Yes / No",
            "answer": "Depends on context",
            "principle": str(principle),
        }


# === Factory Function ===


def create_principle_teacher(loader: "PrincipleLoader") -> PrincipleTeacher:
    """
    Create a PrincipleTeacher instance.

    Args:
        loader: PrincipleLoader for file access

    Returns:
        Configured PrincipleTeacher
    """
    return PrincipleTeacher(loader=loader)


# === Exports ===

__all__ = [
    "PrincipleTeacher",
    "create_principle_teacher",
    "PRINCIPLE_EXAMPLES",
    "PRINCIPLE_EXERCISES",
]
