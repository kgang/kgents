"""
Ground Agent (⊥)

Ground: Void → Facts
Ground() = {Kent's preferences, world state, initial conditions}

The empirical seed. The irreducible facts about the person and world
that cannot be derived.

Why irreducible: Kent's preference for "direct but warm" communication is a
                 fact about Kent, not a theorem. The current state of the world
                 is given, not computed.

What it grounds: K-gent's persona. The starting point for all personalization.
                 The connection between formal system and reality.
"""

from datetime import datetime
from typing import Any
from .types import (
    Agent,
    GroundState,
    PersonaState,
    WorldState,
    Identity,
    Preferences,
    CommunicationPrefs,
    AestheticsPrefs,
    Patterns,
    Context,
    Project,
)


# The persona seed from spec/k-gent/persona.md
KENT_PERSONA = PersonaState(
    identity=Identity(
        name="Kent",
        roles=["researcher", "creator", "thinker"]
    ),
    preferences=Preferences(
        communication=CommunicationPrefs(
            style="direct but warm",
            length="concise preferred",
            formality="casual with substance"
        ),
        aesthetics=AestheticsPrefs(
            design="minimal, functional",
            prose="clear over clever"
        ),
        values=[
            "intellectual honesty",
            "ethical technology",
            "joy in creation",
            "composability"
        ],
        dislikes=[
            "unnecessary jargon",
            "feature creep",
            "surveillance capitalism"
        ]
    ),
    patterns=Patterns(
        thinking=[
            "starts from first principles",
            "asks 'what would falsify this?'",
            "seeks composable abstractions"
        ],
        decision_making=[
            "prefers reversible choices",
            "values optionality"
        ],
        communication=[
            "uses analogies frequently",
            "appreciates precision in technical contexts"
        ]
    ),
    context=Context(
        current_focus="kgents specification",
        recent_interests=[
            "category theory",
            "scientific agents",
            "personal AI"
        ],
        active_projects=[
            Project(
                name="kgents",
                status="active",
                goals=["spec A/B/C/K", "reference implementation"]
            )
        ]
    )
)


class Ground(Agent[None, GroundState]):
    """
    The empirical seed.

    Type signature: Ground: Void → Facts

    Contents:
        - Persona seed: Name, roles, preferences, patterns, values
        - World seed: Date, context, active projects
        - History seed: Past decisions, established patterns

    Ground produces the irreducible facts that bootstrap the system.
    """

    def __init__(self, persona: PersonaState | None = None):
        self._persona = persona or KENT_PERSONA

    @property
    def name(self) -> str:
        return "Ground"

    @property
    def genus(self) -> str:
        return "bootstrap"

    @property
    def purpose(self) -> str:
        return "Empirical seed; irreducible facts about person and world"

    async def invoke(self, input: None = None) -> GroundState:
        """Return the ground state (persona + world)"""
        return GroundState(
            persona=self._persona,
            world=WorldState(
                date=datetime.now().isoformat(),
                runtime="claude-openrouter"
            )
        )

    def query(self, aspect: str) -> Any:
        """
        Query a specific aspect of the ground state.

        Examples:
            ground.query("preferences.communication.style")
            ground.query("patterns.thinking")
            ground.query("identity.name")
        """
        parts = aspect.split(".")
        current: Any = self._persona

        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            elif isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current


# Singleton instance with Kent's persona
ground_agent = Ground()


async def ground() -> GroundState:
    """Convenience function to get ground state"""
    return await ground_agent.invoke(None)
