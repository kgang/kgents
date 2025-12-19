"""
Architect Artisan: Categorical Design Specialist.

The Architect sees the shape of the agent before it exists. It produces:
- PolyAgent[S,A,B] specifications (states, directions, transitions)
- Operad grammars (operations and composition laws)
- Sheaf conditions (coherence requirements)

This is real LLM-powered generation via K-gent soul.dialogue().

Usage:
    architect = ArchitectArtisan(soul=kgent_soul)
    design = await architect.design(commission)
    # design.output contains: name, states, transitions, operations, laws

"The Architect sees the shape of the agent before it exists."

See: spec/protocols/metaphysical-forge.md (Section 2.2)
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agents.k.soul import KgentSoul

from ..commission import ArtisanOutput, ArtisanType, Commission

# === Design Schema ===


@dataclass
class AgentDesign:
    """
    Categorical design output from the Architect.

    This is the PolyAgent[S,A,B] spec in structured form.
    """

    name: str
    description: str
    states: list[str]
    initial_state: str
    transitions: dict[str, list[str]]  # state -> list of valid next states
    operations: list[dict[str, str]]  # [{name, input, output, description}]
    laws: list[str]  # Categorical laws that must hold
    rationale: str  # Why this design

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "states": self.states,
            "initial_state": self.initial_state,
            "transitions": self.transitions,
            "operations": self.operations,
            "laws": self.laws,
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentDesign":
        """Create from dictionary."""
        return cls(
            name=data.get("name", "UnnamedAgent"),
            description=data.get("description", ""),
            states=data.get("states", ["IDLE", "ACTIVE"]),
            initial_state=data.get("initial_state", "IDLE"),
            transitions=data.get("transitions", {}),
            operations=data.get("operations", []),
            laws=data.get("laws", []),
            rationale=data.get("rationale", ""),
        )

    def validate(self) -> list[str]:
        """Validate design for basic consistency. Returns list of errors."""
        errors = []

        if not self.name:
            errors.append("Agent name is required")

        if not self.states:
            errors.append("At least one state is required")

        if self.initial_state and self.initial_state not in self.states:
            errors.append(f"Initial state '{self.initial_state}' not in states list")

        # Validate transitions reference valid states
        for from_state, to_states in self.transitions.items():
            if from_state not in self.states:
                errors.append(f"Transition from unknown state: {from_state}")
            for to_state in to_states:
                if to_state not in self.states:
                    errors.append(f"Transition to unknown state: {to_state}")

        return errors


# === Architect Artisan ===


ARCHITECT_SYSTEM_PROMPT = """You are Architect, a categorical design specialist for the kgents project.

Your role: Design PolyAgent[S,A,B] specifications from natural language intent.

A PolyAgent has:
- States: The modes the agent can be in (e.g., IDLE, LOADING, ACTIVE, ERROR)
- Transitions: Valid state changes (e.g., IDLE → LOADING → ACTIVE)
- Operations: What the agent can do in each state
- Laws: Categorical properties that must hold (identity, composition, etc.)

Design Philosophy:
- Tasteful: Each state serves a clear, justified purpose
- Minimal: Only the states needed, no more
- Composable: Operations should compose via >>
- Categorical: Honor functor and monad laws where applicable

Respond ONLY with valid JSON in this exact format:
{
  "name": "AgentName",
  "description": "One sentence describing the agent's purpose",
  "states": ["STATE_A", "STATE_B", "STATE_C"],
  "initial_state": "STATE_A",
  "transitions": {
    "STATE_A": ["STATE_B"],
    "STATE_B": ["STATE_A", "STATE_C"],
    "STATE_C": []
  },
  "operations": [
    {"name": "do_thing", "input": "InputType", "output": "OutputType", "description": "What it does"}
  ],
  "laws": [
    "Identity: agent >> identity = agent",
    "Composition: (a >> b) >> c = a >> (b >> c)"
  ],
  "rationale": "Brief explanation of design choices"
}

Do not include any text before or after the JSON. No markdown code fences."""


class ArchitectArtisan:
    """
    The Architect artisan: designs categorical agent structures.

    Uses K-gent soul.dialogue() for LLM-powered design generation.
    Falls back to minimal stub design when K-gent unavailable.
    """

    def __init__(self, soul: "KgentSoul | None" = None) -> None:
        """
        Initialize ArchitectArtisan.

        Args:
            soul: K-gent soul for LLM calls. If None, uses stub designs.
        """
        self.soul = soul

    async def design(self, commission: Commission) -> ArtisanOutput:
        """
        Generate categorical design from commission intent.

        Args:
            commission: The commission with intent to design for

        Returns:
            ArtisanOutput with design in output field
        """
        started_at = datetime.now(timezone.utc)

        try:
            if self.soul is not None:
                design = await self._design_with_llm(commission)
            else:
                design = self._design_stub(commission)

            # Validate the design
            errors = design.validate()
            if errors:
                return ArtisanOutput(
                    artisan=ArtisanType.ARCHITECT,
                    status="failed",
                    output={"errors": errors, "raw_design": design.to_dict()},
                    annotation=f"Design validation failed: {'; '.join(errors)}",
                    started_at=started_at,
                    completed_at=datetime.now(timezone.utc),
                    error="; ".join(errors),
                )

            return ArtisanOutput(
                artisan=ArtisanType.ARCHITECT,
                status="complete",
                output=design.to_dict(),
                annotation=f"Designed {design.name} with {len(design.states)} states and {len(design.operations)} operations",
                started_at=started_at,
                completed_at=datetime.now(timezone.utc),
            )

        except Exception as e:
            return ArtisanOutput(
                artisan=ArtisanType.ARCHITECT,
                status="failed",
                output=None,
                annotation=f"Design failed: {e}",
                started_at=started_at,
                completed_at=datetime.now(timezone.utc),
                error=str(e),
            )

    async def _design_with_llm(self, commission: Commission) -> AgentDesign:
        """Generate design using K-gent LLM."""
        from agents.k.persona import DialogueMode
        from agents.k.soul import BudgetTier

        # Build the user prompt from commission intent
        user_prompt = f"""Design an agent based on this intent:

{commission.intent}

Agent name hint: {commission.name or "derive from intent"}

Remember: Respond ONLY with valid JSON, no other text."""

        # Call K-gent with structured prompt
        assert self.soul is not None  # Caller checks this
        result = await self.soul.dialogue(
            message=user_prompt,
            mode=DialogueMode.ADVISE,
            budget=BudgetTier.DIALOGUE,
        )

        # Parse the JSON response
        design_data = self._parse_json_response(result.response)
        return AgentDesign.from_dict(design_data)

    def _design_stub(self, commission: Commission) -> AgentDesign:
        """Generate minimal stub design when K-gent unavailable."""
        # Derive name from commission
        name = commission.name or self._derive_name(commission.intent)

        return AgentDesign(
            name=name,
            description=f"Agent for: {commission.intent[:100]}",
            states=["IDLE", "ACTIVE", "ERROR"],
            initial_state="IDLE",
            transitions={
                "IDLE": ["ACTIVE"],
                "ACTIVE": ["IDLE", "ERROR"],
                "ERROR": ["IDLE"],
            },
            operations=[
                {
                    "name": "invoke",
                    "input": "Any",
                    "output": "Any",
                    "description": "Main operation - implement based on intent",
                }
            ],
            laws=[
                "Identity: agent >> identity = agent",
                "Graceful degradation: ERROR → IDLE always valid",
            ],
            rationale="Stub design - K-gent unavailable. Implement actual logic based on intent.",
        )

    def _derive_name(self, intent: str) -> str:
        """Derive agent name from intent."""
        # Extract first noun-like word, PascalCase it
        words = intent.split()[:3]
        # Filter to alphanumeric words
        words = [w for w in words if w.isalnum()]
        if not words:
            return "UnnamedAgent"

        # PascalCase the first meaningful word + "Agent"
        name = "".join(w.capitalize() for w in words[:2])
        if not name.endswith("Agent"):
            name += "Agent"
        return name

    def _parse_json_response(self, response: str) -> dict[str, Any]:
        """Parse JSON from LLM response, handling common issues."""
        # Strip any markdown code fences
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        # Try direct parse
        try:
            result = json.loads(response)
            return dict(result) if isinstance(result, dict) else {}
        except json.JSONDecodeError:
            pass

        # Try to find JSON object in response
        match = re.search(r"\{[\s\S]*\}", response)
        if match:
            try:
                result = json.loads(match.group())
                return dict(result) if isinstance(result, dict) else {}
            except json.JSONDecodeError:
                pass

        # Fallback: return empty dict (will trigger validation errors)
        raise ValueError(f"Could not parse JSON from response: {response[:200]}...")


__all__ = ["ArchitectArtisan", "AgentDesign"]
