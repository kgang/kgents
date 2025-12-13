"""
Tutorial: K-gent Dialogue - Chat with Kent's Simulacrum.

Introduces K-gent Soul - the digital simulacra that provides
personality-aligned responses and governance.
"""

from __future__ import annotations

from ..tutorial import Tutorial, TutorialStep


async def _run_soul_basic() -> str:
    """Demonstrate basic soul dialogue."""
    try:
        from agents.k import DialogueMode, KgentSoul

        soul = KgentSoul()
        output = await soul.dialogue(
            "What makes a good agent design?",
            mode=DialogueMode.REFLECT,
        )
        return f"Mode: {output.mode.value}\nResponse: {output.response[:200]}..."
    except ImportError:
        return "(agents.k not available - showing pattern only)"
    except Exception as e:
        return f"(Demo requires LLM - pattern shown above)\nError: {e}"


async def _run_soul_modes() -> str:
    """Show different dialogue modes."""
    try:
        from agents.k import DialogueMode, KgentSoul

        soul = KgentSoul()

        # Get a starter for each mode
        starters = []
        for mode in [
            DialogueMode.REFLECT,
            DialogueMode.ADVISE,
            DialogueMode.CHALLENGE,
            DialogueMode.EXPLORE,
        ]:
            starter = soul.get_starter(mode)
            starters.append(f'{mode.value}: "{starter}"')

        return "\n".join(starters)
    except ImportError:
        return "(agents.k not available - showing pattern only)"


SOUL_TUTORIAL = Tutorial(
    name="K-gent Dialogue",
    description="""K-gent Soul is Kent's digital simulacra - a personality model
that responds based on declared preferences and eigenvectors.

It's NOT a chatbot. It's a GOVERNANCE FUNCTOR that ensures
agent responses align with the persona's values.

Four dialogue modes:
  - REFLECT: Mirror back for examination
  - ADVISE: Offer preference-aligned suggestions
  - CHALLENGE: Push back constructively
  - EXPLORE: Follow tangents, generate hypotheses""",
    steps=[
        TutorialStep(
            title="Basic Soul Dialogue",
            code="""
from agents.k import KgentSoul, DialogueMode

# Create a soul instance
soul = KgentSoul()

# Have a dialogue
output = await soul.dialogue(
    "What makes a good agent design?",
    mode=DialogueMode.REFLECT,
)

print(output.response)
# -> A thoughtful, Kent-like reflection on agent design
""",
            explanation="KgentSoul provides dialogue that feels like Kent on his best day.",
            execute=_run_soul_basic,
            next_hint="Each mode (REFLECT, ADVISE, CHALLENGE, EXPLORE) has a different feel",
        ),
        TutorialStep(
            title="The Four Dialogue Modes",
            code="""
from agents.k import DialogueMode

# REFLECT - Mirror back for examination
# "Let me understand: you're saying..."
# Best for: clarifying your own thinking

# ADVISE - Offer preference-aligned suggestions
# "Based on what matters to you, consider..."
# Best for: getting recommendations

# CHALLENGE - Push back constructively
# "Have you considered the opposite view..."
# Best for: stress-testing ideas

# EXPLORE - Follow tangents, generate hypotheses
# "That reminds me of... what if we..."
# Best for: creative brainstorming

# Each mode activates different eigenvectors
# (personality dimensions) of K-gent
""",
            explanation="Modes aren't just prompts - they activate different personality dimensions.",
            execute=_run_soul_modes,
            next_hint="Try: kgents soul challenge 'I think X is the best approach'",
        ),
        TutorialStep(
            title="Soul as Governance Functor",
            code="""
# K-gent is NOT just a chatbot. It's a GOVERNANCE FUNCTOR.
#
# Traditional chatbot:
#   input -> LLM -> output
#
# K-gent Soul:
#   input -> [Eigenvector Alignment] -> LLM -> [Principle Check] -> output
#
# The soul ensures responses align with:
# - Declared preferences (what Kent values)
# - Eigenvectors (personality coordinates)
# - Principles (tasteful, curated, ethical, joy-inducing)
#
# Use @Capability.Soulful to add soul governance to any agent:

from agents.a import Capability

@Capability.Soulful(persona="Kent")
class MyAdvisor(Agent[str, str]):
    async def invoke(self, input: str) -> str:
        # Soul governance wraps this automatically
        return self.process(input)
""",
            explanation="Soul governance ensures consistency - every response feels 'on brand'.",
            next_hint="Try: kgents soul starters (to see starter prompts for each mode)",
        ),
        TutorialStep(
            title="Try It Now",
            code="""
# From the command line:

# Interactive dialogue (default: REFLECT mode)
$ kgents soul

# Specific mode with prompt
$ kgents soul challenge "I think premature optimization is fine"

# Quick response (fewer tokens)
$ kgents soul advise "Should I refactor this?" --quick

# See all starter prompts
$ kgents soul starters

# View soul state
$ kgents soul manifest
""",
            explanation="K-gent is always available via the CLI for quick consultations.",
            next_hint="The soul learns from interactions - try a few dialogues!",
        ),
    ],
    completion_message="""You've learned about K-gent Soul:

  - KgentSoul provides personality-aligned dialogue
  - Four modes: REFLECT, ADVISE, CHALLENGE, EXPLORE
  - Soul is a governance functor, not just a chatbot

Try it now: `kgents soul challenge "your idea here"`

Or explore freely: `kgents play repl`""",
)
