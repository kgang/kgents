"""
Define Agent - concept.define path handler.

Maps concept.define AGENTESE path to LLM-backed definition generation.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from runtime.base import AgentContext, LLMAgent


@dataclass
class DefineInput:
    """Input for definition agent."""

    term: str
    context: str = ""  # Optional context for the term


@dataclass
class DefineOutput:
    """Output from definition agent."""

    term: str
    definition: str
    examples: list[str]
    related_terms: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "term": self.term,
            "definition": self.definition,
            "examples": self.examples,
            "related_terms": self.related_terms,
        }


class DefineAgent(LLMAgent[DefineInput, DefineOutput]):
    """
    LLM agent for concept.define path.

    Takes a term and optional context, returns a structured definition.

    Usage:
        agent = DefineAgent()
        result = await runtime.execute(agent, DefineInput(term="agent"))
        print(result.output.definition)
    """

    @property
    def name(self) -> str:
        return "concept.define"

    def build_prompt(self, input: DefineInput) -> AgentContext:
        """Build LLM prompt for definition."""
        context_clause = ""
        if input.context:
            context_clause = f"\n\nContext: {input.context}"

        return AgentContext(
            system_prompt=(
                "You are a precise definition engine for the AGENTESE system. "
                "Provide clear, concise definitions that capture essential meaning. "
                "Focus on operational definitions useful for agents."
            ),
            messages=[
                {
                    "role": "user",
                    "content": f"Define the term: {input.term}{context_clause}\n\n"
                    "Respond with a JSON object:\n"
                    "```json\n"
                    "{\n"
                    '  "term": "<the term>",\n'
                    '  "definition": "<clear definition>",\n'
                    '  "examples": ["<example1>", "<example2>"],\n'
                    '  "related_terms": ["<term1>", "<term2>"]\n'
                    "}\n"
                    "```",
                }
            ],
            temperature=0.3,
            max_tokens=500,
        )

    def parse_response(self, response: str) -> DefineOutput:
        """Parse LLM response to DefineOutput."""
        # Extract JSON from response
        try:
            # Try to find JSON in code block
            if "```json" in response:
                json_start = response.index("```json") + 7
                json_end = response.index("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.index("```") + 3
                json_end = response.index("```", json_start)
                json_str = response[json_start:json_end].strip()
            else:
                # Assume raw JSON
                json_str = response.strip()

            data = json.loads(json_str)

            return DefineOutput(
                term=data.get("term", ""),
                definition=data.get("definition", ""),
                examples=data.get("examples", []),
                related_terms=data.get("related_terms", []),
            )

        except (json.JSONDecodeError, ValueError) as e:
            # Fallback: use raw response as definition
            return DefineOutput(
                term="",
                definition=response,
                examples=[],
                related_terms=[],
            )

    async def invoke(self, input: DefineInput) -> DefineOutput:
        """Not implemented - use runtime.execute instead."""
        raise NotImplementedError("Use runtime.execute(agent, input) instead")
