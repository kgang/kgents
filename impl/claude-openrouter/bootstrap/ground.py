"""
Ground (⊥) - The empirical seed.

Type: Void → Facts
Returns: {Kent's preferences, world state, initial conditions}

The irreducible facts about the person and world that cannot be derived.

Why irreducible: Kent's preference for "direct but warm" is a fact about Kent,
                 not a theorem. The current state of the world is given.
What it grounds: K-gent's persona. The starting point for personalization.

Contents:
- Persona seed: Name, roles, preferences, patterns, values
- World seed: Date, context, active projects
- History seed: Past decisions, established patterns

THE BOOTSTRAP PARADOX:
> Ground cannot be bypassed. LLMs can amplify but not replace Ground.

What LLMs CAN do:
- Amplify Ground (generate variations, explore implications)
- Apply Ground (translate preferences into code)
- Extend Ground (infer related preferences from stated ones)

What LLMs CANNOT do:
- Create Ground from nothing
- Replace human judgment about what matters
- Substitute for real-world usage feedback
"""

from datetime import date
from typing import Optional

from .types import Agent, Facts, PersonaSeed, WorldSeed


class Ground(Agent[None, Facts]):
    """
    The empirical seed: loads irreducible facts about person and world.

    Usage:
        ground = Ground()
        facts = await ground.invoke(None)

        # Access persona
        facts.persona.name  # "Kent"
        facts.persona.preferences["communication"]["style"]  # "direct but warm"

        # Access world
        facts.world.date  # current date
        facts.world.active_projects  # ongoing work

    The Ground agent can be initialized with custom facts (for testing)
    or will use the default Kent persona from spec.
    """

    def __init__(self, facts: Optional[Facts] = None):
        """
        Initialize Ground with optional custom facts.

        If no facts provided, loads the default Kent persona from spec.
        """
        self._facts = facts or self._load_default_facts()

    @property
    def name(self) -> str:
        return "Ground"

    async def invoke(self, _: None) -> Facts:
        """Return the grounded facts. Input is ignored (Void → Facts)."""
        return self._facts

    def _load_default_facts(self) -> Facts:
        """
        Load the default Kent persona from spec/k-gent/persona.md.

        This is the irreducible seed - human judgment captured as data.
        """
        return Facts(
            persona=PersonaSeed(
                name="Kent",
                roles=["researcher", "creator", "thinker"],
                preferences={
                    "communication": {
                        "style": "direct but warm",
                        "length": "concise preferred",
                        "formality": "casual with substance",
                    },
                    "aesthetics": {
                        "design": "minimal, functional",
                        "prose": "clear over clever",
                    },
                },
                patterns={
                    "thinking": [
                        "starts from first principles",
                        "asks 'what would falsify this?'",
                        "seeks composable abstractions",
                    ],
                    "decision_making": [
                        "prefers reversible choices",
                        "values optionality",
                    ],
                    "communication": [
                        "uses analogies frequently",
                        "appreciates precision in technical contexts",
                    ],
                },
                values=[
                    "intellectual honesty",
                    "ethical technology",
                    "joy in creation",
                    "composability",
                ],
                dislikes=[
                    "unnecessary jargon",
                    "feature creep",
                    "surveillance capitalism",
                ],
            ),
            world=WorldSeed(
                date=date.today().isoformat(),
                context={
                    "current_focus": "kgents specification",
                    "recent_interests": [
                        "category theory",
                        "scientific agents",
                        "personal AI",
                    ],
                },
                active_projects=[
                    {
                        "name": "kgents",
                        "status": "active",
                        "goals": ["spec A/B/C/K", "reference implementation"],
                    }
                ],
            ),
            history={},
        )


# The LLM/Human boundary:
#
# Spec + Ground = Human territory (irreducible, already provided)
# Impl = LLM territory (mechanical translation from spec)
# Polish = Hybrid territory (accumulated wisdom from real usage)
