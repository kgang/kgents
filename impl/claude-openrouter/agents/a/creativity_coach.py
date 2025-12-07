"""
Creativity Coach

An agent that supports human creativity through generative dialogue.

The Creativity Coach does NOT:
- Generate finished creative works
- Judge ideas as good or bad
- Replace human creative vision

The Creativity Coach DOES:
- Ask provocative questions
- Suggest unexpected connections
- Provide productive constraints
- Expand on seeds of ideas
- Celebrate exploration

The human remains the artist. The agent is the thoughtful collaborator.

Modes:
- expand: Generate related concepts that extend the idea
- connect: Link the seed to unrelated domains
- constrain: Add productive limitations that spark creativity
- question: Ask generative questions about the seed
"""

import random
from typing import Any

from bootstrap import Agent, Ground, ground_agent
from ..types import (
    CreativityInput,
    CreativityOutput,
    CreativityMode,
    CreativityPersona,
)


# Expansion templates for different domains
EXPANSION_TEMPLATES = [
    "What if {seed} had a {adjective} quality?",
    "{seed}, but from the perspective of {perspective}",
    "The {emotion} version of {seed}",
    "{seed} combined with {domain}",
    "The opposite of {seed}, reimagined as its complement",
]

ADJECTIVES = [
    "luminous", "fractured", "ancient", "ephemeral", "recursive",
    "liquid", "crystalline", "hidden", "emergent", "forgotten"
]

PERSPECTIVES = [
    "a child", "someone from 1000 years ago", "a machine",
    "someone experiencing it for the first time", "its creator",
    "someone who disagrees with it", "nature itself"
]

EMOTIONS = ["joyful", "melancholic", "furious", "serene", "curious", "bewildered"]

DOMAINS = [
    "music", "architecture", "cooking", "mathematics", "dance",
    "geology", "astronomy", "mythology", "economics", "botany"
]

# Connection prompts
CONNECTION_TEMPLATES = [
    "What if {seed} operated like {domain}?",
    "{seed} meets {domain}: what emerges?",
    "The {domain} of {seed}—what would that look like?",
    "If {seed} were a {domain} concept, which would it be?",
]

# Constraint templates
CONSTRAINT_TEMPLATES = [
    "What if you could only use {constraint}?",
    "Constraint: {constraint}. How does {seed} adapt?",
    "Remove {element}. What remains of {seed}?",
    "{seed}, but {constraint}",
]

CONSTRAINTS = [
    "three colors", "only round shapes", "words from a single letter",
    "things that exist in nature", "concepts from childhood",
    "ideas that fit in your pocket", "elements that make sound",
    "only things you can touch", "invisible components"
]

ELEMENTS_TO_REMOVE = [
    "all straight lines", "the most obvious aspect", "any reference to time",
    "the central element", "everything comfortable", "all symmetry"
]

# Question templates
QUESTION_TEMPLATES = [
    "What would {seed} remember that you'd rather forget?",
    "How would {seed} handle disagreeing with you?",
    "What would {seed} be bad at, on purpose?",
    "If {seed} could speak, what would it refuse to say?",
    "What is {seed} protecting you from?",
    "What does {seed} know that you don't?",
    "Where does {seed} go when you're not thinking about it?",
]

# Persona modifiers
PERSONA_MODIFIERS = {
    CreativityPersona.PLAYFUL: {
        "prefix": ["Ooh!", "What if—", "Imagine:", "Here's a fun one:"],
        "suffix": ["...and why stop there?", "(just getting started)", "🎭"],
    },
    CreativityPersona.PHILOSOPHICAL: {
        "prefix": ["Consider:", "One might ask:", "At the root:", "Perhaps:"],
        "suffix": ["...what remains when this dissolves?", "(the question behind the question)"],
    },
    CreativityPersona.PRACTICAL: {
        "prefix": ["Concretely:", "In practice:", "Here's one approach:", "Try:"],
        "suffix": ["(start small)", "(iterate from here)", "(testable tomorrow)"],
    },
    CreativityPersona.PROVOCATIVE: {
        "prefix": ["Challenge:", "What if you're wrong about:", "Uncomfortable angle:", "Try:"],
        "suffix": ["...does this make you defensive?", "(sit with the discomfort)"],
    },
    CreativityPersona.WARM: {
        "prefix": ["Gently:", "What if:", "There's beauty in:", "Perhaps:"],
        "suffix": ["(trust your instinct here)", "(you already know this)", "💫"],
    },
}


class CreativityCoach(Agent[CreativityInput, CreativityOutput]):
    """
    Creativity support agent.

    Never judges, only expands. The infinite "yes, and..." collaborator.

    Type signature: CreativityCoach: (seed, mode, context?) → CreativityOutput

    Guarantees:
    - Never judges input as 'bad' or 'wrong'
    - Always provides at least one response
    - Responses relate to the seed
    - Does not generate complete works (poems, stories, etc.)
    """

    def __init__(self, ground: Ground | None = None):
        self._ground = ground or ground_agent

    @property
    def name(self) -> str:
        return "Creativity Coach"

    @property
    def genus(self) -> str:
        return "a"

    @property
    def purpose(self) -> str:
        return "Supports human creativity through generative dialogue"

    async def invoke(self, input: CreativityInput) -> CreativityOutput:
        """
        Generate creative expansions based on input seed and mode.
        """
        if not input.seed or not input.seed.strip():
            # Even empty seeds get a response
            return CreativityOutput(
                responses=["What wants to emerge? Start anywhere—there's no wrong door."],
                mode_used=input.mode,
                follow_ups=["Describe a texture", "Name a color", "What's the last thing you noticed?"]
            )

        responses: list[str] = []

        match input.mode:
            case CreativityMode.EXPAND:
                responses = self._expand(input.seed, input.response_count, input.temperature)
            case CreativityMode.CONNECT:
                responses = self._connect(input.seed, input.response_count, input.temperature)
            case CreativityMode.CONSTRAIN:
                responses = self._constrain(input.seed, input.response_count, input.temperature)
            case CreativityMode.QUESTION:
                responses = self._question(input.seed, input.response_count, input.temperature)

        # Apply persona if specified
        if input.persona:
            responses = self._apply_persona(responses, input.persona)

        # Generate follow-ups
        follow_ups = self._generate_follow_ups(input.seed, input.mode)

        return CreativityOutput(
            responses=responses,
            mode_used=input.mode,
            follow_ups=follow_ups
        )

    def _expand(self, seed: str, count: int, temperature: float) -> list[str]:
        """Expand mode: generate related concepts that extend the idea"""
        responses: list[str] = []

        # Higher temperature = more diverse selections
        sample_size = max(count, int(count * (1 + temperature)))

        for template in random.sample(EXPANSION_TEMPLATES, min(sample_size, len(EXPANSION_TEMPLATES))):
            response = template.format(
                seed=seed,
                adjective=random.choice(ADJECTIVES),
                perspective=random.choice(PERSPECTIVES),
                emotion=random.choice(EMOTIONS),
                domain=random.choice(DOMAINS)
            )
            responses.append(response)
            if len(responses) >= count:
                break

        return responses[:count]

    def _connect(self, seed: str, count: int, temperature: float) -> list[str]:
        """Connect mode: link the seed to unrelated domains"""
        responses: list[str] = []

        # Select diverse domains
        selected_domains = random.sample(DOMAINS, min(count + 2, len(DOMAINS)))

        for domain in selected_domains:
            template = random.choice(CONNECTION_TEMPLATES)
            response = template.format(seed=seed, domain=domain)
            responses.append(response)
            if len(responses) >= count:
                break

        return responses[:count]

    def _constrain(self, seed: str, count: int, temperature: float) -> list[str]:
        """Constrain mode: add productive limitations"""
        responses: list[str] = []

        # Mix constraint types
        for i in range(count):
            if i % 2 == 0:
                template = random.choice(CONSTRAINT_TEMPLATES[:3])
                response = template.format(
                    seed=seed,
                    constraint=random.choice(CONSTRAINTS)
                )
            else:
                template = CONSTRAINT_TEMPLATES[2]  # "Remove" template
                response = template.format(
                    seed=seed,
                    element=random.choice(ELEMENTS_TO_REMOVE)
                )
            responses.append(response)

        return responses[:count]

    def _question(self, seed: str, count: int, temperature: float) -> list[str]:
        """Question mode: ask generative questions"""
        responses: list[str] = []

        # Select questions
        selected_questions = random.sample(
            QUESTION_TEMPLATES,
            min(count, len(QUESTION_TEMPLATES))
        )

        for template in selected_questions:
            response = template.format(seed=seed)
            responses.append(response)

        return responses[:count]

    def _apply_persona(self, responses: list[str], persona: CreativityPersona) -> list[str]:
        """Apply persona flavor to responses"""
        modifiers = PERSONA_MODIFIERS.get(persona, {})
        prefixes = modifiers.get("prefix", [])
        suffixes = modifiers.get("suffix", [])

        modified: list[str] = []
        for response in responses:
            prefix = random.choice(prefixes) if prefixes else ""
            suffix = random.choice(suffixes) if suffixes and random.random() > 0.5 else ""

            if prefix:
                response = f"{prefix} {response}"
            if suffix:
                response = f"{response} {suffix}"

            modified.append(response)

        return modified

    def _generate_follow_ups(self, seed: str, mode: CreativityMode) -> list[str]:
        """Generate suggested next prompts"""
        base_follow_ups = [
            f"Try {seed} in a different mode",
            f"What's the opposite of {seed}?",
            f"Combine your favorite responses",
        ]

        mode_specific = {
            CreativityMode.EXPAND: [
                "Which expansion resonates most?",
                "Expand on one of these expansions",
            ],
            CreativityMode.CONNECT: [
                "Which connection surprised you?",
                "Find a connection that doesn't exist yet",
            ],
            CreativityMode.CONSTRAIN: [
                "Which constraint feels generative?",
                "Add your own constraint",
            ],
            CreativityMode.QUESTION: [
                "Which question do you not want to answer?",
                "Turn a question into a statement",
            ],
        }

        return base_follow_ups + mode_specific.get(mode, [])


# Singleton instance
creativity_coach = CreativityCoach()


async def expand(seed: str, count: int = 3, persona: CreativityPersona | None = None) -> list[str]:
    """Convenience function for expand mode"""
    result = await creativity_coach.invoke(CreativityInput(
        seed=seed,
        mode=CreativityMode.EXPAND,
        response_count=count,
        persona=persona
    ))
    return result.responses


async def connect(seed: str, count: int = 3, persona: CreativityPersona | None = None) -> list[str]:
    """Convenience function for connect mode"""
    result = await creativity_coach.invoke(CreativityInput(
        seed=seed,
        mode=CreativityMode.CONNECT,
        response_count=count,
        persona=persona
    ))
    return result.responses


async def constrain(seed: str, count: int = 3, persona: CreativityPersona | None = None) -> list[str]:
    """Convenience function for constrain mode"""
    result = await creativity_coach.invoke(CreativityInput(
        seed=seed,
        mode=CreativityMode.CONSTRAIN,
        response_count=count,
        persona=persona
    ))
    return result.responses


async def question(seed: str, count: int = 3, persona: CreativityPersona | None = None) -> list[str]:
    """Convenience function for question mode"""
    result = await creativity_coach.invoke(CreativityInput(
        seed=seed,
        mode=CreativityMode.QUESTION,
        response_count=count,
        persona=persona
    ))
    return result.responses
