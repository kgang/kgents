"""
Composable morphisms for Robin agent.

These are reusable components that can be composed with other agents:
- NarrativeSynthesizer: ComponentData → str
- NextQuestionGenerator: QuestionData → list[str]
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from agents.h import DialecticOutput
from agents.k import PersonaResponse
from bootstrap.types import Agent
from runtime.base import Runtime

from .hypothesis import HypothesisOutput


@dataclass
class SynthesisInput:
    """Input for narrative synthesis agent."""

    domain: str
    query: str
    persona: PersonaResponse
    kgent: Any  # DialogueOutput - avoiding import to prevent circular dependency
    hypotheses: HypothesisOutput
    dialectic: Optional[DialecticOutput] = None


class NarrativeSynthesizer(Agent[SynthesisInput, str]):
    """
    Morphism: SynthesisInput → str

    Creates coherent narrative from component outputs.
    Reusable for any agent that combines persona + hypotheses + dialectic.
    """

    @property
    def name(self) -> str:
        return "NarrativeSynthesizer"

    async def invoke(
        self, input: SynthesisInput, runtime: Optional[Runtime] = None
    ) -> str:
        """Synthesize narrative from components."""
        parts = []

        # Opening based on persona
        if input.persona.patterns:
            parts.append(
                f"Given your tendency to {input.persona.patterns[0].lower()}, "
                f"let's approach {input.domain} through that lens."
            )

        # Hypothesis summary
        if input.hypotheses.hypotheses:
            top_hyp = input.hypotheses.hypotheses[0]
            parts.append(
                f"The most promising hypothesis ({top_hyp.confidence:.0%} confidence): "
                f"{top_hyp.statement}"
            )
            if len(input.hypotheses.hypotheses) > 1:
                parts.append(
                    f"Alternative view: {input.hypotheses.hypotheses[1].statement}"
                )

        # Dialectic insight
        if input.dialectic:
            if input.dialectic.productive_tension:
                parts.append(
                    "These views are in productive tension—don't rush to resolve them."
                )
            elif input.dialectic.synthesis:
                parts.append(f"Synthesis emerges: {input.dialectic.synthesis}")

        # K-gent reflection integration
        if (
            hasattr(input.kgent, "referenced_patterns")
            and input.kgent.referenced_patterns
        ):
            parts.append(
                f"This connects to your pattern of {input.kgent.referenced_patterns[0]}."
            )

        return " ".join(parts) if parts else "Further exploration needed."


@dataclass
class QuestionInput:
    """Input for next question generator."""

    hypotheses: HypothesisOutput
    dialectic: Optional[DialecticOutput] = None


class NextQuestionGenerator(Agent[QuestionInput, list[str]]):
    """
    Morphism: QuestionInput → list[str]

    Generates next exploration questions from hypotheses and dialectic.
    Reusable for any agent that needs to suggest follow-up queries.
    """

    @property
    def name(self) -> str:
        return "NextQuestionGenerator"

    async def invoke(
        self, input: QuestionInput, runtime: Optional[Runtime] = None
    ) -> list[str]:
        """Generate questions to continue the inquiry."""
        questions = []

        # From suggested tests
        for test in input.hypotheses.suggested_tests[:2]:
            questions.append(f"How might we test: {test}?")

        # From falsification criteria
        if input.hypotheses.hypotheses:
            for f in input.hypotheses.hypotheses[0].falsifiable_by[:1]:
                questions.append(f"What would it mean if: {f}?")

        # From dialectic tension
        if input.dialectic and input.dialectic.productive_tension:
            questions.append(
                "What conditions would resolve this tension vs. reveal it as fundamental?"
            )

        return questions[:4]  # Limit to 4 questions
