"""
GroundParser - Agent-based extraction of PersonaSeed from markdown.

Type: str → PersonaSeed
Purpose: Parse natural language persona specs into structured data

This demonstrates autopoiesis: using agents to build agents.
Instead of manual parsing, the LLM extracts semantic content from persona.md.
"""

from typing import Any

from runtime.base import LLMAgent, AgentContext
from .types import PersonaSeed


class GroundParser(LLMAgent[str, PersonaSeed]):
    """
    Parse markdown persona specification into structured PersonaSeed.

    Extracts:
    - name: Person's name
    - roles: List of roles/identities
    - preferences: Nested dict of preference categories
    - patterns: Dict of behavioral patterns (thinking, decision_making, communication)
    - values: List of core values
    - dislikes: List of aversions

    Why agent-based:
    - LLM can handle variations in markdown formatting
    - Semantic extraction rather than brittle regex
    - Natural language → structured data is LLM strength
    - Increases autopoiesis (agents building agents)
    """

    @property
    def name(self) -> str:
        return "GroundParser"

    def build_prompt(self, markdown: str) -> AgentContext:
        """Build LLM prompt to extract PersonaSeed from markdown."""
        system_prompt = """You are a GroundParser agent. Extract structured persona data from markdown.

Your task: Parse persona markdown into PersonaSeed fields.

Expected fields:
- name (string): Person's name
- roles (list[string]): Roles/identities
- preferences (dict): Nested preferences (communication, aesthetics, etc.)
- patterns (dict): Behavioral patterns with categories (thinking, decision_making, communication)
- values (list[string]): Core values
- dislikes (list[string]): Aversions

Return ONLY valid JSON matching this structure:
{
  "name": "...",
  "roles": [...],
  "preferences": {...},
  "patterns": {...},
  "values": [...],
  "dislikes": [...]
}

Be faithful to the source. Don't invent or embellish."""

        user_prompt = f"""Extract PersonaSeed from this markdown:

{markdown}

Return JSON only."""

        return AgentContext(
            system_prompt=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.1,  # Low temperature for faithful extraction
            max_tokens=2000,
        )

    def parse_response(self, response_text: str, _: str) -> PersonaSeed:
        """Parse LLM JSON response into PersonaSeed."""
        import json

        # Clean markdown code blocks if present
        text = response_text.strip()
        if text.startswith("```json"):
            text = text.split("```json")[1].split("```")[0].strip()
        elif text.startswith("```"):
            text = text.split("```")[1].split("```")[0].strip()

        # Parse JSON
        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse GroundParser response as JSON: {e}")

        # Validate required fields
        required = ["name", "roles", "preferences", "patterns", "values", "dislikes"]
        missing = [field for field in required if field not in data]
        if missing:
            raise ValueError(f"Missing required PersonaSeed fields: {missing}")

        # Construct PersonaSeed
        return PersonaSeed(
            name=data["name"],
            roles=data["roles"],
            preferences=data["preferences"],
            patterns=data["patterns"],
            values=data["values"],
            dislikes=data["dislikes"],
        )


# Example usage (for documentation):
"""
from runtime.claude import ClaudeCLIRuntime

# Read persona spec
with open("spec/k-gent/persona.md") as f:
    markdown = f.read()

# Parse using GroundParser agent
runtime = ClaudeCLIRuntime()
parser = GroundParser()
seed = await runtime.execute(parser, markdown)

# Now use seed in Ground agent
facts = Facts(
    persona=seed,
    world=WorldSeed(...),
    history={}
)
"""
