"""
K-gent Persona: The interactive persona model.

K-gent is Ground projected through persona_schema:
- Queryable: Other agents ask "what would Kent prefer?"
- Composable: Provides personalization interface
- Dialogic: Four modes - reflect, advise, challenge, explore
"""

from dataclasses import dataclass, field
from typing import Any, Optional
from enum import Enum

from bootstrap.types import Agent
from bootstrap.ground import Ground, Facts


class DialogueMode(Enum):
    """The four dialogue modes of K-gent."""
    REFLECT = "reflect"    # Mirror back for examination
    ADVISE = "advise"      # Offer preference-aligned suggestions
    CHALLENGE = "challenge"  # Push back constructively
    EXPLORE = "explore"    # Help explore possibility space


@dataclass
class PersonaSeed:
    """
    The irreducible seed of K-gent.

    This is what Ground provides - raw facts about Kent.
    Cannot be derived, must be given.
    """
    name: str = "Kent"
    roles: list[str] = field(default_factory=lambda: ["researcher", "creator", "thinker"])

    # Explicit preferences
    preferences: dict[str, Any] = field(default_factory=lambda: {
        "communication": {
            "style": "direct but warm",
            "length": "concise preferred",
            "formality": "casual with substance",
        },
        "aesthetics": {
            "design": "minimal, functional",
            "prose": "clear over clever",
        },
        "values": [
            "intellectual honesty",
            "ethical technology",
            "joy in creation",
            "composability",
        ],
        "dislikes": [
            "unnecessary jargon",
            "feature creep",
            "surveillance capitalism",
        ],
    })

    # Observed patterns
    patterns: dict[str, list[str]] = field(default_factory=lambda: {
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
    })


@dataclass
class PersonaState:
    """
    Full persona state including context and confidence.

    Extends PersonaSeed with runtime state.
    """
    seed: PersonaSeed
    current_focus: str = "kgents specification"
    recent_interests: list[str] = field(default_factory=lambda: [
        "category theory",
        "scientific agents",
        "personal AI",
    ])
    active_projects: list[dict[str, Any]] = field(default_factory=lambda: [
        {
            "name": "kgents",
            "status": "active",
            "goals": ["spec A/B/C/K", "reference implementation"],
        }
    ])

    # Confidence tracking for preferences
    confidence: dict[str, float] = field(default_factory=dict)

    # Source tracking: "explicit" | "inferred" | "inherited"
    sources: dict[str, str] = field(default_factory=dict)


@dataclass
class PersonaQuery:
    """Query to K-gent for preferences/patterns."""
    aspect: str  # "preference" | "pattern" | "context" | "all"
    topic: Optional[str] = None  # Optional filter
    for_agent: Optional[str] = None  # Which agent is asking


@dataclass
class PersonaResponse:
    """Response to a persona query."""
    preferences: list[str]
    patterns: list[str]
    suggested_style: list[str]
    confidence: float = 1.0


@dataclass
class DialogueInput:
    """Input for K-gent dialogue."""
    message: str
    mode: DialogueMode = DialogueMode.REFLECT


@dataclass
class DialogueOutput:
    """Output from K-gent dialogue."""
    response: str
    mode: DialogueMode
    referenced_preferences: list[str] = field(default_factory=list)
    referenced_patterns: list[str] = field(default_factory=list)


class PersonaQueryAgent(Agent[PersonaQuery, PersonaResponse]):
    """
    Query K-gent's preferences and patterns.

    Used by other agents to personalize their behavior.
    """

    def __init__(self, state: Optional[PersonaState] = None):
        self._state = state or PersonaState(seed=PersonaSeed())

    @property
    def name(self) -> str:
        return "PersonaQuery"

    async def invoke(self, query: PersonaQuery) -> PersonaResponse:
        """Query preferences and patterns."""
        seed = self._state.seed

        preferences = []
        patterns = []
        style = []

        if query.aspect in ("preference", "all"):
            # Extract relevant preferences
            if query.topic:
                # Filter by topic
                for key, value in seed.preferences.items():
                    if query.topic.lower() in key.lower():
                        if isinstance(value, dict):
                            preferences.extend([f"{k}: {v}" for k, v in value.items()])
                        elif isinstance(value, list):
                            preferences.extend(value)
                        else:
                            preferences.append(str(value))
            else:
                # All preferences
                preferences = seed.preferences.get("values", [])

        if query.aspect in ("pattern", "all"):
            # Extract patterns
            if query.topic:
                for key, value in seed.patterns.items():
                    if query.topic.lower() in key.lower():
                        patterns.extend(value)
            else:
                # All patterns
                for pats in seed.patterns.values():
                    patterns.extend(pats)

        # Generate style suggestions based on requesting agent
        if query.for_agent:
            style = self._style_for_agent(query.for_agent)
        else:
            style = [
                seed.preferences.get("communication", {}).get("style", "direct"),
                seed.preferences.get("communication", {}).get("length", "concise"),
            ]

        return PersonaResponse(
            preferences=preferences,
            patterns=patterns,
            suggested_style=style,
            confidence=0.9,  # High confidence for explicit preferences
        )

    def _style_for_agent(self, agent: str) -> list[str]:
        """Generate style suggestions for specific agents."""
        styles = {
            "robin": [
                "be direct about uncertainty",
                "connect to first principles",
                "value falsifiability",
            ],
            "hypothesis": [
                "prefer mechanistic explanations",
                "epistemic humility",
                "ask what would disprove this",
            ],
            "creativity": [
                "expand, don't judge",
                "use analogies",
                "seek unexpected connections",
            ],
        }
        return styles.get(agent.lower(), ["be direct but warm", "prefer concise"])


class KgentAgent(Agent[DialogueInput, DialogueOutput]):
    """
    The main K-gent dialogue agent.

    Four modes:
    - REFLECT: Mirror back for examination
    - ADVISE: Offer preference-aligned suggestions
    - CHALLENGE: Push back constructively
    - EXPLORE: Help explore possibility space
    """

    def __init__(self, state: Optional[PersonaState] = None):
        self._state = state or PersonaState(seed=PersonaSeed())
        self._query_agent = PersonaQueryAgent(self._state)

    @property
    def name(self) -> str:
        return "K-gent"

    @property
    def state(self) -> PersonaState:
        return self._state

    async def invoke(self, input: DialogueInput) -> DialogueOutput:
        """
        Engage in dialogue with K-gent.

        Mode determines response style:
        - reflect: "You've said before..."
        - advise: "Your pattern is to..."
        - challenge: "That sounds like it conflicts with..."
        - explore: "Given your interest in..."
        """
        mode = input.mode
        message = input.message
        seed = self._state.seed

        # Find relevant preferences and patterns
        referenced_prefs = []
        referenced_pats = []

        # Check for preference matches
        for key, value in seed.preferences.items():
            if isinstance(value, list):
                for v in value:
                    if any(word in message.lower() for word in v.lower().split()):
                        referenced_prefs.append(v)

        # Check for pattern matches
        for category, patterns in seed.patterns.items():
            for p in patterns:
                if any(word in message.lower() for word in p.lower().split()[:3]):
                    referenced_pats.append(p)

        # Generate response based on mode
        response = self._generate_response(mode, message, referenced_prefs, referenced_pats)

        return DialogueOutput(
            response=response,
            mode=mode,
            referenced_preferences=referenced_prefs[:3],  # Limit to top 3
            referenced_patterns=referenced_pats[:3],
        )

    def _generate_response(
        self,
        mode: DialogueMode,
        message: str,
        prefs: list[str],
        pats: list[str],
    ) -> str:
        """Generate response based on mode."""
        seed = self._state.seed

        if mode == DialogueMode.REFLECT:
            if prefs or pats:
                refs = prefs[:2] + pats[:1]
                return (
                    f"You've expressed before that you value: {', '.join(refs)}. "
                    f"What about this current situation connects to those?"
                )
            return (
                "I don't see a direct connection to stated preferences. "
                "What aspect would you like to examine?"
            )

        elif mode == DialogueMode.ADVISE:
            comm_style = seed.preferences.get("communication", {}).get("style", "direct")
            if pats:
                return (
                    f"Your pattern is to {pats[0]}. "
                    f"Given that, consider: does this align with your tendency?"
                )
            return (
                f"Based on your preference for {comm_style} communication, "
                f"what's the simplest path forward here?"
            )

        elif mode == DialogueMode.CHALLENGE:
            dislikes = seed.preferences.get("dislikes", [])
            if dislikes:
                return (
                    f"This might conflict with your dislike of '{dislikes[0]}'. "
                    f"Is there a simpler approach that avoids this?"
                )
            return (
                "What would happen if you did the opposite of what you're considering? "
                "Sometimes the contrarian view reveals hidden assumptions."
            )

        elif mode == DialogueMode.EXPLORE:
            interests = self._state.recent_interests[:2]
            if interests:
                return (
                    f"Given your recent interest in {', '.join(interests)}, "
                    f"what connections do you see? What might {interests[0]} suggest here?"
                )
            return (
                "Let's explore the possibility space. "
                "What are three very different approaches to this?"
            )

        return "I'm here to help you think through this."


# Convenience functions

def kgent(state: Optional[PersonaState] = None) -> KgentAgent:
    """Create a K-gent dialogue agent."""
    return KgentAgent(state)


def query_persona(state: Optional[PersonaState] = None) -> PersonaQueryAgent:
    """Create a persona query agent."""
    return PersonaQueryAgent(state)
