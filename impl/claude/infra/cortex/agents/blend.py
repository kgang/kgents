"""
Blend Agent - concept.blend.forge path handler.

Maps concept.blend.forge AGENTESE path to LLM-backed conceptual blending.
Based on Fauconnier & Turner's Conceptual Blending Theory.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from runtime.base import AgentContext, LLMAgent


@dataclass
class BlendInput:
    """Input for blending agent."""

    concepts: list[str]
    goal: str = ""  # Optional goal for the blend


@dataclass
class BlendOutput:
    """Output from blending agent."""

    blend: str
    rationale: str
    novel_properties: list[str]
    input_spaces: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "blend": self.blend,
            "rationale": self.rationale,
            "novel_properties": self.novel_properties,
            "input_spaces": self.input_spaces,
        }


class BlendAgent(LLMAgent[BlendInput, BlendOutput]):
    """
    LLM agent for concept.blend.forge path.

    Takes multiple concepts and blends them into a novel concept
    with emergent properties.

    Usage:
        agent = BlendAgent()
        result = await runtime.execute(
            agent,
            BlendInput(concepts=["surgeon", "butcher"])
        )
        print(result.output.blend)
        # -> "precision violence" or similar emergent blend
    """

    @property
    def name(self) -> str:
        return "concept.blend.forge"

    def build_prompt(self, input: BlendInput) -> AgentContext:
        """Build LLM prompt for conceptual blending."""
        goal_clause = ""
        if input.goal:
            goal_clause = f"\n\nGoal: {input.goal}"

        return AgentContext(
            system_prompt=(
                "You are a conceptual blending engine based on Fauconnier & Turner's theory. "
                "Create novel concepts by blending input concepts, identifying:\n"
                "1. Shared structure between input spaces\n"
                "2. Selective projection to the blend\n"
                "3. Emergent properties not in either input\n\n"
                "Focus on blends that yield genuine insight or novel utility."
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"Blend these concepts: {input.concepts}{goal_clause}\n\n"
                    "Respond with a JSON object:\n"
                    "```json\n"
                    "{\n"
                    '  "blend": "<the blended concept name>",\n'
                    '  "rationale": "<why this blend works>",\n'
                    '  "novel_properties": ["<emergent property 1>", "<emergent property 2>"],\n'
                    '  "input_spaces": {\n'
                    '    "<concept1>": ["<relevant feature 1>", "<relevant feature 2>"],\n'
                    '    "<concept2>": ["<relevant feature 1>", "<relevant feature 2>"]\n'
                    "  }\n"
                    "}\n"
                    "```",
                }
            ],
            temperature=0.7,  # Higher temperature for creativity
            max_tokens=800,
        )

    def parse_response(self, response: str) -> BlendOutput:
        """Parse LLM response to BlendOutput."""
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

            return BlendOutput(
                blend=data.get("blend", ""),
                rationale=data.get("rationale", ""),
                novel_properties=data.get("novel_properties", []),
                input_spaces=data.get("input_spaces", {}),
            )

        except (json.JSONDecodeError, ValueError):
            return BlendOutput(
                blend=response[:100],
                rationale="Parse error - raw response used",
                novel_properties=[],
                input_spaces={},
            )

    async def invoke(self, input: BlendInput) -> BlendOutput:
        """Not implemented - use runtime.execute instead."""
        raise NotImplementedError("Use runtime.execute(agent, input) instead")
