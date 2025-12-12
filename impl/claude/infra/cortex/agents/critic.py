"""
Critic Agent - concept.refine and self.judgment.critique path handler.

Maps critique-related AGENTESE paths to LLM-backed dialectical refinement.
Implements the "critic" archetype for self-improvement.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from runtime.base import AgentContext, LLMAgent


@dataclass
class CriticInput:
    """Input for critic agent."""

    statement: str
    context: str = ""  # Optional context
    mode: str = "dialectical"  # dialectical, constructive, or socratic


@dataclass
class CriticOutput:
    """Output from critic agent."""

    original: str
    critique: str
    refined: str
    confidence: float
    suggestions: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original": self.original,
            "critique": self.critique,
            "refined": self.refined,
            "confidence": self.confidence,
            "suggestions": self.suggestions,
        }


class CriticAgent(LLMAgent[CriticInput, CriticOutput]):
    """
    LLM agent for concept.refine and self.judgment.critique paths.

    Takes a statement and provides dialectical critique with refinement.

    Usage:
        agent = CriticAgent()
        result = await runtime.execute(
            agent,
            CriticInput(statement="All agents should be autonomous.")
        )
        print(result.output.critique)
        print(result.output.refined)
    """

    @property
    def name(self) -> str:
        return "concept.refine"

    def build_prompt(self, input: CriticInput) -> AgentContext:
        """Build LLM prompt for critique."""
        context_clause = ""
        if input.context:
            context_clause = f"\n\nContext: {input.context}"

        mode_instructions = {
            "dialectical": (
                "Apply Hegelian dialectic: identify the thesis's inherent contradictions, "
                "propose an antithesis, and synthesize a higher truth."
            ),
            "constructive": (
                "Provide constructive critique: identify what works, what could be improved, "
                "and offer specific actionable suggestions."
            ),
            "socratic": (
                "Apply Socratic questioning: probe assumptions, seek definitions, "
                "and guide toward clearer thinking through questions."
            ),
        }

        mode_instruction = mode_instructions.get(
            input.mode,
            mode_instructions["dialectical"],
        )

        return AgentContext(
            system_prompt=(
                f"You are a dialectical refinement engine. {mode_instruction}\n\n"
                "Your goal is to strengthen ideas through critique, not to dismiss them. "
                "Find the steel-man version of the argument."
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"Critique and refine: {input.statement}{context_clause}\n\n"
                    "Respond with a JSON object:\n"
                    "```json\n"
                    "{\n"
                    '  "original": "<the original statement>",\n'
                    '  "critique": "<your critique>",\n'
                    '  "refined": "<the improved statement>",\n'
                    '  "confidence": <0.0-1.0>,\n'
                    '  "suggestions": ["<suggestion 1>", "<suggestion 2>"]\n'
                    "}\n"
                    "```",
                }
            ],
            temperature=0.5,
            max_tokens=800,
        )

    def parse_response(self, response: str) -> CriticOutput:
        """Parse LLM response to CriticOutput."""
        try:
            # Extract JSON from code block
            if "```json" in response:
                json_start = response.index("```json") + 7
                json_end = response.index("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.index("```") + 3
                json_end = response.index("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                json_str = response.strip()

            data = json.loads(json_str)

            return CriticOutput(
                original=data.get("original", ""),
                critique=data.get("critique", ""),
                refined=data.get("refined", ""),
                confidence=float(data.get("confidence", 0.5)),
                suggestions=data.get("suggestions", []),
            )

        except (json.JSONDecodeError, ValueError):
            return CriticOutput(
                original="",
                critique=response,
                refined="",
                confidence=0.0,
                suggestions=[],
            )

    async def invoke(self, input: CriticInput) -> CriticOutput:
        """Not implemented - use runtime.execute instead."""
        raise NotImplementedError("Use runtime.execute(agent, input) instead")
