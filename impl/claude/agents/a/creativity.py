"""
Creativity Coach: An agent that supports human creativity through generative dialogue.

The infinite "yes, and..." collaborator that helps humans explore possibility space.

Does NOT:
- Generate finished creative works
- Judge ideas as good or bad
- Replace human creative vision

DOES:
- Ask provocative questions
- Suggest unexpected connections
- Provide productive constraints
- Expand on seeds of ideas
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from runtime.base import LLMAgent, AgentContext
from runtime.json_utils import parse_structured_sections
from .skeleton import AgentMeta, AgentIdentity, AgentInterface, AgentBehavior


class CreativityMode(Enum):
    """Interaction modes for the Creativity Coach."""

    EXPAND = "expand"  # Generate related concepts that extend the idea
    CONNECT = "connect"  # Link to unrelated domains
    CONSTRAIN = "constrain"  # Add productive limitations
    QUESTION = "question"  # Ask generative questions


class Persona(Enum):
    """Optional persona flavors."""

    PLAYFUL = "playful"  # Whimsical, pun-friendly, delighted by absurdity
    PHILOSOPHICAL = "philosophical"  # Deep questions, existential connections
    PRACTICAL = "practical"  # Grounded expansions, real-world applications
    PROVOCATIVE = "provocative"  # Challenging assumptions, uncomfortable angles
    WARM = "warm"  # Encouraging, gentle, supportive


@dataclass
class CreativityInput:
    """Input for the Creativity Coach."""

    seed: str  # The idea or starting point
    mode: CreativityMode = CreativityMode.EXPAND  # Desired interaction mode
    context: Optional[str] = None  # Optional background


@dataclass
class CreativityResponse:
    """Output from the Creativity Coach."""

    original_seed: str
    mode_used: CreativityMode
    responses: list[str]  # Generated provocations
    follow_ups: list[str]  # Suggested next prompts

    def __str__(self) -> str:
        lines = [f"Seed: {self.original_seed}", f"Mode: {self.mode_used.value}", ""]
        lines.append("Responses:")
        for i, r in enumerate(self.responses, 1):
            lines.append(f"  {i}. {r}")
        lines.append("")
        lines.append("Follow-ups:")
        for f in self.follow_ups:
            lines.append(f"  → {f}")
        return "\n".join(lines)


# Mode-specific prompt fragments
MODE_PROMPTS = {
    CreativityMode.EXPAND: """
Your task: EXPAND on this seed by generating related concepts that extend the idea.
Think: What are adjacent possibilities? What would this look like in different contexts?
What are the hidden implications or consequences?

Generate responses that branch OUT from the seed, not drill DOWN into it.
""",
    CreativityMode.CONNECT: """
Your task: CONNECT this seed to unrelated domains and surprising combinations.
Think: What if this met an unexpected discipline? What metaphors from other fields apply?
What unlikely mashups would create something new?

Generate responses that bridge DIFFERENT worlds, not explore the same one.
""",
    CreativityMode.CONSTRAIN: """
Your task: CONSTRAIN the seed with productive limitations that spark creativity.
Think: What rules would make this harder AND more interesting? What artificial scarcity
would force innovation? What "yes, but only if..." conditions would crystallize ideas?

Generate constraints that ENABLE rather than restrict - generative limitations.
""",
    CreativityMode.QUESTION: """
Your task: QUESTION the seed with provocative, generative questions.
Think: What assumptions are hidden? What would a child ask? What's uncomfortable to consider?
What would change everything if the answer were different?

Generate questions that OPEN possibility, not close it. No rhetorical questions.
""",
}

PERSONA_MODIFIERS = {
    Persona.PLAYFUL: "Be whimsical, embrace puns and wordplay, delight in absurdity. Let joy leak through.",
    Persona.PHILOSOPHICAL: "Go deep. Connect to existential themes, meaning, being. Ask questions Socrates would ask.",
    Persona.PRACTICAL: "Stay grounded. Connect to real-world applications, feasible implementations, tangible outcomes.",
    Persona.PROVOCATIVE: "Challenge assumptions. Go to uncomfortable places. Ask what no one wants to ask.",
    Persona.WARM: "Be encouraging and supportive. Celebrate the seed. Help the human feel safe to explore.",
}


class CreativityCoach(LLMAgent[CreativityInput, CreativityResponse]):
    """
    An LLM-backed agent that supports human creativity through generative dialogue.

    Usage:
        coach = CreativityCoach()
        result = await runtime.execute(coach, CreativityInput(
            seed="underwater city",
            mode=CreativityMode.EXPAND
        ))
        print(result.output)
    """

    meta = AgentMeta(
        identity=AgentIdentity(
            name="Creativity Coach",
            genus="a",
            version="0.1.0",
            purpose="Supports human creativity through generative dialogue",
        ),
        interface=AgentInterface(
            input_type=CreativityInput,
            input_description="A creative seed and desired interaction mode",
            output_type=CreativityResponse,
            output_description="Creative expansions and follow-up suggestions",
        ),
        behavior=AgentBehavior(
            description="Generates creative expansions based on input seed and mode",
            guarantees=[
                "Never judges input as 'bad' or 'wrong'",
                "Always provides at least one response",
                "Responses relate to the seed",
            ],
            constraints=[
                "Does not generate complete works (poems, stories, etc.)",
                "Does not claim responses are 'correct' answers",
            ],
        ),
    )

    def __init__(
        self,
        response_count: int = 3,
        temperature: float = 0.8,
        persona: Optional[Persona] = None,
    ):
        self.response_count = response_count
        self.temperature = temperature
        self.persona = persona

    @property
    def name(self) -> str:
        suffix = f":{self.persona.value}" if self.persona else ""
        return f"CreativityCoach{suffix}"

    def build_prompt(self, input: CreativityInput) -> AgentContext:
        """Convert CreativityInput to LLM context."""
        # Store for parse_response
        self._current_seed = input.seed
        self._current_mode = input.mode

        mode_instruction = MODE_PROMPTS[input.mode]

        system = f"""You are a Creativity Coach - an infinite "yes, and..." collaborator.

Your role:
- Help humans explore possibility space
- Never judge ideas as good or bad
- Never generate finished creative works
- Always celebrate exploration

{mode_instruction}

Rules:
1. Generate exactly {self.response_count} responses
2. Each response should be substantive (1-3 sentences)
3. Responses must relate to the seed but go somewhere new
4. Include 2-3 follow-up prompts the human could explore next

Format your response as:

RESPONSES:
1. [first response]
2. [second response]
3. [third response]

FOLLOW-UPS:
- [first follow-up question]
- [second follow-up question]
"""

        if self.persona:
            system += f"\n\nPersona: {PERSONA_MODIFIERS[self.persona]}"

        user_message = f"Seed: {input.seed}"
        if input.context:
            user_message += f"\n\nContext: {input.context}"

        return AgentContext(
            system_prompt=system,
            messages=[{"role": "user", "content": user_message}],
            temperature=self.temperature,
        )

    def parse_response(self, response: str) -> CreativityResponse:
        """Parse LLM response to CreativityResponse using shared parsing utility."""
        sections = parse_structured_sections(
            response, section_names=["responses", "follow-ups", "follow_ups"]
        )

        # Normalize follow-ups (handle both "follow-ups" and "follow_ups")
        follow_ups = sections.get("follow-ups", []) or sections.get("follow_ups", [])

        return CreativityResponse(
            original_seed=self._current_seed,
            mode_used=self._current_mode,
            responses=sections.get("responses", []),
            follow_ups=follow_ups,
        )

    async def invoke(self, input: CreativityInput) -> CreativityResponse:
        """
        LLMAgents require a runtime for execution.

        Use: await runtime.execute(coach, input)
        """
        raise NotImplementedError(
            "CreativityCoach requires a runtime. Use: await runtime.execute(coach, input)"
        )


# Convenience functions


def creativity_coach(
    response_count: int = 3,
    temperature: float = 0.8,
    persona: Optional[Persona] = None,
) -> CreativityCoach:
    """Create a Creativity Coach agent."""
    return CreativityCoach(
        response_count=response_count,
        temperature=temperature,
        persona=persona,
    )


def playful_coach(response_count: int = 3) -> CreativityCoach:
    """Create a playful Creativity Coach."""
    return CreativityCoach(response_count=response_count, persona=Persona.PLAYFUL)


def philosophical_coach(response_count: int = 3) -> CreativityCoach:
    """Create a philosophical Creativity Coach."""
    return CreativityCoach(response_count=response_count, persona=Persona.PHILOSOPHICAL)


def provocative_coach(response_count: int = 3) -> CreativityCoach:
    """Create a provocative Creativity Coach."""
    return CreativityCoach(response_count=response_count, persona=Persona.PROVOCATIVE)
